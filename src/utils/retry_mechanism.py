"""
API 重试机制 - 支持指数退避、条件重试、重试统计
"""
import logging
import time
import functools
from typing import Callable, Any, Optional, Type, Tuple, List
from enum import Enum
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略"""
    FIXED = "fixed"  # 固定延迟
    LINEAR = "linear"  # 线性退避
    EXPONENTIAL = "exponential"  # 指数退避
    RANDOM = "random"  # 随机延迟


class RetryConfig:
    """重试配置"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        retry_on: Optional[List[Type[Exception]]] = None,
        dont_retry_on: Optional[List[Type[Exception]]] = None,
    ):
        """
        初始化重试配置
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            max_delay: 最大延迟（秒）
            backoff_factor: 退避因子
            strategy: 重试策略
            jitter: 是否添加随机抖动
            retry_on: 需要重试的异常类型
            dont_retry_on: 不需要重试的异常类型
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.strategy = strategy
        self.jitter = jitter
        self.retry_on = retry_on or [Exception]
        self.dont_retry_on = dont_retry_on or []

    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        if self.strategy == RetryStrategy.FIXED:
            delay = self.initial_delay
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.initial_delay * attempt
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        elif self.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(self.initial_delay, self.max_delay)
        else:
            delay = self.initial_delay

        # 限制最大延迟
        delay = min(delay, self.max_delay)

        # 添加随机抖动
        if self.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        exception_type = type(exception)

        # 检查不重试列表
        for exc_type in self.dont_retry_on:
            if isinstance(exception, exc_type):
                return False

        # 检查重试列表
        for exc_type in self.retry_on:
            if isinstance(exception, exc_type):
                return True

        return False


class RetryStatistics:
    """重试统计信息"""

    def __init__(self):
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.total_retries = 0
        self.total_delay = 0.0
        self.last_error: Optional[Exception] = None
        self.error_counts: dict = {}
        self.created_at = datetime.now()

    def record_success(self, attempt: int, delay: float = 0):
        """记录成功"""
        self.total_attempts += 1
        self.successful_attempts += 1
        if attempt > 1:
            self.total_retries += attempt - 1
        self.total_delay += delay

    def record_failure(self, exception: Exception, attempt: int, delay: float = 0):
        """记录失败"""
        self.total_attempts += 1
        self.failed_attempts += 1
        if attempt > 1:
            self.total_retries += attempt - 1
        self.total_delay += delay
        self.last_error = exception

        exc_name = type(exception).__name__
        self.error_counts[exc_name] = self.error_counts.get(exc_name, 0) + 1

    def get_stats(self) -> dict:
        """获取统计信息"""
        success_rate = (
            self.successful_attempts / self.total_attempts * 100
            if self.total_attempts > 0 else 0
        )

        avg_delay = (
            self.total_delay / self.total_retries
            if self.total_retries > 0 else 0
        )

        uptime = datetime.now() - self.created_at

        return {
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "success_rate": f"{success_rate:.2f}%",
            "total_retries": self.total_retries,
            "avg_retry_delay": f"{avg_delay:.3f}s",
            "total_delay": f"{self.total_delay:.3f}s",
            "last_error": str(self.last_error) if self.last_error else None,
            "error_counts": self.error_counts,
            "uptime": str(uptime),
        }


class RetryManager:
    """重试管理器"""

    def __init__(self):
        self.stats: dict = {}
        self.configs: dict = {}

    def register_config(self, name: str, config: RetryConfig) -> None:
        """注册重试配置"""
        self.configs[name] = config
        self.stats[name] = RetryStatistics()
        logger.info(f"重试配置 '{name}' 已注册")

    def get_config(self, name: str) -> Optional[RetryConfig]:
        """获取重试配置"""
        return self.configs.get(name)

    def get_stats(self, name: str) -> Optional[dict]:
        """获取重试统计"""
        if name in self.stats:
            return self.stats[name].get_stats()
        return None

    def print_stats(self, name: Optional[str] = None) -> None:
        """打印统计信息"""
        print("\n" + "=" * 70)
        print("API 重试统计信息")
        print("=" * 70)

        if name:
            stats = self.get_stats(name)
            if stats:
                print(f"\n【{name}】")
                for key, value in stats.items():
                    print(f"  {key:20} : {value}")
        else:
            for config_name in self.configs:
                stats = self.get_stats(config_name)
                if stats:
                    print(f"\n【{config_name}】")
                    for key, value in stats.items():
                        print(f"  {key:20} : {value}")

        print("=" * 70 + "\n")


# 全局重试管理器实例
_retry_manager = RetryManager()


def get_retry_manager() -> RetryManager:
    """获取全局重试管理器"""
    return _retry_manager


def register_retry_config(name: str, config: RetryConfig) -> None:
    """注册重试配置"""
    _retry_manager.register_config(name, config)


def retry(
    config: Optional[RetryConfig] = None,
    config_name: Optional[str] = None,
) -> Callable:
    """
    重试装饰器
    Args:
        config: 重试配置对象
        config_name: 配置名称（从全局管理器获取）
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 获取配置
            if config_name:
                actual_config = _retry_manager.get_config(config_name)
                if not actual_config:
                    logger.warning(f"未找到重试配置 '{config_name}'，使用默认配置")
                    actual_config = config or RetryConfig()
            else:
                actual_config = config or RetryConfig()

            # 获取统计对象
            stats_key = config_name or func.__name__
            if stats_key not in _retry_manager.stats:
                _retry_manager.stats[stats_key] = RetryStatistics()
            stats = _retry_manager.stats[stats_key]

            last_exception = None
            total_delay = 0.0

            for attempt in range(1, actual_config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    stats.record_success(attempt, total_delay)

                    if attempt > 1:
                        logger.info(
                            f"函数 '{func.__name__}' 在第 {attempt} 次尝试成功"
                        )

                    return result
                except Exception as e:
                    last_exception = e

                    # 判断是否应该重试
                    if not actual_config.should_retry(e):
                        logger.debug(
                            f"异常 {type(e).__name__} 不在重试列表中，不再重试"
                        )
                        stats.record_failure(e, attempt, total_delay)
                        raise

                    # 如果是最后一次尝试
                    if attempt == actual_config.max_retries:
                        logger.error(
                            f"函数 '{func.__name__}' 在第 {attempt} 次尝试后失败"
                        )
                        stats.record_failure(e, attempt, total_delay)
                        raise

                    # 计算延迟
                    delay = actual_config.calculate_delay(attempt)
                    total_delay += delay

                    logger.warning(
                        f"函数 '{func.__name__}' 第 {attempt} 次尝试失败: "
                        f"{type(e).__name__}: {str(e)}，"
                        f"将在 {delay:.2f}s 后重试"
                    )

                    # 等待
                    time.sleep(delay)

            # 不应该到达这里
            if last_exception:
                stats.record_failure(last_exception, actual_config.max_retries, total_delay)
                raise last_exception

        return wrapper

    return decorator


def retry_with_config(config: RetryConfig) -> Callable:
    """使用配置对象的重试装饰器"""
    return retry(config=config)


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
) -> Callable:
    """简化的重试装饰器"""
    config = RetryConfig(
        max_retries=max_retries,
        initial_delay=initial_delay,
        strategy=strategy,
    )
    return retry(config=config)


# 预定义的常见配置
DEFAULT_API_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    initial_delay=0.5,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
)

CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    initial_delay=2.0,
    max_delay=10.0,
    strategy=RetryStrategy.FIXED,
)

# 注册预定义配置
register_retry_config("default", DEFAULT_API_CONFIG)
register_retry_config("aggressive", AGGRESSIVE_RETRY_CONFIG)
register_retry_config("conservative", CONSERVATIVE_RETRY_CONFIG)
