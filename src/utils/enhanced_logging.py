"""
增强日志模块 - 支持详细错误日志、文件输出、格式化
"""
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
import json


class EnhancedFormatter(logging.Formatter):
    """增强日志格式化器"""

    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
        'RESET': '\033[0m',      # 重置
    }

    def __init__(self, use_colors: bool = True, include_location: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
        self.include_location = include_location

        if include_location:
            fmt = '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
        else:
            fmt = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):
        # 添加颜色
        if self.use_colors:
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        # 添加异常详情
        if record.exc_info:
            record.msg = f"{record.msg}\n{self._format_exception(record.exc_info)}"
            record.exc_info = None

        return super().format(record)

    def _format_exception(self, exc_info) -> str:
        """格式化异常信息"""
        if not exc_info:
            return ""

        exc_type, exc_value, exc_tb = exc_info
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)

        return "".join(tb_lines)


class ErrorContextLogger:
    """错误上下文日志器 - 记录更多上下文信息"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """设置上下文信息"""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """清除上下文"""
        self.context.clear()

    def _format_context(self) -> str:
        """格式化上下文"""
        if not self.context:
            return ""
        return f" | Context: {json.dumps(self.context, ensure_ascii=False, default=str)}"

    def debug(self, msg: str, **kwargs) -> None:
        self.logger.debug(f"{msg}{self._format_context()}", **kwargs)

    def info(self, msg: str, **kwargs) -> None:
        self.logger.info(f"{msg}{self._format_context()}", **kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        self.logger.warning(f"{msg}{self._format_context()}", **kwargs)

    def error(self, msg: str, exc_info: bool = True, **kwargs) -> None:
        self.logger.error(f"{msg}{self._format_context()}", exc_info=exc_info, **kwargs)

    def critical(self, msg: str, exc_info: bool = True, **kwargs) -> None:
        self.logger.critical(f"{msg}{self._format_context()}", exc_info=exc_info, **kwargs)

    def exception(self, msg: str, **kwargs) -> None:
        self.logger.exception(f"{msg}{self._format_context()}", **kwargs)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    include_location: bool = True,
) -> logging.Logger:
    """
    配置增强日志系统

    Args:
        level: 日志级别
        log_file: 日志文件名（None 则自动生成）
        log_dir: 日志目录
        max_file_size: 单文件最大大小
        backup_count: 保留的备份文件数
        include_location: 是否包含代码位置
    """
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(EnhancedFormatter(use_colors=True, include_location=include_location))
    root_logger.addHandler(console_handler)

    # 文件处理器
    if log_file or log_dir:
        os.makedirs(log_dir, exist_ok=True)

        if not log_file:
            log_file = f"vimaster_{datetime.now().strftime('%Y%m%d')}.log"

        log_path = os.path.join(log_dir, log_file)

        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(EnhancedFormatter(use_colors=False, include_location=True))
            root_logger.addHandler(file_handler)
        except Exception as e:
            root_logger.warning(f"无法创建日志文件: {e}")

    # 错误日志单独文件
    error_log_path = os.path.join(log_dir, "errors.log")
    try:
        error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(EnhancedFormatter(use_colors=False, include_location=True))
        root_logger.addHandler(error_handler)
    except Exception:
        pass

    return root_logger


def get_context_logger(name: str) -> ErrorContextLogger:
    """获取上下文日志器"""
    return ErrorContextLogger(logging.getLogger(name))


def log_exception(logger: Optional[logging.Logger] = None):
    """装饰器：自动记录函数异常"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _logger.error(
                    f"函数 {func.__name__} 执行异常: {str(e)}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "func_args": str(args)[:200],  # 避免与 LogRecord.args 冲突
                        "func_kwargs": str(kwargs)[:200],
                    }
                )
                raise
        return wrapper
    return decorator
