"""
单元测试 - 风险管理 Agent (Agent 8)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, CompetitiveModality, RiskLevel
)
from src.agents.risk_management_agent import RiskManagementAgent


class TestRiskManagementAgent:
    """风险管理 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = RiskManagementAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "风险管理Agent"
        assert self.agent.description == "风险评估与规避"

    def test_ability_circle_match_high_score(self):
        """测试高评分时的能力圈匹配度"""
        self.context.overall_score = 8.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        # 能力圈匹配度 = 综合评分 / 10
        assert result.risk_assessment.ability_circle_match == 0.8

    def test_ability_circle_match_low_score(self):
        """测试低评分时的能力圈匹配度"""
        self.context.overall_score = 2.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.ability_circle_match == 0.2

    def test_leverage_risk_low(self):
        """测试低杠杆风险（负债率 < 30%）"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.05  # < 30%
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.leverage_risk == 0.2

    def test_leverage_risk_medium(self):
        """测试中等杠杆风险（负债率 30%-50%）"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.40
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.leverage_risk == 0.4

    def test_leverage_risk_high(self):
        """测试高杠杆风险（负债率 50%-70%）"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.60
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.leverage_risk == 0.6

    def test_leverage_risk_very_high(self):
        """测试极高杠杆风险（负债率 > 70%）"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.85
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.leverage_risk == 0.8

    def test_industry_risk_low_moat(self):
        """测试低行业风险（护城河强）"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        self.context.competitive_moat = CompetitiveModality(
            overall_score=9.0  # 强劲护城河
        )

        result = self.agent.analyze(self.context)

        # 行业风险 = 1 - (护城河强度 / 10)
        assert abs(result.risk_assessment.industry_risk - 0.1) < 0.001

    def test_industry_risk_high_moat(self):
        """测试高行业风险（护城河弱）"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        self.context.competitive_moat = CompetitiveModality(
            overall_score=3.0  # 弱护城河
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.industry_risk == 0.7

    def test_company_risk_high_score(self):
        """测试低公司风险（综合评分高）"""
        self.context.overall_score = 8.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        # 公司风险 = 1 - (综合评分 / 10)
        assert abs(result.risk_assessment.company_risk - 0.2) < 0.001

    def test_company_risk_low_score(self):
        """测试高公司风险（综合评分低）"""
        self.context.overall_score = 2.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.company_risk == 0.8

    def test_overall_risk_level_low(self):
        """测试低风险等级"""
        self.context.overall_score = 8.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.20  # 低负债
        )

        self.context.competitive_moat = CompetitiveModality(
            overall_score=9.0  # 强护城河
        )

        result = self.agent.analyze(self.context)

        # 综合风险应该低
        assert result.risk_assessment.overall_risk_level == RiskLevel.LOW

    def test_overall_risk_level_medium(self):
        """测试中等风险等级"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.40
        )

        self.context.competitive_moat = CompetitiveModality(
            overall_score=5.0
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.overall_risk_level == RiskLevel.MEDIUM

    def test_overall_risk_level_high(self):
        """测试高风险等级"""
        self.context.overall_score = 3.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.60
        )

        result = self.agent.analyze(self.context)

        assert result.risk_assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]

    def test_overall_risk_level_very_high(self):
        """测试极高风险等级"""
        self.context.overall_score = 0.0  # 最低评分，使 company_risk = 1.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=1.0  # 极高负债，使 leverage_risk = 0.8
        )
        # 添加弱护城河，使 industry_risk 也很高
        self.context.competitive_moat = CompetitiveModality(
            overall_score=0.0  # 无护城河，使 industry_risk = 1.0
        )

        result = self.agent.analyze(self.context)

        # 综合风险 = 0.8*0.3 + 1.0*0.3 + 1.0*0.4 = 0.24 + 0.3 + 0.4 = 0.94 -> 9.4分 > 8.0
        assert result.risk_assessment.overall_risk_level == RiskLevel.VERY_HIGH

    def test_risk_mitigation_strategies_ability_circle(self):
        """测试能力圈风险缓解策略"""
        self.context.overall_score = 2.0  # 低评分
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        result = self.agent.analyze(self.context)

        # 能力圈匹配度低时应该有相应策略
        if result.risk_assessment.ability_circle_match < 0.5:
            assert "能力圈" in str(result.risk_assessment.risk_mitigation_strategies)

    def test_risk_mitigation_strategies_leverage(self):
        """测试杠杆风险缓解策略"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.70  # 高负债
        )

        result = self.agent.analyze(self.context)

        # 高杠杆风险时应该有缓解策略
        if result.risk_assessment.leverage_risk > 0.6:
            assert len(result.risk_assessment.risk_mitigation_strategies) > 0

    def test_risk_mitigation_strategies_high_risk(self):
        """测试高风险缓解策略"""
        self.context.overall_score = 2.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.70
        )

        result = self.agent.analyze(self.context)

        # 高风险或极高风险时应该有止损策略
        if result.risk_assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            strategies_str = str(result.risk_assessment.risk_mitigation_strategies)
            assert len(result.risk_assessment.risk_mitigation_strategies) > 0

    def test_600519_risk_analysis(self):
        """测试 600519 的风险分析（中等风险）"""
        self.context.overall_score = 10.06
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            pe_ratio=35.2,
            debt_ratio=0.05
        )

        self.context.competitive_moat = CompetitiveModality(
            overall_score=9.0
        )

        result = self.agent.analyze(self.context)

        # 600519 的综合评分 10.06，负债率低，护城河强
        # 风险等级应该在低到中等范围内
        assert result.risk_assessment.overall_risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.overall_score = 5.0
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1000.0,
            debt_ratio=0.30
        )

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

