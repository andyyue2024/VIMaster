"""
单元测试 - 安全边际 Agent (Agent 5)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, ValuationAnalysis
)
from src.agents.safety_margin_agent import SafetyMarginAgent


class TestSafetyMarginAgent:
    """安全边际 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = SafetyMarginAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "安全边际Agent"
        assert self.agent.description == "价格与价值差异分析"

    def test_large_safety_margin_20_percent(self):
        """测试安全边际 >= 20% 的情况（优秀）"""
        fair_price = 1000.0
        current_price = 800.0  # (1000 - 800) / 1000 = 20%

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=15.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 安全边际 >= 20% 时
        assert result.safety_margin_ok == True
        assert abs(result.valuation.margin_of_safety - 20.0) < 1.0

    def test_medium_safety_margin_10_percent(self):
        """测试安全边际 10%-20% 的情况（良好）"""
        fair_price = 1000.0
        current_price = 900.0  # (1000 - 900) / 1000 = 10%

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=15.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 安全边际 10%-20% 时
        assert result.safety_margin_ok == True
        assert abs(result.valuation.margin_of_safety - 10.0) < 1.0

    def test_small_safety_margin_5_percent(self):
        """测试安全边际 0-10% 的情况（一般）"""
        fair_price = 1000.0
        current_price = 950.0  # (1000 - 950) / 1000 = 5%

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=15.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 安全边际 0%-10% 时
        assert result.safety_margin_ok == True
        assert abs(result.valuation.margin_of_safety - 5.0) < 1.0

    def test_no_safety_margin_negative(self):
        """测试无安全边际（高估）的情况"""
        fair_price = 800.0
        current_price = 1000.0  # (800 - 1000) / 800 = -25%

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 无安全边际（安全边际为负）
        assert result.safety_margin_ok == False
        assert result.valuation.margin_of_safety < 0

    def test_zero_safety_margin(self):
        """测试零安全边际（价格 = 合理价格）"""
        fair_price = 1000.0
        current_price = 1000.0  # 相等

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=20.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 零安全边际
        assert result.safety_margin_ok == True
        assert abs(result.valuation.margin_of_safety - 0.0) < 0.1

    def test_analyze_without_valuation(self):
        """测试没有估值对象的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0
        )
        # 不设置 valuation

        result = self.agent.analyze(self.context)

        # 应该返回原始上下文，不进行分析
        assert result.stock_code == "600519"

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            intrinsic_value=1000.0
        )
        # 不设置 financial_metrics

        result = self.agent.analyze(self.context)

        # 应该返回原始上下文
        assert result.stock_code == "600519"

    def test_analyze_with_none_fair_price(self):
        """测试 fair_price 为 None 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=None,  # None
            intrinsic_value=None
        )

        result = self.agent.analyze(self.context)

        # 应该返回原始上下文
        assert result.stock_code == "600519"

    def test_analyze_with_none_current_price(self):
        """测试 current_price 为 None 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=None,  # None
            pe_ratio=20.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            intrinsic_value=1000.0
        )

        result = self.agent.analyze(self.context)

        # 应该返回原始上下文
        assert result.stock_code == "600519"

    def test_valuation_score_high_margin(self):
        """测试高安全边际时的评分"""
        fair_price = 1000.0
        current_price = 700.0  # (1000 - 700) / 1000 = 30%

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=10.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 高安全边际应该得高分
        assert result.safety_margin_ok == True

    def test_valuation_score_low_margin(self):
        """测试低安全边际时的评分"""
        fair_price = 1000.0
        current_price = 950.0  # (1000 - 950) / 1000 = 5%

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=18.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 低安全边际应该得低分
        assert result.safety_margin_ok == True

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,
            pe_ratio=15.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            intrinsic_value=1000.0
        )

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

    def test_600519_example(self):
        """测试 600519 实际案例（严重高估）"""
        fair_price = 766.64
        current_price = 1800.5

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=fair_price,
            intrinsic_value=fair_price
        )

        result = self.agent.analyze(self.context)

        # 安全边际应该是负的
        assert result.safety_margin_ok == False
        assert result.valuation.margin_of_safety < 0

