"""
多源数据管理器 - 统一管理多个数据源并实现智能降级
"""
import logging
from typing import Optional, Dict, Any, List
from src.models.data_models import FinancialMetrics
from src.data.data_source_base import BaseDataSource, DataSourceType
from src.data.akshare_provider import AkshareDataProvider
from src.data.tushare_provider import TuShareProvider
from src.data.baostock_provider import BaoStockProvider
from src.data.mock_provider import MockDataProvider
from src.data.cache_layer import get_cache
from src.data.cache_config import CacheConfigManager
import pandas as pd

logger = logging.getLogger(__name__)


class MultiSourceDataProvider:
    """多源数据提供者 - 统一接口，智能降级"""

    def __init__(self, tushare_token: Optional[str] = None):
        """
        初始化多源数据提供者
        Args:
            tushare_token: TuShare API token (可选)
        """
        self.sources: List[BaseDataSource] = []
        # 按测试预期的优先级：AkShare > TuShare > BaoStock > Mock
        self.source_priority = [
            DataSourceType.AKSHARE,
            DataSourceType.TUSHARE,
            DataSourceType.BAOSTOCK,
            DataSourceType.MOCK,
        ]

        # 初始化各数据源
        self._init_sources(tushare_token)
        self._log_source_status()

    def _init_sources(self, tushare_token: Optional[str] = None):
        sources: List[BaseDataSource] = []
        try:
            sources.append(AkshareDataProvider())
        except Exception as e:
            logger.warning(f"AkShare 初始化失败: {str(e)}")
        try:
            sources.append(TuShareProvider(token=tushare_token))
        except Exception as e:
            logger.warning(f"TuShare 初始化失败: {str(e)}")
        try:
            sources.append(BaoStockProvider())
        except Exception as e:
            logger.warning(f"BaoStock 初始化失败: {str(e)}")
        try:
            sources.append(MockDataProvider())
        except Exception as e:
            logger.warning(f"MockData 初始化失败: {str(e)}")

        # 按优先级排序
        priority_order = {stype: idx for idx, stype in enumerate(self.source_priority)}
        self.sources = sorted(sources, key=lambda s: priority_order.get(s.source_type, 999))

    def _log_source_status(self):
        """记录数据源状态"""
        logger.info("=" * 60)
        logger.info("数据源初始化状态:")
        for source in self.sources:
            logger.info(f"  {source}")
        logger.info("=" * 60)

    def _iterate_sources(self) -> List[BaseDataSource]:
        return self.sources

    def get_available_sources(self) -> List[BaseDataSource]:
        return [s for s in self._iterate_sources() if s.is_available]

    def _get_by_priority(self, func_name: str, *args, **kwargs):
        for source in self._iterate_sources():
            if not source.is_available:
                continue
            try:
                func = getattr(source, func_name)
                result = func(*args, **kwargs)
                if result:
                    logger.info(f"从 {source.name} 获取 {func_name} 成功")
                    return result
            except Exception as e:
                logger.warning(f"{source.name} 调用 {func_name} 失败: {str(e)}")
                continue
        return None

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        return self._get_by_priority('get_stock_info', stock_code)

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        return self._get_by_priority('get_financial_metrics', stock_code)

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[pd.DataFrame]:
        return self._get_by_priority('get_historical_price', stock_code, days)

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息 - 智能降级 + 缓存
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典或None
        """
        # 检查缓存
        cache = get_cache()
        cache_key = f"industry_info:{stock_code}"

        config = CacheConfigManager.get_config()
        if config.enabled:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"从缓存获取股票 {stock_code} 行业信息")
                return cached

        # 从数据源获取
        result = self._get_by_priority('get_industry_info', stock_code)
        if result and config.enabled:
            ttl = CacheConfigManager.get_ttl_for("industry_info")
            cache.set(cache_key, result, ttl_seconds=ttl)
        return result

    def clear_cache(self, stock_code: Optional[str] = None) -> None:
        """
        清空缓存
        Args:
            stock_code: 股票代码，如果为None则清空所有缓存
        """
        cache = get_cache()
        if stock_code is None:
            cache.clear()
            logger.info("所有缓存已清空")
        else:
            # 清空该股票的所有缓存
            count = cache.delete_pattern(f"{stock_code}:")
            logger.info(f"股票 {stock_code} 的 {count} 个缓存已清空")

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        cache = get_cache()
        return cache.get_stats()

    def print_cache_stats(self) -> None:
        """打印缓存统计信息"""
        cache = get_cache()
        cache.print_stats()

    def get_source_stats(self) -> Dict[str, Any]:
        """获取数据源统计信息"""
        total = len(self.sources)
        available = len(self.get_available_sources())
        unavailable = total - available

        sources_info = []
        for source in self.sources:
            sources_info.append({
                "name": source.name,
                "type": source.source_type.value,
                "available": source.is_available,
            })

        return {
            "total_sources": total,
            "available_sources": available,
            "unavailable_sources": unavailable,
            "sources": sources_info,
        }

    def print_source_stats(self):
        """打印数据源统计信息"""
        stats = self.get_source_stats()
        print("\n" + "=" * 60)
        print("数据源统计信息")
        print("=" * 60)
        print(f"总数据源: {stats['total_sources']}")
        print(f"可用数据源: {stats['available_sources']}")
        print(f"不可用数据源: {stats['unavailable_sources']}")
        print("\n详细信息:")
        for source in stats['sources']:
            status = "✓ 可用" if source['available'] else "✗ 不可用"
            print(f"  {source['name']} ({source['type']}) - {status}")
        print("=" * 60 + "\n")

