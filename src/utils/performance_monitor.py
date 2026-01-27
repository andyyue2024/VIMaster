"""
性能监控模块 - 支持函数耗时、内存使用、性能报告
"""
import logging
import time
import functools
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import json
import os

logger = logging.getLogger(__name__)

# 尝试导入 psutil（可选依赖）
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_ms: float = 0.0
    memory_start_mb: float = 0.0
    memory_end_mb: float = 0.0
    memory_delta_mb: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "memory_delta_mb": round(self.memory_delta_mb, 2),
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
        }


class PerformanceMonitor:
    """性能监控器"""

    _instance: Optional["PerformanceMonitor"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.metrics: List[PerformanceMetric] = []
        self.active_timers: Dict[str, PerformanceMetric] = {}
        self.enabled = True
        self._lock = threading.Lock()
        self._initialized = True

    def enable(self) -> None:
        """启用监控"""
        self.enabled = True

    def disable(self) -> None:
        """禁用监控"""
        self.enabled = False

    def clear(self) -> None:
        """清除所有指标"""
        with self._lock:
            self.metrics.clear()
            self.active_timers.clear()

    def start_timer(self, name: str, **metadata) -> None:
        """开始计时"""
        if not self.enabled:
            return

        metric = PerformanceMetric(
            name=name,
            start_time=time.time(),
            memory_start_mb=self._get_memory_usage(),
            metadata=metadata,
        )

        with self._lock:
            self.active_timers[name] = metric

    def stop_timer(self, name: str, success: bool = True, error: Optional[str] = None) -> Optional[PerformanceMetric]:
        """停止计时"""
        if not self.enabled:
            return None

        with self._lock:
            metric = self.active_timers.pop(name, None)

        if metric:
            metric.end_time = time.time()
            metric.duration_ms = (metric.end_time - metric.start_time) * 1000
            metric.memory_end_mb = self._get_memory_usage()
            metric.memory_delta_mb = metric.memory_end_mb - metric.memory_start_mb
            metric.success = success
            metric.error = error

            with self._lock:
                self.metrics.append(metric)

            # 记录慢操作
            if metric.duration_ms > 1000:  # 超过 1 秒
                logger.warning(f"慢操作检测: {name} 耗时 {metric.duration_ms:.2f}ms")

            return metric
        return None

    @contextmanager
    def measure(self, name: str, **metadata):
        """上下文管理器方式测量"""
        self.start_timer(name, **metadata)
        error = None
        success = True
        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            self.stop_timer(name, success=success, error=error)

    def _get_memory_usage(self) -> float:
        """获取当前内存使用 (MB)"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except Exception:
                pass
        return 0.0

    def get_metrics(self, name: Optional[str] = None) -> List[PerformanceMetric]:
        """获取指标"""
        with self._lock:
            if name:
                return [m for m in self.metrics if m.name == name]
            return list(self.metrics)

    def get_statistics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """获取统计信息"""
        metrics = self.get_metrics(name)

        if not metrics:
            return {}

        durations = [m.duration_ms for m in metrics]
        memory_deltas = [m.memory_delta_mb for m in metrics]

        return {
            "count": len(metrics),
            "success_count": sum(1 for m in metrics if m.success),
            "error_count": sum(1 for m in metrics if not m.success),
            "duration": {
                "total_ms": sum(durations),
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
            },
            "memory": {
                "avg_delta_mb": sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
                "max_delta_mb": max(memory_deltas) if memory_deltas else 0,
            },
        }

    def get_report(self) -> Dict[str, Any]:
        """获取完整性能报告"""
        with self._lock:
            metrics_by_name: Dict[str, List[PerformanceMetric]] = {}
            for m in self.metrics:
                if m.name not in metrics_by_name:
                    metrics_by_name[m.name] = []
                metrics_by_name[m.name].append(m)

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "operations": {},
        }

        for name, metrics in metrics_by_name.items():
            durations = [m.duration_ms for m in metrics]
            report["operations"][name] = {
                "count": len(metrics),
                "success_rate": sum(1 for m in metrics if m.success) / len(metrics) * 100,
                "avg_duration_ms": sum(durations) / len(durations),
                "max_duration_ms": max(durations),
                "min_duration_ms": min(durations),
            }

        return report

    def print_report(self) -> None:
        """打印性能报告"""
        report = self.get_report()

        print("\n" + "=" * 80)
        print("性能监控报告")
        print("=" * 80)
        print(f"生成时间: {report['generated_at']}")
        print(f"总操作数: {report['total_operations']}")
        print("\n操作详情:")
        print("-" * 80)

        for name, stats in report.get("operations", {}).items():
            print(f"\n{name}:")
            print(f"  调用次数: {stats['count']}")
            print(f"  成功率:   {stats['success_rate']:.1f}%")
            print(f"  平均耗时: {stats['avg_duration_ms']:.2f}ms")
            print(f"  最大耗时: {stats['max_duration_ms']:.2f}ms")
            print(f"  最小耗时: {stats['min_duration_ms']:.2f}ms")

        print("=" * 80)

    def save_report(self, path: str) -> None:
        """保存性能报告到文件"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        report = self.get_report()
        report["metrics"] = [m.to_dict() for m in self.metrics]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"性能报告已保存: {path}")


# 全局监控器实例
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """获取全局监控器"""
    return _monitor


def measure_time(name: Optional[str] = None, log_result: bool = True):
    """
    装饰器：测量函数执行时间

    Args:
        name: 指标名称（默认使用函数名）
        log_result: 是否记录结果日志
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metric_name = name or f"{func.__module__}.{func.__name__}"
            monitor = get_monitor()

            monitor.start_timer(metric_name, function=func.__name__)

            try:
                result = func(*args, **kwargs)
                metric = monitor.stop_timer(metric_name, success=True)

                if log_result and metric:
                    logger.debug(f"{metric_name} 执行完成: {metric.duration_ms:.2f}ms")

                return result
            except Exception as e:
                monitor.stop_timer(metric_name, success=False, error=str(e))
                raise

        return wrapper
    return decorator


def measure_async_time(name: Optional[str] = None, log_result: bool = True):
    """装饰器：测量异步函数执行时间"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            metric_name = name or f"{func.__module__}.{func.__name__}"
            monitor = get_monitor()

            monitor.start_timer(metric_name, function=func.__name__)

            try:
                result = await func(*args, **kwargs)
                metric = monitor.stop_timer(metric_name, success=True)

                if log_result and metric:
                    logger.debug(f"{metric_name} 执行完成: {metric.duration_ms:.2f}ms")

                return result
            except Exception as e:
                monitor.stop_timer(metric_name, success=False, error=str(e))
                raise

        return wrapper
    return decorator


class SystemMonitor:
    """系统资源监控"""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "psutil_available": PSUTIL_AVAILABLE,
        }

        if PSUTIL_AVAILABLE:
            try:
                info["cpu"] = {
                    "percent": psutil.cpu_percent(interval=0.1),
                    "count": psutil.cpu_count(),
                }

                mem = psutil.virtual_memory()
                info["memory"] = {
                    "total_gb": mem.total / 1024 / 1024 / 1024,
                    "available_gb": mem.available / 1024 / 1024 / 1024,
                    "percent": mem.percent,
                }

                process = psutil.Process()
                info["process"] = {
                    "memory_mb": process.memory_info().rss / 1024 / 1024,
                    "cpu_percent": process.cpu_percent(),
                    "threads": process.num_threads(),
                }
            except Exception as e:
                info["error"] = str(e)

        return info

    @staticmethod
    def print_system_info() -> None:
        """打印系统信息"""
        info = SystemMonitor.get_system_info()

        print("\n" + "=" * 60)
        print("系统资源监控")
        print("=" * 60)

        if not PSUTIL_AVAILABLE:
            print("psutil 不可用，无法获取详细信息")
            print("安装: pip install psutil")
        else:
            print(f"CPU 使用率: {info.get('cpu', {}).get('percent', 'N/A')}%")
            print(f"内存使用率: {info.get('memory', {}).get('percent', 'N/A')}%")
            print(f"进程内存:   {info.get('process', {}).get('memory_mb', 'N/A'):.1f} MB")
            print(f"进程线程:   {info.get('process', {}).get('threads', 'N/A')}")

        print("=" * 60)
