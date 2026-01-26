"""
实时数据缓存机制单元测试
"""
import pytest
import sys
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.cache_layer import RealTimeCache, CacheEntry, get_cache, init_cache
from src.data.cache_config import CacheConfig, CacheConfigManager, get_cache_config, set_cache_config


class TestCacheEntry:
    """缓存条目测试"""

    def test_cache_entry_creation(self):
        """测试缓存条目创建"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            ttl_seconds=300
        )

        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.ttl_seconds == 300

    def test_cache_entry_not_expired(self):
        """测试缓存条目未过期"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            ttl_seconds=300
        )

        assert not entry.is_expired()

    def test_cache_entry_expired(self):
        """测试缓存条目已过期"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now() - timedelta(seconds=350),
            ttl_seconds=300
        )

        assert entry.is_expired()

    def test_cache_entry_no_ttl(self):
        """测试没有 TTL 的缓存条目"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            ttl_seconds=0  # 无过期时间
        )

        assert not entry.is_expired()


class TestRealTimeCache:
    """实时缓存测试"""

    def setup_method(self):
        """测试前的设置"""
        self.cache = RealTimeCache(
            max_size=100,
            default_ttl_seconds=300,
            refresh_interval_seconds=60,
            enable_background_refresh=False
        )

    def test_cache_initialization(self):
        """测试缓存初始化"""
        assert self.cache.max_size == 100
        assert len(self.cache.cache) == 0
        assert self.cache.hits == 0
        assert self.cache.misses == 0

    def test_cache_set_and_get(self):
        """测试设置和获取缓存"""
        self.cache.set("key1", "value1")

        result = self.cache.get("key1")

        assert result == "value1"
        assert self.cache.hits == 1

    def test_cache_get_nonexistent(self):
        """测试获取不存在的缓存"""
        result = self.cache.get("nonexistent")

        assert result is None
        assert self.cache.misses == 1

    def test_cache_delete(self):
        """测试删除缓存"""
        self.cache.set("key1", "value1")
        deleted = self.cache.delete("key1")

        assert deleted is True
        assert self.cache.get("key1") is None

    def test_cache_clear(self):
        """测试清空缓存"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()

        assert len(self.cache.cache) == 0

    def test_cache_delete_pattern(self):
        """测试按模式删除缓存"""
        self.cache.set("stock:600519", "data1")
        self.cache.set("stock:000858", "data2")
        self.cache.set("industry:tech", "data3")

        deleted = self.cache.delete_pattern("stock:")

        assert deleted == 2
        assert self.cache.get("stock:600519") is None
        assert self.cache.get("industry:tech") == "data3"

    def test_cache_lru_eviction(self):
        """测试 LRU 驱逐"""
        cache = RealTimeCache(max_size=3, enable_background_refresh=False)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 访问 key1，使其变为最新
        cache.get("key1")

        # 添加 key4，应该驱逐 key2（最旧的）
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # 仍然存在
        assert cache.get("key2") is None  # 被驱逐
        assert cache.get("key3") == "value3"  # 仍然存在
        assert cache.get("key4") == "value4"  # 新键存在

    def test_cache_ttl_expiry(self):
        """测试 TTL 过期"""
        cache = RealTimeCache(enable_background_refresh=False)
        cache.set("key1", "value1", ttl_seconds=1)

        # 立即获取应该成功
        assert cache.get("key1") == "value1"

        # 等待 TTL 过期
        time.sleep(1.1)

        # 再次获取应该失败
        assert cache.get("key1") is None

    def test_cache_stats(self):
        """测试缓存统计"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # 命中
        self.cache.get("key2")  # 未命中

        stats = self.cache.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["cache_size"] == 1
        assert "hit_rate" in stats

    def test_cache_refresh_callback(self):
        """测试刷新回调"""
        call_count = [0]

        def refresh_callback():
            call_count[0] += 1
            return f"refreshed_{call_count[0]}"

        self.cache.set("key1", "initial_value", refresh_callback=refresh_callback)

        # 手动刷新
        self.cache.refresh_all()

        assert call_count[0] == 1

    def test_cache_thread_safety(self):
        """测试线程安全性"""
        cache = RealTimeCache(enable_background_refresh=False)
        errors = []

        def worker(thread_id):
            try:
                for i in range(100):
                    cache.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")
                    cache.get(f"key_{thread_id}_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestCacheConfig:
    """缓存配置测试"""

    def test_cache_config_creation(self):
        """测试配置创建"""
        config = CacheConfig()

        assert config.enabled is True
        assert config.max_size == 1000
        assert config.default_ttl == 300

    def test_cache_config_validation(self):
        """测试配置验证"""
        config = CacheConfig(max_size=-1)
        config.validate()

        assert config.max_size == 1000  # 应该被更正

    def test_cache_config_manager_singleton(self):
        """测试配置管理器单例"""
        manager1 = CacheConfigManager()
        manager2 = CacheConfigManager()

        assert manager1 is manager2

    def test_cache_config_get_ttl(self):
        """测试获取 TTL"""
        config = CacheConfig()
        CacheConfigManager.set_config(config)

        ttl = CacheConfigManager.get_ttl_for("stock_info")

        assert ttl == config.stock_info_ttl

    def test_cache_config_update(self):
        """测试更新配置"""
        config = CacheConfig()
        CacheConfigManager.set_config(config)

        CacheConfigManager.update_config(max_size=500)

        updated_config = CacheConfigManager.get_config()
        assert updated_config.max_size == 500


class TestCacheGlobalInstance:
    """全局缓存实例测试"""

    def test_get_global_cache(self):
        """测试获取全局缓存"""
        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2

    def test_init_global_cache(self):
        """测试初始化全局缓存"""
        cache = init_cache(max_size=500)

        assert cache.max_size == 500

    def test_get_cache_config(self):
        """测试获取缓存配置"""
        config = get_cache_config()

        assert isinstance(config, CacheConfig)

    def test_set_cache_config(self):
        """测试设置缓存配置"""
        set_cache_config(max_size=750, default_ttl=600)

        config = get_cache_config()
        assert config.max_size == 750
        assert config.default_ttl == 600


class TestCachePerformance:
    """缓存性能测试"""

    def test_cache_hit_performance(self):
        """测试缓存命中性能"""
        cache = RealTimeCache(enable_background_refresh=False)

        # 设置 1000 个缓存条目
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")

        # 测试随机访问性能
        start_time = time.time()
        for i in range(10000):
            cache.get(f"key_{i % 1000}")
        elapsed = time.time() - start_time

        # 应该在 1 秒内完成
        assert elapsed < 1.0
        assert cache.hits > 9000

    def test_cache_miss_performance(self):
        """测试缓存未命中性能"""
        cache = RealTimeCache(enable_background_refresh=False)

        start_time = time.time()
        for i in range(10000):
            cache.get(f"nonexistent_{i}")
        elapsed = time.time() - start_time

        # 应该快速返回
        assert elapsed < 1.0
        assert cache.misses == 10000

