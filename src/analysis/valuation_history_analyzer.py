"""
历史估值对比模块 - 分析股票的历史估值变化
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from src.data import MultiSourceDataProvider
from src.models.data_models import FinancialMetrics
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ValuationPoint:
    """估值数据点"""
    date: datetime
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    price: Optional[float] = None
    roe: Optional[float] = None


@dataclass
class ValuationTrend:
    """估值趋势"""
    stock_code: str
    stock_name: str
    data_points: List[ValuationPoint] = field(default_factory=list)

    # 统计指标
    avg_pe_ratio: Optional[float] = None
    min_pe_ratio: Optional[float] = None
    max_pe_ratio: Optional[float] = None
    median_pe_ratio: Optional[float] = None
    std_dev_pe: Optional[float] = None

    avg_pb_ratio: Optional[float] = None
    min_pb_ratio: Optional[float] = None
    max_pb_ratio: Optional[float] = None

    avg_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    # 估值评级
    current_valuation_grade: str = "未评级"  # 便宜、合理、贵
    historical_avg_grade: str = "未评级"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "data_points": len(self.data_points),
            "avg_pe_ratio": self.avg_pe_ratio,
            "min_pe_ratio": self.min_pe_ratio,
            "max_pe_ratio": self.max_pe_ratio,
            "current_valuation_grade": self.current_valuation_grade,
            "historical_avg_grade": self.historical_avg_grade,
        }


@dataclass
class ValuationComparison:
    """估值对比"""
    stock_code: str
    current_pe: Optional[float] = None
    historical_avg_pe: Optional[float] = None
    pe_vs_avg: Optional[float] = None  # 当前PE / 历史平均PE
    valuation_percentile: Optional[float] = None  # 当前估值在历史中的百分位

    # 建议
    valuation_signal: str = "持有"  # 买入、持有、卖出
    signal_confidence: float = 0.0  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "stock_code": self.stock_code,
            "current_pe": self.current_pe,
            "historical_avg_pe": self.historical_avg_pe,
            "pe_vs_avg": self.pe_vs_avg,
            "valuation_percentile": self.valuation_percentile,
            "valuation_signal": self.valuation_signal,
            "signal_confidence": self.signal_confidence,
        }


class ValuationAnalyzer:
    """历史估值对比分析器"""

    def __init__(self, data_provider: Optional[MultiSourceDataProvider] = None):
        """
        初始化估值分析器
        Args:
            data_provider: 数据提供者
        """
        self.data_provider = data_provider or MultiSourceDataProvider()
        self.valuation_cache: Dict[str, ValuationTrend] = {}

    def analyze_valuation_history(
        self,
        stock_code: str,
        days: int = 365
    ) -> Optional[ValuationTrend]:
        """
        分析股票的历史估值
        Args:
            stock_code: 股票代码
            days: 分析天数
        Returns:
            ValuationTrend 对象
        """
        if stock_code in self.valuation_cache:
            return self.valuation_cache[stock_code]

        try:
            logger.info(f"分析 {stock_code} 的历史估值，周期: {days} 天")

            # 获取历史价格数据
            price_data = self._get_historical_price(stock_code, days)
            if not price_data:
                logger.warning(f"无法获取 {stock_code} 的历史价格")
                return None

            # 获取当前财务指标
            current_metrics = self._get_financial_metrics(stock_code)
            if not current_metrics:
                logger.warning(f"无法获取 {stock_code} 的财务指标")
                return None

            # 创建估值趋势对象
            trend = ValuationTrend(
                stock_code=stock_code,
                stock_name=stock_code,  # 使用代码作为名称
            )

            # 构建数据点
            for date, price in price_data:
                point = ValuationPoint(
                    date=date,
                    price=price,
                    pe_ratio=self._calculate_pe(price, current_metrics),
                    pb_ratio=self._calculate_pb(price, current_metrics),
                    roe=current_metrics.roe,
                )
                trend.data_points.append(point)

            # 计算统计指标
            self._calculate_trend_statistics(trend)

            # 评级
            self._grade_valuation(trend)

            # 缓存结果
            self.valuation_cache[stock_code] = trend

            return trend
        except Exception as e:
            logger.error(f"分析 {stock_code} 的历史估值失败: {str(e)}")
            return None

    def compare_valuation_history(
        self,
        stock_code: str,
        days: int = 365
    ) -> Optional[ValuationComparison]:
        """
        对比股票的当前估值与历史平均值
        Args:
            stock_code: 股票代码
            days: 分析天数
        Returns:
            ValuationComparison 对象
        """
        try:
            # 获取估值趋势
            trend = self.analyze_valuation_history(stock_code, days)
            if not trend:
                return None

            # 获取当前PE
            current_metrics = self._get_financial_metrics(stock_code)
            if not current_metrics or not current_metrics.pe_ratio:
                return None

            # 创建对比对象
            comparison = ValuationComparison(
                stock_code=stock_code,
                current_pe=current_metrics.pe_ratio,
                historical_avg_pe=trend.avg_pe_ratio,
            )

            # 计算相对值
            if trend.avg_pe_ratio and trend.avg_pe_ratio > 0:
                comparison.pe_vs_avg = current_metrics.pe_ratio / trend.avg_pe_ratio

                # 计算百分位
                pe_list = [p.pe_ratio for p in trend.data_points
                          if p.pe_ratio and p.pe_ratio > 0]
                if pe_list:
                    comparison.valuation_percentile = self._calculate_percentile(
                        current_metrics.pe_ratio, pe_list
                    )

            # 生成信号
            self._generate_valuation_signal(comparison, trend)

            return comparison
        except Exception as e:
            logger.error(f"对比 {stock_code} 的历史估值失败: {str(e)}")
            return None

    def compare_stocks_valuation(
        self,
        stock_codes: List[str],
        days: int = 365
    ) -> List[ValuationComparison]:
        """
        对比多只股票的历史估值
        Args:
            stock_codes: 股票代码列表
            days: 分析天数
        Returns:
            对比结果列表
        """
        results = []
        for code in stock_codes:
            comparison = self.compare_valuation_history(code, days)
            if comparison:
                results.append(comparison)
        return results

    def get_valuation_statistics(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取估值统计信息
        Args:
            stock_code: 股票代码
        Returns:
            统计信息字典
        """
        trend = self.valuation_cache.get(stock_code)
        if not trend:
            trend = self.analyze_valuation_history(stock_code)

        if not trend:
            return None

        return {
            "stock_code": stock_code,
            "data_points": len(trend.data_points),
            "pe_stats": {
                "avg": trend.avg_pe_ratio,
                "min": trend.min_pe_ratio,
                "max": trend.max_pe_ratio,
                "median": trend.median_pe_ratio,
                "std_dev": trend.std_dev_pe,
            },
            "pb_stats": {
                "avg": trend.avg_pb_ratio,
                "min": trend.min_pb_ratio,
                "max": trend.max_pb_ratio,
            },
            "price_stats": {
                "avg": trend.avg_price,
                "min": trend.min_price,
                "max": trend.max_price,
            },
        }

    # 辅助方法

    def _get_historical_price(
        self,
        stock_code: str,
        days: int
    ) -> Optional[List[Tuple[datetime, float]]]:
        """获取历史价格数据"""
        try:
            df = self.data_provider.get_historical_price(stock_code, days)

            if df is None or df.empty:
                return None

            price_list = []
            for _, row in df.iterrows():
                try:
                    date = datetime.strptime(str(row.get('date', '')), '%Y%m%d')
                    price = float(row.get('close', 0))
                    if price > 0:
                        price_list.append((date, price))
                except:
                    continue

            return price_list if price_list else None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 历史价格失败: {str(e)}")
            return None

    def _get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """获取财务指标"""
        try:
            return self.data_provider.get_financial_metrics(stock_code)
        except Exception as e:
            logger.warning(f"获取 {stock_code} 财务指标失败: {str(e)}")
            return None

    @staticmethod
    def _calculate_pe(price: float, metrics: FinancialMetrics) -> Optional[float]:
        """计算PE"""
        if metrics.earnings_per_share and metrics.earnings_per_share > 0:
            return price / metrics.earnings_per_share
        return metrics.pe_ratio

    @staticmethod
    def _calculate_pb(price: float, metrics: FinancialMetrics) -> Optional[float]:
        """计算PB"""
        if metrics.book_value_per_share and metrics.book_value_per_share > 0:
            return price / metrics.book_value_per_share
        return metrics.pb_ratio

    @staticmethod
    def _calculate_trend_statistics(trend: ValuationTrend) -> None:
        """计算趋势统计"""
        pe_list = [p.pe_ratio for p in trend.data_points if p.pe_ratio and p.pe_ratio > 0]
        pb_list = [p.pb_ratio for p in trend.data_points if p.pb_ratio and p.pb_ratio > 0]
        price_list = [p.price for p in trend.data_points if p.price and p.price > 0]

        # PE统计
        if pe_list:
            trend.avg_pe_ratio = statistics.mean(pe_list)
            trend.min_pe_ratio = min(pe_list)
            trend.max_pe_ratio = max(pe_list)
            trend.median_pe_ratio = statistics.median(pe_list)
            if len(pe_list) > 1:
                trend.std_dev_pe = statistics.stdev(pe_list)

        # PB统计
        if pb_list:
            trend.avg_pb_ratio = statistics.mean(pb_list)
            trend.min_pb_ratio = min(pb_list)
            trend.max_pb_ratio = max(pb_list)

        # 价格统计
        if price_list:
            trend.avg_price = statistics.mean(price_list)
            trend.min_price = min(price_list)
            trend.max_price = max(price_list)

    @staticmethod
    def _grade_valuation(trend: ValuationTrend) -> None:
        """评级估值"""
        if not trend.data_points:
            return

        latest_point = trend.data_points[0]

        # 当前估值评级
        if trend.avg_pe_ratio and latest_point.pe_ratio:
            ratio = latest_point.pe_ratio / trend.avg_pe_ratio
            if ratio < 0.8:
                trend.current_valuation_grade = "便宜"
            elif ratio > 1.2:
                trend.current_valuation_grade = "贵"
            else:
                trend.current_valuation_grade = "合理"

    @staticmethod
    def _calculate_percentile(value: float, values: List[float]) -> float:
        """计算百分位"""
        if not values:
            return 50.0

        sorted_values = sorted(values)
        rank = sum(1 for v in sorted_values if v < value)
        return (rank / len(sorted_values)) * 100

    @staticmethod
    def _generate_valuation_signal(
        comparison: ValuationComparison,
        trend: ValuationTrend
    ) -> None:
        """生成估值信号"""
        if not comparison.pe_vs_avg:
            return

        # 基于PE vs 平均的倍数
        if comparison.pe_vs_avg < 0.7:
            comparison.valuation_signal = "买入"
            comparison.signal_confidence = 0.9
        elif comparison.pe_vs_avg < 0.9:
            comparison.valuation_signal = "买入"
            comparison.signal_confidence = 0.7
        elif comparison.pe_vs_avg < 1.1:
            comparison.valuation_signal = "持有"
            comparison.signal_confidence = 0.6
        elif comparison.pe_vs_avg < 1.3:
            comparison.valuation_signal = "持有"
            comparison.signal_confidence = 0.7
        else:
            comparison.valuation_signal = "卖出"
            comparison.signal_confidence = 0.8
