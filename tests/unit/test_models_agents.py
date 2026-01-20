"""
单元测试 - 测试各个 Agent 和数据模型的功能
"""
import pytest
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, 'E:\\Workplace-Pycharm\\VIMaster')

from src.models.data_models import (
    FinancialMetrics, CompetitiveModality, ValuationAnalysis,
    BuySignalAnalysis, SellSignalAnalysis, RiskAssessment,
    InvestmentDecision, StockAnalysisContext, InvestmentSignal, RiskLevel
)
from src.agents.base_agent import BaseAgent
from src.agents.value_investing_agents import (
    EquityThinkingAgent, MoatAgent, FinancialAnalysisAgent,
    ValuationAgent, SafetyMarginAgent
)


class TestDataModels:
    """测试数据模型"""

    def test_financial_metrics_creation(self):
        """测试财务指标创建"""
        metrics = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.5,
            pb_ratio=10.2,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0
        )

        assert metrics.stock_code == "600519"
        assert metrics.pe_ratio == 25.5
        assert metrics.roe == 0.20
        assert metrics.current_price == 1000.0

    def test_stock_analysis_context_creation(self):
        """测试股票分析上下文创建"""
        context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

        assert context.stock_code == "600519"
        assert context.stock_name == "贵州茅台"
        assert context.overall_score == 0.0
        assert context.final_signal == InvestmentSignal.HOLD

    def test_competitive_moat_creation(self):
        """测试护城河数据模型"""
        moat = CompetitiveModality(
            brand_strength=0.8,
            cost_advantage=0.7,
            network_effect=0.6,
            switching_cost=0.5,
            overall_score=8.0
        )

        assert moat.brand_strength == 0.8
        assert moat.overall_score == 8.0

    def test_valuation_analysis_creation(self):
        """测试估值分析"""
        valuation = ValuationAnalysis(
            stock_code="600519",
            intrinsic_value=1200.0,
            current_price=1000.0,
            margin_of_safety=16.67
        )

        assert valuation.intrinsic_value == 1200.0
        assert valuation.margin_of_safety == 16.67

    def test_investment_signal_enum(self):
        """测试投资信号枚举"""
        assert InvestmentSignal.STRONG_BUY.value == "strong_buy"
        assert InvestmentSignal.BUY.value == "buy"
        assert InvestmentSignal.HOLD.value == "hold"
        assert InvestmentSignal.SELL.value == "sell"
        assert InvestmentSignal.STRONG_SELL.value == "strong_sell"

    def test_risk_level_enum(self):
        """测试风险等级枚举"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.VERY_HIGH.value == "very_high"

    def test_context_to_dict(self):
        """测试上下文转换为字典"""
        context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台",
            overall_score=75.0,
            final_signal=InvestmentSignal.BUY
        )

        result = context.to_dict()
        assert result["stock_code"] == "600519"
        assert result["stock_name"] == "贵州茅台"
        assert result["overall_score"] == 75.0
        assert result["final_signal"] == "buy"


class TestAgents:
    """测试 Agent"""

    def create_mock_context(self):
        """创建测试用的 mock 上下文"""
        context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

        # 创建财务指标
        context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,  # 20%
            gross_margin=0.60,  # 60%
            current_price=1000.0,
            earnings_per_share=40.0,
            debt_ratio=0.25,  # 25%
            profit_growth=0.15  # 15%
        )

        return context

    def test_equity_thinking_agent(self):
        """测试股权思维 Agent"""
        agent = EquityThinkingAgent()
        context = self.create_mock_context()

        result = agent.analyze(context)

        assert result.stock_code == "600519"
        assert result.overall_score > 0  # 应该增加评分

    def test_moat_agent(self):
        """测试护城河 Agent"""
        agent = MoatAgent()
        context = self.create_mock_context()

        result = agent.analyze(context)

        assert result.competitive_moat is not None
        assert result.competitive_moat.overall_score > 0

    def test_financial_analysis_agent(self):
        """测试财务分析 Agent"""
        agent = FinancialAnalysisAgent()
        context = self.create_mock_context()

        result = agent.analyze(context)

        assert result.stock_code == "600519"
        # ROE=20% 和毛利率=60% 应该给出较高评分
        assert result.overall_score >= 5.0

    def test_valuation_agent(self):
        """测试估值 Agent"""
        agent = ValuationAgent()
        context = self.create_mock_context()

        result = agent.analyze(context)

        assert result.valuation is not None
        assert result.valuation.stock_code == "600519"
        assert result.valuation.intrinsic_value is not None
        assert result.valuation.fair_price is not None

    def test_safety_margin_agent(self):
        """测试安全边际 Agent"""
        agent = SafetyMarginAgent()
        context = self.create_mock_context()

        # 设置估值信息
        context.valuation = ValuationAnalysis(
            stock_code="600519",
            fair_price=1200.0,
            intrinsic_value=1200.0,
            current_price=1000.0
        )

        result = agent.analyze(context)

        assert result.valuation.margin_of_safety > 0
        assert result.safety_margin_ok is True

    def test_agent_execution_time(self):
        """测试 Agent 执行时间记录"""
        agent = EquityThinkingAgent()
        context = self.create_mock_context()

        result = agent.execute(context)

        assert agent.execution_time is not None
        assert agent.execution_time >= 0
        assert agent.last_execution is not None


class TestFinancialLogic:
    """测试财务计算逻辑"""

    def test_pe_valuation_calculation(self):
        """测试 PE 估值计算"""
        metrics = FinancialMetrics(
            stock_code="600519",
            pe_ratio=20.0,
            current_price=1000.0
        )

        # 假设合理 PE 为 25
        fair_pe = 25
        fair_price = metrics.current_price / metrics.pe_ratio * fair_pe if metrics.pe_ratio != 0 else metrics.current_price

        assert fair_price == 1250.0

    def test_safety_margin_calculation(self):
        """测试安全边际计算"""
        fair_price = 1200.0
        current_price = 1000.0

        margin = (fair_price - current_price) / fair_price
        margin_percent = margin * 100

        assert abs(margin_percent - 16.67) < 0.1

    def test_roe_scoring(self):
        """测试 ROE 评分逻辑"""
        def score_roe(roe):
            if roe > 0.20:
                return 10.0
            elif roe > 0.15:
                return 8.0
            elif roe > 0.10:
                return 6.0
            else:
                return 2.0

        assert score_roe(0.25) == 10.0
        assert score_roe(0.18) == 8.0
        assert score_roe(0.12) == 6.0
        assert score_roe(0.05) == 2.0


class TestMockIntegration:
    """使用 Mock 的集成测试"""

    @patch('src.data.akshare_provider.AkshareDataProvider.get_stock_info')
    def test_agent_with_mocked_data(self, mock_get_stock_info):
        """测试带 Mock 数据的 Agent"""
        mock_get_stock_info.return_value = {
            "code": "600519",
            "name": "贵州茅台",
            "current_price": 1000.0,
            "pe_ratio": 25.0,
            "pb_ratio": 10.0,
        }

        context = StockAnalysisContext(stock_code="600519")
        agent = EquityThinkingAgent()

        # Agent 可以处理 Mock 返回的数据
        result = agent.analyze(context)

        assert result.stock_code == "600519"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
