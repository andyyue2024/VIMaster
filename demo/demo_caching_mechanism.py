"""
实时数据缓存演示脚本
"""
import sys
from pathlib import Path
import time
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data import MultiSourceDataProvider
from src.data.cache_layer import get_cache, init_cache
from src.data.cache_config import CacheConfigManager, set_cache_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_caching():
    """演示 1: 基础缓存功能"""
    print("\n" + "=" * 80)
    print("演示 1: 基础缓存功能")
    print("=" * 80)

    provider = MultiSourceDataProvider()

    # 首次获取（从数据源）
    print("\n【首次获取数据（从数据源）】")
    start = time.time()
    metrics1 = provider.get_financial_metrics("600519")
    elapsed1 = time.time() - start
    print(f"耗时: {elapsed1:.3f} 秒")

    # 第二次获取（从缓存）
    print("\n【第二次获取数据（从缓存）】")
    start = time.time()
    metrics2 = provider.get_financial_metrics("600519")
    elapsed2 = time.time() - start
    print(f"耗时: {elapsed2:.3f} 秒")
    print(f"加速比: {elapsed1/elapsed2:.1f}x")

    # 验证数据一致性
    if metrics1 and metrics2:
        print(f"\n数据一致性: {metrics1 == metrics2}")


def demo_cache_configuration():
    """演示 2: 缓存配置"""
    print("\n" + "=" * 80)
    print("演示 2: 缓存配置")
    print("=" * 80)

    # 获取当前配置
    config = CacheConfigManager.get_config()
    print(f"\n当前配置:")
    print(f"  启用: {config.enabled}")
    print(f"  最大大小: {config.max_size}")
    print(f"  默认 TTL: {config.default_ttl}s")
    print(f"  股票信息 TTL: {config.stock_info_ttl}s")
    print(f"  财务指标 TTL: {config.financial_metrics_ttl}s")
    print(f"  历史价格 TTL: {config.historical_price_ttl}s")

    # 修改配置
    print("\n【修改缓存配置】")
    set_cache_config(
        default_ttl=600,  # 改为 10 分钟
        max_size=500,  # 改为 500 条
        enable_background_refresh=True
    )

    updated_config = CacheConfigManager.get_config()
    print(f"更新后:")
    print(f"  默认 TTL: {updated_config.default_ttl}s")
    print(f"  最大大小: {updated_config.max_size}")
    print(f"  后台刷新: {updated_config.enable_background_refresh}")


def demo_cache_statistics():
    """演示 3: 缓存统计"""
    print("\n" + "=" * 80)
    print("演示 3: 缓存统计")
    print("=" * 80)

    provider = MultiSourceDataProvider()

    # 进行多次查询
    print("\n【执行多次数据查询】")
    stocks = ["600519", "000858", "000651", "600036"]

    # 第一轮：从数据源
    print("\n第一轮查询（从数据源）:")
    for code in stocks:
        provider.get_financial_metrics(code)
        print(f"  {code}: 已获取")

    # 第二轮：从缓存
    print("\n第二轮查询（从缓存）:")
    for code in stocks:
        provider.get_financial_metrics(code)
        print(f"  {code}: 已获取")

    # 显示统计信息
    print("\n【缓存统计信息】")
    provider.print_cache_stats()


def demo_cache_invalidation():
    """演示 4: 缓存失效"""
    print("\n" + "=" * 80)
    print("演示 4: 缓存失效和清除")
    print("=" * 80)

    provider = MultiSourceDataProvider()

    # 缓存数据
    print("\n【缓存数据】")
    provider.get_stock_info("600519")
    provider.get_financial_metrics("600519")
    provider.get_industry_info("600519")
    print("已缓存 600519 的三类数据")

    stats_before = provider.get_cache_stats()
    print(f"缓存大小: {stats_before['cache_size']}")

    # 清除特定股票的缓存
    print("\n【清除 600519 的缓存】")
    provider.clear_cache("600519")

    stats_after = provider.get_cache_stats()
    print(f"缓存大小: {stats_after['cache_size']}")

    # 清除所有缓存
    print("\n【清除所有缓存】")
    provider.get_stock_info("000858")
    provider.get_financial_metrics("000858")
    provider.clear_cache()

    stats_final = provider.get_cache_stats()
    print(f"最终缓存大小: {stats_final['cache_size']}")


def demo_multi_type_caching():
    """演示 5: 多类型数据缓存"""
    print("\n" + "=" * 80)
    print("演示 5: 多类型数据缓存")
    print("=" * 80)

    provider = MultiSourceDataProvider()

    print("\n【缓存不同类型的数据】")

    # 股票信息
    print("\n1. 股票信息")
    start = time.time()
    info = provider.get_stock_info("600519")
    print(f"   首次: {time.time()-start:.3f}s")

    start = time.time()
    info = provider.get_stock_info("600519")
    print(f"   再次: {time.time()-start:.3f}s")

    # 财务指标
    print("\n2. 财务指标")
    start = time.time()
    metrics = provider.get_financial_metrics("600519")
    print(f"   首次: {time.time()-start:.3f}s")

    start = time.time()
    metrics = provider.get_financial_metrics("600519")
    print(f"   再次: {time.time()-start:.3f}s")

    # 行业信息
    print("\n3. 行业信息")
    start = time.time()
    industry = provider.get_industry_info("600519")
    print(f"   首次: {time.time()-start:.3f}s")

    start = time.time()
    industry = provider.get_industry_info("600519")
    print(f"   再次: {time.time()-start:.3f}s")

    # 历史价格（需要时间更长）
    print("\n4. 历史价格")
    start = time.time()
    prices = provider.get_historical_price("600519", days=100)
    print(f"   首次: {time.time()-start:.3f}s")

    start = time.time()
    prices = provider.get_historical_price("600519", days=100)
    print(f"   再次: {time.time()-start:.3f}s")

    # 显示统计
    print("\n【最终统计】")
    provider.print_cache_stats()


def demo_cache_size_and_eviction():
    """演示 6: 缓存大小限制和 LRU 驱逐"""
    print("\n" + "=" * 80)
    print("演示 6: 缓存大小限制和 LRU 驱逐")
    print("=" * 80)

    # 初始化一个小缓存（用于演示）
    cache = init_cache(max_size=5, default_ttl=3600)

    print("\n【演示 LRU 驱逐】")
    print("缓存大小: 5 个条目")

    # 添加 6 个条目，应该驱逐 1 个
    for i in range(6):
        cache.set(f"key_{i}", f"value_{i}")
        print(f"添加 key_{i}")

    stats = cache.get_stats()
    print(f"\n缓存状态: {stats['cache_size']}/{stats['max_size']}")
    print(f"驱逐次数: {stats['evictions']}")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 实时数据缓存机制演示")
    print("=" * 80)

    try:
        demo_basic_caching()
        demo_cache_configuration()
        demo_cache_statistics()
        demo_cache_invalidation()
        demo_multi_type_caching()
        demo_cache_size_and_eviction()

        print("\n" + "=" * 80)
        print("演示完成！")
        print("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"演示出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
