"""
定时报告服务 - 整合定时任务、报告生成、邮件发送
"""
import logging
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from src.schedulers.task_scheduler import TaskScheduler, ScheduledTask, ScheduleFrequency
from src.notifications.email_sender import EmailSender, EmailConfig
from src.reports import ReportManager, StockReportData, PortfolioReportData, ReportTemplate

logger = logging.getLogger(__name__)


@dataclass
class ReportJobConfig:
    """报告任务配置"""
    job_id: str
    name: str
    stock_codes: List[str]

    # 调度设置
    frequency: str = "daily"  # daily, weekly, monthly
    time_of_day: str = "09:00"
    day_of_week: str = "monday"

    # 报告设置
    report_formats: List[str] = None  # ["pdf", "excel"]
    output_dir: str = "reports/scheduled"

    # 邮件设置
    send_email: bool = True
    email_recipients: List[str] = None
    email_subject: str = "VIMaster 定时投资分析报告"

    def __post_init__(self):
        if self.report_formats is None:
            self.report_formats = ["pdf", "excel"]
        if self.email_recipients is None:
            self.email_recipients = []


class ScheduledReportService:
    """定时报告服务"""

    def __init__(
        self,
        email_config: Optional[EmailConfig] = None,
        report_template: Optional[ReportTemplate] = None
    ):
        self.scheduler = TaskScheduler()
        self.email_sender = EmailSender(email_config)
        self.report_manager = ReportManager(report_template)
        self.jobs: Dict[str, ReportJobConfig] = {}

        # 注册报告任务处理器
        self.scheduler.register_handler("report", self._handle_report_task)
        self.scheduler.register_handler("portfolio_report", self._handle_portfolio_report_task)

    def add_stock_report_job(self, config: ReportJobConfig) -> None:
        """添加单股报告定时任务"""
        task = ScheduledTask(
            task_id=config.job_id,
            name=config.name,
            frequency=ScheduleFrequency(config.frequency),
            time_of_day=config.time_of_day,
            day_of_week=config.day_of_week,
            task_type="report",
            params={
                "stock_codes": config.stock_codes,
                "report_formats": config.report_formats,
                "output_dir": config.output_dir,
                "send_email": config.send_email,
                "email_recipients": config.email_recipients,
                "email_subject": config.email_subject,
            }
        )

        self.jobs[config.job_id] = config
        self.scheduler.add_task(task)
        logger.info(f"已添加定时报告任务: {config.name}")

    def add_portfolio_report_job(self, config: ReportJobConfig) -> None:
        """添加组合报告定时任务"""
        task = ScheduledTask(
            task_id=config.job_id,
            name=config.name,
            frequency=ScheduleFrequency(config.frequency),
            time_of_day=config.time_of_day,
            day_of_week=config.day_of_week,
            task_type="portfolio_report",
            params={
                "stock_codes": config.stock_codes,
                "report_formats": config.report_formats,
                "output_dir": config.output_dir,
                "send_email": config.send_email,
                "email_recipients": config.email_recipients,
                "email_subject": config.email_subject,
            }
        )

        self.jobs[config.job_id] = config
        self.scheduler.add_task(task)
        logger.info(f"已添加组合报告定时任务: {config.name}")

    def _handle_report_task(self, task: ScheduledTask) -> None:
        """处理单股报告任务"""
        try:
            params = task.params
            stock_codes = params.get("stock_codes", [])
            report_formats = params.get("report_formats", ["pdf"])
            output_dir = params.get("output_dir", "reports/scheduled")
            send_email = params.get("send_email", False)
            email_recipients = params.get("email_recipients", [])
            email_subject = params.get("email_subject", "VIMaster 定时报告")

            # 生成报告
            generated_files = []
            for stock_code in stock_codes:
                files = self._generate_stock_report(stock_code, output_dir, report_formats)
                generated_files.extend(files)

            # 发送邮件
            if send_email and email_recipients and generated_files:
                self._send_report_email(email_recipients, email_subject, generated_files)

            logger.info(f"报告任务完成: {task.name}, 生成 {len(generated_files)} 个文件")
        except Exception as e:
            logger.error(f"报告任务失败: {str(e)}")

    def _handle_portfolio_report_task(self, task: ScheduledTask) -> None:
        """处理组合报告任务"""
        try:
            params = task.params
            stock_codes = params.get("stock_codes", [])
            report_formats = params.get("report_formats", ["pdf"])
            output_dir = params.get("output_dir", "reports/scheduled")
            send_email = params.get("send_email", False)
            email_recipients = params.get("email_recipients", [])
            email_subject = params.get("email_subject", "VIMaster 组合报告")

            # 生成组合报告
            generated_files = self._generate_portfolio_report(stock_codes, output_dir, report_formats)

            # 发送邮件
            if send_email and email_recipients and generated_files:
                self._send_report_email(email_recipients, email_subject, generated_files)

            logger.info(f"组合报告任务完成: {task.name}, 生成 {len(generated_files)} 个文件")
        except Exception as e:
            logger.error(f"组合报告任务失败: {str(e)}")

    def _generate_stock_report(
        self,
        stock_code: str,
        output_dir: str,
        formats: List[str]
    ) -> List[str]:
        """生成单股报告"""
        from src.schedulers.workflow_scheduler import AnalysisManager

        os.makedirs(output_dir, exist_ok=True)
        generated_files = []

        try:
            # 获取分析数据
            manager = AnalysisManager()
            context = manager.analyze_single_stock(stock_code)

            if not context:
                logger.warning(f"无法获取股票 {stock_code} 的分析数据")
                return generated_files

            # 构建报告数据
            data = self._context_to_report_data(context)

            # 生成报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            if "pdf" in formats:
                pdf_path = os.path.join(output_dir, f"{stock_code}_{timestamp}.pdf")
                if self.report_manager.generate_pdf(data, pdf_path):
                    generated_files.append(pdf_path)

            if "excel" in formats:
                excel_path = os.path.join(output_dir, f"{stock_code}_{timestamp}.xlsx")
                if self.report_manager.generate_excel(data, excel_path):
                    generated_files.append(excel_path)
        except Exception as e:
            logger.error(f"生成股票 {stock_code} 报告失败: {str(e)}")

        return generated_files

    def _generate_portfolio_report(
        self,
        stock_codes: List[str],
        output_dir: str,
        formats: List[str]
    ) -> List[str]:
        """生成组合报告"""
        from src.schedulers.workflow_scheduler import AnalysisManager

        os.makedirs(output_dir, exist_ok=True)
        generated_files = []

        try:
            # 获取分析数据
            manager = AnalysisManager()
            report = manager.analyze_portfolio(stock_codes)

            if not report:
                logger.warning("无法获取组合分析数据")
                return generated_files

            # 构建报告数据
            portfolio_data = PortfolioReportData(
                report_id=report.report_id,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                total_stocks=report.total_stocks_analyzed,
                strong_buy_count=report.strong_buy_count,
                buy_count=report.buy_count,
                hold_count=report.hold_count,
                sell_count=report.sell_count,
                strong_sell_count=report.strong_sell_count,
            )

            for stock in report.stocks:
                portfolio_data.stocks.append(self._context_to_report_data(stock))

            # 生成报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            if "pdf" in formats:
                pdf_path = os.path.join(output_dir, f"portfolio_{timestamp}.pdf")
                if self.report_manager.generate_portfolio_pdf(portfolio_data, pdf_path):
                    generated_files.append(pdf_path)

            if "excel" in formats:
                excel_path = os.path.join(output_dir, f"portfolio_{timestamp}.xlsx")
                if self.report_manager.generate_portfolio_excel(portfolio_data, excel_path):
                    generated_files.append(excel_path)
        except Exception as e:
            logger.error(f"生成组合报告失败: {str(e)}")

        return generated_files

    def _context_to_report_data(self, context) -> StockReportData:
        """将分析上下文转换为报告数据"""
        data = StockReportData(stock_code=context.stock_code)

        if context.financial_metrics:
            fm = context.financial_metrics
            data.current_price = fm.current_price
            data.pe_ratio = fm.pe_ratio
            data.pb_ratio = fm.pb_ratio
            data.roe = fm.roe
            data.gross_margin = fm.gross_margin
            data.debt_ratio = fm.debt_ratio
            data.free_cash_flow = fm.free_cash_flow

        if context.valuation:
            val = context.valuation
            data.intrinsic_value = val.intrinsic_value
            data.fair_price = val.fair_price
            data.margin_of_safety = val.margin_of_safety
            data.valuation_score = val.valuation_score

        if context.competitive_moat:
            moat = context.competitive_moat
            data.moat_score = moat.overall_score

        if context.risk_assessment:
            risk = context.risk_assessment
            data.risk_level = risk.overall_risk_level.value if risk.overall_risk_level else ""
            data.leverage_risk = risk.leverage_risk

        data.final_signal = context.final_signal.value if context.final_signal else ""
        data.overall_score = context.overall_score

        if context.investment_decision:
            dec = context.investment_decision
            data.decision = dec.decision.value if dec.decision else ""
            data.position_size = dec.position_size
            data.stop_loss = dec.stop_loss_price
            data.take_profit = dec.take_profit_price

        return data

    def _send_report_email(
        self,
        recipients: List[str],
        subject: str,
        report_files: List[str]
    ) -> bool:
        """发送报告邮件"""
        return self.email_sender.send_report(
            to=recipients,
            subject=subject,
            report_files=report_files
        )

    def start(self) -> None:
        """启动服务"""
        self.scheduler.start()
        logger.info("定时报告服务已启动")

    def stop(self) -> None:
        """停止服务"""
        self.scheduler.stop()
        logger.info("定时报告服务已停止")

    def run_job_now(self, job_id: str) -> bool:
        """立即执行任务"""
        return self.scheduler.run_task_now(job_id)

    def list_jobs(self) -> List[Dict[str, Any]]:
        """列出所有任务"""
        return [
            {
                "job_id": t.task_id,
                "name": t.name,
                "frequency": t.frequency.value,
                "time_of_day": t.time_of_day,
                "enabled": t.enabled,
                "last_run": t.last_run,
            }
            for t in self.scheduler.get_tasks()
        ]
