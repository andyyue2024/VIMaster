# API 重试机制 - 完整使用指南

**版本**: v4.0  
**日期**: 2026年1月27日  
**状态**: ✅ **完成并可用**

---

## 📋 概述

VIMaster 现已实现一个完整的 **API 重试机制**，包括：
- 🔄 多种重试策略（固定、线性、指数、随机）
- 🛡️ 断路器模式防止级联故障
- 🚦 速率限制保护 API
- 📊 条件重试（基于返回值）
- 📈 完整的重试统计和监控
- 🧵 线程安全的并发处理

---

## 🚀 快速开始

### 基础重试

```python
from src.utils.retry_mechanism import with_retry

@with_retry(max_retries=3, initial_delay=1.0)
def fetch_stock_data(code: str):
    # 可能会失败的 API 调用
    return api.get_price(code)

# 如果失败，自动重试最多 3 次
price = fetch_stock_data("600519")
```

### 指数退避重试

```python
from src.utils.retry_mechanism import retry, RetryConfig, RetryStrategy

config = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
)

@retry(config=config)
def download_data():
    return api.download()
```

### 断路器保护

```python
from src.utils.advanced_retry import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

def call_unstable_api():
    # 如果连续失败 5 次，自动断路
    # 快速失败，避免浪费资源
    return breaker.call(api.request)
```

### 速率限制

```python
from src.utils.advanced_retry import RateLimiter

limiter = RateLimiter(max_requests=10, window_seconds=1.0)

def make_request():
    if not limiter.allow_request():
        limiter.wait_if_needed()  # 自动等待
    return api.request()
```

---

## 🎯 核心功能详解

### 1. 重试配置 (RetryConfig)

```python
from src.utils.retry_mechanism import RetryConfig, RetryStrategy

config = RetryConfig(
    # 重试次数
    max_retries=3,
    
    # 初始延迟（秒）
    initial_delay=1.0,
    
    # 最大延迟（秒）
    max_delay=60.0,
    
    # 退避因子（用于指数和线性）
    backoff_factor=2.0,
    
    # 重试策略
    strategy=RetryStrategy.EXPONENTIAL,
    
    # 添加随机抖动（防止惊群）
    jitter=True,
    
    # 需要重试的异常类型
    retry_on=[ConnectionError, TimeoutError],
    
    # 不需要重试的异常类型
    dont_retry_on=[ValueError],
)
```

### 2. 重试策略对比

| 策略 | 延迟计算 | 用途 |
|------|---------|------|
| **FIXED** | 固定延迟 | 简单稳定场景 |
| **LINEAR** | 线性增长 | 逐步退避 |
| **EXPONENTIAL** | 指数增长 | 标准推荐，处理不稳定 API |
| **RANDOM** | 随机延迟 | 分散并发请求 |

```python
# 延迟计算示例
config = RetryConfig(initial_delay=1.0, backoff_factor=2.0)

# FIXED: 1.0, 1.0, 1.0
# LINEAR: 1.0, 2.0, 3.0
# EXPONENTIAL: 1.0, 2.0, 4.0, 8.0
# RANDOM: 1.0~60.0, 1.0~60.0, ...
```

### 3. 装饰器使用

```python
# 方式 1: 使用配置名称（预注册的配置）
@retry(config_name="default")
def api_call():
    return requests.get("http://api.example.com")

# 方式 2: 传入配置对象
config = RetryConfig(max_retries=5)
@retry(config=config)
def api_call():
    return requests.get("http://api.example.com")

# 方式 3: 简化版（推荐）
@with_retry(max_retries=3, initial_delay=1.0)
def api_call():
    return requests.get("http://api.example.com")
```

### 4. 断路器模式

```python
from src.utils.advanced_retry import CircuitBreaker, CircuitBreakerState

breaker = CircuitBreaker(
    failure_threshold=5,  # 5 次失败后打开
    recovery_timeout=60.0,  # 60 秒后尝试恢复
)

def call_api():
    return breaker.call(api.request)

# 断路器状态
# CLOSED: 正常工作
# OPEN: 熔断，快速失败
# HALF_OPEN: 恢复中，允许有限尝试
```

工作流程：
```
CLOSED ─失败达到阈值─> OPEN ─等待超时─> HALF_OPEN ─成功─> CLOSED
                                        └─失败─> OPEN
```

### 5. 速率限制

```python
from src.utils.advanced_retry import RateLimiter

# 限制：每秒最多 10 个请求
limiter = RateLimiter(max_requests=10, window_seconds=1.0)

# 检查是否允许
if limiter.allow_request():
    api.request()

# 或者自动等待
limiter.wait_if_needed()
api.request()

# 获取统计信息
stats = limiter.get_stats()
# {'max_requests': 10, 'window_seconds': 1.0, 'current_requests': 7, 'utilization': '70.0%'}
```

### 6. 条件重试

```python
from src.utils.advanced_retry import ConditionalRetry

def should_retry(result):
    # 如果结果为 None，继续重试
    return result is None

retrier = ConditionalRetry(
    max_retries=5,
    delay=1.0,
    should_retry_func=should_retry,
)

result = retrier.call(api.get_data)  # 直到获得非 None 的结果
```

---

## 📊 重试统计和监控

```python
from src.utils.retry_mechanism import get_retry_manager

manager = get_retry_manager()

# 注册自定义配置
from src.utils.retry_mechanism import RetryConfig
config = RetryConfig(max_retries=3)
manager.register_config("api_v1", config)

# 获取统计信息
stats = manager.get_stats("api_v1")
# {
#     'total_attempts': 100,
#     'successful_attempts': 95,
#     'failed_attempts': 5,
#     'success_rate': '95.00%',
#     'total_retries': 8,
#     'avg_retry_delay': '1.234s',
#     'total_delay': '9.872s',
#     'error_counts': {'ConnectionError': 3, 'TimeoutError': 2},
# }

# 打印统计信息
manager.print_stats()  # 打印所有配置的统计
manager.print_stats("api_v1")  # 打印指定配置的统计
```

---

## 🎯 使用场景

### 场景 1: 调用不稳定的数据 API

```python
@with_retry(max_retries=3, initial_delay=0.5)
def get_stock_price(code: str):
    response = requests.get(f"https://api.example.com/price/{code}")
    return response.json()["price"]

# 如果 API 偶尔超时，会自动重试
price = get_stock_price("600519")
```

### 场景 2: 下载大文件

```python
@with_retry(
    max_retries=5,
    initial_delay=2.0,
    strategy=RetryStrategy.EXPONENTIAL
)
def download_large_file(url: str):
    response = requests.get(url, timeout=30)
    return response.content
```

### 场景 3: 保护 API 不被淹没

```python
from src.utils.advanced_retry import CircuitBreaker, RateLimiter

class APIClient:
    def __init__(self):
        self.breaker = CircuitBreaker(failure_threshold=5)
        self.limiter = RateLimiter(max_requests=100, window_seconds=1.0)
    
    def request(self, endpoint: str):
        # 速率限制
        self.limiter.wait_if_needed()
        
        # 断路器保护
        def fetch():
            return requests.get(f"https://api.example.com/{endpoint}")
        
        return self.breaker.call(fetch)
```

### 场景 4: 批量 API 调用

```python
manager = get_retry_manager()

# 注册高级重试配置用于批量操作
batch_config = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,  # 防止同时重试
)
manager.register_config("batch", batch_config)

@retry(config_name="batch")
def fetch_batch_data(codes: List[str]):
    return api.batch_get(codes)
```

---

## ⚙️ 预定义配置

```python
# 默认配置
DEFAULT_API_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
)

# 激进重试（适用于关键操作）
AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    initial_delay=0.5,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,
)

# 保守重试（适用于稳定的 API）
CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    initial_delay=2.0,
    max_delay=10.0,
    strategy=RetryStrategy.FIXED,
)
```

使用：
```python
@retry(config_name="default")  # 使用默认配置
def api_call():
    return api.request()

@retry(config_name="aggressive")  # 使用激进配置
def critical_api_call():
    return api.critical_request()

@retry(config_name="conservative")  # 使用保守配置
def stable_api_call():
    return api.stable_request()
```

---

## 🧵 线程安全

所有重试机制都是线程安全的：

```python
import threading

limiter = RateLimiter(max_requests=10)
breaker = CircuitBreaker(failure_threshold=5)

def worker():
    for _ in range(100):
        # 线程安全的操作
        if limiter.allow_request():
            breaker.call(api.request)

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

---

## 🐛 常见问题

### Q1: 为什么我的重试没有生效？

**A**: 检查异常类型是否在 `retry_on` 列表中。默认只重试 `Exception` 及其子类。

```python
config = RetryConfig(
    retry_on=[ConnectionError, TimeoutError, ValueError],
)
```

### Q2: 如何避免重试造成的"惊群"?

**A**: 使用 `jitter=True` 添加随机抖动，或使用 `RANDOM` 策略。

```python
config = RetryConfig(
    strategy=RetryStrategy.EXPONENTIAL,
    jitter=True,  # 自动添加随机抖动
)
```

### Q3: 断路器什么时候会自动恢复？

**A**: 在 `recovery_timeout` 秒后，断路器会进入 `HALF_OPEN` 状态并尝试一个请求。成功则关闭，失败则重新打开。

```python
breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0,  # 60 秒后尝试恢复
)
```

### Q4: 怎样监控重试的效果？

**A**: 使用 `RetryManager` 获取统计信息。

```python
manager = get_retry_manager()
stats = manager.get_stats("api_name")
print(f"成功率: {stats['success_rate']}")
print(f"平均重试延迟: {stats['avg_retry_delay']}")
```

---

## 📈 性能考虑

- **重试延迟**: 总延迟 = (初始延迟 + 退避延迟) × 重试次数
- **超时设置**: 确保单个请求超时 < 重试总时间
- **并发问题**: 使用 `jitter` 防止并发重试时的资源竞争

---

## 📚 文件清单

| 文件 | 说明 | 行数 |
|------|------|------|
| src/utils/retry_mechanism.py | 基础重试机制 | 450+ |
| src/utils/advanced_retry.py | 断路器、限流等 | 350+ |
| tests/unit/test_retry_mechanism.py | 单元测试 | 400+ |
| demo_retry_mechanism.py | 8 个演示场景 | 350+ |

---

**项目状态**: 🟢 **完成并可用**  
**版本**: v4.0  
**质量**: ⭐⭐⭐⭐⭐
