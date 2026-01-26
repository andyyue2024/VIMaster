"""
数据源基类 - 定义所有数据提供者的通用接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from src.models.data_models import FinancialMetrics
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """数据源类型枚举"""
    AKSHARE = "akshare"
    TUSHARE = "tushare"
    BAOSTOCK = "baostock"
    MOCK = "mock"


class BaseDataSource(ABC):
    """数据源基类"""

    def __init__(self, name: str, source_type: DataSourceType):
        self.name = name
        self.source_type = source_type
        self.is_available = False
        self._test_connection()

    @abstractmethod
    def _test_connection(self) -> bool:
        """
        测试数据源连接
        Returns:
            True if available, False otherwise
        """
        pass

    @abstractmethod
    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息
        Args:
            stock_code: 股票代码
        Returns:
            股票信息字典或None
        """
        pass

    @abstractmethod
    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象或None
        """
        pass

    @abstractmethod
    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[Any]:
        """
        获取历史价格数据
        Args:
            stock_code: 股票代码
            days: 获取天数
        Returns:
            历史价格数据或None
        """
        pass

    @abstractmethod
    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典或None
        """
        pass

    def __str__(self) -> str:
        status = "✓" if self.is_available else "✗"
        return f"{self.name} ({self.source_type.value}) [{status}]"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} available={self.is_available}>"

