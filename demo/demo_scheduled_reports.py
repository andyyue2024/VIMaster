"""
定时报告演示脚本
"""
import sys
from pathlib import Path
import time
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.services import ScheduledReportService, ReportJobConfig
from src.notifications import EmailConfig, EmailSender
from src.schedulers.task_scheduler import TaskScheduler, ScheduledTask, ScheduleFrequency

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_task_scheduler():
    """演示 1: 任务调度器"""
    print("\n" + "=" * 80)
    print("演示 1: 任务调度器基础用法")
    print("=" * 80)

    scheduler = TaskScheduler()

    # 注册处理器
    def my_handler(task):
        print(f"  执行任务: {task.name}")
        print(f"  参数: {task.params}")

    scheduler.register_handler("custom", my_handler)

    # 添加一次性任务
    task = ScheduledTask(
        task_id="demo_task_1",
        name="演示任务",
        frequency=ScheduleFrequency.ONCE,
        task_type="custom",
        params={"message": "Hello World!"},
    )

    scheduler.add_task(task)
    print("✓ 一次性任务已执行")

    # 列出任务
    print(f"\n当前任务数: {len(scheduler.get_tasks())}")


def demo_email_config():
    """演示 2: 邮件配置"""
    print("\n" + "=" * 80)
    print("演示 2: 邮件配置")
    print("=" * 80)

    # 创建配置
    config = EmailConfig(
        smtp_server="smtp.qq.com",
        smtp_port=465,
        use_ssl=True,
        sender_email="your_email@qq.com",
        sender_password="your_authorization_code",
        sender_name="VIMaster 报告系统",
        default_recipients=["recipient@example.com"],
    )

    print(f"SMTP 服务器: {config.smtp_server}:{config.smtp_port}")
    print(f"发送者: {config.sender_name}")
    print(f"SSL: {config.use_ssl}")

    # 保存配置
    config.save("config/demo_email_config.json")
    print("✓ 邮件配置已保存到 config/demo_email_config.json")
    print("\n注意: 请编辑配置文件填入真实的邮箱和授权码后再使用")


def demo_scheduled_report_service():
    """演示 3: 定时报告服务"""
    print("\n" + "=" * 80)
    print("演示 3: 定时报告服务")
    print("=" * 80)

    # 创建服务
    service = ScheduledReportService()

    # 添加每日报告任务
    daily_job = ReportJobConfig(
        job_id="daily_report",
        name="每日股票分析报告",
        stock_codes=["600519", "000858"],
        frequency="daily",
        time_of_day="09:00",
        report_formats=["pdf", "excel"],
        output_dir="reports/daily",
        send_email=False,  # 演示时不发送邮件
    )

    service.add_stock_report_job(daily_job)
    print(f"✓ 已添加每日报告任务: {daily_job.name}")

    # 添加周度组合报告任务
    weekly_job = ReportJobConfig(
        job_id="weekly_portfolio",
        name="周度投资组合报告",
        stock_codes=["600519", "000858", "000651", "600036"],
        frequency="weekly",
        time_of_day="18:00",
        day_of_week="friday",
        report_formats=["pdf"],
        output_dir="reports/weekly",
        send_email=False,
    )

    service.add_portfolio_report_job(weekly_job)
    print(f"✓ 已添加周度组合报告任务: {weekly_job.name}")

    # 列出任务
    print("\n当前任务列表:")
    for job in service.list_jobs():
        print(f"  - {job['name']} ({job['frequency']}) @ {job['time_of_day']}")


def demo_run_job_now():
    """演示 4: 立即执行任务"""
    print("\n" + "=" * 80)
    print("演示 4: 立即执行报告任务")
    print("=" * 80)

    service = ScheduledReportService()

    # 添加任务
    job = ReportJobConfig(
        job_id="immediate_report",
        name="立即生成报告",
        stock_codes=["600519"],
        frequency="once",
        report_formats=["excel"],
        output_dir="reports/immediate",
        send_email=False,
    )

    service.add_stock_report_job(job)

    print("正在生成报告...")
    service.run_job_now("immediate_report")
    print("✓ 报告已生成，请查看 reports/immediate 目录")


def demo_service_lifecycle():
    """演示 5: 服务生命周期"""
    print("\n" + "=" * 80)
    print("演示 5: 定时服务生命周期")
    print("=" * 80)

    service = ScheduledReportService()

    # 添加每小时任务（演示用）
    job = ReportJobConfig(
        job_id="hourly_check",
        name="每小时检查任务",
        stock_codes=["600519"],
        frequency="hourly",
        send_email=False,
    )

    service.add_stock_report_job(job)

    print("启动定时服务...")
    service.start()
    print("✓ 服务已启动（后台运行）")

    print("等待 3 秒...")
    time.sleep(3)

    print("停止服务...")
    service.stop()
    print("✓ 服务已停止")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 定时报告功能演示")
    print("=" * 80)

    try:
        demo_task_scheduler()
        demo_email_config()
        demo_scheduled_report_service()
        demo_run_job_now()
        demo_service_lifecycle()

        print("\n" + "=" * 80)
        print("演示完成！")
        print("=" * 80)
        print("\n使用提示:")
        print("1. 编辑 config/email_config.json 配置邮箱信息")
        print("2. 使用 ScheduledReportService 添加定时任务")
        print("3. 调用 service.start() 启动后台调度")
        print("4. 报告将按计划自动生成并发送")
        print()
    except Exception as e:
        logger.error(f"演示失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
