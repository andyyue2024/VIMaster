"""
定时报告功能单元测试
"""
import sys
from pathlib import Path
import tempfile
import os
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.schedulers.task_scheduler import (
    TaskScheduler,
    ScheduledTask,
    ScheduleFrequency,
)
from src.notifications.email_sender import (
    EmailConfig,
    EmailMessage,
    EmailSender,
)
from src.services.scheduled_report_service import (
    ScheduledReportService,
    ReportJobConfig,
)


class TestScheduledTask:
    """定时任务测试"""

    def test_task_creation(self):
        """测试任务创建"""
        task = ScheduledTask(
            task_id="test_1",
            name="测试任务",
            frequency=ScheduleFrequency.DAILY,
            time_of_day="09:00",
        )

        assert task.task_id == "test_1"
        assert task.frequency == ScheduleFrequency.DAILY
        assert task.enabled is True

    def test_task_to_dict(self):
        """测试转换为字典"""
        task = ScheduledTask(
            task_id="test_1",
            name="测试任务",
            frequency=ScheduleFrequency.WEEKLY,
            day_of_week="friday",
        )

        data = task.to_dict()

        assert data["task_id"] == "test_1"
        assert data["frequency"] == "weekly"
        assert data["day_of_week"] == "friday"

    def test_task_from_dict(self):
        """测试从字典创建"""
        data = {
            "task_id": "test_2",
            "name": "测试任务2",
            "frequency": "monthly",
            "day_of_month": 15,
        }

        task = ScheduledTask.from_dict(data)

        assert task.task_id == "test_2"
        assert task.frequency == ScheduleFrequency.MONTHLY
        assert task.day_of_month == 15


class TestTaskScheduler:
    """任务调度器测试"""

    def test_scheduler_creation(self):
        """测试调度器创建"""
        scheduler = TaskScheduler()

        assert len(scheduler.tasks) == 0
        assert scheduler._running is False

    def test_register_handler(self):
        """测试注册处理器"""
        scheduler = TaskScheduler()

        def my_handler(task):
            pass

        scheduler.register_handler("custom", my_handler)

        assert "custom" in scheduler.task_handlers

    def test_add_task(self):
        """测试添加任务"""
        scheduler = TaskScheduler()

        task = ScheduledTask(
            task_id="test_1",
            name="测试任务",
            frequency=ScheduleFrequency.DAILY,
        )

        scheduler.add_task(task)

        assert "test_1" in scheduler.tasks

    def test_remove_task(self):
        """测试移除任务"""
        scheduler = TaskScheduler()

        task = ScheduledTask(
            task_id="test_1",
            name="测试任务",
            frequency=ScheduleFrequency.DAILY,
        )

        scheduler.add_task(task)
        result = scheduler.remove_task("test_1")

        assert result is True
        assert "test_1" not in scheduler.tasks

    def test_save_and_load_tasks(self):
        """测试保存和加载任务"""
        scheduler = TaskScheduler()

        task = ScheduledTask(
            task_id="test_1",
            name="测试任务",
            frequency=ScheduleFrequency.DAILY,
        )

        scheduler.add_task(task)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "tasks.json")
            scheduler.save_tasks(path)

            new_scheduler = TaskScheduler()
            new_scheduler.load_tasks(path)

            assert "test_1" in new_scheduler.tasks


class TestEmailConfig:
    """邮件配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = EmailConfig()

        assert config.smtp_server == "smtp.qq.com"
        assert config.smtp_port == 465
        assert config.use_ssl is True

    def test_custom_config(self):
        """测试自定义配置"""
        config = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            use_ssl=False,
            use_tls=True,
        )

        assert config.smtp_server == "smtp.gmail.com"
        assert config.use_tls is True

    def test_config_save_and_load(self):
        """测试保存和加载"""
        config = EmailConfig(
            smtp_server="smtp.test.com",
            sender_email="test@test.com",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "email.json")
            config.save(path)

            loaded = EmailConfig.load(path)

            assert loaded.smtp_server == "smtp.test.com"
            assert loaded.sender_email == "test@test.com"


class TestEmailMessage:
    """邮件消息测试"""

    def test_message_creation(self):
        """测试消息创建"""
        message = EmailMessage(
            to=["test@example.com"],
            subject="测试邮件",
            body="这是测试内容",
        )

        assert len(message.to) == 1
        assert message.subject == "测试邮件"

    def test_message_with_attachments(self):
        """测试带附件的消息"""
        message = EmailMessage(
            to=["test@example.com"],
            subject="测试邮件",
            body="内容",
            attachments=["file1.pdf", "file2.xlsx"],
        )

        assert len(message.attachments) == 2


class TestReportJobConfig:
    """报告任务配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = ReportJobConfig(
            job_id="job_1",
            name="测试任务",
            stock_codes=["600519"],
        )

        assert config.frequency == "daily"
        assert "pdf" in config.report_formats
        assert "excel" in config.report_formats

    def test_custom_config(self):
        """测试自定义配置"""
        config = ReportJobConfig(
            job_id="job_1",
            name="周报",
            stock_codes=["600519", "000858"],
            frequency="weekly",
            day_of_week="friday",
            send_email=True,
            email_recipients=["test@example.com"],
        )

        assert config.frequency == "weekly"
        assert config.day_of_week == "friday"
        assert len(config.email_recipients) == 1


class TestScheduledReportService:
    """定时报告服务测试"""

    def test_service_creation(self):
        """测试服务创建"""
        service = ScheduledReportService()

        assert service.scheduler is not None
        assert service.email_sender is not None
        assert service.report_manager is not None

    def test_add_job(self):
        """测试添加任务"""
        service = ScheduledReportService()

        job = ReportJobConfig(
            job_id="test_job",
            name="测试任务",
            stock_codes=["600519"],
        )

        service.add_stock_report_job(job)

        jobs = service.list_jobs()
        assert len(jobs) == 1
        assert jobs[0]["job_id"] == "test_job"

    def test_service_lifecycle(self):
        """测试服务生命周期"""
        service = ScheduledReportService()

        service.start()
        assert service.scheduler._running is True

        service.stop()
        # 等待停止
        time.sleep(0.5)
