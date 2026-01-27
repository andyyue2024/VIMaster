"""
可视化功能单元测试
"""
import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.visualization import (
    ChartConfig,
    StockVisualizer,
    create_visualizer,
    check_visualization_available,
    MATPLOTLIB_AVAILABLE,
)


class TestChartConfig:
    """图表配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = ChartConfig()

        assert config.width == 12
        assert config.height == 8
        assert config.dpi == 100
        assert len(config.colors) == 10

    def test_custom_config(self):
        """测试自定义配置"""
        config = ChartConfig(
            width=16,
            height=10,
            dpi=150,
            colors=['#ff0000', '#00ff00'],
        )

        assert config.width == 16
        assert config.dpi == 150
        assert len(config.colors) == 2


class TestStockVisualizer:
    """股票可视化器测试"""

    def test_visualizer_creation(self):
        """测试创建可视化器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            assert visualizer.output_dir == tmpdir
            assert visualizer.config is not None

    def test_create_visualizer(self):
        """测试便捷函数"""
        visualizer = create_visualizer()

        assert isinstance(visualizer, StockVisualizer)

    def test_check_available(self):
        """测试可用性检查"""
        result = check_visualization_available()

        assert result == MATPLOTLIB_AVAILABLE


class TestRadarChart:
    """雷达图测试"""

    def test_radar_chart(self):
        """测试雷达图生成"""
        if not MATPLOTLIB_AVAILABLE:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            scores = {
                '财务': 8.0,
                '估值': 7.0,
                '护城河': 9.0,
                '风险': 6.0,
            }

            path = visualizer.plot_score_radar("600519", scores)

            assert path is not None
            assert os.path.exists(path)


class TestValuationChart:
    """估值图测试"""

    def test_valuation_chart(self):
        """测试估值对比图"""
        if not MATPLOTLIB_AVAILABLE:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            path = visualizer.plot_valuation_comparison(
                "600519", 1800, 2000, 2200
            )

            assert path is not None
            assert os.path.exists(path)


class TestFinancialChart:
    """财务图测试"""

    def test_financial_chart(self):
        """测试财务指标图"""
        if not MATPLOTLIB_AVAILABLE:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            metrics = {
                'roe': 0.30,
                'gross_margin': 0.90,
                'pe_ratio': 30,
                'pb_ratio': 10,
                'debt_ratio': 0.25,
            }

            path = visualizer.plot_financial_metrics("600519", metrics)

            assert path is not None
            assert os.path.exists(path)


class TestSignalGauge:
    """信号仪表盘测试"""

    def test_signal_gauge(self):
        """测试信号仪表盘"""
        if not MATPLOTLIB_AVAILABLE:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            path = visualizer.plot_signal_gauge("600519", 78.5, "买入")

            assert path is not None
            assert os.path.exists(path)


class TestPortfolioChart:
    """组合图测试"""

    def test_portfolio_chart(self):
        """测试组合配置图"""
        if not MATPLOTLIB_AVAILABLE:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            stocks = [
                {'stock_code': '600519', 'position_size': 0.4, 'overall_score': 80, 'signal': '买入'},
                {'stock_code': '000858', 'position_size': 0.6, 'overall_score': 70, 'signal': '持有'},
            ]

            path = visualizer.plot_portfolio_allocation(stocks)

            assert path is not None
            assert os.path.exists(path)


class TestRiskChart:
    """风险图测试"""

    def test_risk_chart(self):
        """测试风险分析图"""
        if not MATPLOTLIB_AVAILABLE:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = StockVisualizer(output_dir=tmpdir)

            risk_data = {
                '杠杆风险': 0.3,
                '行业风险': 0.4,
                '公司风险': 0.2,
            }

            path = visualizer.plot_risk_analysis("600519", risk_data)

            assert path is not None
            assert os.path.exists(path)
