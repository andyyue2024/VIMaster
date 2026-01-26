"""
高级分析功能单元测试
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis import (
    ValuationAnalyzer,
    PortfolioOptimizer,
    PortfolioStrategy,
    ComprehensiveAnalyzer,
    ValuationTrend,
    ValuationPoint,
)


class TestValuationAnalyzer:
    """历史估值分析器测试"""

    def setup_method(self):
        """测试前的设置"""
        self.analyzer = ValuationAnalyzer()

    def test_initialization(self):
        """测试初始化"""
        assert self.analyzer is not None
        assert len(self.analyzer.valuation_cache) == 0

    def test_valuation_point_creation(self):
        """测试估值数据点创建"""
        point = ValuationPoint(
            date=datetime.now(),
            pe_ratio=25.0,
            pb_ratio=5.0,
            price=1000.0
        )

        assert point.pe_ratio == 25.0
        assert point.pb_ratio == 5.0
        assert point.price == 1000.0

    def test_valuation_trend_creation(self):
        """测试估值趋势创建"""
        trend = ValuationTrend(
            stock_code="600519",
            stock_name="贵州茅台"
        )

        assert trend.stock_code == "600519"
        assert len(trend.data_points) == 0

    def test_valuation_trend_to_dict(self):
        """测试估值趋势转换为字典"""
        trend = ValuationTrend(
            stock_code="600519",
            stock_name="贵州茅台",
            avg_pe_ratio=25.0,
            min_pe_ratio=20.0,
            max_pe_ratio=30.0,
        )

        d = trend.to_dict()

        assert d["stock_code"] == "600519"
        assert d["avg_pe_ratio"] == 25.0


class TestPortfolioOptimizer:
    """投资组合优化器测试"""

    def setup_method(self):
        """测试前的设置"""
        self.optimizer = PortfolioOptimizer()

    def test_initialization(self):
        """测试初始化"""
        assert self.optimizer is not None

    def test_portfolio_strategy_enum(self):
        """测试投资策略枚举"""
        assert PortfolioStrategy.VALUE.value == "价值型"
        assert PortfolioStrategy.GROWTH.value == "成长型"
        assert PortfolioStrategy.BALANCED.value == "平衡型"
        assert PortfolioStrategy.INCOME.value == "收益型"
        assert PortfolioStrategy.CONSERVATIVE.value == "保守型"

    def test_calculate_portfolio_metrics(self):
        """测试投资组合指标计算"""
        positions = [
            {"stock_code": "600519", "weight": 0.3, "overall_score": 8.0},
            {"stock_code": "000858", "weight": 0.2, "overall_score": 6.0},
            {"stock_code": "000651", "weight": 0.5, "overall_score": 5.0},
        ]

        metrics = self.optimizer.calculate_portfolio_metrics(positions)

        assert "total_weight" in metrics
        assert "average_score" in metrics
        assert metrics["total_weight"] == 1.0

    def test_generate_portfolio_recommendation_empty(self):
        """测试空列表生成投资组合"""
        result = self.optimizer.generate_portfolio_recommendation([], PortfolioStrategy.BALANCED)
        assert result is None

    def test_portfolio_recommendation_to_dict(self):
        """测试投资组合建议转换为字典"""
        from src.analysis import PortfolioRecommendation, PortfolioPosition

        rec = PortfolioRecommendation(strategy=PortfolioStrategy.BALANCED)
        rec.positions.append(
            PortfolioPosition(
                stock_code="600519",
                stock_name="贵州茅台",
                weight=0.5
            )
        )

        d = rec.to_dict()

        assert d["strategy"] == "平衡型"
        assert len(d["positions"]) == 1


class TestComprehensiveAnalyzer:
    """综合分析器测试"""

    def setup_method(self):
        """测试前的设置"""
        self.analyzer = ComprehensiveAnalyzer()

    def test_initialization(self):
        """测试初始化"""
        assert self.analyzer is not None
        assert self.analyzer.industry_comparator is not None
        assert self.analyzer.valuation_analyzer is not None
        assert self.analyzer.portfolio_optimizer is not None

    def test_analyze_stock_comprehensive_result_structure(self):
        """测试股票综合分析结果结构"""
        result = self.analyzer.analyze_stock_comprehensive("600519", industry="白酒")

        if result:
            assert "stock_code" in result
            assert "basic_analysis" in result
            assert result["stock_code"] == "600519"

    def test_portfolio_strategies_supported(self):
        """测试支持的投资策略"""
        strategies = [
            PortfolioStrategy.VALUE,
            PortfolioStrategy.GROWTH,
            PortfolioStrategy.BALANCED,
            PortfolioStrategy.INCOME,
            PortfolioStrategy.CONSERVATIVE,
        ]

        assert len(strategies) == 5
        for strategy in strategies:
            assert strategy.value is not None


class TestValuationComparison:
    """估值对比测试"""

    def test_valuation_comparison_structure(self):
        """测试估值对比结构"""
        from src.analysis import ValuationComparison

        comp = ValuationComparison(
            stock_code="600519",
            current_pe=35.2,
            historical_avg_pe=25.0,
            pe_vs_avg=1.41,
            valuation_percentile=75.0,
            valuation_signal="卖出",
            signal_confidence=0.8
        )

        assert comp.stock_code == "600519"
        assert comp.pe_vs_avg == 1.41
        assert comp.valuation_signal == "卖出"

        d = comp.to_dict()
        assert d["stock_code"] == "600519"


class TestPortfolioPosition:
    """投资组合持仓测试"""

    def test_portfolio_position_creation(self):
        """测试投资组合持仓创建"""
        from src.analysis import PortfolioPosition

        pos = PortfolioPosition(
            stock_code="600519",
            stock_name="贵州茅台",
            weight=0.3,
            target_price=1800.0,
            stop_loss_price=1500.0,
            risk_level="中等"
        )

        assert pos.stock_code == "600519"
        assert pos.weight == 0.3
        assert pos.risk_level == "中等"


class TestAnalysisIntegration:
    """分析功能集成测试"""

    def setup_method(self):
        """测试前的设置"""
        self.analyzer = ComprehensiveAnalyzer()

    def test_industry_comparator_available(self):
        """测试行业对比分析器可用"""
        industries = self.analyzer.industry_comparator.get_available_industries()
        assert len(industries) > 0

    def test_valuation_analyzer_available(self):
        """测试估值分析器可用"""
        assert self.analyzer.valuation_analyzer is not None

    def test_portfolio_optimizer_available(self):
        """测试投资组合优化器可用"""
        assert self.analyzer.portfolio_optimizer is not None

