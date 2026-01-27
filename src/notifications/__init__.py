"""notifications 包初始化"""
from src.notifications.email_sender import (
    EmailConfig,
    EmailMessage,
    EmailSender,
    create_email_sender,
)

__all__ = [
    "EmailConfig",
    "EmailMessage",
    "EmailSender",
    "create_email_sender",
]
