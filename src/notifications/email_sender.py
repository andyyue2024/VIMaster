"""
邮件发送模块 - 支持发送报告邮件
"""
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os
import json

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_server: str = "smtp.qq.com"
    smtp_port: int = 465
    use_ssl: bool = True
    use_tls: bool = False

    # 发送者信息
    sender_email: str = ""
    sender_password: str = ""  # 授权码
    sender_name: str = "VIMaster 报告系统"

    # 默认收件人
    default_recipients: List[str] = None

    # 邮件设置
    default_subject_prefix: str = "[VIMaster]"

    def __post_init__(self):
        if self.default_recipients is None:
            self.default_recipients = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "use_ssl": self.use_ssl,
            "use_tls": self.use_tls,
            "sender_email": self.sender_email,
            "sender_password": "***",  # 不保存密码
            "sender_name": self.sender_name,
            "default_recipients": self.default_recipients,
            "default_subject_prefix": self.default_subject_prefix,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EmailConfig":
        config = EmailConfig()
        for key in ["smtp_server", "smtp_port", "use_ssl", "use_tls",
                    "sender_email", "sender_password", "sender_name",
                    "default_subject_prefix"]:
            if key in data:
                setattr(config, key, data[key])
        if "default_recipients" in data:
            config.default_recipients = data["default_recipients"]
        return config

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> "EmailConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return EmailConfig.from_dict(data)


@dataclass
class EmailMessage:
    """邮件消息"""
    to: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    attachments: List[str] = None  # 附件文件路径列表
    cc: List[str] = None
    bcc: List[str] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []


class EmailSender:
    """邮件发送器"""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()

    def set_config(self, config: EmailConfig) -> None:
        self.config = config

    def load_config(self, path: str) -> None:
        self.config = EmailConfig.load(path)

    def send(self, message: EmailMessage) -> bool:
        """发送邮件"""
        try:
            if not self.config.sender_email or not self.config.sender_password:
                logger.error("邮件配置不完整：缺少发送者邮箱或密码")
                return False

            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg["To"] = ", ".join(message.to)
            msg["Subject"] = f"{self.config.default_subject_prefix} {message.subject}"

            if message.cc:
                msg["Cc"] = ", ".join(message.cc)

            # 添加正文
            if message.body:
                msg.attach(MIMEText(message.body, "plain", "utf-8"))

            if message.html_body:
                msg.attach(MIMEText(message.html_body, "html", "utf-8"))

            # 添加附件
            for attachment_path in message.attachments:
                if os.path.exists(attachment_path):
                    self._add_attachment(msg, attachment_path)

            # 发送邮件
            all_recipients = message.to + message.cc + message.bcc

            if self.config.use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port, context=context) as server:
                    server.login(self.config.sender_email, self.config.sender_password)
                    server.sendmail(self.config.sender_email, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                    if self.config.use_tls:
                        server.starttls()
                    server.login(self.config.sender_email, self.config.sender_password)
                    server.sendmail(self.config.sender_email, all_recipients, msg.as_string())

            logger.info(f"邮件发送成功: {message.subject} -> {message.to}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False

    def _add_attachment(self, msg: MIMEMultipart, file_path: str) -> None:
        """添加附件"""
        try:
            filename = os.path.basename(file_path)

            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={filename}",
            )
            msg.attach(part)
        except Exception as e:
            logger.warning(f"添加附件失败 {file_path}: {str(e)}")

    def send_report(
        self,
        to: List[str],
        subject: str,
        report_files: List[str],
        body: Optional[str] = None
    ) -> bool:
        """发送报告邮件（便捷方法）"""
        if body is None:
            body = f"""
您好，

附件是 VIMaster 自动生成的投资分析报告。

报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
附件数量: {len(report_files)}

本邮件由系统自动发送，请勿回复。

---
VIMaster 价值投资分析系统
"""

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a5f7a;">📊 VIMaster 投资分析报告</h2>
        <p>您好，</p>
        <p>附件是 VIMaster 自动生成的投资分析报告。</p>
        <ul>
            <li><strong>报告生成时间:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}</li>
            <li><strong>附件数量:</strong> {len(report_files)}</li>
        </ul>
        <p style="color: #666; font-size: 12px;">本邮件由系统自动发送，请勿回复。</p>
        <hr style="border: none; border-top: 1px solid #ddd;">
        <p style="color: #999; font-size: 11px;">VIMaster 价值投资分析系统</p>
    </div>
</body>
</html>
"""

        message = EmailMessage(
            to=to,
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=report_files,
        )

        return self.send(message)


# 便捷函数
def create_email_sender(config_path: Optional[str] = None) -> EmailSender:
    """创建邮件发送器"""
    sender = EmailSender()
    if config_path and os.path.exists(config_path):
        sender.load_config(config_path)
    return sender
