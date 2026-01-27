"""
高级重试机制 - 支持断路器、限流、条件判断
"""
import logging
import time
import threading
from typing import Callable, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """断路器状态"""
    CLOSED = "closed"  # 正常工作
    OPEN = "open"  # 熔断（不再尝试）
    HALF_OPEN = "half_open"  # 半开（允许有限尝试）


class CircuitBreaker:
    """
    断路器 - 防止级联故障

    工作流程:
    1. CLOSED: 正常请求通过，计数失败次数
    2. OPEN: 达到失败阈值，快速失败不尝试
    3. HALF_OPEN: 等待后尝试恢复，成功则关闭，失败继续打开
    """

    def __init__(
        self,
        failure_threshold: int = 5,  # 失败阈值
        recovery_timeout: float = 60.0,  # 恢复等待时间（秒）
        expected_exception: Optional[List[type]] = None,
    ):
        """
        初始化断路器
        Args:
            failure_threshold: 打开断路器的失败次数
            recovery_timeout: 从 OPEN 到 HALF_OPEN 的等待时间
            expected_exception: 应该计数的异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception or [Exception]

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_open_time: Optional[datetime] = None
        self.lock = threading.RLock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过断路器调用函数
        Args:
            func: 要调用的函数
            args: 位置参数
            kwargs: 关键字参数
        Returns:
            函数返回值
        Raises:
            CircuitBreakerOpen: 断路器打开时
        """
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return self._call_closed(func, *args, **kwargs)
            elif self.state == CircuitBreakerState.OPEN:
                return self._call_open(func, *args, **kwargs)
            else:  # HALF_OPEN
                return self._call_half_open(func, *args, **kwargs)

    def _call_closed(self, func: Callable, *args, **kwargs) -> Any:
        """CLOSED 状态下的调用"""
        try:
            result = func(*args, **kwargs)
            # 重置失败计数
            self.failure_count = 0
            self.success_count += 1
            return result
        except Exception as e:
            if self._should_count_failure(e):
                self.failure_count += 1
                self.last_failure_time = datetime.now()

                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    self.last_open_time = datetime.now()
                    logger.error(
                        f"断路器打开：失败次数达到 {self.failure_count}"
                    )
            raise

    def _call_open(self, func: Callable, *args, **kwargs) -> Any:
        """OPEN 状态下的调用"""
        # 检查是否应该尝试恢复
        if self.last_open_time:
            elapsed = (datetime.now() - self.last_open_time).total_seconds()
            if elapsed > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.failure_count = 0
                self.success_count = 0
                logger.info("断路器转换到 HALF_OPEN 状态，尝试恢复")
                return self._call_half_open(func, *args, **kwargs)

        # 仍然处于 OPEN 状态，快速失败
        raise CircuitBreakerOpen(
            f"断路器已打开，故障恢复中... "
            f"(将在 {self.recovery_timeout}s 后重试)"
        )

    def _call_half_open(self, func: Callable, *args, **kwargs) -> Any:
        """HALF_OPEN 状态下的调用"""
        try:
            result = func(*args, **kwargs)
            self.success_count += 1

            # 恢复成功，关闭断路器
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            logger.info("断路器已关闭，服务恢复正常")

            return result
        except Exception as e:
            if self._should_count_failure(e):
                self.failure_count += 1

                # 在 HALF_OPEN 状态再次失败，重新打开
                if self.failure_count >= 1:
                    self.state = CircuitBreakerState.OPEN
                    self.last_open_time = datetime.now()
                    logger.error("HALF_OPEN 恢复失败，重新打开断路器")
            raise

    def _should_count_failure(self, exception: Exception) -> bool:
        """判断是否应该计数失败"""
        for exc_type in self.expected_exception:
            if isinstance(exception, exc_type):
                return True
        return False

    def get_state(self) -> dict:
        """获取断路器状态"""
        with self.lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat()
                if self.last_failure_time else None,
                "last_open_time": self.last_open_time.isoformat()
                if self.last_open_time else None,
            }

    def reset(self) -> None:
        """重置断路器"""
        with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.last_open_time = None
            logger.info("断路器已重置")


class CircuitBreakerOpen(Exception):
    """断路器打开异常"""
    pass


class RateLimiter:
    """
    速率限制器 - 控制请求频率
    """

    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0):
        """
        初始化速率限制器
        Args:
            max_requests: 时间窗口内允许的最大请求数
            window_seconds: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        """
        判断是否允许请求
        Returns:
            True 允许，False 拒绝
        """
        with self.lock:
            now = time.time()
            # 清除过期请求
            self.requests = [
                req_time for req_time in self.requests
                if now - req_time < self.window_seconds
            ]

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def wait_if_needed(self) -> float:
        """
        如果需要，等待直到允许请求
        Returns:
            等待的时间（秒）
        """
        wait_time = 0.0
        while not self.allow_request():
            with self.lock:
                if self.requests:
                    wait_time = self.window_seconds - (time.time() - self.requests[0])
                    if wait_time > 0:
                        time.sleep(min(wait_time, 0.1))
        return wait_time

    def get_stats(self) -> dict:
        """获取统计信息"""
        with self.lock:
            return {
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds,
                "current_requests": len(self.requests),
                "utilization": f"{len(self.requests) / self.max_requests * 100:.1f}%",
            }


class ConditionalRetry:
    """
    条件重试 - 根据函数返回值判断是否重试
    """

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        should_retry_func: Optional[Callable[[Any], bool]] = None,
    ):
        """
        初始化条件重试
        Args:
            max_retries: 最大重试次数
            delay: 重试延迟（秒）
            should_retry_func: 判断是否重试的函数
        """
        self.max_retries = max_retries
        self.delay = delay
        self.should_retry_func = should_retry_func

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        条件重试调用函数
        Args:
            func: 要调用的函数
            args: 位置参数
            kwargs: 关键字参数
        Returns:
            函数返回值
        """
        for attempt in range(1, self.max_retries + 1):
            result = func(*args, **kwargs)

            # 判断是否需要重试
            should_retry = False
            if self.should_retry_func:
                should_retry = self.should_retry_func(result)

            if not should_retry:
                if attempt > 1:
                    logger.info(f"第 {attempt} 次尝试成功")
                return result

            if attempt < self.max_retries:
                logger.warning(
                    f"第 {attempt} 次尝试返回不满足条件，"
                    f"将在 {self.delay}s 后重试"
                )
                time.sleep(self.delay)

        logger.error(f"条件重试失败，已达到最大尝试次数 {self.max_retries}")
        return result
