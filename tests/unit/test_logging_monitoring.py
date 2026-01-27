"""
增强日志和性能监控单元测试
"""
import sys
from pathlib import Path
import tempfile
import os
import time
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.utils.enhanced_logging import (
    setup_logging,
    get_context_logger,
    log_exception,
    EnhancedFormatter,
    ErrorContextLogger,
)
from src.utils.performance_monitor import (
    PerformanceMonitor,
    PerformanceMetric,
    SystemMonitor,
    get_monitor,
    measure_time,
)


class TestEnhancedLogging:
    """增强日志测试"""

    def test_setup_logging(self):
        """测试日志初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(
                level="DEBUG",
                log_dir=tmpdir,
            )

            assert logger is not None
            assert os.path.exists(os.path.join(tmpdir, "errors.log"))

    def test_enhanced_formatter(self):
        """测试增强格式化器"""
        formatter = EnhancedFormatter(use_colors=False, include_location=True)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="测试消息",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert "测试消息" in formatted
        assert "INFO" in formatted

    def test_context_logger(self):
        """测试上下文日志器"""
        base_logger = logging.getLogger("test_context")
        ctx_logger = ErrorContextLogger(base_logger)

        ctx_logger.set_context(stock_code="600519", user="test")

        # 上下文应该被设置
        assert ctx_logger.context["stock_code"] == "600519"

        ctx_logger.clear_context()
        assert len(ctx_logger.context) == 0

    def test_log_exception_decorator(self):
        """测试异常日志装饰器"""
        @log_exception()
        def failing_function():
            raise ValueError("测试错误")

        try:
            failing_function()
        except ValueError:
            pass  # 预期的异常


class TestPerformanceMonitor:
    """性能监控测试"""

    def setup_method(self):
        get_monitor().clear()

    def test_monitor_singleton(self):
        """测试单例模式"""
        m1 = PerformanceMonitor()
        m2 = PerformanceMonitor()

        assert m1 is m2

    def test_timer(self):
        """测试计时器"""
        monitor = get_monitor()

        monitor.start_timer("test_operation")
        time.sleep(0.1)
        metric = monitor.stop_timer("test_operation")

        assert metric is not None
        assert metric.duration_ms >= 100  # 至少 100ms

    def test_measure_context_manager(self):
        """测试上下文管理器方式"""
        monitor = get_monitor()

        with monitor.measure("context_test"):
            time.sleep(0.05)

        metrics = monitor.get_metrics("context_test")

        assert len(metrics) == 1
        assert metrics[0].success is True

    def test_measure_time_decorator(self):
        """测试装饰器方式"""
        monitor = get_monitor()

        @measure_time("decorated_function")
        def my_function():
            time.sleep(0.05)
            return "result"

        result = my_function()

        assert result == "result"

        metrics = monitor.get_metrics("decorated_function")
        assert len(metrics) == 1

    def test_statistics(self):
        """测试统计信息"""
        monitor = get_monitor()

        for i in range(5):
            monitor.start_timer("stats_test")
            time.sleep(0.01)
            monitor.stop_timer("stats_test")

        stats = monitor.get_statistics("stats_test")

        assert stats["count"] == 5
        assert stats["success_count"] == 5
        assert stats["duration"]["avg_ms"] > 0

    def test_report_generation(self):
        """测试报告生成"""
        monitor = get_monitor()

        monitor.start_timer("report_test")
        monitor.stop_timer("report_test")

        report = monitor.get_report()

        assert "generated_at" in report
        assert "total_operations" in report
        assert "report_test" in report.get("operations", {})

    def test_save_report(self):
        """测试保存报告"""
        monitor = get_monitor()

        monitor.start_timer("save_test")
        monitor.stop_timer("save_test")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "perf_report.json")
            monitor.save_report(path)

            assert os.path.exists(path)


class TestSystemMonitor:
    """系统监控测试"""

    def test_get_system_info(self):
        """测试获取系统信息"""
        info = SystemMonitor.get_system_info()

        assert "timestamp" in info
        assert "psutil_available" in info


class TestPerformanceMetric:
    """性能指标测试"""

    def test_metric_creation(self):
        """测试指标创建"""
        metric = PerformanceMetric(
            name="test",
            start_time=time.time(),
            duration_ms=100.5,
            success=True,
        )

        assert metric.name == "test"
        assert metric.duration_ms == 100.5
        assert metric.success is True

    def test_metric_to_dict(self):
        """测试转换为字典"""
        metric = PerformanceMetric(
            name="test",
            duration_ms=50.0,
            success=True,
        )

        data = metric.to_dict()

        assert data["name"] == "test"
        assert data["duration_ms"] == 50.0
        assert data["success"] is True
