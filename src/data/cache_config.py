"""
缓存配置模块 - 集中管理缓存配置
"""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """缓存配置"""

    # 基础配置
    enabled: bool = True  # 是否启用缓存
    max_size: int = 1000  # 最大缓存条目数

    # TTL 配置（秒）
    default_ttl: int = 300  # 默认 TTL（5 分钟）
    stock_info_ttl: int = 3600  # 股票信息 TTL（1 小时）
    financial_metrics_ttl: int = 86400  # 财务指标 TTL（1 天）
    historical_price_ttl: int = 86400  # 历史价格 TTL（1 天）
    industry_info_ttl: int = 604800  # 行业信息 TTL（7 天）

    # 刷新配置（秒）
    refresh_interval: int = 60  # 刷新间隔（1 分钟）
    enable_background_refresh: bool = True  # 启用后台刷新

    # 智能刷新配置
    enable_smart_refresh: bool = True  # 启用智能刷新（基于市场时间）
    market_open_hour: int = 9  # 市场开盘时间（小时）
    market_close_hour: int = 15  # 市场收盘时间（小时）
    market_open_refresh_interval: int = 300  # 市场开放时间刷新间隔（5 分钟）
    market_close_refresh_interval: int = 3600  # 市场关闭时间刷新间隔（1 小时）

    # 监控和统计
    enable_stats: bool = True  # 启用统计
    log_cache_operations: bool = False  # 记录缓存操作日志

    # 持久化配置（可选）
    enable_persistence: bool = False  # 启用持久化
    persistence_path: Optional[str] = None  # 持久化文件路径
    auto_load_on_start: bool = True  # 启动时自动加载持久化数据

    def validate(self) -> bool:
        """验证配置"""
        if self.max_size <= 0:
            logger.warning("缓存大小必须大于 0，使用默认值 1000")
            self.max_size = 1000

        if self.default_ttl <= 0:
            logger.warning("默认 TTL 必须大于 0，使用默认值 300")
            self.default_ttl = 300

        return True


# 默认配置
DEFAULT_CACHE_CONFIG = CacheConfig()


class CacheConfigManager:
    """缓存配置管理器"""

    _instance: Optional['CacheConfigManager'] = None
    _config: CacheConfig = DEFAULT_CACHE_CONFIG

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls) -> CacheConfig:
        """获取配置"""
        return cls._config

    @classmethod
    def set_config(cls, config: CacheConfig) -> None:
        """设置配置"""
        config.validate()
        cls._config = config
        logger.info("缓存配置已更新")

    @classmethod
    def update_config(cls, **kwargs) -> None:
        """更新配置（部分）"""
        for key, value in kwargs.items():
            if hasattr(cls._config, key):
                setattr(cls._config, key, value)
        cls._config.validate()
        logger.info(f"缓存配置已部分更新: {kwargs}")

    @classmethod
    def get_ttl_for(cls, data_type: str) -> int:
        """获取指定数据类型的 TTL"""
        ttl_map = {
            "stock_info": cls._config.stock_info_ttl,
            "financial_metrics": cls._config.financial_metrics_ttl,
            "historical_price": cls._config.historical_price_ttl,
            "industry_info": cls._config.industry_info_ttl,
        }
        return ttl_map.get(data_type, cls._config.default_ttl)

    @classmethod
    def get_refresh_interval(cls) -> int:
        """获取刷新间隔"""
        if cls._config.enable_smart_refresh:
            from datetime import datetime
            current_hour = datetime.now().hour

            if cls._config.market_open_hour <= current_hour < cls._config.market_close_hour:
                # 市场开放时间
                return cls._config.market_open_refresh_interval
            else:
                # 市场关闭时间
                return cls._config.market_close_refresh_interval

        return cls._config.refresh_interval


def get_cache_config() -> CacheConfig:
    """获取缓存配置"""
    return CacheConfigManager.get_config()


def set_cache_config(**kwargs) -> None:
    """设置缓存配置"""
    CacheConfigManager.update_config(**kwargs)
