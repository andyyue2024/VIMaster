"""
行业对比分析模块 - 支持同行业股票对比分析
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from src.data import MultiSourceDataProvider
from src.models.data_models import FinancialMetrics
import statistics

logger = logging.getLogger(__name__)


@dataclass
class IndustryMetrics:
    """行业指标"""
    industry_name: str
    stock_codes: List[str] = field(default_factory=list)
    avg_pe_ratio: Optional[float] = None
    avg_pb_ratio: Optional[float] = None
    avg_roe: Optional[float] = None
    avg_gross_margin: Optional[float] = None
    avg_debt_ratio: Optional[float] = None
    median_pe_ratio: Optional[float] = None
    median_pb_ratio: Optional[float] = None
    median_roe: Optional[float] = None

    stocks_metrics: Dict[str, FinancialMetrics] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "industry_name": self.industry_name,
            "stock_count": len(self.stock_codes),
            "avg_pe_ratio": self.avg_pe_ratio,
            "avg_pb_ratio": self.avg_pb_ratio,
            "avg_roe": self.avg_roe,
            "avg_gross_margin": self.avg_gross_margin,
            "avg_debt_ratio": self.avg_debt_ratio,
            "median_pe_ratio": self.median_pe_ratio,
            "median_pb_ratio": self.median_pb_ratio,
            "median_roe": self.median_roe,
        }


@dataclass
class StockIndustryComparison:
    """股票行业对比"""
    stock_code: str
    stock_name: str
    industry: str
    metrics: Optional[FinancialMetrics] = None
    industry_metrics: Optional[IndustryMetrics] = None

    # 相对于行业的评分
    pe_percentile: Optional[float] = None  # PE 在行业中的百分位
    pb_percentile: Optional[float] = None  # PB 在行业中的百分位
    roe_percentile: Optional[float] = None  # ROE 在行业中的百分位
    gross_margin_percentile: Optional[float] = None  # 毛利率在行业中的百分位

    # 相对于行业平均值的倍数
    pe_vs_industry_avg: Optional[float] = None
    pb_vs_industry_avg: Optional[float] = None
    roe_vs_industry_avg: Optional[float] = None

    # 评级
    competitiveness_score: float = 0.0  # 0-10
    valuation_score: float = 0.0  # 0-10
    growth_score: float = 0.0  # 0-10

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "industry": self.industry,
            "pe_percentile": self.pe_percentile,
            "pb_percentile": self.pb_percentile,
            "roe_percentile": self.roe_percentile,
            "pe_vs_industry_avg": self.pe_vs_industry_avg,
            "pb_vs_industry_avg": self.pb_vs_industry_avg,
            "roe_vs_industry_avg": self.roe_vs_industry_avg,
            "competitiveness_score": self.competitiveness_score,
            "valuation_score": self.valuation_score,
            "growth_score": self.growth_score,
        }


class IndustryComparator:
    """行业对比分析器"""

    # 预定义行业和代表股票
    INDUSTRY_STOCKS = {
        "白酒": ["600519", "000858", "600989"],  # 茅台、五粮液、宜宾五粮液
        "家电": ["000651", "000333", "600690"],  # 格力、美的、海尔
        "银行": ["600036", "600000", "601398"],  # 招商银行、浦发银行、工商银行
        "食品饮料": ["000858", "601933", "600298"],  # 五粮液、永辉超市、南华期货
        "房地产": ["600048", "601766", "601288"],  # 保利发展、中国中车、农业银行
        "消费": ["600688", "000651", "601888"],  # 上海石化、格力电器、中国国旅
        "医药": ["601858", "601889", "600276"],  # 中国神华、伊利股份、恒瑞医药
        "科技": ["603290", "002594", "300059"],  # 斯达半导、比亚迪、东方财富
    }

    def __init__(self, data_provider: Optional[MultiSourceDataProvider] = None):
        """
        初始化行业对比分析器
        Args:
            data_provider: 数据提供者，如果为None则创建新的 MultiSourceDataProvider
        """
        self.data_provider = data_provider or MultiSourceDataProvider()
        self.industry_cache: Dict[str, IndustryMetrics] = {}

    def get_industry_stocks(self, industry: str) -> List[str]:
        """获取行业内的股票代码"""
        return self.INDUSTRY_STOCKS.get(industry, [])

    def get_available_industries(self) -> List[str]:
        """获取所有可用的行业"""
        return list(self.INDUSTRY_STOCKS.keys())

    def analyze_industry(self, industry: str) -> Optional[IndustryMetrics]:
        """
        分析整个行业的财务指标
        Args:
            industry: 行业名称
        Returns:
            IndustryMetrics 对象
        """
        if industry in self.industry_cache:
            return self.industry_cache[industry]

        try:
            stock_codes = self.get_industry_stocks(industry)
            if not stock_codes:
                logger.warning(f"未找到行业 {industry} 的股票")
                return None

            logger.info(f"分析行业: {industry}, 股票数: {len(stock_codes)}")

            # 获取所有股票的财务指标
            metrics_list = []
            stocks_metrics = {}

            for code in stock_codes:
                try:
                    metrics = self._get_financial_metrics(code)
                    if metrics:
                        metrics_list.append(metrics)
                        stocks_metrics[code] = metrics
                except Exception as e:
                    logger.warning(f"获取 {code} 财务指标失败: {str(e)}")

            if not metrics_list:
                logger.warning(f"无法获取行业 {industry} 的任何财务指标")
                return None

            # 计算行业指标
            industry_metrics = self._calculate_industry_metrics(
                industry, stock_codes, metrics_list, stocks_metrics
            )

            # 缓存结果
            self.industry_cache[industry] = industry_metrics

            return industry_metrics
        except Exception as e:
            logger.error(f"分析行业 {industry} 失败: {str(e)}")
            return None

    def compare_stock_with_industry(
        self,
        stock_code: str,
        industry: str
    ) -> Optional[StockIndustryComparison]:
        """
        将股票与行业进行对比
        Args:
            stock_code: 股票代码
            industry: 行业名称
        Returns:
            StockIndustryComparison 对象
        """
        try:
            # 获取股票信息
            stock_metrics = self._get_financial_metrics(stock_code)
            if not stock_metrics:
                logger.warning(f"无法获取股票 {stock_code} 的财务指标")
                return None

            # 获取行业信息
            industry_metrics = self.analyze_industry(industry)
            if not industry_metrics:
                logger.warning(f"无法获取行业 {industry} 的财务指标")
                return None

            # 创建对比对象
            comparison = StockIndustryComparison(
                stock_code=stock_code,
                stock_name=stock_metrics.stock_code,  # 使用代码作为名称
                industry=industry,
                metrics=stock_metrics,
                industry_metrics=industry_metrics,
            )

            # 计算对比指标
            self._calculate_comparison_metrics(comparison)

            return comparison
        except Exception as e:
            logger.error(f"对比股票 {stock_code} 与行业 {industry} 失败: {str(e)}")
            return None

    def rank_stocks_in_industry(self, industry: str) -> List[tuple]:
        """
        对行业内的股票进行排名
        Args:
            industry: 行业名称
        Returns:
            排名列表 [(stock_code, score, metrics), ...]
        """
        try:
            stock_codes = self.get_industry_stocks(industry)
            comparisons = []

            for code in stock_codes:
                comparison = self.compare_stock_with_industry(code, industry)
                if comparison:
                    # 计算综合评分
                    score = (
                        comparison.competitiveness_score * 0.4 +
                        comparison.valuation_score * 0.3 +
                        comparison.growth_score * 0.3
                    )
                    comparisons.append((code, score, comparison.metrics))

            # 按评分降序排列
            comparisons.sort(key=lambda x: x[1], reverse=True)

            return comparisons
        except Exception as e:
            logger.error(f"排名行业 {industry} 的股票失败: {str(e)}")
            return []

    def compare_multiple_industries(self, industries: List[str]) -> Dict[str, IndustryMetrics]:
        """
        对比多个行业
        Args:
            industries: 行业名称列表
        Returns:
            行业指标字典
        """
        results = {}
        for industry in industries:
            metrics = self.analyze_industry(industry)
            if metrics:
                results[industry] = metrics
        return results

    def _get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """获取股票财务指标"""
        try:
            return self.data_provider.get_financial_metrics(stock_code)
        except Exception as e:
            logger.warning(f"获取 {stock_code} 财务指标失败: {str(e)}")
            return None

    def _calculate_industry_metrics(
        self,
        industry_name: str,
        stock_codes: List[str],
        metrics_list: List[FinancialMetrics],
        stocks_metrics: Dict[str, FinancialMetrics]
    ) -> IndustryMetrics:
        """计算行业指标"""
        # 提取有效的数值
        pe_ratios = [m.pe_ratio for m in metrics_list if m.pe_ratio and m.pe_ratio > 0]
        pb_ratios = [m.pb_ratio for m in metrics_list if m.pb_ratio and m.pb_ratio > 0]
        roes = [m.roe for m in metrics_list if m.roe and m.roe > 0]
        margins = [m.gross_margin for m in metrics_list if m.gross_margin and m.gross_margin > 0]
        debt_ratios = [m.debt_ratio for m in metrics_list if m.debt_ratio is not None and m.debt_ratio >= 0]

        # 计算平均值
        industry_metrics = IndustryMetrics(
            industry_name=industry_name,
            stock_codes=stock_codes,
            avg_pe_ratio=statistics.mean(pe_ratios) if pe_ratios else None,
            avg_pb_ratio=statistics.mean(pb_ratios) if pb_ratios else None,
            avg_roe=statistics.mean(roes) if roes else None,
            avg_gross_margin=statistics.mean(margins) if margins else None,
            avg_debt_ratio=statistics.mean(debt_ratios) if debt_ratios else None,
            median_pe_ratio=statistics.median(pe_ratios) if pe_ratios else None,
            median_pb_ratio=statistics.median(pb_ratios) if pb_ratios else None,
            median_roe=statistics.median(roes) if roes else None,
            stocks_metrics=stocks_metrics,
        )

        return industry_metrics

    def _calculate_comparison_metrics(self, comparison: StockIndustryComparison) -> None:
        """计算对比指标"""
        metrics = comparison.metrics
        industry = comparison.industry_metrics

        if not metrics or not industry:
            return

        # PE 百分位（较低较好）
        if metrics.pe_ratio and industry.avg_pe_ratio:
            comparison.pe_vs_industry_avg = metrics.pe_ratio / industry.avg_pe_ratio
            comparison.pe_percentile = self._calculate_percentile(
                metrics.pe_ratio,
                [m.pe_ratio for m in industry.stocks_metrics.values()
                 if m.pe_ratio and m.pe_ratio > 0],
                higher_is_better=False
            )

        # PB 百分位（较低较好）
        if metrics.pb_ratio and industry.avg_pb_ratio:
            comparison.pb_vs_industry_avg = metrics.pb_ratio / industry.avg_pb_ratio
            comparison.pb_percentile = self._calculate_percentile(
                metrics.pb_ratio,
                [m.pb_ratio for m in industry.stocks_metrics.values()
                 if m.pb_ratio and m.pb_ratio > 0],
                higher_is_better=False
            )

        # ROE 百分位（较高较好）
        if metrics.roe and industry.avg_roe:
            comparison.roe_vs_industry_avg = metrics.roe / industry.avg_roe
            comparison.roe_percentile = self._calculate_percentile(
                metrics.roe,
                [m.roe for m in industry.stocks_metrics.values()
                 if m.roe and m.roe > 0],
                higher_is_better=True
            )

        # 计算竞争力评分（基于 ROE）
        if comparison.roe_percentile is not None:
            comparison.competitiveness_score = comparison.roe_percentile * 10

        # 计算估值评分（基于 PE 和 PB）
        pe_score = (100 - (comparison.pe_percentile or 50)) / 10 if comparison.pe_percentile else 5
        pb_score = (100 - (comparison.pb_percentile or 50)) / 10 if comparison.pb_percentile else 5
        comparison.valuation_score = (pe_score + pb_score) / 2

        # 计算成长评分（基于 ROE vs 行业平均）
        if comparison.roe_vs_industry_avg:
            growth_ratio = min(comparison.roe_vs_industry_avg, 2.0) / 2 * 10
            comparison.growth_score = growth_ratio
        else:
            comparison.growth_score = 5.0

    @staticmethod
    def _calculate_percentile(
        value: float,
        values: List[float],
        higher_is_better: bool = True
    ) -> float:
        """
        计算百分位
        Args:
            value: 目标值
            values: 所有值列表
            higher_is_better: 值越大越好
        Returns:
            0-100 的百分位
        """
        if not values:
            return 50.0

        sorted_values = sorted(values)
        rank = sum(1 for v in sorted_values if (v < value if higher_is_better else v > value))
        percentile = (rank / len(sorted_values)) * 100

        return percentile if higher_is_better else (100 - percentile)

