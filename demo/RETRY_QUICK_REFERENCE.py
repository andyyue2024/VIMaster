"""
API 重试机制 - 快速参考卡
"""

# ============================================================================
# VIMaster v4.0 - API 重试机制快速参考
# ============================================================================

# 导入
from src.utils import (
    # 基础重试
    RetryConfig,
    RetryStrategy,
    retry,
    with_retry,
    get_retry_manager,
    register_retry_config,
    DEFAULT_API_CONFIG,
    AGGRESSIVE_RETRY_CONFIG,
    CONSERVATIVE_RETRY_CONFIG,
    # 高级功能
    CircuitBreaker,
    RateLimiter,
    ConditionalRetry,
)

# ============================================================================
# 1. 最简单的重试
# ============================================================================

@with_retry(max_retries=3, initial_delay=1.0)
def simple_api_call():
    """最简单的重试方式"""
    return api.get_data()

# ============================================================================
# 2. 自定义重试配置
# ============================================================================

# 固定延迟
@with_retry(max_retries=3, initial_delay=2.0)
def fixed_delay_retry():
    """固定延迟重试"""
    pass

# 指数退避（推荐）
config = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
)

@retry(config=config)
def exponential_backoff():
    """指数退避重试"""
    pass

# 线性退避
@with_retry(
    max_retries=4,
    initial_delay=1.0,
    strategy=RetryStrategy.LINEAR
)
def linear_backoff():
    """线性退避重试"""
    pass

# ============================================================================
# 3. 异常选择性重试
# ============================================================================

config = RetryConfig(
    max_retries=3,
    retry_on=[ConnectionError, TimeoutError],
    dont_retry_on=[ValueError],
)

@retry(config=config)
def selective_retry():
    """
    只重试网络异常，不重试业务异常
    ConnectionError: 重试
    TimeoutError: 重试
    ValueError: 不重试，立即失败
    """
    pass

# ============================================================================
# 4. 使用预定义配置
# ============================================================================

# 默认配置（推荐用于大多数场景）
@retry(config_name="default")
def api_with_default_config():
    pass

# 激进重试（关键操作）
@retry(config_name="aggressive")
def critical_operation():
    pass

# 保守重试（稳定 API）
@retry(config_name="conservative")
def stable_api():
    pass

# ============================================================================
# 5. 断路器 - 防止级联故障
# ============================================================================

breaker = CircuitBreaker(
    failure_threshold=5,  # 5 次失败后打开
    recovery_timeout=60.0  # 60 秒后尝试恢复
)

try:
    result = breaker.call(api.request)
except CircuitBreakerOpen as e:
    print(f"API 不可用: {e}")

# 获取状态
state = breaker.get_state()
# {'state': 'closed', 'failure_count': 0, 'success_count': 5, ...}

# ============================================================================
# 6. 速率限制 - 保护 API
# ============================================================================

limiter = RateLimiter(
    max_requests=10,  # 每秒最多 10 个请求
    window_seconds=1.0
)

# 方式 1: 检查是否允许
if limiter.allow_request():
    api.request()

# 方式 2: 自动等待
limiter.wait_if_needed()
api.request()

# 获取统计
stats = limiter.get_stats()
# {'max_requests': 10, 'window_seconds': 1.0, 'current_requests': 7, ...}

# ============================================================================
# 7. 条件重试 - 基于返回值
# ============================================================================

def should_retry(result):
    """判断是否需要继续重试"""
    return result is None  # 如果返回 None，继续重试

retrier = ConditionalRetry(
    max_retries=5,
    delay=1.0,
    should_retry_func=should_retry,
)

result = retrier.call(get_async_result)

# ============================================================================
# 8. 重试统计和监控
# ============================================================================

manager = get_retry_manager()

# 获取指定配置的统计
stats = manager.get_stats("api_name")
# {
#     'total_attempts': 100,
#     'successful_attempts': 95,
#     'failed_attempts': 5,
#     'success_rate': '95.00%',
#     'total_retries': 8,
#     'error_counts': {'ConnectionError': 3, 'TimeoutError': 2},
# }

# 打印所有统计信息
manager.print_stats()

# 打印特定配置的统计信息
manager.print_stats("api_name")

# ============================================================================
# 9. 真实场景 - 完整示例
# ============================================================================

class StockDataProvider:
    def __init__(self):
        self.breaker = CircuitBreaker(failure_threshold=5)
        self.limiter = RateLimiter(max_requests=100, window_seconds=1.0)

    @with_retry(max_retries=3, initial_delay=0.5)
    def get_price(self, code: str):
        """获取股票价格（带重试）"""
        # 检查速率限制
        self.limiter.wait_if_needed()

        # 通过断路器调用 API
        def fetch():
            return requests.get(f"https://api.example.com/price/{code}")

        return self.breaker.call(fetch)

    def get_prices_batch(self, codes: list):
        """批量获取价格"""
        prices = {}
        for code in codes:
            try:
                prices[code] = self.get_price(code)
            except Exception as e:
                print(f"获取 {code} 失败: {e}")
        return prices

# 使用
provider = StockDataProvider()
prices = provider.get_prices_batch(["600519", "000858", "000651"])

# ============================================================================
# 10. 配置注册和管理
# ============================================================================

# 注册自定义配置
custom_config = RetryConfig(
    max_retries=4,
    initial_delay=0.5,
    strategy=RetryStrategy.EXPONENTIAL,
)
register_retry_config("my_api", custom_config)

# 使用注册的配置
@retry(config_name="my_api")
def use_custom_config():
    pass

# ============================================================================
# 常见问题和答案
# ============================================================================

"""
Q1: 重试中如何处理日志？
A: 装饰器自动记录重试信息，使用 logging 模块查看：
   logger = logging.getLogger("src.utils.retry_mechanism")
   logger.setLevel(logging.DEBUG)

Q2: 如何在线程环境中安全使用重试？
A: 所有重试机制都是线程安全的，直接使用即可。

Q3: 断路器打开时是否完全无法访问？
A: 不会。在 recovery_timeout 后会进入 HALF_OPEN 状态，
   尝试一个请求来判断服务是否恢复。

Q4: 为什么需要 jitter？
A: 防止"惊群"现象。当多个客户端同时重试时，
   jitter 会错开它们的重试时间，减少对服务器的冲击。

Q5: 怎样监控整个系统的重试效果？
A: 使用 RetryManager.print_stats() 或
   manager.get_stats(name) 获取统计信息。

Q6: 可以组合多个机制吗？
A: 可以！建议的组合：
   装饰器重试 + 断路器保护 + 速率限制
   @retry
   def api():
       limiter.wait_if_needed()
       return breaker.call(request)
"""

# ============================================================================
# 重试策略延迟计算参考
# ============================================================================

"""
初始延迟 = 1.0s，最大延迟 = 60.0s，退避因子 = 2.0

固定延迟（FIXED）:
  1.0s, 1.0s, 1.0s, 1.0s, ...

线性退避（LINEAR）:
  1.0s, 2.0s, 3.0s, 4.0s, 5.0s, ...

指数退避（EXPONENTIAL）:
  1.0s, 2.0s, 4.0s, 8.0s, 16.0s, 32.0s, 60.0s(限制)

随机（RANDOM）:
  随机在 1.0s 到 60.0s 之间
"""

# ============================================================================
# 更多信息
# ============================================================================

# 完整文档: API_RETRY_GUIDE.md
# 演示脚本: demo_retry_mechanism.py
# 单元测试: tests/unit/test_retry_mechanism.py
