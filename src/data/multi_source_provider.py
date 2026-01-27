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
        self.source_priority = [
            DataSourceType.TUSHARE,
            DataSourceType.BAOSTOCK,
            DataSourceType.AKSHARE,
            DataSourceType.MOCK,
        ]

        # 初始化各数据源
        self._init_sources(tushare_token)
        self._log_source_status()

    def _init_sources(self, tushare_token: Optional[str] = None):
        """初始化所有数据源"""
        # TuShare
        try:
            ts_provider = TuShareProvider(token=tushare_token)
            self.sources.append(ts_provider)
        except Exception as e:
            logger.warning(f"TuShare 初始化失败: {str(e)}")

        # BaoStock
        try:
            bs_provider = BaoStockProvider()
            self.sources.append(bs_provider)
        except Exception as e:
            logger.warning(f"BaoStock 初始化失败: {str(e)}")

        # AkShare (始终可用，作为备选)
        try:
            ak_provider = AkshareDataProvider
            # 将 AkshareDataProvider 包装为 BaseDataSource 兼容形式
            logger.info("AkShare 已添加为备选数据源")
        except Exception as e:
            logger.warning(f"AkShare 初始化失败: {str(e)}")

    def _log_source_status(self):
        """记录数据源状态"""
        logger.info("=" * 60)
        logger.info("数据源初始化状态:")
        for source in self.sources:
            logger.info(f"  {source}")
        logger.info("=" * 60)

    def get_available_sources(self) -> List[BaseDataSource]:
        """获取所有可用的数据源"""
        return [s for s in self.sources if s.is_available]

    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票信息 - 智能降级
        Args:
            stock_code: 股票代码
        Returns:
            股票信息字典或None
        """
        for source in self.sources:
            if source.is_available:
                try:
                    result = source.get_stock_info(stock_code)
                    if result:
                        logger.info(f"从 {source.name} 获取股票 {stock_code} 信息成功")
                        return result
                except Exception as e:
                    logger.warning(f"从 {source.name} 获取信息失败: {str(e)}")
                    continue

        # 降级到 AkShare
        try:
            result = AkshareDataProvider.get_stock_info(stock_code)
            if result:
                logger.info(f"从 AkShare 获取股票 {stock_code} 信息成功（备选）")
                return result
        except Exception as e:
            logger.warning(f"AkShare 降级失败: {str(e)}")

        return None

    def get_financial_metrics(self, stock_code: str) -> Optional[FinancialMetrics]:
        """
        获取财务指标 - 智能降级
        Args:
            stock_code: 股票代码
        Returns:
            FinancialMetrics 对象或None
        """
        for source in self.sources:
            if source.is_available:
                try:
                    result = source.get_financial_metrics(stock_code)
                    if result:
                        logger.info(f"从 {source.name} 获取股票 {stock_code} 财务指标成功")
                        return result
                except Exception as e:
                    logger.warning(f"从 {source.name} 获取财务指标失败: {str(e)}")
                    continue

        # 降级到 AkShare
        try:
            result = AkshareDataProvider.get_financial_metrics(stock_code)
            if result:
                logger.info(f"从 AkShare 获取股票 {stock_code} 财务指标成功（备选）")
                return result
        except Exception as e:
            logger.warning(f"AkShare 降级失败: {str(e)}")

        return None

    def get_historical_price(self, stock_code: str, days: int = 250) -> Optional[pd.DataFrame]:
        """
        获取历史价格 - 智能降级
        Args:
            stock_code: 股票代码
            days: 获取天数
        Returns:
            历史价格DataFrame或None
        """
        for source in self.sources:
            if source.is_available:
                try:
                    result = source.get_historical_price(stock_code, days)
                    if result is not None and not (isinstance(result, pd.DataFrame) and result.empty):
                        logger.info(f"从 {source.name} 获取股票 {stock_code} 历史价格成功")
                        return result
                except Exception as e:
                    logger.warning(f"从 {source.name} 获取历史价格失败: {str(e)}")
                    continue

        # 降级到 AkShare
        try:
            result = AkshareDataProvider.get_historical_price(stock_code, days)
            if result is not None and not result.empty:
                logger.info(f"从 AkShare 获取股票 {stock_code} 历史价格成功（备选）")
                return result
        except Exception as e:
            logger.warning(f"AkShare 降级失败: {str(e)}")

        return None

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
        result = None
        for source in self.sources:
            if source.is_available:
                try:
                    result = source.get_industry_info(stock_code)
                    if result:
                        logger.info(f"从 {source.name} 获取股票 {stock_code} 行业信息成功")
                        # 存入缓存
                        if config.enabled:
                            ttl = CacheConfigManager.get_ttl_for("industry_info")
                            cache.set(cache_key, result, ttl_seconds=ttl)
                        return result
                except Exception as e:
                    logger.warning(f"从 {source.name} 获取行业信息失败: {str(e)}")
                    continue

        # 降级到 AkShare
        try:
            result = AkshareDataProvider.get_industry_info(stock_code)
            if result:
                logger.info(f"从 AkShare 获取股票 {stock_code} 行业信息成功（备选）")
                # 存入缓存
                if config.enabled:
                    ttl = CacheConfigManager.get_ttl_for("industry_info")
                    cache.set(cache_key, result, ttl_seconds=ttl)
                return result
        except Exception as e:
            logger.warning(f"AkShare 降级失败: {str(e)}")

        return None

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

