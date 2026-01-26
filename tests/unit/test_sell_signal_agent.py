"""
单元测试 - 卖出纪律 Agent (Agent 7)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, ValuationAnalysis, InvestmentSignal
)
from src.agents.sell_signal_agent import SellSignalAgent


class TestSellSignalAgent:
    """卖出纪律 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = SellSignalAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "卖出纪律Agent"
        assert self.agent.description == "卖出信号识别"

    def test_fundamental_deterioration_signal(self):
        """测试基本面恶化信号（利润增长 < -20%）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0,
            profit_growth=-0.25  # -25% < -20%
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1000.0,
            valuation_score=5.0
        )

        self.context.overall_score = 3.0

        result = self.agent.analyze(self.context)

        # 应该识别基本面恶化
        assert result.sell_signal.fundamental_deterioration == True

    def test_severe_overvaluation_signal_pe(self):
        """测试严重高估信号（PE > 30）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2  # > 30
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 应该识别严重高估
        assert result.sell_signal.is_severely_overvalued == True

    def test_severe_overvaluation_signal_valuation_score(self):
        """测试严重高估信号（估值评分 < 2）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0  # < 2
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 应该识别严重高估
        assert result.sell_signal.is_severely_overvalued == True

    def test_better_opportunity_signal(self):
        """测试更好机会信号（评分 < 4 且基本面恶化）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0,
            profit_growth=-0.25
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=800.0,
            valuation_score=3.0
        )

        self.context.overall_score = 3.5  # < 4

        result = self.agent.analyze(self.context)

        # 应该识别更好机会
        if result.sell_signal.fundamental_deterioration:
            assert result.sell_signal.better_opportunity_exists == True

    def test_strong_sell_signal(self):
        """测试强烈卖出信号（多个卖出因素）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            profit_growth=-0.25
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 应该生成强烈卖出信号
        if result.sell_signal.fundamental_deterioration or result.sell_signal.is_severely_overvalued:
            assert result.sell_signal.sell_signal == InvestmentSignal.STRONG_SELL or \
                   result.sell_signal.sell_signal == InvestmentSignal.SELL

    def test_sell_signal(self):
        """测试卖出信号（单个卖出因素）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 应该生成卖出信号（600519 案例）
        assert result.sell_signal.sell_signal in [
            InvestmentSignal.SELL,
            InvestmentSignal.STRONG_SELL
        ]

    def test_hold_signal_no_sell_factors(self):
        """测试持有信号（无卖出因素）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,
            pe_ratio=15.0,
            profit_growth=0.15
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=900.0,
            valuation_score=7.0
        )

        self.context.overall_score = 6.0

        result = self.agent.analyze(self.context)

        # 应该是持有信号
        assert result.sell_signal.sell_signal == InvestmentSignal.HOLD

    def test_recommended_sell_price(self):
        """测试推荐卖出价"""
        current_price = 1800.5
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=current_price,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 应该设置推荐卖出价
        assert result.sell_signal.recommended_sell_price == current_price

    def test_analyze_without_valuation(self):
        """测试没有估值对象的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            pe_ratio=20.0
        )
        # 不设置 valuation

        result = self.agent.analyze(self.context)

        assert result.sell_signal is not None

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=900.0,
            valuation_score=5.0
        )
        # 不设置 financial_metrics

        result = self.agent.analyze(self.context)

        assert result.sell_signal is not None

    def test_sell_signal_confidence_high(self):
        """测试卖出信号置信度高"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            profit_growth=-0.25
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 多个卖出因素时置信度应该高
        if result.sell_signal.sell_signal == InvestmentSignal.STRONG_SELL:
            assert result.sell_signal.confidence_score >= 0.8

    def test_sell_signal_confidence_medium(self):
        """测试卖出信号置信度中等"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.analyze(self.context)

        # 单个卖出因素时置信度应该中等
        if result.sell_signal.sell_signal == InvestmentSignal.SELL:
            assert result.sell_signal.confidence_score >= 0.6

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2
        )

        self.context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=766.64,
            valuation_score=1.0
        )

        self.context.overall_score = 10.0

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

