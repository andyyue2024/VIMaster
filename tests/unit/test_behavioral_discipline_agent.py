"""
单元测试 - 心理纪律 Agent (Agent 9)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, BuySignalAnalysis,
    SellSignalAnalysis, RiskAssessment, CompetitiveModality,
    ValuationAnalysis, InvestmentSignal, RiskLevel
)
from src.agents.behavioral_discipline_agent import BehavioralDisciplineAgent


class TestBehavioralDisciplineAgent:
    """心理纪律 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = BehavioralDisciplineAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "心理纪律Agent"
        assert self.agent.description == "行为纪律与投资决策检查清单"

    def test_strong_buy_decision(self):
        """测试强烈买入决策"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=600.0,
            roe=0.25,
            gross_margin=0.60,
            free_cash_flow=100e8,
            debt_ratio=0.20
        )

        self.context.buy_signal = BuySignalAnalysis(
            stock_code="600519",
            buy_signal=InvestmentSignal.STRONG_BUY,
            confidence_score=0.9
        )

        self.context.sell_signal = SellSignalAnalysis(
            stock_code="600519",
            sell_signal=InvestmentSignal.HOLD,
            confidence_score=0.0
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.LOW
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0

        result = self.agent.analyze(self.context)

        # 买入信号强于卖出信号
        assert result.investment_decision.decision == InvestmentSignal.STRONG_BUY

    def test_sell_decision(self):
        """测试卖出决策（卖出信号强于买入信号）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,
            gross_margin=0.92,
            free_cash_flow=150e8,
            debt_ratio=0.05
        )

        self.context.buy_signal = BuySignalAnalysis(
            stock_code="600519",
            buy_signal=InvestmentSignal.HOLD,
            confidence_score=0.0
        )

        self.context.sell_signal = SellSignalAnalysis(
            stock_code="600519",
            sell_signal=InvestmentSignal.SELL,
            confidence_score=0.7
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.MEDIUM
        )

        self.context.safety_margin_ok = False
        self.context.overall_score = 10.06

        result = self.agent.analyze(self.context)

        # 卖出信号强于买入信号
        assert result.investment_decision.decision == InvestmentSignal.SELL

    def test_hold_decision_no_signals(self):
        """测试持有决策（无强信号）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        self.context.buy_signal = BuySignalAnalysis(
            stock_code="600519",
            buy_signal=InvestmentSignal.HOLD,
            confidence_score=0.0
        )

        self.context.sell_signal = SellSignalAnalysis(
            stock_code="600519",
            sell_signal=InvestmentSignal.HOLD,
            confidence_score=0.0
        )

        result = self.agent.analyze(self.context)

        assert result.investment_decision.decision == InvestmentSignal.HOLD

    def test_stop_loss_and_take_profit_low_risk(self):
        """测试低风险下的止损和止盈"""
        current_price = 1000.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            roe=0.25,
            gross_margin=0.60,
            free_cash_flow=100e8,
            debt_ratio=0.20
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.LOW
        )

        result = self.agent.analyze(self.context)

        # 低风险：止损 -15%，止盈 +30%
        assert abs(result.investment_decision.stop_loss_price - current_price * 0.85) < 1
        assert abs(result.investment_decision.take_profit_price - current_price * 1.30) < 1

    def test_stop_loss_and_take_profit_medium_risk(self):
        """测试中等风险下的止损和止盈"""
        current_price = 1000.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.40
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.MEDIUM
        )

        result = self.agent.analyze(self.context)

        # 中等风险：止损 -10%，止盈 +20%
        assert abs(result.investment_decision.stop_loss_price - current_price * 0.90) < 1
        assert abs(result.investment_decision.take_profit_price - current_price * 1.20) < 1

    def test_stop_loss_and_take_profit_high_risk(self):
        """测试高风险下的止损和止盈"""
        current_price = 1000.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            roe=0.10,
            gross_margin=0.30,
            free_cash_flow=50e8,
            debt_ratio=0.60
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.HIGH
        )

        result = self.agent.analyze(self.context)

        # 高风险：止损 -8%，止盈 +15%
        assert abs(result.investment_decision.stop_loss_price - current_price * 0.92) < 1
        assert abs(result.investment_decision.take_profit_price - current_price * 1.15) < 1

    def test_position_size_low_risk(self):
        """测试低风险下的建议仓位"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            roe=0.25,
            gross_margin=0.60,
            free_cash_flow=100e8,
            debt_ratio=0.20
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.LOW
        )

        result = self.agent.analyze(self.context)

        # 低风险：建议仓位 80%
        assert result.investment_decision.position_size == 0.8

    def test_position_size_medium_risk(self):
        """测试中等风险下的建议仓位"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            roe=0.20,
            gross_margin=0.50,
            free_cash_flow=100e8,
            debt_ratio=0.40
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.MEDIUM
        )

        result = self.agent.analyze(self.context)

        # 中等风险：建议仓位 60%
        assert result.investment_decision.position_size == 0.6

    def test_position_size_high_risk(self):
        """测试高风险下的建议仓位"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            roe=0.10,
            gross_margin=0.30,
            free_cash_flow=50e8,
            debt_ratio=0.60
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.HIGH
        )

        result = self.agent.analyze(self.context)

        # 高风险：建议仓位 40%
        assert result.investment_decision.position_size == 0.4

    def test_position_size_very_high_risk(self):
        """测试极高风险下的建议仓位"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            roe=0.05,
            gross_margin=0.20,
            free_cash_flow=-50e8,
            debt_ratio=0.80
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.VERY_HIGH
        )

        result = self.agent.analyze(self.context)

        # 极高风险：建议仓位 20%
        assert result.investment_decision.position_size == 0.2

    def test_checklist_passed_all_items(self):
        """测试决策清单全部通过"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,
            roe=0.25,
            gross_margin=0.60,
            free_cash_flow=100e8,
            debt_ratio=0.20
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0
        self.context.competitive_moat = CompetitiveModality(overall_score=6.0)
        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.LOW
        )

        result = self.agent.analyze(self.context)

        # 所有条件都满足时清单应该通过
        assert result.investment_decision.checklist_passed == True

    def test_checklist_failed_no_safety_margin(self):
        """测试决策清单因无安全边际而失败"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,
            gross_margin=0.92,
            free_cash_flow=150e8,
            debt_ratio=0.05
        )

        self.context.safety_margin_ok = False  # 无安全边际
        self.context.overall_score = 10.06
        self.context.competitive_moat = CompetitiveModality(overall_score=9.0)
        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.MEDIUM
        )

        result = self.agent.analyze(self.context)

        # 没有安全边际时清单失败
        assert result.investment_decision.checklist_passed == False

    def test_checklist_failed_very_high_risk(self):
        """测试决策清单因极高风险而失败"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,
            roe=0.25,
            gross_margin=0.60,
            free_cash_flow=100e8,
            debt_ratio=0.20
        )

        self.context.safety_margin_ok = True
        self.context.overall_score = 6.0
        self.context.competitive_moat = CompetitiveModality(overall_score=6.0)
        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.VERY_HIGH  # 极高风险
        )

        result = self.agent.analyze(self.context)

        # 极高风险时清单失败
        assert result.investment_decision.checklist_passed == False

    def test_conviction_level_set_correctly(self):
        """测试信念强度被正确设置"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,
            gross_margin=0.92,
            free_cash_flow=150e8,
            debt_ratio=0.05
        )

        self.context.sell_signal = SellSignalAnalysis(
            stock_code="600519",
            sell_signal=InvestmentSignal.SELL,
            confidence_score=0.7
        )

        result = self.agent.analyze(self.context)

        # 信念强度应该等于卖出信号的置信度
        assert result.investment_decision.conviction_level == 0.7

    def test_600519_example(self):
        """测试 600519 实际案例"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,
            gross_margin=0.92,
            free_cash_flow=150e8,
            debt_ratio=0.05
        )

        self.context.buy_signal = BuySignalAnalysis(
            stock_code="600519",
            buy_signal=InvestmentSignal.HOLD,
            confidence_score=0.0
        )

        self.context.sell_signal = SellSignalAnalysis(
            stock_code="600519",
            sell_signal=InvestmentSignal.SELL,
            confidence_score=0.7
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.MEDIUM
        )

        self.context.safety_margin_ok = False
        self.context.overall_score = 10.06
        self.context.competitive_moat = CompetitiveModality(overall_score=9.0)

        result = self.agent.analyze(self.context)

        # 600519 应该是卖出信号
        assert result.investment_decision.decision == InvestmentSignal.SELL
        assert result.investment_decision.conviction_level == 0.7
        assert result.investment_decision.checklist_passed == False

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            roe=0.25,
            gross_margin=0.60,
            free_cash_flow=100e8,
            debt_ratio=0.30
        )

        self.context.risk_assessment = RiskAssessment(
            stock_code="600519",
            overall_risk_level=RiskLevel.MEDIUM
        )

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

