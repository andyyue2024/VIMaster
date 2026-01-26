"""
TuShare 数据提供者 - 从 TuShare 获取股票财务数据
"""
import logging
from typing import Optional, Dict, Any
import tushare as ts
from src.models.data_models import FinancialMetrics
from src.data.data_source_base import BaseDataSource, DataSourceType
from datetime import datetime

logger = logging.getLogger(__name__)


class TuShareProvider(BaseDataSource):
    """TuShare 数据提供者"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or ""
        if self.token:
            try:
                ts.set_token(self.token)
                self.pro = ts.pro_api()
            except Exception as e:
                logger.warning(f"TuShare token 无效: {str(e)}")
                self.pro = None
        else:
            logger.warning("未提供 TuShare token，将使用有限功能")
            self.pro = None

        super().__init__("TuShare", DataSourceType.TUSHARE)

    def _test_connection(self) -> bool:
        """测试 TuShare 连接"""
        try:
            if self.pro is None:
                logger.warning("TuShare API 未初始化")
                self.is_available = False
                return False

            # 尝试获取基础数据来验证连接
            df = self.pro.trade_cal(exchange='SSE', start_date='20260101', end_date='20260101')
            if df is not None and not df.empty:
                self.is_available = True
                logger.info("TuShare 连接成功")
                return True
            else:
                self.is_available = False
                return False
        except Exception as e:
            logger.warning(f"TuShare 连接失败: {str(e)}")
            self.is_available = False
            return False

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息
        Args:
            stock_code: 股票代码 (如 600519)
        Returns:
            股票信息字典或None
        """
        if not self.is_available or self.pro is None:
            return None

        try:
            # TuShare 使用 TS_CODE (如 600519.SH)
            ts_code = self._convert_to_ts_code(stock_code)

            # 获取基础数据
            df = self.pro.daily(ts_code=ts_code, start_date='20260101', end_date='20260126')

            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "code": stock_code,
                    "ts_code": ts_code,
                    "current_price": float(latest['close']) if 'close' in latest else None,
                    "volume": float(latest['vol']) if 'vol' in latest else None,
                    "trade_date": latest['trade_date'] if 'trade_date' in latest else None,
                }
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 信息失败: {str(e)}")
            return None

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象或None
        """
        if not self.is_available or self.pro is None:
            return None

        try:
            ts_code = self._convert_to_ts_code(stock_code)

            # 获取基础数据（最近价格）
            stock_info = self.get_stock_info(stock_code)
            if not stock_info:
                return None

            # 获取财务指标
            df_fin = self.pro.income(ts_code=ts_code, start_date='20250101', end_date='20251231')

            if df_fin is not None and not df_fin.empty:
                latest_fin = df_fin.iloc[0]

                # 获取资产负债表数据（用于计算负债率）
                df_balance = self.pro.balancesheet(ts_code=ts_code, start_date='20250101', end_date='20251231')

                debt_ratio = None
                if df_balance is not None and not df_balance.empty:
                    latest_balance = df_balance.iloc[0]
                    # 负债率 = 总负债 / 总资产
                    if 'liab_total' in latest_balance.columns and 'assets_total' in latest_balance.columns:
                        total_liab = float(latest_balance['liab_total']) if latest_balance['liab_total'] else 0
                        total_assets = float(latest_balance['assets_total']) if latest_balance['assets_total'] else 1
                        debt_ratio = total_liab / total_assets if total_assets > 0 else None

                metrics = FinancialMetrics(
                    stock_code=stock_code,
                    current_price=stock_info.get('current_price'),
                    roe=float(latest_fin['roe']) / 100 if 'roe' in latest_fin and latest_fin['roe'] else None,
                    gross_margin=float(latest_fin['grossprofit_margin']) / 100 if 'grossprofit_margin' in latest_fin else None,
                    debt_ratio=debt_ratio,
                    update_time=datetime.now()
                )
                return metrics
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 财务指标失败: {str(e)}")
            return None

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[Any]:
        """
        获取历史价格数据
        Args:
            stock_code: 股票代码
            days: 获取天数
        Returns:
            历史价格DataFrame或None
        """
        if not self.is_available or self.pro is None:
            return None

        try:
            ts_code = self._convert_to_ts_code(stock_code)
            df = self.pro.daily(ts_code=ts_code, start_date='20250101', end_date='20260126')

            if df is not None and not df.empty:
                return df.head(days)
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 历史价格失败: {str(e)}")
            return None

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典或None
        """
        if not self.is_available or self.pro is None:
            return None

        try:
            ts_code = self._convert_to_ts_code(stock_code)

            # 获取股票基础信息
            df = self.pro.stock_basic(exchange='', fields='ts_code,symbol,name,area,industry,list_date')

            if df is not None and not df.empty:
                stock_data = df[df['ts_code'] == ts_code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    return {
                        "industry": row.get('industry', ''),
                        "area": row.get('area', ''),
                        "list_date": row.get('list_date', ''),
                    }
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 行业信息失败: {str(e)}")
            return None

    @staticmethod
    def _convert_to_ts_code(stock_code: str) -> str:
        """
        将普通股票代码转换为 TuShare TS_CODE 格式
        600519 -> 600519.SH
        000858 -> 000858.SZ
        """
        if '.' in stock_code:
            return stock_code

        if stock_code.startswith('6'):
            return f"{stock_code}.SH"
        else:
            return f"{stock_code}.SZ"

