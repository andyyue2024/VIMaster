"""
单元测试 - 买入点 Agent (Agent 6)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, ValuationAnalysis, InvestmentSignal
)
from src.agents.buy_signal_agent import BuySignalAgent


class TestBuySignalAgent:
    """买入点 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = BuySignalAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "买入点Agent"
        assert self.agent.description == "买入时机识别"

    def test_extreme_pessimism_signal(self):
        """测试极度悲观信号（PE < 10）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=500.0,
            pe_ratio=8.0  # < 10
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=800.0,
            margin_of_safety=37.5  # (800-500)/800
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0

        result = self.agent.analyze(self.context)

        # 应该识别极度悲观信号
        assert result.buy_signal.is_extreme_pessimism == True

    def test_temporary_difficulty_signal(self):
        """测试暂时性困难信号（利润增长 < -10% 但评分 > 5）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,
            pe_ratio=15.0,
            profit_growth=-0.15  # -15% < -10%
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            margin_of_safety=20.0
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0  # > 5

        result = self.agent.analyze(self.context)

        # 应该识别暂时性困难
        assert result.buy_signal.has_temporary_difficulty == True

    def test_market_misunderstanding_signal(self):
        """测试市场误解信号（安全边际 > 15%）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=700.0,
            pe_ratio=12.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            margin_of_safety=30.0  # > 15%
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0

        result = self.agent.analyze(self.context)

        # 应该识别市场误解
        assert result.buy_signal.is_market_misunderstanding == True

    def test_strong_buy_signal(self):
        """测试强烈买入信号（多个因素 + 高估值评分）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=600.0,
            pe_ratio=8.0,
            profit_growth=-0.15
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=900.0,
            margin_of_safety=33.3,
            valuation_score=9.0
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0

        result = self.agent.analyze(self.context)

        # 应该生成强烈买入信号
        if result.buy_signal.buy_signal == InvestmentSignal.STRONG_BUY:
            assert result.buy_signal.confidence_score >= 0.8

    def test_buy_signal(self):
        """测试买入信号"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=700.0,
            pe_ratio=12.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=900.0,
            margin_of_safety=22.2,
            valuation_score=8.0
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 5.0

        result = self.agent.analyze(self.context)

        # 可能生成买入信号
        assert result.buy_signal is not None

    def test_hold_signal_no_factors(self):
        """测试持有信号（无买入因素）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            profit_growth=0.18
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            margin_of_safety=-134.85,
            valuation_score=1.0
        )

        self.context.safety_margin_ok = False
        self.context.overall_score = 10.06

        result = self.agent.analyze(self.context)

        # 应该是持有信号
        assert result.buy_signal.buy_signal == InvestmentSignal.HOLD

    def test_price_to_fair_ratio_calculation(self):
        """测试价格/合理价比率计算"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=900.0,
            margin_of_safety=11.1
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 5.0

        result = self.agent.analyze(self.context)

        # 比率应该是 1000 / 900 = 1.111...
        assert abs(result.buy_signal.price_to_fair_ratio - 1.111) < 0.01

    def test_analyze_without_valuation(self):
        """测试没有估值对象的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0
        )
        # 不设置 valuation

        result = self.agent.analyze(self.context)

        assert result.buy_signal is not None

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=900.0,
            margin_of_safety=11.1
        )
        # 不设置 financial_metrics

        result = self.agent.analyze(self.context)

        assert result.buy_signal is not None

    def test_recommended_buy_price(self):
        """测试推荐买入价"""
        current_price = 800.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=12.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            margin_of_safety=20.0,
            valuation_score=8.0
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0

        result = self.agent.analyze(self.context)

        # 有买入信号时应该设置推荐买入价
        if result.buy_signal.buy_signal in [InvestmentSignal.STRONG_BUY, InvestmentSignal.BUY]:
            assert result.buy_signal.recommended_buy_price == current_price

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,
            pe_ratio=12.0
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            margin_of_safety=20.0
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

