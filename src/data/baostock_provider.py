"""
BaoStock 数据提供者 - 从 BaoStock 获取股票财务数据
"""
import logging
from typing import Optional, Dict, Any
import baostock as bs
import pandas as pd
from src.models.data_models import FinancialMetrics
from src.data.data_source_base import BaseDataSource, DataSourceType
from datetime import datetime

logger = logging.getLogger(__name__)


class BaoStockProvider(BaseDataSource):
    """BaoStock 数据提供者"""

    def __init__(self):
        self.logged_in = False
        super().__init__("BaoStock", DataSourceType.BAOSTOCK)

    def _test_connection(self) -> bool:
        """测试 BaoStock 连接"""
        try:
            # 尝试登录 BaoStock
            lg = bs.login()
            if lg.error_code == '0':
                self.logged_in = True
                self.is_available = True
                logger.info("BaoStock 连接成功")
                bs.logout()
                return True
            else:
                logger.warning(f"BaoStock 登录失败: {lg.error_msg}")
                self.is_available = False
                return False
        except Exception as e:
            logger.warning(f"BaoStock 连接异常: {str(e)}")
            self.is_available = False
            return False

    def _ensure_login(self) -> bool:
        """确保登录 BaoStock"""
        if not self.logged_in:
            try:
                lg = bs.login()
                if lg.error_code == '0':
                    self.logged_in = True
                    return True
                else:
                    logger.warning(f"BaoStock 登录失败: {lg.error_msg}")
                    return False
            except Exception as e:
                logger.warning(f"BaoStock 登录异常: {str(e)}")
                return False
        return True

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息
        Args:
            stock_code: 股票代码
        Returns:
            股票信息字典或None
        """
        if not self.is_available:
            return None

        try:
            if not self._ensure_login():
                return None

            # 转换代码格式
            bs_code = self._convert_to_bs_code(stock_code)

            # 获取最近一天的日线数据
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,code,close,volume",
                end_date='20260126',
                frequence="d",
                adjustflag="2"
            )

            if rs.error_code == '0':
                data_list = []
                while (rs.next()):
                    data_list.append(rs.get_row_data())

                if data_list:
                    latest = data_list[0]
                    return {
                        "code": stock_code,
                        "bs_code": bs_code,
                        "current_price": float(latest[2]) if latest[2] else None,
                        "volume": float(latest[3]) if latest[3] else None,
                        "date": latest[0],
                    }
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 信息失败: {str(e)}")
            return None
        finally:
            try:
                bs.logout()
                self.logged_in = False
            except:
                pass

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象或None
        """
        if not self.is_available:
            return None

        try:
            if not self._ensure_login():
                return None

            bs_code = self._convert_to_bs_code(stock_code)

            # 获取股票基本信息
            stock_info = self.get_stock_info(stock_code)
            if not stock_info:
                return None

            # 获取财务指标数据
            rs = bs.query_performance(
                code=bs_code,
                start_year=2025,
                start_quarter=4,
                end_year=2025,
                end_quarter=4
            )

            roe = None
            gross_margin = None
            debt_ratio = None

            if rs.error_code == '0':
                while (rs.next()):
                    row_data = rs.get_row_data()
                    # 提取财务指标
                    # BaoStock 返回的字段: code, year, quarter, roe, eps, grossprofitmargin等
                    try:
                        roe = float(row_data[3]) / 100 if row_data[3] else None
                        gross_margin = float(row_data[7]) / 100 if len(row_data) > 7 and row_data[7] else None
                    except:
                        pass

            # 获取负债率
            rs_balance = bs.query_balance_development(
                code=bs_code,
                start_year=2025,
                start_quarter=4,
                end_year=2025,
                end_quarter=4
            )

            if rs_balance.error_code == '0':
                while (rs_balance.next()):
                    row_data = rs_balance.get_row_data()
                    try:
                        # 提取负债率数据
                        total_liab = float(row_data[4]) if len(row_data) > 4 and row_data[4] else None
                        total_assets = float(row_data[3]) if len(row_data) > 3 and row_data[3] else None
                        if total_liab and total_assets:
                            debt_ratio = total_liab / total_assets
                    except:
                        pass

            metrics = FinancialMetrics(
                stock_code=stock_code,
                current_price=stock_info.get('current_price'),
                roe=roe,
                gross_margin=gross_margin,
                debt_ratio=debt_ratio,
                update_time=datetime.now()
            )
            return metrics
        except Exception as e:
            logger.warning(f"获取 {stock_code} 财务指标失败: {str(e)}")
            return None
        finally:
            try:
                bs.logout()
                self.logged_in = False
            except:
                pass

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[Any]:
        """
        获取历史价格数据
        Args:
            stock_code: 股票代码
            days: 获取天数
        Returns:
            历史价格DataFrame或None
        """
        if not self.is_available:
            return None

        try:
            if not self._ensure_login():
                return None

            bs_code = self._convert_to_bs_code(stock_code)

            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,code,close,volume",
                end_date='20260126',
                frequence="d",
                adjustflag="2"
            )

            if rs.error_code == '0':
                data_list = []
                while (rs.next() and len(data_list) < days):
                    data_list.append(rs.get_row_data())

                if data_list:
                    df = pd.DataFrame(data_list, columns=['date', 'code', 'close', 'volume'])
                    return df
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 历史价格失败: {str(e)}")
            return None
        finally:
            try:
                bs.logout()
                self.logged_in = False
            except:
                pass

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典或None
        """
        if not self.is_available:
            return None

        try:
            if not self._ensure_login():
                return None

            bs_code = self._convert_to_bs_code(stock_code)

            # 获取股票基础信息
            rs = bs.query_stock_basic()

            if rs.error_code == '0':
                while (rs.next()):
                    row_data = rs.get_row_data()
                    if row_data[1] == bs_code:  # row_data[1] 是代码
                        return {
                            "industry": row_data[5] if len(row_data) > 5 else '',
                            "market": row_data[2] if len(row_data) > 2 else '',
                        }
            return None
        except Exception as e:
            logger.warning(f"获取 {stock_code} 行业信息失败: {str(e)}")
            return None
        finally:
            try:
                bs.logout()
                self.logged_in = False
            except:
                pass

    @staticmethod
    def _convert_to_bs_code(stock_code: str) -> str:
        """
        将普通股票代码转换为 BaoStock 代码格式
        600519 -> sh.600519
        000858 -> sz.000858
        """
        if '.' in stock_code:
            return stock_code

        if stock_code.startswith('6'):
            return f"sh.{stock_code}"
        else:
            return f"sz.{stock_code}"

