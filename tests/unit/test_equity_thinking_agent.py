"""
单元测试 - 股权思维 Agent (Agent 1)
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, InvestmentSignal
)
from src.agents.equity_thinking_agent import EquityThinkingAgent


class TestEquityThinkingAgent:
    """股权思维 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = EquityThinkingAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "股权思维Agent"
        assert self.agent.description == "企业所有权分析与长期利润增长评估"

    def test_analyze_with_high_roe(self):
        """测试 ROE > 15% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,  # 32% > 15%
            profit_growth=0.18,
            free_cash_flow=150e8
        )

        result = self.agent.analyze(self.context)

        # 盈利能力评分应该是 7（ROE > 15% 但 < 20%）
        assert result.overall_score > 0

    def test_analyze_with_medium_roe(self):
        """测试 ROE 在 10%-15% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.12,
            profit_growth=0.08,
            free_cash_flow=100e8
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_analyze_with_low_roe(self):
        """测试 ROE <= 10% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.08,
            profit_growth=0.03,
            free_cash_flow=50e8
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        # 不设置 financial_metrics
        result = self.agent.analyze(self.context)

        # 应该返回原始上下文，不改变评分
        assert result.stock_code == "600519"
        assert result.overall_score == 0.0

    def test_analyze_with_high_profit_growth(self):
        """测试利润增长 > 15% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            profit_growth=0.20,  # 20% > 15%
            free_cash_flow=150e8
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score > 0

    def test_analyze_with_positive_cash_flow(self):
        """测试正的自由现金流情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            profit_growth=0.15,
            free_cash_flow=100e8  # 正值
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score > 0

    def test_analyze_with_negative_cash_flow(self):
        """测试负的自由现金流情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            profit_growth=0.15,
            free_cash_flow=-50e8  # 负值
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            profit_growth=0.15,
            free_cash_flow=150e8
        )

        result = self.agent.execute(self.context)

        # execute 方法应该调用 analyze 并记录执行时间
        assert self.agent.execution_time is not None
        assert self.agent.execution_time >= 0
        assert self.agent.last_execution is not None
        assert result.stock_code == "600519"

    def test_multiple_analyses_accumulate_score(self):
        """测试多次分析会累积评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            profit_growth=0.18,
            free_cash_flow=150e8
        )

        initial_score = self.context.overall_score
        result = self.agent.analyze(self.context)

        # 分析后评分应该增加
        assert result.overall_score > initial_score

    def test_agent_string_representation(self):
        """测试 Agent 的字符串表示"""
        str_repr = str(self.agent)
        assert "股权思维Agent" in str_repr

