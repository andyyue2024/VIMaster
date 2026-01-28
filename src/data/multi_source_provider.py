"""
多源数据管理器 - 统一管理多个数据源并实现智能降级

功能特点：
1. 多数据源自动切换管理
2. 按优先级依次尝试：AkShare > TuShare > BaoStock > Mock
3. 确保 Mock 数据作为最后保障
4. 集成实时数据缓存机制
5. 统一对外接口
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
    """
    多源数据提供者 - 统一接口，智能降级

    数据源优先级（从高到低）：
    1. AkShare (东方财富) - 免费、稳定、数据丰富
    2. TuShare - 需要 token，数据专业
    3. BaoStock - 免费、历史数据丰富
    4. Mock - 本地预定义数据，最后保障
    """

    def __init__(self, tushare_token: Optional[str] = None):
        """
        初始化多源数据提供者
        Args:
            tushare_token: TuShare API token (可选)
        """
        self.sources: List[BaseDataSource] = []

        # 数据源优先级：AkShare > TuShare > BaoStock > Mock
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
        """初始化所有数据源并按优先级排序"""
        sources: List[BaseDataSource] = []

        # AkShare (优先级最高)
        try:
            sources.append(AkshareDataProvider())
            logger.info("AkShare 数据源初始化成功")
        except Exception as e:
            logger.warning(f"AkShare 初始化失败: {str(e)}")

        # TuShare
        try:
            sources.append(TuShareProvider(token=tushare_token))
            logger.info("TuShare 数据源初始化成功")
        except Exception as e:
            logger.warning(f"TuShare 初始化失败: {str(e)}")

        # BaoStock
        try:
            sources.append(BaoStockProvider())
            logger.info("BaoStock 数据源初始化成功")
        except Exception as e:
            logger.warning(f"BaoStock 初始化失败: {str(e)}")

        # Mock (始终可用，最后保障)
        try:
            sources.append(MockDataProvider())
            logger.info("MockData 数据源初始化成功 (备用)")
        except Exception as e:
            logger.warning(f"MockData 初始化失败: {str(e)}")

        # 按优先级排序
        priority_order = {stype: idx for idx, stype in enumerate(self.source_priority)}
        self.sources = sorted(sources, key=lambda s: priority_order.get(s.source_type, 999))

    def _log_source_status(self):
        """记录数据源状态"""
        logger.info("=" * 60)
        logger.info("数据源初始化状态 (按优先级排序):")
        for idx, source in enumerate(self.sources, 1):
            status = "✓ 可用" if source.is_available else "✗ 不可用"
            logger.info(f"  {idx}. {source.name} ({source.source_type.value}) - {status}")
        logger.info("=" * 60)

    def _iterate_sources(self) -> List[BaseDataSource]:
        """返回按优先级排序的数据源列表"""
        return self.sources

    def get_available_sources(self) -> List[BaseDataSource]:
        """获取所有可用的数据源"""
        return [s for s in self._iterate_sources() if s.is_available]

    def _get_by_priority(self, func_name: str, *args, **kwargs):
        """
        按优先级依次尝试获取数据
        确保 Mock 作为最后保障
        """
        errors = []
        for source in self._iterate_sources():
            if not source.is_available:
                continue
            try:
                func = getattr(source, func_name)
                result = func(*args, **kwargs)
                if result is not None:
                    # 对于 DataFrame 需要检查是否为空
                    if isinstance(result, pd.DataFrame) and result.empty:
                        continue
                    logger.debug(f"从 {source.name} 获取 {func_name} 成功")
                    return result
            except Exception as e:
                errors.append(f"{source.name}: {str(e)}")
                logger.warning(f"{source.name} 调用 {func_name} 失败: {str(e)}")
                continue

        if errors:
            logger.error(f"所有数据源获取 {func_name} 失败: {'; '.join(errors)}")
        return None

    def _get_with_cache(self, cache_key: str, func_name: str, *args, **kwargs):
        """带缓存的数据获取"""
        cache = get_cache()
        config = CacheConfigManager.get_config()

        # 检查缓存
        if config.enabled:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"从缓存获取: {cache_key}")
                return cached

        # 从数据源获取
        result = self._get_by_priority(func_name, *args, **kwargs)

        # 存入缓存
        if result is not None and config.enabled:
            ttl = CacheConfigManager.get_ttl_for(func_name)
            cache.set(cache_key, result, ttl_seconds=ttl)
            logger.debug(f"已缓存: {cache_key}, TTL={ttl}s")

        return result

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票信息
        Args:
            stock_code: 股票代码
        Returns:
            股票信息字典
        """
        cache_key = f"stock_info:{stock_code}"
        return self._get_with_cache(cache_key, 'get_stock_info', stock_code)

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象
        """
        cache_key = f"financial_metrics:{stock_code}"
        return self._get_with_cache(cache_key, 'get_financial_metrics', stock_code)

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[pd.DataFrame]:
        """
        获取历史价格
        Args:
            stock_code: 股票代码
            days: 天数
        Returns:
            历史价格 DataFrame
        """
        cache_key = f"historical_price:{stock_code}:{days}"
        return self._get_with_cache(cache_key, 'get_historical_price', stock_code, days)

    def get_industry_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取行业信息
        Args:
            stock_code: 股票代码
        Returns:
            行业信息字典
        """
        cache_key = f"industry_info:{stock_code}"
        return self._get_with_cache(cache_key, 'get_industry_info', stock_code)

    def clear_cache(self, stock_code: Optional[str] = None) -> int:
        """
        清空缓存
        Args:
            stock_code: 股票代码，如果为 None 则清空所有缓存
        Returns:
            清除的缓存数量
        """
        cache = get_cache()
        if stock_code is None:
            count = cache.clear()
            logger.info(f"已清空所有缓存，共 {count} 条")
            return count
        else:
            # 清空该股票的所有缓存
            patterns = [
                f"stock_info:{stock_code}",
                f"financial_metrics:{stock_code}",
                f"historical_price:{stock_code}:*",
                f"industry_info:{stock_code}",
            ]
            count = 0
            for pattern in patterns:
                count += cache.delete_pattern(pattern)
            logger.info(f"已清空股票 {stock_code} 的缓存，共 {count} 条")
            return count

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
        for idx, source in enumerate(self.sources, 1):
            sources_info.append({
                "priority": idx,
                "name": source.name,
                "type": source.source_type.value,
                "available": source.is_available,
            })

        return {
            "total_sources": total,
            "available_sources": available,
            "unavailable_sources": unavailable,
            "priority_order": [s.value for s in self.source_priority],
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
        print(f"\n优先级顺序: {' > '.join(stats['priority_order'])}")
        print("\n详细信息:")
        for source in stats['sources']:
            status = "✓ 可用" if source['available'] else "✗ 不可用"
            print(f"  {source['priority']}. {source['name']} ({source['type']}) - {status}")
        print("=" * 60 + "\n")

    def get_mock_provider(self) -> Optional[MockDataProvider]:
        """获取 Mock 数据提供者实例"""
        for source in self.sources:
            if isinstance(source, MockDataProvider):
                return source
        return None

    def get_mock_stocks(self) -> List[str]:
        """获取 Mock 数据支持的股票列表"""
        mock = self.get_mock_provider()
        if mock:
            return mock.get_all_stocks()
        return []

    def get_mock_industries(self) -> List[str]:
        """获取 Mock 数据支持的行业列表"""
        mock = self.get_mock_provider()
        if mock:
            return mock.get_available_industries()
        return []
