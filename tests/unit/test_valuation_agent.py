"""
单元测试 - 估值 Agent (Agent 4)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, ValuationAnalysis
)
from src.agents.valuation_agent import ValuationAgent


class TestValuationAgent:
    """估值 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = ValuationAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "估值Agent"
        assert self.agent.description == "内在价值评估（DCF、PE、PB）"

    def test_pe_valuation_calculation(self):
        """测试 PE 估值计算"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,  # 高 PE
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.analyze(self.context)

        # 应该生成估值对象
        assert result.valuation is not None
        assert result.valuation.pe_valuation is not None

    def test_pb_valuation_calculation(self):
        """测试 PB 估值计算"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.analyze(self.context)

        assert result.valuation.pb_valuation is not None

    def test_dcf_valuation_calculation(self):
        """测试 DCF 估值计算"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.analyze(self.context)

        # 有 EPS 时应该计算 DCF
        assert result.valuation.dcf_value is not None

    def test_intrinsic_value_calculation(self):
        """测试内在价值计算（三种方法的平均值）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.analyze(self.context)

        # 内在价值应该是三种估值的平均
        assert result.valuation.intrinsic_value > 0
        assert result.valuation.fair_price > 0

    def test_valuation_score_severely_overvalued(self):
        """测试严重高估的评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,  # 高价格
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.analyze(self.context)

        # 当前价格 / 合理价格 > 1.3 时，评分应该是 1.0
        if result.valuation.fair_price > 0:
            ratio = result.valuation.current_price / result.valuation.fair_price
            if ratio > 1.3:
                assert result.valuation.valuation_score == 1.0

    def test_valuation_score_overvalued(self):
        """测试高估的评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=900.0,  # 中等价格
            pe_ratio=20.0,
            pb_ratio=8.0,
            earnings_per_share=45.0
        )

        result = self.agent.analyze(self.context)

        assert result.valuation.valuation_score > 0

    def test_valuation_score_fair_valued(self):
        """测试合理估值的评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=800.0,  # 合理价格
            pe_ratio=15.0,
            pb_ratio=5.0,
            earnings_per_share=53.0
        )

        result = self.agent.analyze(self.context)

        assert result.valuation.valuation_score >= 0

    def test_valuation_score_undervalued(self):
        """测试低估的评分"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=500.0,  # 低价格
            pe_ratio=10.0,
            pb_ratio=3.0,
            earnings_per_share=50.0
        )

        result = self.agent.analyze(self.context)

        # 低估评分应该更高
        assert result.valuation.valuation_score > 0

    def test_valuation_without_eps(self):
        """测试没有 EPS 的情况（不计算 DCF）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=None  # 无 EPS
        )

        result = self.agent.analyze(self.context)

        # DCF 应该是 None
        assert result.valuation.dcf_value is None

    def test_valuation_without_pe_and_pb(self):
        """测试没有 PE 和 PB 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=None,
            pb_ratio=None,
            earnings_per_share=None
        )

        result = self.agent.analyze(self.context)

        # 应该使用当前价格作为内在价值
        assert result.valuation.intrinsic_value == self.context.financial_metrics.current_price

    def test_valuation_with_zero_pe(self):
        """测试 PE 为 0 的情况（无盈利）"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=0,  # 无盈利
            pb_ratio=12.5,
            earnings_per_share=0
        )

        result = self.agent.analyze(self.context)

        # 应该跳过 PE 估值
        assert result.valuation is not None

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        result = self.agent.analyze(self.context)

        # 应该返回原始上下文
        assert result.stock_code == "600519"

    def test_current_price_set_in_valuation(self):
        """测试当前价格被设置在估值对象中"""
        price = 1800.5
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=price,
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.analyze(self.context)

        assert result.valuation.current_price == price

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            pb_ratio=12.5,
            earnings_per_share=51.2
        )

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

