"""
实时数据缓存层 - 支持 TTL、自动刷新、线程安全
"""
import logging
import threading
import time
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int
    refresh_callback: Optional[Callable] = None
    last_refreshed_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl_seconds <= 0:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds

    def should_refresh(self, refresh_interval: int) -> bool:
        """检查是否需要刷新"""
        if self.refresh_callback is None:
            return False
        if self.last_refreshed_at is None:
            return True
        elapsed = (datetime.now() - self.last_refreshed_at).total_seconds()
        return elapsed > refresh_interval

    def refresh(self) -> bool:
        """刷新缓存值"""
        if self.refresh_callback is None:
            return False
        try:
            self.value = self.refresh_callback()
            self.last_refreshed_at = datetime.now()
            logger.debug(f"缓存 {self.key} 刷新成功")
            return True
        except Exception as e:
            logger.warning(f"缓存 {self.key} 刷新失败: {str(e)}")
            return False


class RealTimeCache:
    """实时数据缓存 - 线程安全、支持 TTL 和自动刷新"""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl_seconds: int = 300,
        refresh_interval_seconds: int = 60,
        enable_background_refresh: bool = True
    ):
        """
        初始化缓存
        Args:
            max_size: 最大缓存条目数
            default_ttl_seconds: 默认 TTL（秒）
            refresh_interval_seconds: 刷新间隔（秒）
            enable_background_refresh: 是否启用后台刷新
        """
        self.max_size = max_size
        self.default_ttl_seconds = default_ttl_seconds
        self.refresh_interval_seconds = refresh_interval_seconds
        self.enable_background_refresh = enable_background_refresh

        # 使用 OrderedDict 实现 LRU
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()

        # 统计信息
        self.hits = 0
        self.misses = 0
        self.refreshes = 0
        self.evictions = 0

        # 后台刷新线程
        self._refresh_thread: Optional[threading.Thread] = None
        self._stop_refresh = False

        if enable_background_refresh:
            self._start_background_refresh()

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        Args:
            key: 缓存键
        Returns:
            缓存值或None
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]

            # 检查过期
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None

            # 移到最后（LRU）
            self.cache.move_to_end(key)
            self.hits += 1

            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        refresh_callback: Optional[Callable] = None
    ) -> None:
        """
        设置缓存值
        Args:
            key: 缓存键
            value: 缓存值
            ttl_seconds: TTL（秒），None 表示使用默认值
            refresh_callback: 刷新回调函数
        """
        with self.lock:
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

            # 如果键已存在，先删除
            if key in self.cache:
                del self.cache[key]

            # 检查是否需要驱逐
            if len(self.cache) >= self.max_size:
                # 驱逐最旧的条目（LRU）
                oldest_key, _ = self.cache.popitem(last=False)
                self.evictions += 1
                logger.debug(f"缓存已满，驱逐最旧条目: {oldest_key}")

            # 创建新条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                ttl_seconds=ttl,
                refresh_callback=refresh_callback
            )

            self.cache[key] = entry
            logger.debug(f"缓存 {key} 已设置，TTL: {ttl}s")

    def delete(self, key: str) -> bool:
        """
        删除缓存值
        Args:
            key: 缓存键
        Returns:
            是否成功删除
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"缓存 {key} 已删除")
                return True
            return False

    def clear(self) -> None:
        """清空所有缓存"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"缓存已清空（{count} 个条目）")

    def delete_pattern(self, pattern: str) -> int:
        """
        按模式删除缓存
        Args:
            pattern: 键的前缀模式（如 "stock:600519"）
        Returns:
            删除的条目数
        """
        with self.lock:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                del self.cache[key]
            logger.debug(f"按模式 {pattern} 删除了 {len(keys_to_delete)} 个缓存")
            return len(keys_to_delete)

    def refresh_all(self) -> int:
        """
        刷新所有支持刷新的缓存
        Returns:
            成功刷新的条目数
        """
        with self.lock:
            refreshed = 0
            for entry in self.cache.values():
                if entry.refresh_callback and entry.refresh():
                    refreshed += 1
            self.refreshes += refreshed
            logger.info(f"刷新了 {refreshed} 个缓存")
            return refreshed

    def _start_background_refresh(self) -> None:
        """启动后台刷新线程"""
        if self._refresh_thread is None or not self._refresh_thread.is_alive():
            self._refresh_thread = threading.Thread(
                target=self._background_refresh_loop,
                daemon=True
            )
            self._refresh_thread.start()
            logger.info("后台缓存刷新线程已启动")

    def _background_refresh_loop(self) -> None:
        """后台刷新循环"""
        while not self._stop_refresh:
            try:
                time.sleep(self.refresh_interval_seconds)

                with self.lock:
                    refreshed = 0
                    for entry in list(self.cache.values()):
                        if entry.should_refresh(self.refresh_interval_seconds):
                            if entry.refresh():
                                refreshed += 1

                    if refreshed > 0:
                        self.refreshes += refreshed
                        logger.debug(f"后台刷新了 {refreshed} 个缓存")
            except Exception as e:
                logger.error(f"后台刷新失败: {str(e)}")

    def stop_background_refresh(self) -> None:
        """停止后台刷新线程"""
        self._stop_refresh = True
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
            logger.info("后台缓存刷新线程已停止")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "cache_size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "refreshes": self.refreshes,
                "evictions": self.evictions,
                "total_requests": total_requests,
            }

    def print_stats(self) -> None:
        """打印缓存统计信息"""
        stats = self.get_stats()
        print("\n" + "=" * 60)
        print("缓存统计信息")
        print("=" * 60)
        for key, value in stats.items():
            print(f"{key:20} : {value}")
        print("=" * 60 + "\n")


# 全局缓存实例
_global_cache: Optional[RealTimeCache] = None


def get_cache() -> RealTimeCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = RealTimeCache(
            max_size=1000,
            default_ttl_seconds=300,  # 5 分钟
            refresh_interval_seconds=60,  # 1 分钟
            enable_background_refresh=True
        )
    return _global_cache


def init_cache(**kwargs) -> RealTimeCache:
    """初始化全局缓存"""
    global _global_cache
    _global_cache = RealTimeCache(**kwargs)
    return _global_cache
