"""
实时数据缓存 - 快速参考卡
"""

# ============================================================================
# VIMaster v3.0 - 实时数据缓存机制快速参考
# ============================================================================

# 导入
from src.data import (
    MultiSourceDataProvider,     # 多源数据提供者（已集成缓存）
    RealTimeCache,              # 缓存实现
    CacheConfig,                # 缓存配置
    CacheConfigManager,         # 配置管理器
    get_cache,                  # 获取全局缓存
    init_cache,                 # 初始化全局缓存
    get_cache_config,           # 获取配置
    set_cache_config,           # 设置配置
)

# ============================================================================
# 1. 基本使用
# ============================================================================

provider = MultiSourceDataProvider()

# 首次调用：从数据源获取（1-5 秒）
metrics = provider.get_financial_metrics("600519")

# 后续调用：从缓存获取（1-5 毫秒）
metrics = provider.get_financial_metrics("600519")

# ============================================================================
# 2. 查看统计信息
# ============================================================================

# 方式 1: 通过数据提供者
stats = provider.get_cache_stats()
provider.print_cache_stats()

# 方式 2: 直接访问缓存
cache = get_cache()
stats = cache.get_stats()
cache.print_stats()

# 统计包含:
# - cache_size: 当前缓存大小
# - max_size: 最大缓存大小
# - hits: 命中次数
# - misses: 未命中次数
# - hit_rate: 命中率（百分比）
# - refreshes: 刷新次数
# - evictions: 驱逐次数
# - total_requests: 总请求数

# ============================================================================
# 3. 配置缓存
# ============================================================================

# 方式 1: 部分更新
from src.data.cache_config import CacheConfigManager

CacheConfigManager.update_config(
    default_ttl=600,  # 10 分钟
    max_size=500,  # 500 个条目
    enable_background_refresh=True
)

# 方式 2: 使用辅助函数
set_cache_config(
    default_ttl=600,
    stock_info_ttl=1800,  # 30 分钟
    financial_metrics_ttl=86400  # 1 天
)

# 方式 3: 创建完整配置
config = CacheConfig(
    max_size=1000,
    default_ttl=300,
    refresh_interval_seconds=60,
    enable_background_refresh=True
)
CacheConfigManager.set_config(config)

# ============================================================================
# 4. TTL 配置（生存时间，单位：秒）
# ============================================================================

# 默认 TTL：
# - default_ttl = 300（5 分钟）
# - stock_info_ttl = 3600（1 小时）
# - financial_metrics_ttl = 86400（1 天）
# - historical_price_ttl = 86400（1 天）
# - industry_info_ttl = 604800（7 天）

# 修改 TTL：
set_cache_config(
    default_ttl=600,  # 改为 10 分钟
    stock_info_ttl=7200,  # 改为 2 小时
)

# ============================================================================
# 5. 清除缓存
# ============================================================================

# 清除特定股票的缓存
provider.clear_cache("600519")

# 清除所有缓存
provider.clear_cache()

# 按模式删除
cache = get_cache()
cache.delete_pattern("stock:")  # 删除所有 "stock:" 开头的缓存

# 删除单个条目
cache.delete("specific_key")

# 清空所有
cache.clear()

# ============================================================================
# 6. 直接使用缓存
# ============================================================================

cache = RealTimeCache(
    max_size=1000,
    default_ttl_seconds=300,
    refresh_interval_seconds=60,
    enable_background_refresh=True
)

# 设置缓存
cache.set("key", "value", ttl_seconds=600)

# 获取缓存
value = cache.get("key")

# 删除缓存
cache.delete("key")

# 刷新单个或所有缓存
cache.refresh_all()

# ============================================================================
# 7. 性能对比
# ============================================================================

import time

# 首次查询（从数据源）
start = time.time()
metrics = provider.get_financial_metrics("600519")
time1 = time.time() - start

# 第二次查询（从缓存）
start = time.time()
metrics = provider.get_financial_metrics("600519")
time2 = time.time() - start

print(f"首次: {time1:.3f}s")
print(f"缓存: {time2:.3f}s")
print(f"加速比: {time1/time2:.0f}x")

# 期望结果:
# 首次: 2.500s
# 缓存: 0.005s
# 加速比: 500x

# ============================================================================
# 8. 后台刷新
# ============================================================================

# 启用后台刷新
set_cache_config(enable_background_refresh=True)

# 禁用后台刷新
set_cache_config(enable_background_refresh=False)

# 手动刷新
cache = get_cache()
refreshed_count = cache.refresh_all()
print(f"刷新了 {refreshed_count} 个缓存")

# ============================================================================
# 9. 智能市场时间刷新
# ============================================================================

# 根据市场时间自动调整刷新频率：
# - 市场开放时间（9:00-15:00）：每 5 分钟刷新一次
# - 市场关闭时间：每 1 小时刷新一次

set_cache_config(
    enable_smart_refresh=True,  # 启用智能刷新
    market_open_hour=9,  # 早上 9 点
    market_close_hour=15,  # 下午 3 点
    market_open_refresh_interval=300,  # 市场开放时 5 分钟
    market_close_refresh_interval=3600  # 市场关闭时 1 小时
)

# ============================================================================
# 10. 线程安全
# ============================================================================

import threading

# 缓存是线程安全的，可以在多线程中直接使用
cache = get_cache()

def worker():
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}")
        cache.get(f"key_{i}")

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# 无需额外的同步机制

# ============================================================================
# 常见问题
# ============================================================================

# Q1: 如何禁用缓存？
set_cache_config(enabled=False)

# Q2: 缓存的默认大小是多少？
config = get_cache_config()
print(config.max_size)  # 1000

# Q3: 缓存什么时候自动清除过期数据？
# A: 访问过期数据时自动清除，后台刷新线程会定期更新

# Q4: 如何监控缓存性能？
stats = get_cache().get_stats()
print(f"命中率: {stats['hit_rate']}")

# Q5: 可以自定义刷新回调吗？
# A: 可以，在 set() 时传入 refresh_callback 参数

# ============================================================================
# 最佳实践
# ============================================================================

# ✓ 根据数据特性设置合适的 TTL
# ✓ 监控缓存命中率，优化配置
# ✓ 在数据源更新时及时清除缓存
# ✓ 定期检查缓存大小，避免内存溢出
# ✓ 在多线程应用中放心使用缓存

# ============================================================================
# 更多信息
# ============================================================================

# 完整文档: REAL_TIME_CACHING_GUIDE.md
# 演示脚本: demo_caching_mechanism.py
# 单元测试: tests/unit/test_cache_layer.py
