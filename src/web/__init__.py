"""web 包初始化"""
from src.web.app import (
    create_web_app,
    run_web_server,
    FLASK_AVAILABLE,
)

__all__ = [
    "create_web_app",
    "run_web_server",
    "FLASK_AVAILABLE",
]
