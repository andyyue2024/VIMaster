# 定时报告功能指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持 **定时生成和发送报告** 功能，包括：

- ⏰ **定时任务调度** - 支持每日、每周、每月、每小时调度
- 📧 **邮件发送** - 支持 SMTP 邮件发送，附件自动添加
- 📊 **自动报告生成** - PDF/Excel 格式自动生成
- 🔄 **服务化运行** - 后台持续运行，按计划执行

---

## 🚀 快速开始

### 安装依赖

```bash
pip install schedule
```

### 配置邮箱

编辑 `config/email_config.json`：

```json
{
  "smtp_server": "smtp.qq.com",
  "smtp_port": 465,
  "use_ssl": true,
  "sender_email": "your_email@qq.com",
  "sender_password": "your_authorization_code",
  "sender_name": "VIMaster 报告系统"
}
```

### 创建定时任务

```python
from src.services import ScheduledReportService, ReportJobConfig

# 创建服务
service = ScheduledReportService()

# 添加每日报告任务
job = ReportJobConfig(
    job_id="daily_report",
    name="每日股票分析报告",
    stock_codes=["600519", "000858"],
    frequency="daily",
    time_of_day="09:00",
    send_email=True,
    email_recipients=["investor@example.com"],
)

service.add_stock_report_job(job)

# 启动服务
service.start()
```

---

## ⏰ 调度频率

| 频率 | 参数 | 说明 |
|------|------|------|
| **每日** | `frequency="daily"` | 每天在指定时间执行 |
| **每周** | `frequency="weekly"` | 每周指定日期执行 |
| **每月** | `frequency="monthly"` | 每月指定日期执行 |
| **每小时** | `frequency="hourly"` | 每小时执行一次 |
| **一次性** | `frequency="once"` | 立即执行一次 |

### 示例

```python
# 每日 9:00 执行
ReportJobConfig(
    job_id="daily",
    name="每日报告",
    stock_codes=["600519"],
    frequency="daily",
    time_of_day="09:00",
)

# 每周五 18:00 执行
ReportJobConfig(
    job_id="weekly",
    name="周报",
    stock_codes=["600519"],
    frequency="weekly",
    time_of_day="18:00",
    day_of_week="friday",
)

# 每月 1 号执行
ReportJobConfig(
    job_id="monthly",
    name="月报",
    stock_codes=["600519"],
    frequency="monthly",
    day_of_month=1,
)
```

---

## 📧 邮件配置

### EmailConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `smtp_server` | str | "smtp.qq.com" | SMTP 服务器 |
| `smtp_port` | int | 465 | SMTP 端口 |
| `use_ssl` | bool | True | 使用 SSL |
| `use_tls` | bool | False | 使用 TLS |
| `sender_email` | str | "" | 发送者邮箱 |
| `sender_password` | str | "" | 授权码 |
| `sender_name` | str | "VIMaster" | 发送者名称 |

### 常见邮箱配置

```python
# QQ 邮箱
EmailConfig(
    smtp_server="smtp.qq.com",
    smtp_port=465,
    use_ssl=True,
    sender_email="xxx@qq.com",
    sender_password="授权码",
)

# 网易邮箱
EmailConfig(
    smtp_server="smtp.163.com",
    smtp_port=465,
    use_ssl=True,
)

# Gmail
EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    use_ssl=False,
    use_tls=True,
)
```

---

## 📊 报告任务配置

### ReportJobConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `job_id` | str | - | 任务唯一标识 |
| `name` | str | - | 任务名称 |
| `stock_codes` | List[str] | - | 股票代码列表 |
| `frequency` | str | "daily" | 调度频率 |
| `time_of_day` | str | "09:00" | 执行时间 |
| `day_of_week` | str | "monday" | 周几执行 |
| `report_formats` | List[str] | ["pdf","excel"] | 报告格式 |
| `output_dir` | str | "reports/scheduled" | 输出目录 |
| `send_email` | bool | True | 是否发送邮件 |
| `email_recipients` | List[str] | [] | 收件人列表 |
| `email_subject` | str | "VIMaster..." | 邮件主题 |

---

## 🔧 API 参考

### ScheduledReportService

```python
class ScheduledReportService:
    def __init__(self, email_config=None, report_template=None)
    
    # 添加任务
    def add_stock_report_job(self, config: ReportJobConfig) -> None
    def add_portfolio_report_job(self, config: ReportJobConfig) -> None
    
    # 服务控制
    def start(self) -> None
    def stop(self) -> None
    
    # 任务管理
    def run_job_now(self, job_id: str) -> bool
    def list_jobs(self) -> List[Dict]
```

### TaskScheduler

```python
class TaskScheduler:
    def register_handler(self, task_type: str, handler: Callable) -> None
    def add_task(self, task: ScheduledTask) -> None
    def remove_task(self, task_id: str) -> bool
    def enable_task(self, task_id: str) -> bool
    def disable_task(self, task_id: str) -> bool
    def run_task_now(self, task_id: str) -> bool
    def start(self) -> None
    def stop(self) -> None
```

### EmailSender

```python
class EmailSender:
    def send(self, message: EmailMessage) -> bool
    def send_report(self, to, subject, report_files, body=None) -> bool
```

---

## 🎯 使用场景

### 场景 1: 每日晨报

```python
service = ScheduledReportService()

job = ReportJobConfig(
    job_id="morning_report",
    name="每日晨报",
    stock_codes=["600519", "000858", "000651"],
    frequency="daily",
    time_of_day="08:30",
    send_email=True,
    email_recipients=["team@company.com"],
    email_subject="每日投资分析晨报",
)

service.add_portfolio_report_job(job)
service.start()
```

### 场景 2: 周五收盘总结

```python
job = ReportJobConfig(
    job_id="weekly_summary",
    name="周度总结",
    stock_codes=["600519", "000858", "000651", "600036"],
    frequency="weekly",
    time_of_day="17:00",
    day_of_week="friday",
    send_email=True,
    email_recipients=["manager@company.com"],
)

service.add_portfolio_report_job(job)
```

### 场景 3: 立即生成报告

```python
service = ScheduledReportService()

job = ReportJobConfig(
    job_id="urgent_report",
    name="紧急报告",
    stock_codes=["600519"],
    frequency="once",
    send_email=True,
    email_recipients=["investor@example.com"],
)

service.add_stock_report_job(job)
service.run_job_now("urgent_report")
```

---

## 📂 文件清单

| 文件 | 说明 |
|------|------|
| `src/schedulers/task_scheduler.py` | 任务调度器 (200+ 行) |
| `src/notifications/email_sender.py` | 邮件发送器 (200+ 行) |
| `src/services/scheduled_report_service.py` | 定时报告服务 (300+ 行) |
| `config/email_config.json` | 邮件配置模板 |
| `demo_scheduled_reports.py` | 演示脚本 |
| `tests/unit/test_scheduled_reports.py` | 单元测试 |

---

## ⚙️ 依赖说明

| 依赖 | 用途 | 安装命令 |
|------|------|---------|
| schedule | 任务调度 | `pip install schedule` |
| reportlab | PDF 生成 | `pip install reportlab` |
| openpyxl | Excel 生成 | `pip install openpyxl` |

---

## 🔒 安全提示

1. **不要将密码提交到版本控制**
   - 使用环境变量或独立的配置文件
   - `config/email_config.json` 已在 `.gitignore` 中

2. **使用授权码而非密码**
   - QQ/网易等邮箱需要开启 SMTP 并获取授权码
   - Gmail 需要开启"应用专用密码"

3. **限制收件人**
   - 只发送给授权的收件人
   - 定期审核收件人列表

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
