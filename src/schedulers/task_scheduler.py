"""
定时任务调度器 - 支持定时生成和发送报告
"""
import logging
import threading
import time
import schedule
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """调度频率"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"
    CUSTOM = "custom"  # 自定义 cron 表达式


@dataclass
class ScheduledTask:
    """定时任务配置"""
    task_id: str
    name: str
    frequency: ScheduleFrequency
    time_of_day: str = "09:00"  # HH:MM 格式
    day_of_week: str = "monday"  # 周几（用于 weekly）
    day_of_month: int = 1  # 几号（用于 monthly）
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None

    # 任务参数
    task_type: str = "report"  # report, analysis, etc.
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "frequency": self.frequency.value,
            "time_of_day": self.time_of_day,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "task_type": self.task_type,
            "params": self.params,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ScheduledTask":
        return ScheduledTask(
            task_id=data.get("task_id", ""),
            name=data.get("name", ""),
            frequency=ScheduleFrequency(data.get("frequency", "daily")),
            time_of_day=data.get("time_of_day", "09:00"),
            day_of_week=data.get("day_of_week", "monday"),
            day_of_month=data.get("day_of_month", 1),
            enabled=data.get("enabled", True),
            last_run=data.get("last_run"),
            next_run=data.get("next_run"),
            task_type=data.get("task_type", "report"),
            params=data.get("params", {}),
        )


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def register_handler(self, task_type: str, handler: Callable) -> None:
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
        logger.info(f"已注册任务处理器: {task_type}")

    def add_task(self, task: ScheduledTask) -> None:
        """添加定时任务"""
        with self._lock:
            self.tasks[task.task_id] = task
            self._schedule_task(task)
            logger.info(f"已添加定时任务: {task.name} ({task.task_id})")

    def remove_task(self, task_id: str) -> bool:
        """移除定时任务"""
        with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                schedule.clear(task_id)
                logger.info(f"已移除定时任务: {task_id}")
                return True
            return False

    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].enabled = True
                self._schedule_task(self.tasks[task_id])
                return True
            return False

    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].enabled = False
                schedule.clear(task_id)
                return True
            return False

    def _schedule_task(self, task: ScheduledTask) -> None:
        """调度任务"""
        if not task.enabled:
            return

        schedule.clear(task.task_id)

        job = None
        if task.frequency == ScheduleFrequency.DAILY:
            job = schedule.every().day.at(task.time_of_day)
        elif task.frequency == ScheduleFrequency.WEEKLY:
            day_map = {
                "monday": schedule.every().monday,
                "tuesday": schedule.every().tuesday,
                "wednesday": schedule.every().wednesday,
                "thursday": schedule.every().thursday,
                "friday": schedule.every().friday,
                "saturday": schedule.every().saturday,
                "sunday": schedule.every().sunday,
            }
            if task.day_of_week.lower() in day_map:
                job = day_map[task.day_of_week.lower()].at(task.time_of_day)
        elif task.frequency == ScheduleFrequency.HOURLY:
            job = schedule.every().hour
        elif task.frequency == ScheduleFrequency.ONCE:
            # 一次性任务，立即执行
            self._execute_task(task)
            return

        if job:
            job.do(self._execute_task, task).tag(task.task_id)

    def _execute_task(self, task: ScheduledTask) -> None:
        """执行任务"""
        try:
            logger.info(f"开始执行任务: {task.name}")

            handler = self.task_handlers.get(task.task_type)
            if handler:
                handler(task)
                task.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"任务执行完成: {task.name}")
            else:
                logger.warning(f"未找到任务处理器: {task.task_type}")
        except Exception as e:
            logger.error(f"任务执行失败 {task.name}: {str(e)}")

    def start(self) -> None:
        """启动调度器"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("任务调度器已启动")

    def stop(self) -> None:
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("任务调度器已停止")

    def _run_loop(self) -> None:
        """调度循环"""
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def run_task_now(self, task_id: str) -> bool:
        """立即执行任务"""
        if task_id in self.tasks:
            self._execute_task(self.tasks[task_id])
            return True
        return False

    def get_tasks(self) -> List[ScheduledTask]:
        """获取所有任务"""
        return list(self.tasks.values())

    def save_tasks(self, path: str) -> None:
        """保存任务配置"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        data = {"tasks": [t.to_dict() for t in self.tasks.values()]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"任务配置已保存: {path}")

    def load_tasks(self, path: str) -> None:
        """加载任务配置"""
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for task_data in data.get("tasks", []):
            task = ScheduledTask.from_dict(task_data)
            self.add_task(task)
        logger.info(f"已加载 {len(self.tasks)} 个任务")
