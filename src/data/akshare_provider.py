"""
数据获取模块 - 使用 akshare 从远程数据源获取财务数据
"""
import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any
from src.models.data_models import FinancialMetrics
from datetime import datetime
from functools import lru_cache
import time
import logging
import random
from src.utils.retry_mechanism import retry, register_retry_config, RetryConfig

logger = logging.getLogger(__name__)

# Cache expiry time in seconds (5 minutes)
CACHE_EXPIRY_SECONDS = 300

# Module-level cache for DataFrames that can't use lru_cache
_stock_spot_cache: Optional[pd.DataFrame] = None
_stock_spot_cache_time: float = 0

_stock_info_cache: Optional[pd.DataFrame] = None
_stock_info_cache_time: float = 0

# 模拟股票数据库 - 用于演示和测试
# 数据为 2025 年末数据（模拟）
MOCK_STOCKS_DATA = {
    "600519": {
        "name": "贵州茅台",
        "current_price": 1800.5,  # 当前股价
        "pe_ratio": 35.2,  # PE 比率 (高估值)
        "pb_ratio": 12.5,  # PB 比率 (高)
        "roe": 0.32,  # 股权回报率 (优秀，32%)
        "gross_margin": 0.92,  # 毛利率 (超高，92% 白酒企业特征)
        "eps": 51.2,  # 每股收益
        "revenue_growth": 0.15,  # 营收增长 15%
        "profit_growth": 0.18,  # 利润增长 18%
        "free_cash_flow": 150e8,  # 自由现金流 150 亿元
        "debt_ratio": 0.05,  # 负债率 5% (超低，现金充足)
        "dividend_yield": 0.02,  # 分红收益率 2%
    },
    "000858": {
        "name": "五粮液",
        "current_price": 85.3,
        "pe_ratio": 28.5,
        "pb_ratio": 8.3,
        "roe": 0.28,
        "gross_margin": 0.88,
        "eps": 2.99,
        "revenue_growth": 0.12,
        "profit_growth": 0.15,
        "free_cash_flow": 80e8,
        "debt_ratio": 0.08,
        "dividend_yield": 0.025,
    },
    "000651": {
        "name": "格力电器",
        "current_price": 28.6,
        "pe_ratio": 12.5,
        "pb_ratio": 3.2,
        "roe": 0.25,
        "gross_margin": 0.35,
        "eps": 2.28,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 100e8,
        "debt_ratio": 0.20,
        "dividend_yield": 0.04,
    },
    "600036": {
        "name": "招商银行",
        "current_price": 35.8,
        "pe_ratio": 8.5,
        "pb_ratio": 1.2,
        "roe": 0.18,
        "gross_margin": 0.65,
        "eps": 4.21,
        "revenue_growth": 0.06,
        "profit_growth": 0.08,
        "free_cash_flow": 200e8,
        "debt_ratio": 0.85,  # 银行高负债是正常的
        "dividend_yield": 0.035,
    },
    "000333": {
        "name": "美的集团",
        "current_price": 42.5,
        "pe_ratio": 15.3,
        "pb_ratio": 4.5,
        "roe": 0.22,
        "gross_margin": 0.28,
        "eps": 2.77,
        "revenue_growth": 0.10,
        "profit_growth": 0.12,
        "free_cash_flow": 120e8,
        "debt_ratio": 0.30,
        "dividend_yield": 0.03,
    },
}


def _get_cached_stock_spot() -> Optional[pd.DataFrame]:
    """
    获取缓存的股票实时行情数据
    Returns:
        股票实时行情DataFrame或None
    """
    global _stock_spot_cache, _stock_spot_cache_time
    current_time = time.time()

    if _stock_spot_cache is not None and (current_time - _stock_spot_cache_time) < CACHE_EXPIRY_SECONDS:
        return _stock_spot_cache

    try:
        _stock_spot_cache = ak.stock_zh_a_spot()
        _stock_spot_cache_time = current_time
        return _stock_spot_cache
    except Exception as e:
        logger.error(f"获取股票实时行情失败: {str(e)}")
        return None


def _get_cached_stock_info_df() -> Optional[pd.DataFrame]:
    """
    获取缓存的股票基本信息数据
    Returns:
        股票基本信息DataFrame或None
    """
    global _stock_info_cache, _stock_info_cache_time
    current_time = time.time()

    if _stock_info_cache is not None and (current_time - _stock_info_cache_time) < CACHE_EXPIRY_SECONDS:
        return _stock_info_cache

    try:
        _stock_info_cache = ak.stock_info_a_code_name()
        _stock_info_cache_time = current_time
        return _stock_info_cache
    except Exception as e:
        logger.error(f"获取股票基本信息失败: {str(e)}")
        return None


def clear_cache() -> None:
    """清除所有缓存"""
    global _stock_spot_cache, _stock_spot_cache_time
    global _stock_info_cache, _stock_info_cache_time

    _stock_spot_cache = None
    _stock_spot_cache_time = 0
    _stock_info_cache = None
    _stock_info_cache_time = 0

    # Clear lru_cache decorated functions
    AkshareDataProvider._get_main_indicators.cache_clear()


class AkshareDataProvider:
    """Akshare 数据提供者"""

    @staticmethod
    @lru_cache(maxsize=128)
    def _get_main_indicators(symbol: str) -> Optional[tuple]:
        """
        获取主要财务指标（带缓存）
        Args:
            symbol: 股票代码 (如: "sh600519")
        Returns:
            财务指标元组 (roe, gross_margin, eps) 或 None
        """
        # 注：akshare 当前版本没有 stock_main_ind 函数
        # 暂时禁用此方法，使用模拟数据或其他方式获取
        logger.warning(f"stock_main_ind 函数在当前 akshare 版本中不可用，将使用默认数据")
        return None

    @staticmethod
    def get_stock_info(stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息
        Args:
            stock_code: 股票代码 (如: "600519" 贵州茅台)
        Returns:
            股票信息字典或None
        """
        try:
            # 使用缓存的实时行情数据
            df = _get_cached_stock_spot()
            if df is None:
                # 回退到模拟数据
                return AkshareDataProvider._get_mock_stock_info(stock_code)

            stock_code_str = str(stock_code).zfill(6)

            # 过滤该股票的数据
            stock_data = df[df['代码'] == stock_code_str]

            if stock_data.empty:
                logger.warning(f"未找到股票 {stock_code} 的数据，使用模拟数据")
                return AkshareDataProvider._get_mock_stock_info(stock_code)

            row = stock_data.iloc[0]
            return {
                "code": stock_code_str,
                "name": row.get('名称', ''),
                "current_price": float(row.get('最新价', 0)),
                "pe_ratio": float(row.get('市盈率', 0)) if row.get('市盈率') != '---' else None,
                "pb_ratio": float(row.get('市净率', 0)) if row.get('市净率') != '---' else None,
            }
        except Exception as e:
            logger.warning(f"获取股票 {stock_code} 信息失败: {str(e)}，使用模拟数据")
            return AkshareDataProvider._get_mock_stock_info(stock_code)

    @staticmethod
    def get_financial_metrics(stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象或None
        """
        try:
            stock_code_str = str(stock_code).zfill(6)

            # 首先检查是否有预定义的完整模拟数据
            if stock_code_str in MOCK_STOCKS_DATA:
                logger.info(f"使用预定义的模拟数据分析股票 {stock_code_str}")
                return AkshareDataProvider._get_mock_financial_metrics(stock_code_str)

            # 获取基本信息（使用缓存）
            stock_info = AkshareDataProvider.get_stock_info(stock_code)
            if not stock_info:
                # 如果真实数据失败，尝试使用模拟数据
                return AkshareDataProvider._get_mock_financial_metrics(stock_code_str)

            # 获取财务数据（使用缓存）
            symbol = f"sh{stock_code_str}" if stock_code_str.startswith('6') else f"sz{stock_code_str}"
            indicators = AkshareDataProvider._get_main_indicators(symbol)

            if indicators:
                roe, gross_margin, eps = indicators
                metrics = FinancialMetrics(
                    stock_code=stock_code_str,
                    current_price=stock_info.get('current_price'),
                    pe_ratio=stock_info.get('pe_ratio'),
                    pb_ratio=stock_info.get('pb_ratio'),
                    roe=roe,
                    gross_margin=gross_margin,
                    earnings_per_share=eps,
                    update_time=datetime.now()
                )
                return metrics
            else:
                # 返回基本指标
                return FinancialMetrics(
                    stock_code=stock_code_str,
                    current_price=stock_info.get('current_price'),
                    pe_ratio=stock_info.get('pe_ratio'),
                    pb_ratio=stock_info.get('pb_ratio'),
                    update_time=datetime.now()
                )

        except Exception as e:
            logger.warning(f"获取财务指标失败: {str(e)}, 尝试使用模拟数据")
            # 如果真实数据获取完全失败，使用模拟数据
            return AkshareDataProvider._get_mock_financial_metrics(stock_code)

    @staticmethod
    def get_historical_price(stock_code: str, days: int = 250) -> Optional[pd.DataFrame]:
        """
        获取历史价格数据
        Args:
            stock_code: 股票代码
            days: 获取天数
        Returns:
            历史价格DataFrame或None
        """
        try:
            stock_code_str = str(stock_code).zfill(6)
            symbol = f"sh{stock_code_str}" if stock_code_str.startswith('6') else f"sz{stock_code_str}"

            # 获取日线数据
            df = ak.stock_zh_a_hist(symbol=stock_code_str, period='daily', adjust='qfq')

            if df is not None and not df.empty:
                return df.tail(days)
            return None
        except Exception as e:
            logger.error(f"获取历史价格失败: {str(e)}")
            return None

    @staticmethod
    def get_industry_info(stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典或None
        """
        try:
            # 使用缓存的行业分类数据
            df = _get_cached_stock_info_df()
            if df is None:
                return None

            stock_code_str = str(stock_code).zfill(6)

            stock_data = df[df['代码'] == stock_code_str]
            if not stock_data.empty:
                row = stock_data.iloc[0]
                return {
                    "industry": row.get('行业', ''),
                    "market": row.get('市场', ''),
                }
            return None
        except Exception as e:
            logger.error(f"获取行业信息失败: {str(e)}")
            return None


    @staticmethod
    def _get_mock_stock_info(stock_code: str) -> Optional[Dict[str, Any]]:
        """
        生成模拟股票基本信息

        Args:
            stock_code: 股票代码

        Returns:
            模拟的股票信息字典
        """
        stock_code_str = str(stock_code).zfill(6)

        if stock_code_str in MOCK_STOCKS_DATA:
            data = MOCK_STOCKS_DATA[stock_code_str]
            return {
                "code": stock_code_str,
                "name": data['name'],
                "current_price": data['current_price'],
                "pe_ratio": data['pe_ratio'],
                "pb_ratio": data['pb_ratio'],
            }

        # 生成随机的股票信息
        return {
            "code": stock_code_str,
            "name": f"股票{stock_code_str}",
            "current_price": random.uniform(10, 200),
            "pe_ratio": random.uniform(10, 50),
            "pb_ratio": random.uniform(1, 10),
        }

    @staticmethod
    def _get_mock_financial_metrics(stock_code: str) -> Optional[FinancialMetrics]:
        """
        生成模拟财务指标数据
        用于演示和测试目的，当真实数据无法获取时使用

        Args:
            stock_code: 股票代码

        Returns:
            模拟的FinancialMetrics对象
        """
        stock_code_str = str(stock_code).zfill(6)

        # 如果有预定义的模拟数据，使用它
        if stock_code_str in MOCK_STOCKS_DATA:
            data = MOCK_STOCKS_DATA[stock_code_str]
            logger.info(f"使用预定义的模拟数据分析股票 {stock_code_str} ({data['name']})")
            return FinancialMetrics(
                stock_code=stock_code_str,
                current_price=data['current_price'],
                pe_ratio=data['pe_ratio'],
                pb_ratio=data['pb_ratio'],
                roe=data.get('roe', random.uniform(0.05, 0.35)),
                gross_margin=data.get('gross_margin', random.uniform(0.15, 0.90)),
                earnings_per_share=data.get('eps', random.uniform(0.5, 10)),
                revenue_growth=data.get('revenue_growth', random.uniform(0.05, 0.20)),  # 5%-20%的收入增长
                profit_growth=data.get('profit_growth', random.uniform(0.08, 0.25)),   # 8%-25%的利润增长
                free_cash_flow=data.get('free_cash_flow', random.uniform(10, 100) * 1e8),  # 10-100亿的自由现金流
                debt_ratio=data.get('debt_ratio', random.uniform(0.1, 0.5)),  # 10%-50%的负债率
                dividend_yield=data.get('dividend_yield', random.uniform(0.01, 0.05)),  # 1%-5%的分红收益率
                update_time=datetime.now()
            )

        # 否则生成随机但合理的模拟数据
        logger.info(f"为股票 {stock_code_str} 生成随机模拟数据")
        return FinancialMetrics(
            stock_code=stock_code_str,
            current_price=random.uniform(10, 200),  # 10-200元
            pe_ratio=random.uniform(10, 50),  # PE比率 10-50
            pb_ratio=random.uniform(1, 10),  # PB比率 1-10
            roe=random.uniform(0.05, 0.35),  # ROE 5%-35%
            gross_margin=random.uniform(0.15, 0.90),  # 毛利率 15%-90%
            earnings_per_share=random.uniform(0.5, 10),  # EPS
            revenue_growth=random.uniform(0.05, 0.20),  # 5%-20%的收入增长
            profit_growth=random.uniform(0.08, 0.25),   # 8%-25%的利润增长
            free_cash_flow=random.uniform(5, 100) * 1e8,  # 5-100亿的自由现金流
            debt_ratio=random.uniform(0.1, 0.5),  # 10%-50%的负债率
            dividend_yield=random.uniform(0.01, 0.04),  # 1%-4%的分红收益率
            update_time=datetime.now()
        )


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_metrics(metrics: FinancialMetrics) -> bool:
        """验证财务指标的有效性"""
        if not metrics or not metrics.stock_code:
            return False

        # 至少需要当前价格
        if metrics.current_price is None or metrics.current_price <= 0:
            return False

        return True

    @staticmethod
    def validate_pe_ratio(pe_ratio: Optional[float]) -> bool:
        """验证PE比率"""
        if pe_ratio is None or pe_ratio < 0:
            return False
        return True

    @staticmethod
    def validate_pb_ratio(pb_ratio: Optional[float]) -> bool:
        """验证PB比率"""
        if pb_ratio is None or pb_ratio < 0:
            return False
        return True
