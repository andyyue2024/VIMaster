"""
标签构造 - 使用历史价格计算未来收益率/超额收益作为训练标签
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_forward_return(prices: pd.Series, horizon_days: int = 252) -> Optional[float]:
    """计算未来 horizon_days 的收益率（简单比例）"""
    if prices is None or len(prices) < horizon_days + 1:
        return None
    start = float(prices.iloc[0])
    end = float(prices.iloc[horizon_days])
    if start <= 0:
        return None
    return (end - start) / start


def compute_excess_return(prices: pd.Series, market_prices: Optional[pd.Series], horizon_days: int = 252) -> Optional[float]:
    """计算未来 horizon 的超额收益（相对市场指数）"""
    r = compute_forward_return(prices, horizon_days)
    if r is None:
        return None
    if market_prices is None or len(market_prices) < horizon_days + 1:
        return r
    rm = compute_forward_return(market_prices, horizon_days)
    if rm is None:
        return r
    return r - rm


def label_from_dataframe(df: pd.DataFrame, price_col: str = "close", market_df: Optional[pd.DataFrame] = None, horizon_days: int = 252) -> Optional[float]:
    """从价格 DataFrame 构建标签（未来收益或超额收益）"""
    if df is None or df.empty or price_col not in df.columns:
        return None
    prices = df[price_col].reset_index(drop=True)
    market_prices = None
    if market_df is not None and price_col in market_df.columns:
        market_prices = market_df[price_col].reset_index(drop=True)
    return compute_excess_return(prices, market_prices, horizon_days)
