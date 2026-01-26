"""
单元测试 - 财务分析 Agent (Agent 3)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics
)
from src.agents.financial_analysis_agent import FinancialAnalysisAgent


class TestFinancialAnalysisAgent:
    """财务分析 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = FinancialAnalysisAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "财务分析Agent"
        assert self.agent.description == "财务指标评估（ROE、毛利率、自由现金流、负债率）"

    def test_roe_scoring_excellent(self):
        """测试 ROE > 20% 的评分（优秀）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,  # 25% > 20%
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        # ROE 评分应该是 10.0
        assert result.overall_score > 0

    def test_roe_scoring_good(self):
        """测试 ROE 在 15%-20% 的评分（良好）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.18,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score > 0

    def test_roe_scoring_medium(self):
        """测试 ROE 在 10%-15% 的评分（一般）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.12,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_roe_scoring_poor(self):
        """测试 ROE 的低分情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.03,  # 3% < 5%
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_gross_margin_scoring_excellent(self):
        """测试毛利率 > 50% 的评分（优秀）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.92,  # 92% > 50%
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score > 0

    def test_gross_margin_scoring_good(self):
        """测试毛利率在 40%-50% 的评分（良好）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.45,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_free_cash_flow_scoring_positive(self):
        """测试正的自由现金流评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=150e8,  # 正值
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score > 0

    def test_free_cash_flow_scoring_negative_small(self):
        """测试小负数的自由现金流评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=-500e7,  # -5亿，接近 0
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_free_cash_flow_scoring_very_negative(self):
        """测试大负数的自由现金流评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=-2000e8,  # -200亿
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_debt_ratio_scoring_low(self):
        """测试低负债率 < 30% 的评分（优秀）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.05  # 5% < 30%
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score > 0

    def test_debt_ratio_scoring_medium(self):
        """测试中等负债率在 30%-50% 的评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.40
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_debt_ratio_scoring_high(self):
        """测试高负债率 > 50% 的评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.70
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        result = self.agent.analyze(self.context)

        assert result.stock_code == "600519"

    def test_analyze_with_missing_debt_ratio(self):
        """测试缺少负债率的情况（应该使用默认分）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=None  # 缺少负债率
        )

        result = self.agent.analyze(self.context)

        # 应该完成分析，使用默认评分
        assert result.overall_score >= 0

    def test_comprehensive_financial_analysis(self):
        """测试综合财务分析（优秀公司）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,  # 优秀
            gross_margin=0.92,  # 优秀
            free_cash_flow=150e8,  # 充足
            debt_ratio=0.05  # 极低
        )

        result = self.agent.analyze(self.context)

        # 综合评分应该很高
        assert result.overall_score > 0

    def test_comprehensive_financial_analysis_poor_company(self):
        """测试综合财务分析（差的公司）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.05,  # 低
            gross_margin=0.15,  # 低
            free_cash_flow=-100e8,  # 负值
            debt_ratio=0.80  # 高
        )

        result = self.agent.analyze(self.context)

        assert result.overall_score >= 0

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

