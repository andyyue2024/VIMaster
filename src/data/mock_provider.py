"""
Mock 数据提供者 - 提供本地内置的模拟股票数据
支持丰富的预定义股票数据，作为最后的数据保障
"""
from typing import Optional, Dict, Any, List
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.data_source_base import BaseDataSource, DataSourceType
from src.models.data_models import FinancialMetrics

# ============================================================================
# 丰富的模拟股票数据库 - 覆盖多行业龙头股
# ============================================================================
MOCK_STOCKS_DATA = {
    # ===== 白酒行业 =====
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
        "market_cap": 22600e8,
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
        "market_cap": 3300e8,
    },
    "000568": {
        "name": "泸州老窖",
        "current_price": 156.8,
        "pe_ratio": 22.5,
        "pb_ratio": 7.2,
        "roe": 0.30,
        "gross_margin": 0.85,
        "eps": 6.97,
        "revenue_growth": 0.18,
        "profit_growth": 0.20,
        "free_cash_flow": 45e8,
        "debt_ratio": 0.10,
        "dividend_yield": 0.028,
        "industry": "白酒",
        "market_cap": 2300e8,
    },
    "002304": {
        "name": "洋河股份",
        "current_price": 78.5,
        "pe_ratio": 18.2,
        "pb_ratio": 3.8,
        "roe": 0.22,
        "gross_margin": 0.75,
        "eps": 4.31,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 35e8,
        "debt_ratio": 0.12,
        "dividend_yield": 0.032,
        "industry": "白酒",
        "market_cap": 1200e8,
    },

    # ===== 家电行业 =====
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
        "market_cap": 1600e8,
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
        "market_cap": 2900e8,
    },
    "600690": {
        "name": "海尔智家",
        "current_price": 22.8,
        "pe_ratio": 14.2,
        "pb_ratio": 2.8,
        "roe": 0.18,
        "gross_margin": 0.30,
        "eps": 1.60,
        "revenue_growth": 0.06,
        "profit_growth": 0.08,
        "free_cash_flow": 60e8,
        "debt_ratio": 0.35,
        "dividend_yield": 0.025,
        "industry": "家电",
        "market_cap": 2100e8,
    },

    # ===== 银行业 =====
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
        "market_cap": 9000e8,
    },
    "601398": {
        "name": "工商银行",
        "current_price": 5.2,
        "pe_ratio": 5.8,
        "pb_ratio": 0.65,
        "roe": 0.12,
        "gross_margin": 0.58,
        "eps": 0.90,
        "revenue_growth": 0.03,
        "profit_growth": 0.04,
        "free_cash_flow": 500e8,
        "debt_ratio": 0.92,
        "dividend_yield": 0.055,
        "industry": "银行",
        "market_cap": 18600e8,
    },
    "601288": {
        "name": "农业银行",
        "current_price": 4.1,
        "pe_ratio": 5.2,
        "pb_ratio": 0.58,
        "roe": 0.11,
        "gross_margin": 0.55,
        "eps": 0.79,
        "revenue_growth": 0.02,
        "profit_growth": 0.03,
        "free_cash_flow": 450e8,
        "debt_ratio": 0.93,
        "dividend_yield": 0.06,
        "industry": "银行",
        "market_cap": 14300e8,
    },
    "600000": {
        "name": "浦发银行",
        "current_price": 8.5,
        "pe_ratio": 4.8,
        "pb_ratio": 0.48,
        "roe": 0.10,
        "gross_margin": 0.52,
        "eps": 1.77,
        "revenue_growth": 0.01,
        "profit_growth": 0.02,
        "free_cash_flow": 150e8,
        "debt_ratio": 0.91,
        "dividend_yield": 0.045,
        "industry": "银行",
        "market_cap": 2500e8,
    },

    # ===== 保险业 =====
    "601318": {
        "name": "中国平安",
        "current_price": 45.6,
        "pe_ratio": 9.8,
        "pb_ratio": 1.1,
        "roe": 0.15,
        "gross_margin": 0.45,
        "eps": 4.65,
        "revenue_growth": 0.05,
        "profit_growth": 0.06,
        "free_cash_flow": 180e8,
        "debt_ratio": 0.88,
        "dividend_yield": 0.04,
        "industry": "保险",
        "market_cap": 8300e8,
    },
    "601628": {
        "name": "中国人寿",
        "current_price": 28.5,
        "pe_ratio": 12.5,
        "pb_ratio": 1.3,
        "roe": 0.12,
        "gross_margin": 0.38,
        "eps": 2.28,
        "revenue_growth": 0.03,
        "profit_growth": 0.04,
        "free_cash_flow": 120e8,
        "debt_ratio": 0.90,
        "dividend_yield": 0.025,
        "industry": "保险",
        "market_cap": 8000e8,
    },

    # ===== 医药行业 =====
    "600276": {
        "name": "恒瑞医药",
        "current_price": 42.8,
        "pe_ratio": 45.2,
        "pb_ratio": 8.5,
        "roe": 0.18,
        "gross_margin": 0.85,
        "eps": 0.95,
        "revenue_growth": 0.12,
        "profit_growth": 0.15,
        "free_cash_flow": 25e8,
        "debt_ratio": 0.08,
        "dividend_yield": 0.008,
        "industry": "医药",
        "market_cap": 2700e8,
    },
    "000538": {
        "name": "云南白药",
        "current_price": 58.2,
        "pe_ratio": 22.5,
        "pb_ratio": 3.8,
        "roe": 0.16,
        "gross_margin": 0.32,
        "eps": 2.59,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 30e8,
        "debt_ratio": 0.15,
        "dividend_yield": 0.025,
        "industry": "医药",
        "market_cap": 1050e8,
    },
    "300760": {
        "name": "迈瑞医疗",
        "current_price": 285.5,
        "pe_ratio": 38.2,
        "pb_ratio": 12.5,
        "roe": 0.32,
        "gross_margin": 0.65,
        "eps": 7.47,
        "revenue_growth": 0.20,
        "profit_growth": 0.22,
        "free_cash_flow": 50e8,
        "debt_ratio": 0.12,
        "dividend_yield": 0.012,
        "industry": "医药",
        "market_cap": 3460e8,
    },

    # ===== 科技行业 =====
    "002415": {
        "name": "海康威视",
        "current_price": 32.5,
        "pe_ratio": 18.5,
        "pb_ratio": 4.2,
        "roe": 0.22,
        "gross_margin": 0.45,
        "eps": 1.76,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 80e8,
        "debt_ratio": 0.25,
        "dividend_yield": 0.028,
        "industry": "科技",
        "market_cap": 3000e8,
    },
    "000725": {
        "name": "京东方A",
        "current_price": 4.2,
        "pe_ratio": 25.5,
        "pb_ratio": 1.5,
        "roe": 0.06,
        "gross_margin": 0.18,
        "eps": 0.16,
        "revenue_growth": 0.05,
        "profit_growth": 0.08,
        "free_cash_flow": 30e8,
        "debt_ratio": 0.55,
        "dividend_yield": 0.015,
        "industry": "科技",
        "market_cap": 1600e8,
    },
    "002230": {
        "name": "科大讯飞",
        "current_price": 48.5,
        "pe_ratio": 85.2,
        "pb_ratio": 6.8,
        "roe": 0.08,
        "gross_margin": 0.42,
        "eps": 0.57,
        "revenue_growth": 0.25,
        "profit_growth": 0.30,
        "free_cash_flow": 5e8,
        "debt_ratio": 0.35,
        "dividend_yield": 0.005,
        "industry": "科技",
        "market_cap": 1120e8,
    },

    # ===== 新能源行业 =====
    "300750": {
        "name": "宁德时代",
        "current_price": 185.5,
        "pe_ratio": 22.8,
        "pb_ratio": 5.2,
        "roe": 0.22,
        "gross_margin": 0.22,
        "eps": 8.14,
        "revenue_growth": 0.35,
        "profit_growth": 0.40,
        "free_cash_flow": 150e8,
        "debt_ratio": 0.45,
        "dividend_yield": 0.008,
        "industry": "新能源",
        "market_cap": 8100e8,
    },
    "002594": {
        "name": "比亚迪",
        "current_price": 225.8,
        "pe_ratio": 28.5,
        "pb_ratio": 4.8,
        "roe": 0.18,
        "gross_margin": 0.20,
        "eps": 7.92,
        "revenue_growth": 0.45,
        "profit_growth": 0.50,
        "free_cash_flow": 100e8,
        "debt_ratio": 0.55,
        "dividend_yield": 0.005,
        "industry": "新能源",
        "market_cap": 6500e8,
    },
    "601012": {
        "name": "隆基绿能",
        "current_price": 18.5,
        "pe_ratio": 12.5,
        "pb_ratio": 2.2,
        "roe": 0.18,
        "gross_margin": 0.18,
        "eps": 1.48,
        "revenue_growth": 0.15,
        "profit_growth": 0.18,
        "free_cash_flow": 60e8,
        "debt_ratio": 0.50,
        "dividend_yield": 0.015,
        "industry": "新能源",
        "market_cap": 1400e8,
    },

    # ===== 消费行业 =====
    "600887": {
        "name": "伊利股份",
        "current_price": 28.5,
        "pe_ratio": 18.5,
        "pb_ratio": 4.2,
        "roe": 0.22,
        "gross_margin": 0.32,
        "eps": 1.54,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 60e8,
        "debt_ratio": 0.40,
        "dividend_yield": 0.035,
        "industry": "消费",
        "market_cap": 1800e8,
    },
    "000568": {
        "name": "泸州老窖",
        "current_price": 156.8,
        "pe_ratio": 22.5,
        "pb_ratio": 7.2,
        "roe": 0.30,
        "gross_margin": 0.85,
        "eps": 6.97,
        "revenue_growth": 0.18,
        "profit_growth": 0.20,
        "free_cash_flow": 45e8,
        "debt_ratio": 0.10,
        "dividend_yield": 0.028,
        "industry": "白酒",
        "market_cap": 2300e8,
    },
    "603288": {
        "name": "海天味业",
        "current_price": 42.5,
        "pe_ratio": 35.2,
        "pb_ratio": 8.5,
        "roe": 0.25,
        "gross_margin": 0.42,
        "eps": 1.21,
        "revenue_growth": 0.05,
        "profit_growth": 0.06,
        "free_cash_flow": 35e8,
        "debt_ratio": 0.08,
        "dividend_yield": 0.022,
        "industry": "消费",
        "market_cap": 1950e8,
    },

    # ===== 房地产行业 =====
    "000002": {
        "name": "万科A",
        "current_price": 8.5,
        "pe_ratio": 8.2,
        "pb_ratio": 0.65,
        "roe": 0.08,
        "gross_margin": 0.22,
        "eps": 1.04,
        "revenue_growth": -0.10,
        "profit_growth": -0.15,
        "free_cash_flow": 50e8,
        "debt_ratio": 0.78,
        "dividend_yield": 0.05,
        "industry": "房地产",
        "market_cap": 1000e8,
    },
    "601668": {
        "name": "中国建筑",
        "current_price": 5.8,
        "pe_ratio": 4.5,
        "pb_ratio": 0.68,
        "roe": 0.15,
        "gross_margin": 0.12,
        "eps": 1.29,
        "revenue_growth": 0.05,
        "profit_growth": 0.06,
        "free_cash_flow": 200e8,
        "debt_ratio": 0.75,
        "dividend_yield": 0.045,
        "industry": "建筑",
        "market_cap": 2400e8,
    },

    # ===== 通信行业 =====
    "600941": {
        "name": "中国移动",
        "current_price": 108.5,
        "pe_ratio": 12.5,
        "pb_ratio": 1.5,
        "roe": 0.12,
        "gross_margin": 0.48,
        "eps": 8.68,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 800e8,
        "debt_ratio": 0.35,
        "dividend_yield": 0.055,
        "industry": "通信",
        "market_cap": 23200e8,
    },
    "601728": {
        "name": "中国电信",
        "current_price": 6.8,
        "pe_ratio": 14.5,
        "pb_ratio": 1.2,
        "roe": 0.08,
        "gross_margin": 0.32,
        "eps": 0.47,
        "revenue_growth": 0.06,
        "profit_growth": 0.08,
        "free_cash_flow": 250e8,
        "debt_ratio": 0.42,
        "dividend_yield": 0.048,
        "industry": "通信",
        "market_cap": 6200e8,
    },

    # ===== 能源行业 =====
    "601857": {
        "name": "中国石油",
        "current_price": 8.5,
        "pe_ratio": 8.2,
        "pb_ratio": 0.95,
        "roe": 0.12,
        "gross_margin": 0.25,
        "eps": 1.04,
        "revenue_growth": 0.10,
        "profit_growth": 0.15,
        "free_cash_flow": 500e8,
        "debt_ratio": 0.45,
        "dividend_yield": 0.065,
        "industry": "能源",
        "market_cap": 15500e8,
    },
    "600028": {
        "name": "中国石化",
        "current_price": 5.2,
        "pe_ratio": 9.5,
        "pb_ratio": 0.78,
        "roe": 0.08,
        "gross_margin": 0.15,
        "eps": 0.55,
        "revenue_growth": 0.08,
        "profit_growth": 0.10,
        "free_cash_flow": 350e8,
        "debt_ratio": 0.50,
        "dividend_yield": 0.072,
        "industry": "能源",
        "market_cap": 6300e8,
    },
}


class MockDataProvider(BaseDataSource):
    """
    Mock 数据提供者 - 提供本地模拟数据

    特点：
    - 始终可用，作为最后的数据保障
    - 覆盖多行业龙头股
    - 支持生成模拟历史价格数据
    """

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
            "market_cap": record.get("market_cap", 0),
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
        return None

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[pd.DataFrame]:
        """
        生成模拟历史价格数据
        Args:
            stock_code: 股票代码
            days: 天数
        Returns:
            模拟的历史价格 DataFrame
        """
        record = self._get_record(stock_code)
        if not record:
            return None

        current_price = record["current_price"]

        # 生成模拟历史数据
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        # 使用随机游走生成价格
        np.random.seed(hash(stock_code) % 2**31)
        returns = np.random.normal(0.0005, 0.02, days)
        prices = current_price * np.exp(np.cumsum(returns[::-1]))[::-1]

        # 生成开高低收
        high = prices * (1 + np.random.uniform(0, 0.03, days))
        low = prices * (1 - np.random.uniform(0, 0.03, days))
        open_price = low + np.random.uniform(0.3, 0.7, days) * (high - low)

        df = pd.DataFrame({
            '日期': dates,
            '开盘': open_price,
            '收盘': prices,
            '最高': high,
            '最低': low,
            '成交量': np.random.randint(100000, 10000000, days),
            '成交额': np.random.randint(10000000, 1000000000, days),
        })

        return df

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        record = self._get_record(stock_code)
        if record:
            return {
                "industry": record.get("industry", ""),
                "market_cap": record.get("market_cap", 0),
                "source": "mock"
            }
        return None

    def get_all_stocks(self) -> List[str]:
        """获取所有支持的股票代码列表"""
        return list(self.data.keys())

    def get_stocks_by_industry(self, industry: str) -> List[str]:
        """按行业获取股票列表"""
        return [
            code for code, data in self.data.items()
            if data.get("industry") == industry
        ]

    def get_available_industries(self) -> List[str]:
        """获取所有可用行业"""
        return list(set(data.get("industry", "") for data in self.data.values()))

    def __str__(self):
        return f"{self.name} ({self.source_type.value}) [✓] ({len(self.data)} stocks)"
