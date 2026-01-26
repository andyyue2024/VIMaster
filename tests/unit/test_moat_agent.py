"""
单元测试 - 护城河 Agent (Agent 2)
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, CompetitiveModality
)
from src.agents.moat_agent import MoatAgent


class TestMoatAgent:
    """护城河 Agent 单元测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.agent = MoatAgent()
        self.context = StockAnalysisContext(
            stock_code="600519",
            stock_name="贵州茅台"
        )

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        assert self.agent.name == "护城河Agent"
        assert self.agent.description == "竞争优势分析"

    def test_analyze_with_high_gross_margin(self):
        """测试毛利率 > 40% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            gross_margin=0.92,  # 92% > 40%
            roe=0.32
        )

        result = self.agent.analyze(self.context)

        # 品牌强度应该是 0.8，成本优势应该是 0.7
        assert result.competitive_moat is not None
        assert result.competitive_moat.brand_strength == 0.8
        assert result.competitive_moat.cost_advantage == 0.7

    def test_analyze_with_medium_gross_margin(self):
        """测试毛利率在 20%-40% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            gross_margin=0.30,
            roe=0.20
        )

        result = self.agent.analyze(self.context)

        assert result.competitive_moat.brand_strength == 0.5
        assert result.competitive_moat.cost_advantage == 0.5

    def test_analyze_with_low_gross_margin(self):
        """测试毛利率 < 20% 的情况"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            gross_margin=0.10,
            roe=0.10
        )

        result = self.agent.analyze(self.context)

        assert result.competitive_moat.brand_strength == 0.2
        assert result.competitive_moat.cost_advantage == 0.2

    def test_analyze_roe_impact_on_moat_score(self):
        """测试 ROE 对护城河评分的影响"""
        # ROE > 20% 时
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            gross_margin=0.50
        )

        result = self.agent.analyze(self.context)
        assert result.competitive_moat.overall_score == 9.0

        # ROE 在 15%-20% 时
        self.context.financial_metrics.roe = 0.18
        result = self.agent.analyze(self.context)
        assert result.competitive_moat.overall_score == 7.0

        # ROE 在 10%-15% 时
        self.context.financial_metrics.roe = 0.12
        result = self.agent.analyze(self.context)
        assert result.competitive_moat.overall_score == 5.0

        # ROE < 10% 时
        self.context.financial_metrics.roe = 0.08
        result = self.agent.analyze(self.context)
        assert result.competitive_moat.overall_score == 3.0

    @patch('src.agents.moat_agent.AkshareDataProvider.get_industry_info')
    def test_analyze_with_internet_industry(self, mock_industry_info):
        """测试互联网行业的网络效应分析"""
        mock_industry_info.return_value = {
            'industry': '互联网服务',
            'market': '上海'
        }

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            gross_margin=0.50
        )

        result = self.agent.analyze(self.context)

        # 互联网行业应该有高的网络效应和转换成本
        assert result.competitive_moat.network_effect == 0.8
        assert result.competitive_moat.switching_cost == 0.7

    @patch('src.agents.moat_agent.AkshareDataProvider.get_industry_info')
    def test_analyze_with_consumer_industry(self, mock_industry_info):
        """测试消费品行业的品牌强度分析"""
        mock_industry_info.return_value = {
            'industry': '食品饮料',
            'market': '上海'
        }

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            gross_margin=0.50
        )

        result = self.agent.analyze(self.context)

        # 消费品行业应该有高的品牌强度和转换成本
        assert result.competitive_moat.brand_strength == 0.8
        assert result.competitive_moat.switching_cost == 0.6

    @patch('src.agents.moat_agent.AkshareDataProvider.get_industry_info')
    def test_analyze_without_industry_info(self, mock_industry_info):
        """测试无行业信息的情况"""
        mock_industry_info.return_value = None

        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            gross_margin=0.50
        )

        result = self.agent.analyze(self.context)

        # 应该使用默认评分
        assert result.competitive_moat is not None

    def test_analyze_without_financial_metrics(self):
        """测试没有财务指标的情况"""
        result = self.agent.analyze(self.context)

        assert result.competitive_moat is not None
        # 没有财务指标时，overall_score 保持默认值 0.0
        assert result.competitive_moat.overall_score == 0.0

    def test_moat_description_generation(self):
        """测试护城河描述的生成"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.32,
            gross_margin=0.92
        )

        result = self.agent.analyze(self.context)

        # description 应该包含各个指标的信息
        assert "品牌强度" in result.competitive_moat.description
        assert "成本优势" in result.competitive_moat.description
        assert "网络效应" in result.competitive_moat.description
        assert "转换成本" in result.competitive_moat.description

    def test_agent_execute_method(self):
        """测试 Agent 的 execute 方法"""
        self.context.financial_metrics = FinancialMetrics(
            stock_code="600519",
            current_price=1800.5,
            roe=0.25,
            gross_margin=0.50
        )

        result = self.agent.execute(self.context)

        assert self.agent.execution_time is not None
        assert self.agent.last_execution is not None

