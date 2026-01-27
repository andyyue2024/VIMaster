"""
数据获取模块 - 使用 akshare 从东方财富数据源获取财务数据
"""
import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any
from src.models.data_models import FinancialMetrics
from datetime import datetime
from functools import lru_cache
import time
import logging
from src.utils.retry_mechanism import retry, register_retry_config, RetryConfig
from src.data.data_source_base import BaseDataSource, DataSourceType

logger = logging.getLogger(__name__)

# Cache expiry time in seconds (5 minutes)
CACHE_EXPIRY_SECONDS = 300

# Module-level cache for DataFrames that can't use lru_cache
_stock_spot_em_cache: Optional[pd.DataFrame] = None
_stock_spot_em_cache_time: float = 0

_stock_info_cache: Optional[pd.DataFrame] = None
_stock_info_cache_time: float = 0

# 东方财富行业分类缓存
_industry_board_cache: Optional[pd.DataFrame] = None
_industry_board_cache_time: float = 0



def _get_cached_stock_spot_em() -> Optional[pd.DataFrame]:
    """
    获取缓存的东方财富股票实时行情数据
    使用东方财富接口: stock_zh_a_spot_em
    Returns:
        股票实时行情DataFrame或None
    """
    global _stock_spot_em_cache, _stock_spot_em_cache_time
    current_time = time.time()

    if _stock_spot_em_cache is not None and (current_time - _stock_spot_em_cache_time) < CACHE_EXPIRY_SECONDS:
        return _stock_spot_em_cache

    try:
        # 使用东方财富接口获取 A 股实时行情
        _stock_spot_em_cache = ak.stock_zh_a_spot_em()
        _stock_spot_em_cache_time = current_time
        logger.info("成功从东方财富获取 A 股实时行情数据")
        return _stock_spot_em_cache
    except Exception as e:
        logger.error(f"从东方财富获取股票实时行情失败: {str(e)}")
        return None


def _get_cached_stock_spot() -> Optional[pd.DataFrame]:
    """
    获取缓存的股票实时行情数据（兼容旧接口）
    优先使用东方财富接口
    Returns:
        股票实时行情DataFrame或None
    """
    # 优先使用东方财富接口
    df = _get_cached_stock_spot_em()
    if df is not None:
        return df

    # 回退到原始接口
    global _stock_spot_em_cache, _stock_spot_em_cache_time
    current_time = time.time()

    try:
        _stock_spot_em_cache = ak.stock_zh_a_spot()
        _stock_spot_em_cache_time = current_time
        return _stock_spot_em_cache
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


def _get_cached_industry_board_em() -> Optional[pd.DataFrame]:
    """
    获取缓存的东方财富行业板块数据
    Returns:
        行业板块DataFrame或None
    """
    global _industry_board_cache, _industry_board_cache_time
    current_time = time.time()

    if _industry_board_cache is not None and (current_time - _industry_board_cache_time) < CACHE_EXPIRY_SECONDS:
        return _industry_board_cache

    try:
        # 东方财富行业板块
        _industry_board_cache = ak.stock_board_industry_name_em()
        _industry_board_cache_time = current_time
        logger.info("成功从东方财富获取行业板块数据")
        return _industry_board_cache
    except Exception as e:
        logger.error(f"从东方财富获取行业板块失败: {str(e)}")
        return None


def clear_cache() -> None:
    """清除所有缓存"""
    global _stock_spot_em_cache, _stock_spot_em_cache_time
    global _stock_info_cache, _stock_info_cache_time
    global _industry_board_cache, _industry_board_cache_time

    _stock_spot_em_cache = None
    _stock_spot_em_cache_time = 0
    _stock_info_cache = None
    _stock_info_cache_time = 0
    _industry_board_cache = None
    _industry_board_cache_time = 0

    # Clear lru_cache decorated functions
    AkshareDataProvider._get_main_indicators.cache_clear()
    AkshareDataProvider._get_individual_info_em.cache_clear()
    AkshareDataProvider._get_financial_indicator_em.cache_clear()


class AkshareDataProvider(BaseDataSource):
    """
    Akshare 数据提供者 - 使用东方财富数据接口
    """

    def __init__(self):
        super().__init__("AkShare", DataSourceType.AKSHARE)
        self.is_available = True

    def _test_connection(self) -> bool:
        return True

    # ---- 业务接口 -----------------------------------------------------
    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息 - 使用东方财富接口
        Args:
            stock_code: 股票代码 (如: "600519" 贵州茅台)
        Returns:
            股票信息字典或None
        """
        try:
            stock_code_str = str(stock_code).zfill(6)
            df = _get_cached_stock_spot_em()
            if df is not None and not df.empty:
                code_col = '代码' if '代码' in df.columns else 'code'
                stock_data = df[df[code_col] == stock_code_str]
                if not stock_data.empty:
                    row = stock_data.iloc[0]

                    # 东方财富接口字段映射
                    name = row.get('名称', row.get('name', ''))
                    current_price = row.get('最新价', row.get('close', 0))
                    pe_ratio = row.get('市盈率-动态', row.get('pe', None))
                    pb_ratio = row.get('市净率', row.get('pb', None))

                    # 额外的东方财富数据
                    change_percent = row.get('涨跌幅', row.get('pct_chg', 0))
                    volume = row.get('成交量', row.get('volume', 0))
                    amount = row.get('成交额', row.get('amount', 0))
                    high = row.get('最高', row.get('high', 0))
                    low = row.get('最低', row.get('low', 0))
                    open_price = row.get('今开', row.get('open', 0))

                    return {
                        "code": stock_code_str,
                        "name": name,
                        "current_price": float(current_price) if current_price else None,
                        "pe_ratio": float(pe_ratio) if pe_ratio and pe_ratio not in ('---', '-') else None,
                        "pb_ratio": float(pb_ratio) if pb_ratio and pb_ratio not in ('---', '-') else None,
                        "change_percent": float(change_percent) if change_percent else 0,
                        "volume": float(volume) if volume else 0,
                        "amount": float(amount) if amount else 0,
                        "high": float(high) if high else None,
                        "low": float(low) if low else None,
                        "open": float(open_price) if open_price else None,
                        "source": "eastmoney"  # 标记数据来源
                    }

            # 如果实时行情获取失败，尝试使用个股信息接口
            individual_info = AkshareDataProvider._get_individual_info_em(stock_code_str)
            if individual_info:
                return {
                    "code": stock_code_str,
                    "name": individual_info.get('股票简称', ''),
                    "current_price": float(individual_info.get('最新价', 0)) if individual_info.get('最新价') else None,
                    "pe_ratio": None,
                    "pb_ratio": None,
                    "industry": individual_info.get('行业', ''),
                    "source": "eastmoney_individual"
                }

            logger.warning(f"未找到股票 {stock_code} 的数据")
            return None
        except Exception as e:
            logger.warning(f"获取股票 {stock_code} 信息失败: {str(e)}")
            return None

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标 - 使用东方财富接口
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象或None
        """
        try:
            stock_code_str = str(stock_code).zfill(6)

            stock_info = self.get_stock_info(stock_code)
            if not stock_info:
                return None

            indicators = AkshareDataProvider._get_main_indicators(stock_code_str)
            roe = gross_margin = eps = debt_ratio = revenue_growth = profit_growth = None
            if indicators:
                roe, gross_margin, eps = indicators

            financial_df = AkshareDataProvider._get_financial_indicator_em(stock_code_str)
            if financial_df is not None and not financial_df.empty:
                latest = financial_df.iloc[0]
                for col in ['资产负债率', 'debt_ratio', '负债率']:
                    if col in financial_df.columns:
                        try:
                            val = latest[col]
                            if pd.notna(val):
                                debt_ratio = float(val) / 100 if float(val) > 1 else float(val)
                        except:
                            pass
                        break
                for col in ['营业收入同比增长率', '营收增长率', 'revenue_growth']:
                    if col in financial_df.columns:
                        try:
                            val = latest[col]
                            if pd.notna(val):
                                revenue_growth = float(val) / 100 if abs(float(val)) > 1 else float(val)
                        except:
                            pass
                        break
                for col in ['净利润同比增长率', '利润增长率', 'profit_growth']:
                    if col in financial_df.columns:
                        try:
                            val = latest[col]
                            if pd.notna(val):
                                profit_growth = float(val) / 100 if abs(float(val)) > 1 else float(val)
                        except:
                            pass
                        break

            return FinancialMetrics(
                stock_code=stock_code_str,
                current_price=stock_info.get('current_price'),
                pe_ratio=stock_info.get('pe_ratio'),
                pb_ratio=stock_info.get('pb_ratio'),
                roe=roe,
                gross_margin=gross_margin,
                earnings_per_share=eps,
                debt_ratio=debt_ratio,
                revenue_growth=revenue_growth,
                profit_growth=profit_growth,
                update_time=datetime.now()
            )
        except Exception as e:
            logger.warning(f"获取财务指标失败: {str(e)}")
            return None

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[pd.DataFrame]:
        """
        获取历史价格数据 - 使用东方财富接口
        Args:
            stock_code: 股票代码
            days: 获取天数
        Returns:
            历史价格DataFrame或None
        """
        try:
            stock_code_str = str(stock_code).zfill(6)

            # 使用东方财富历史行情接口
            df = ak.stock_zh_a_hist(
                symbol=stock_code_str,
                period='daily',
                adjust='qfq'  # 前复权
            )

            if df is not None and not df.empty:
                logger.debug(f"从东方财富获取 {stock_code_str} 历史价格成功，共 {len(df)} 条")
                return df.tail(days)
            return None
        except Exception as e:
            logger.error(f"获取历史价格失败: {str(e)}")
            return None

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息 - 使用东方财富接口
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典或None
        """
        try:
            stock_code_str = str(stock_code).zfill(6)

            # 首先尝试从个股信息获取行业
            individual_info = AkshareDataProvider._get_individual_info_em(stock_code_str)
            if individual_info and individual_info.get('行业'):
                return {
                    "industry": individual_info.get('行业', ''),
                    "market": individual_info.get('上市日期', ''),
                    "total_market_cap": individual_info.get('总市值', ''),
                    "circulating_market_cap": individual_info.get('流通市值', ''),
                    "source": "eastmoney"
                }

            # 回退到缓存的行业分类数据
            df = _get_cached_stock_info_df()
            if df is not None:
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
    @lru_cache(maxsize=128)
    def _get_individual_info_em(stock_code: str) -> Optional[Dict[str, Any]]:
        try:
            stock_code_str = str(stock_code).zfill(6)
            df = ak.stock_individual_info_em(symbol=stock_code_str)
            if df is not None and not df.empty:
                info_dict = {}
                for _, row in df.iterrows():
                    key = row.iloc[0] if len(row) > 0 else None
                    value = row.iloc[1] if len(row) > 1 else None
                    if key:
                        info_dict[key] = value
                logger.debug(f"从东方财富获取 {stock_code_str} 个股信息成功")
                return info_dict
            return None
        except Exception as e:
            logger.warning(f"从东方财富获取个股信息失败: {str(e)}")
            return None

    @staticmethod
    @lru_cache(maxsize=128)
    def _get_financial_indicator_em(stock_code: str) -> Optional[pd.DataFrame]:
        try:
            stock_code_str = str(stock_code).zfill(6)
            df = ak.stock_financial_analysis_indicator(symbol=stock_code_str)
            if df is not None and not df.empty:
                logger.debug(f"从东方财富获取 {stock_code_str} 财务指标成功")
                return df
            return None
        except Exception as e:
            logger.warning(f"从东方财富获取财务指标失败: {str(e)}")
            return None

    @staticmethod
    @lru_cache(maxsize=128)
    def _get_main_indicators(symbol: str) -> Optional[tuple]:
        try:
            stock_code_str = symbol.replace('sh', '').replace('sz', '').zfill(6)
            df = AkshareDataProvider._get_financial_indicator_em(stock_code_str)
            if df is not None and not df.empty:
                latest = df.iloc[0] if not df.empty else None
                if latest is not None:
                    roe = gross_margin = eps = None
                    for col in ['净资产收益率', 'roe', 'ROE', '加权净资产收益率']:
                        if col in df.columns:
                            try:
                                val = latest[col]
                                if pd.notna(val):
                                    roe = float(val) / 100 if float(val) > 1 else float(val)
                            except:
                                pass
                            break
                    for col in ['销售毛利率', '毛利率', 'gross_margin']:
                        if col in df.columns:
                            try:
                                val = latest[col]
                                if pd.notna(val):
                                    gross_margin = float(val) / 100 if float(val) > 1 else float(val)
                            except:
                                pass
                            break
                    for col in ['基本每股收益', '每股收益', 'eps', 'EPS']:
                        if col in df.columns:
                            try:
                                val = latest[col]
                                if pd.notna(val):
                                    eps = float(val)
                            except:
                                pass
                            break
                    if roe is not None or gross_margin is not None or eps is not None:
                        return (roe, gross_margin, eps)
            return None
        except Exception as e:
            logger.warning(f"获取主要财务指标失败: {str(e)}")
            return None

    def __str__(self):
        return f"{self.name} ({self.source_type.value}) [{'✓' if self.is_available else '✗'}]"

class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_metrics(metrics: FinancialMetrics) -> bool:
        if not metrics or not metrics.stock_code:
            return False
        if metrics.current_price is None or metrics.current_price <= 0:
            return False
        return True

    @staticmethod
    def validate_pe_ratio(pe_ratio: Optional[float]) -> bool:
        return pe_ratio is not None and pe_ratio >= 0

    @staticmethod
    def validate_pb_ratio(pb_ratio: Optional[float]) -> bool:
        return pb_ratio is not None and pb_ratio >= 0

