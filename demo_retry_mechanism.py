"""
API 重试机制演示脚本
"""
import sys
from pathlib import Path
import time
import random
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.retry_mechanism import (
    RetryConfig,
    RetryStrategy,
    retry,
    with_retry,
    get_retry_manager,
    register_retry_config,
)
from src.utils.advanced_retry import (
    CircuitBreaker,
    RateLimiter,
    ConditionalRetry,
    CircuitBreakerOpen,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_retry():
    """演示 1: 基础重试"""
    print("\n" + "=" * 80)
    print("演示 1: 基础重试机制")
    print("=" * 80)

    attempt_count = [0]

    @with_retry(max_retries=3, initial_delay=0.5)
    def unstable_api():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError(f"连接失败（第 {attempt_count[0]} 次尝试）")
        return "API 调用成功！"

    print("\n调用不稳定的 API...")
    try:
        result = unstable_api()
        print(f"✓ {result}")
        print(f"总共尝试: {attempt_count[0]} 次")
    except Exception as e:
        print(f"✗ 失败: {str(e)}")


def demo_retry_strategies():
    """演示 2: 不同的重试策略"""
    print("\n" + "=" * 80)
    print("演示 2: 不同的重试策略对比")
    print("=" * 80)

    strategies = [
        ("固定延迟", RetryStrategy.FIXED),
        ("线性退避", RetryStrategy.LINEAR),
        ("指数退避", RetryStrategy.EXPONENTIAL),
    ]

    for name, strategy in strategies:
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.5,
            max_delay=5.0,
            strategy=strategy,
            jitter=False
        )

        print(f"\n【{name}】")
        total_delay = 0
        for attempt in range(1, 4):
            delay = config.calculate_delay(attempt)
            total_delay += delay
            print(f"  第 {attempt} 次重试延迟: {delay:.2f}s (累计: {total_delay:.2f}s)")


def demo_exception_handling():
    """演示 3: 异常处理"""
    print("\n" + "=" * 80)
    print("演示 3: 选择性异常重试")
    print("=" * 80)

    config = RetryConfig(
        max_retries=3,
        initial_delay=0.5,
        retry_on=[ConnectionError, TimeoutError],
        dont_retry_on=[ValueError],
    )

    print("\n可重试的异常: ConnectionError, TimeoutError")
    print("不可重试的异常: ValueError")

    # 测试可重试异常
    print("\n测试 ConnectionError（应该重试）:")
    @retry(config=config)
    def api_with_connection_error():
        raise ConnectionError("网络连接失败")

    try:
        api_with_connection_error()
    except ConnectionError as e:
        print(f"✓ 经过 3 次重试后失败: {str(e)}")

    # 测试不可重试异常
    print("\n测试 ValueError（不应该重试）:")
    @retry(config=config)
    def api_with_value_error():
        raise ValueError("参数错误")

    try:
        api_with_value_error()
    except ValueError as e:
        print(f"✓ 立即失败，未重试: {str(e)}")


def demo_circuit_breaker():
    """演示 4: 断路器"""
    print("\n" + "=" * 80)
    print("演示 4: 断路器防止级联故障")
    print("=" * 80)

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)

    def failing_api():
        raise ConnectionError("API 不可用")

    print("\n【第 1 阶段：CLOSED (正常)】")
    for i in range(1, 4):
        try:
            breaker.call(failing_api)
        except ConnectionError as e:
            print(f"  尝试 {i}: 失败 - {str(e)}")

    print(f"\n断路器状态: {breaker.state.value}")

    print("\n【第 2 阶段：OPEN (快速失败)】")
    for i in range(1, 3):
        try:
            breaker.call(failing_api)
        except CircuitBreakerOpen as e:
            print(f"  尝试 {i}: 快速失败 - {str(e)}")

    print(f"\n【第 3 阶段：等待恢复...】")
    print("等待 2 秒...")
    time.sleep(2.1)

    print("\n【第 4 阶段：HALF_OPEN (尝试恢复)】")

    # 现在 API 已恢复
    def working_api():
        return "API 已恢复"

    try:
        result = breaker.call(working_api)
        print(f"  恢复尝试成功: {result}")
        print(f"  断路器状态: {breaker.state.value}")
    except Exception as e:
        print(f"  恢复失败: {str(e)}")


def demo_rate_limiter():
    """演示 5: 速率限制"""
    print("\n" + "=" * 80)
    print("演示 5: 速率限制保护 API")
    print("=" * 80)

    limiter = RateLimiter(max_requests=3, window_seconds=1.0)

    print("\n限制: 每秒最多 3 个请求")
    print("\n【快速请求】")
    for i in range(1, 5):
        allowed = limiter.allow_request()
        status = "✓ 允许" if allowed else "✗ 拒绝"
        print(f"  请求 {i}: {status}")

    print("\n【等待后重试】")
    print("等待 1.2 秒...")
    time.sleep(1.2)

    for i in range(1, 3):
        allowed = limiter.allow_request()
        status = "✓ 允许" if allowed else "✗ 拒绝"
        print(f"  请求 {i}: {status}")


def demo_conditional_retry():
    """演示 6: 条件重试"""
    print("\n" + "=" * 80)
    print("演示 6: 条件重试（基于返回值）")
    print("=" * 80)

    attempt_count = [0]

    def should_retry_func(result):
        # 如果返回值小于 3，继续重试
        return result < 3

    def get_random_value():
        attempt_count[0] += 1
        value = random.randint(1, 5)
        print(f"  尝试 {attempt_count[0]}: 得到值 {value}")
        return value

    retrier = ConditionalRetry(
        max_retries=5,
        delay=0.3,
        should_retry_func=should_retry_func
    )

    print("\n条件: 返回值需要 >= 3 才能停止重试")
    result = retrier.call(get_random_value)
    print(f"\n✓ 最终得到满足条件的值: {result}")


def demo_retry_statistics():
    """演示 7: 重试统计"""
    print("\n" + "=" * 80)
    print("演示 7: 重试统计和监控")
    print("=" * 80)

    manager = get_retry_manager()

    # 执行多个重试
    print("\n【执行 API 调用】")

    attempt_count = [0]

    @retry(config_name="default")
    def test_api():
        attempt_count[0] += 1
        if attempt_count[0] == 1:
            raise ConnectionError("网络错误")
        return "success"

    print("调用 API (第 1 次失败，第 2 次成功)...")
    test_api()

    # 查看统计
    print("\n【统计信息】")
    manager.print_stats("test_api")


def demo_real_world_scenario():
    """演示 8: 真实场景"""
    print("\n" + "=" * 80)
    print("演示 8: 真实场景 - 获取股票数据的重试")
    print("=" * 80)

    class StockDataProvider:
        def __init__(self):
            self.failure_count = 0
            self.breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)
            self.limiter = RateLimiter(max_requests=5, window_seconds=1.0)

        @with_retry(max_retries=3, initial_delay=0.5)
        def get_stock_price(self, code: str):
            # 检查速率限制
            if not self.limiter.allow_request():
                self.limiter.wait_if_needed()

            # 通过断路器调用
            def fetch_data():
                self.failure_count += 1

                # 模拟 50% 的失败率
                if random.random() < 0.5:
                    raise ConnectionError("网络超时")

                return f"股票 {code} 价格: ¥{random.randint(100, 500)}"

            return self.breaker.call(fetch_data)

    provider = StockDataProvider()

    print("\n获取多只股票的数据 (带有重试、断路器和速率限制)...")
    stocks = ["600519", "000858", "000651"]

    for code in stocks:
        try:
            result = provider.get_stock_price(code)
            print(f"✓ {code}: {result}")
        except Exception as e:
            print(f"✗ {code}: {type(e).__name__}")

    print(f"\n总计: {provider.failure_count} 次 API 调用")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - API 重试机制完整演示")
    print("=" * 80)

    try:
        demo_basic_retry()
        demo_retry_strategies()
        demo_exception_handling()
        demo_circuit_breaker()
        demo_rate_limiter()
        demo_conditional_retry()
        demo_retry_statistics()
        demo_real_world_scenario()

        print("\n" + "=" * 80)
        print("演示完成！")
        print("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"演示出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
