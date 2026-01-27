"""
Mock 数据提供者 - 提供本地内置的模拟股票数据
"""
from typing import Optional, Dict, Any
import random
from datetime import datetime
from src.data.data_source_base import BaseDataSource, DataSourceType
from src.models.data_models import FinancialMetrics

# 统一的模拟数据源
MOCK_STOCKS_DATA = {
    "600519": {
        "name": "贵州茅台",
        "current_price": 1800.5,
        "pe_ratio": 35.2,
        "pb_ratio": 12.5,
        "roe": 0.32,
        "gross_margin": 0.92,
        "eps": 51.2,
        "revenue_growth": 0.15,
        "profit_growth": 0.18,
        "free_cash_flow": 150e8,
        "debt_ratio": 0.05,
        "dividend_yield": 0.02,
        "industry": "白酒",
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
        "industry": "白酒",
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
        "industry": "家电",
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
        "debt_ratio": 0.85,
        "dividend_yield": 0.035,
        "industry": "银行",
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
        "industry": "家电",
    },
}


class MockDataProvider(BaseDataSource):
    """提供本地模拟数据的数据源"""

    def __init__(self):
        self.data = MOCK_STOCKS_DATA
        super().__init__("MockData", DataSourceType.MOCK)
        self.is_available = True  # 始终可用

    def _test_connection(self) -> bool:
        return True

    def _get_record(self, stock_code: str) -> Optional[Dict[str, Any]]:
        code = str(stock_code).zfill(6)
        return self.data.get(code)

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        record = self._get_record(stock_code)
        if not record:
            return None
        return {
            "code": str(stock_code).zfill(6),
            "name": record["name"],
            "current_price": record["current_price"],
            "pe_ratio": record["pe_ratio"],
            "pb_ratio": record["pb_ratio"],
            "industry": record.get("industry", ""),
            "source": "mock"
        }

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        record = self._get_record(stock_code)
        code = str(stock_code).zfill(6)
        if record:
            return FinancialMetrics(
                stock_code=code,
                current_price=record["current_price"],
                pe_ratio=record["pe_ratio"],
                pb_ratio=record["pb_ratio"],
                roe=record.get("roe"),
                gross_margin=record.get("gross_margin"),
                earnings_per_share=record.get("eps"),
                revenue_growth=record.get("revenue_growth"),
                profit_growth=record.get("profit_growth"),
                free_cash_flow=record.get("free_cash_flow"),
                debt_ratio=record.get("debt_ratio"),
                dividend_yield=record.get("dividend_yield"),
                update_time=datetime.now()
            )

        # 未知股票则返回 None
        return None

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[Any]:
        return None  # 模拟数据不提供历史价格

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        record = self._get_record(stock_code)
        if record:
            return {"industry": record.get("industry", ""), "source": "mock"}
        return None

    def __str__(self) -> str:
        return f"{self.name} ({self.source_type.value}) [✓]"
