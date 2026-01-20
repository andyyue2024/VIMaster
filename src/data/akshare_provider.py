"""
数据获取模块 - 使用 akshare 从远程数据源获取财务数据
"""
import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any
from src.models.data_models import FinancialMetrics
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AkshareDataProvider:
    """Akshare 数据提供者"""

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
            # 获取实时行情数据
            df = ak.stock_zh_a_spot()
            stock_code_str = str(stock_code).zfill(6)

            # 过滤该股票的数据
            stock_data = df[df['代码'] == stock_code_str]

            if stock_data.empty:
                logger.warning(f"未找到股票 {stock_code} 的数据")
                return None

            row = stock_data.iloc[0]
            return {
                "code": stock_code_str,
                "name": row.get('名称', ''),
                "current_price": float(row.get('最新价', 0)),
                "pe_ratio": float(row.get('市盈率', 0)) if row.get('市盈率') != '---' else None,
                "pb_ratio": float(row.get('市净率', 0)) if row.get('市净率') != '---' else None,
            }
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 信息失败: {str(e)}")
            return None

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

            # 获取基本信息
            stock_info = AkshareDataProvider.get_stock_info(stock_code)
            if not stock_info:
                return None

            # 获取财务数据
            try:
                # 获取利润表数据
                df_profit = ak.stock_main_ind(symbol=f"sh{stock_code_str}" if stock_code_str.startswith('6') else f"sz{stock_code_str}")

                if not df_profit.empty:
                    latest = df_profit.iloc[0]

                    metrics = FinancialMetrics(
                        stock_code=stock_code_str,
                        current_price=stock_info.get('current_price'),
                        pe_ratio=stock_info.get('pe_ratio'),
                        pb_ratio=stock_info.get('pb_ratio'),
                        roe=float(latest.get('roe', 0)) if latest.get('roe') else None,
                        gross_margin=float(latest.get('毛利率', 0)) if latest.get('毛利率') else None,
                        earnings_per_share=float(latest.get('eps', 0)) if latest.get('eps') else None,
                        update_time=datetime.now()
                    )
                    return metrics
            except Exception as e:
                logger.warning(f"获取 {stock_code} 详细财务数据失败: {str(e)}")
                # 返回基本指标
                return FinancialMetrics(
                    stock_code=stock_code_str,
                    current_price=stock_info.get('current_price'),
                    pe_ratio=stock_info.get('pe_ratio'),
                    pb_ratio=stock_info.get('pb_ratio'),
                    update_time=datetime.now()
                )

        except Exception as e:
            logger.error(f"获取财务指标失败: {str(e)}")
            return None

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
            # 获取行业分类数据
            df = ak.stock_info_a_code_name()
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
