"""
主程序入口 - 支持增强日志和性能监控
"""
import sys
import os
import atexit

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import setup_logging, get_monitor, SystemMonitor
from src.app import main


def cleanup():
    """程序退出时的清理工作"""
    monitor = get_monitor()

    # 打印性能报告（如果有数据）
    if monitor.metrics:
        print("\n--- 性能统计 ---")
        monitor.print_report()

        # 保存性能报告
        try:
            monitor.save_report("logs/performance_report.json")
        except Exception:
            pass


if __name__ == "__main__":
    # 初始化增强日志
    setup_logging(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        log_dir="logs",
        include_location=True,
    )

    # 注册退出清理
    atexit.register(cleanup)

    # 可选：打印系统信息
    if os.environ.get("SHOW_SYSTEM_INFO"):
        SystemMonitor.print_system_info()

    # 运行主程序
    main()
