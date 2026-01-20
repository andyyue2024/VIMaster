"""
集成测试 - 测试工作流调度和端到端分析流程
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, 'E:\\Workplace-Pycharm\\VIMaster')

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, AnalysisReport,
    InvestmentSignal
)
from src.schedulers.workflow_scheduler import (
    WorkflowScheduler, AnalysisManager, ExecutionMode
)
from src.agents.value_investing_agents import EquityThinkingAgent


class TestWorkflowScheduler:
    """测试工作流调度器"""

    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)

        assert scheduler.execution_mode == ExecutionMode.SEQUENTIAL
        assert len(scheduler.agents) == 0

    def test_register_agents(self):
        """测试 Agent 注册"""
        scheduler = WorkflowScheduler()
        scheduler.register_agents()

        assert len(scheduler.agents) == 9
        agent_names = [agent.name for agent in scheduler.agents]

        expected_agents = [
            "股权思维Agent",
            "护城河Agent",
            "财务分析Agent",
            "估值Agent",
            "安全边际Agent",
            "买入点Agent",
            "卖出纪律Agent",
            "风险管理Agent",
            "心理纪律Agent"
        ]

        for expected_name in expected_agents:
            assert expected_name in agent_names

    @patch('src.data.akshare_provider.AkshareDataProvider.get_financial_metrics')
    @patch('src.data.akshare_provider.AkshareDataProvider.get_industry_info')
    def test_analyze_single_stock(self, mock_industry, mock_metrics):
        """测试单个股票分析"""
        # Mock 数据
        mock_metrics.return_value = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0,
            earnings_per_share=40.0,
            debt_ratio=0.25,
            profit_growth=0.15,
            free_cash_flow=1000000000
        )

        mock_industry.return_value = {
            "industry": "食品饮料",
            "market": "沪深京A"
        }

        scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
        scheduler.register_agents()

        result = scheduler.analyze_stock("600519", "贵州茅台")

        assert result is not None
        assert result.stock_code == "600519"
        assert result.overall_score > 0
        assert result.final_signal != InvestmentSignal.HOLD or result.overall_score >= 50

    @patch('src.data.akshare_provider.AkshareDataProvider.get_financial_metrics')
    @patch('src.data.akshare_provider.AkshareDataProvider.get_industry_info')
    def test_analyze_single_stock_no_data(self, mock_industry, mock_metrics):
        """测试无法获取数据的情况"""
        mock_metrics.return_value = None

        scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
        scheduler.register_agents()

        result = scheduler.analyze_stock("000001")

        assert result is None

    @patch('src.schedulers.workflow_scheduler.WorkflowScheduler.analyze_stock')
    def test_analyze_multiple_stocks(self, mock_analyze):
        """测试多股票分析"""
        # Mock 单个股票分析结果
        def create_mock_context(code):
            context = StockAnalysisContext(stock_code=code)
            context.final_signal = InvestmentSignal.BUY
            context.overall_score = 75.0
            return context

        mock_analyze.side_effect = [
            create_mock_context("600519"),
            create_mock_context("000858"),
            None  # 某只股票无法分析
        ]

        scheduler = WorkflowScheduler()
        scheduler.register_agents()

        report = scheduler.analyze_stocks(["600519", "000858", "999999"])

        assert report.total_stocks_analyzed == 2
        assert report.buy_count == 2

    def test_execution_summary(self):
        """测试执行摘要生成"""
        scheduler = WorkflowScheduler()
        scheduler.register_agents()

        summary = scheduler.get_execution_summary()

        assert "工作流执行摘要" in summary
        assert "顺序执行" in summary
        assert "9" in summary or "9个" in summary

    def test_sequential_execution_mode(self):
        """测试顺序执行模式"""
        scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
        scheduler.register_agents()

        context = StockAnalysisContext(stock_code="600519")
        context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0,
            earnings_per_share=40.0,
            debt_ratio=0.25
        )

        # 在不请求 API 的情况下执行分析流程
        result = scheduler._execute_sequential(context)

        assert result.stock_code == "600519"
        # 所有 Agent 都应该执行过
        assert len(scheduler.execution_history) == 9


class TestAnalysisManager:
    """测试分析管理器"""

    def test_manager_initialization(self):
        """测试管理器初始化"""
        manager = AnalysisManager()

        assert manager.scheduler is not None
        assert len(manager.scheduler.agents) == 9

    @patch('src.data.akshare_provider.AkshareDataProvider.get_financial_metrics')
    @patch('src.data.akshare_provider.AkshareDataProvider.get_industry_info')
    def test_analyze_single_stock(self, mock_industry, mock_metrics):
        """测试管理器分析单个股票"""
        mock_metrics.return_value = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0,
            earnings_per_share=40.0,
            debt_ratio=0.25
        )

        mock_industry.return_value = {
            "industry": "食品饮料",
            "market": "沪深京A"
        }

        manager = AnalysisManager()
        result = manager.analyze_single_stock("600519")

        assert result is not None
        assert result.stock_code == "600519"

    @patch('src.schedulers.workflow_scheduler.WorkflowScheduler.analyze_stocks')
    def test_get_investment_recommendations(self, mock_analyze):
        """测试获取投资建议"""
        def create_mock_context(code, signal):
            context = StockAnalysisContext(stock_code=code)
            context.final_signal = signal
            context.overall_score = 75.0
            return context

        report = AnalysisReport(report_id="test_report")
        report.stocks = [
            create_mock_context("600519", InvestmentSignal.STRONG_BUY),
            create_mock_context("000858", InvestmentSignal.BUY),
            create_mock_context("000001", InvestmentSignal.HOLD),
        ]
        report.total_stocks_analyzed = 3

        mock_analyze.return_value = report

        manager = AnalysisManager()
        recommendations = manager.get_investment_recommendations(
            ["600519", "000858", "000001"],
            InvestmentSignal.STRONG_BUY
        )

        assert len(recommendations) == 1
        assert recommendations[0].stock_code == "600519"


class TestWorkflowDataFlow:
    """测试工作流中的数据流转"""

    @patch('src.data.akshare_provider.AkshareDataProvider.get_financial_metrics')
    @patch('src.data.akshare_provider.AkshareDataProvider.get_industry_info')
    def test_data_flow_through_agents(self, mock_industry, mock_metrics):
        """测试数据在 Agent 间的流转"""
        mock_metrics.return_value = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0,
            earnings_per_share=40.0,
            debt_ratio=0.25,
            profit_growth=0.15
        )

        mock_industry.return_value = {
            "industry": "食品饮料",
            "market": "沪深京A"
        }

        scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
        scheduler.register_agents()

        result = scheduler.analyze_stock("600519")

        # 验证数据在流程中被正确传递和补充
        assert result.financial_metrics is not None
        assert result.competitive_moat is not None
        assert result.valuation is not None
        assert result.buy_signal is not None
        assert result.sell_signal is not None
        assert result.risk_assessment is not None
        assert result.investment_decision is not None

    def test_context_updates_through_flow(self):
        """测试上下文在流程中的更新"""
        context = StockAnalysisContext(stock_code="600519")
        context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0
        )

        # 初始评分为 0
        initial_score = context.overall_score

        agent = EquityThinkingAgent()
        result = agent.analyze(context)

        # 执行后评分应该增加
        assert result.overall_score > initial_score


class TestAnalysisReport:
    """测试分析报告生成"""

    def test_report_creation(self):
        """测试报告创建"""
        report = AnalysisReport(report_id="test_report_001")

        assert report.report_id == "test_report_001"
        assert report.total_stocks_analyzed == 0
        assert report.strong_buy_count == 0

    def test_report_signal_counting(self):
        """测试报告中的信号计数"""
        report = AnalysisReport(report_id="test_report")

        # 添加不同信号的股票
        context1 = StockAnalysisContext(stock_code="600519")
        context1.final_signal = InvestmentSignal.STRONG_BUY

        context2 = StockAnalysisContext(stock_code="000858")
        context2.final_signal = InvestmentSignal.BUY

        context3 = StockAnalysisContext(stock_code="000001")
        context3.final_signal = InvestmentSignal.HOLD

        report.stocks = [context1, context2, context3]
        report.total_stocks_analyzed = 3
        report.strong_buy_count = 1
        report.buy_count = 1
        report.hold_count = 1

        assert report.total_stocks_analyzed == 3
        assert report.strong_buy_count == 1
        assert report.buy_count == 1
        assert report.hold_count == 1

    def test_report_summary_generation(self):
        """测试报告摘要生成"""
        report = AnalysisReport(report_id="test_report")
        report.total_stocks_analyzed = 3
        report.strong_buy_count = 1
        report.buy_count = 1
        report.hold_count = 1

        summary = report.generate_summary()

        assert "价值投资分析报告" in summary
        assert "分析股票数: 3" in summary
        assert "强烈买入: 1" in summary


class TestErrorHandling:
    """测试错误处理"""

    @patch('src.data.akshare_provider.AkshareDataProvider.get_financial_metrics')
    def test_graceful_failure_on_bad_data(self, mock_metrics):
        """测试数据异常时的优雅降级"""
        mock_metrics.side_effect = Exception("API Error")

        scheduler = WorkflowScheduler()
        scheduler.register_agents()

        result = scheduler.analyze_stock("600519")

        # 应该返回 None 而不是抛出异常
        assert result is None

    def test_agent_execution_error_handling(self):
        """测试 Agent 执行错误处理"""
        scheduler = WorkflowScheduler()
        scheduler.register_agents()

        # 创建没有财务数据的上下文
        context = StockAnalysisContext(stock_code="600519")

        # 应该能够优雅地处理
        result = scheduler._execute_sequential(context)

        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
