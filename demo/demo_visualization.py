"""
可视化演示脚本
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.visualization import (
    create_visualizer,
    StockVisualizer,
    check_visualization_available,
    MATPLOTLIB_AVAILABLE,
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def demo_radar_chart():
    """演示 1: 评分雷达图"""
    print("\n" + "=" * 80)
    print("演示 1: 评分雷达图")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    visualizer = create_visualizer()

    scores = {
        '护城河': 9.0,
        '财务健康': 8.5,
        '估值吸引力': 7.0,
        '成长性': 6.5,
        '风险控制': 8.0,
        '管理层': 7.5,
    }

    path = visualizer.plot_score_radar("600519", scores, title="贵州茅台 综合评分")

    if path:
        print(f"✓ 雷达图已保存: {path}")


def demo_valuation_chart():
    """演示 2: 估值对比图"""
    print("\n" + "=" * 80)
    print("演示 2: 估值对比图")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    visualizer = create_visualizer()

    path = visualizer.plot_valuation_comparison(
        stock_code="600519",
        current_price=1800.0,
        fair_price=2000.0,
        intrinsic_value=2200.0,
    )

    if path:
        print(f"✓ 估值对比图已保存: {path}")


def demo_financial_chart():
    """演示 3: 财务指标图"""
    print("\n" + "=" * 80)
    print("演示 3: 财务指标图")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    visualizer = create_visualizer()

    metrics = {
        'roe': 0.32,
        'gross_margin': 0.92,
        'pe_ratio': 35.5,
        'pb_ratio': 12.3,
        'debt_ratio': 0.25,
    }

    path = visualizer.plot_financial_metrics("600519", metrics)

    if path:
        print(f"✓ 财务指标图已保存: {path}")


def demo_signal_gauge():
    """演示 4: 信号仪表盘"""
    print("\n" + "=" * 80)
    print("演示 4: 信号仪表盘")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    visualizer = create_visualizer()

    path = visualizer.plot_signal_gauge(
        stock_code="600519",
        overall_score=78.5,
        signal="买入",
    )

    if path:
        print(f"✓ 信号仪表盘已保存: {path}")


def demo_portfolio_chart():
    """演示 5: 投资组合配置图"""
    print("\n" + "=" * 80)
    print("演示 5: 投资组合配置图")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    visualizer = create_visualizer()

    stocks = [
        {'stock_code': '600519', 'position_size': 0.30, 'overall_score': 78.5, 'signal': '买入'},
        {'stock_code': '000858', 'position_size': 0.25, 'overall_score': 65.0, 'signal': '持有'},
        {'stock_code': '000651', 'position_size': 0.25, 'overall_score': 72.0, 'signal': '买入'},
        {'stock_code': '600036', 'position_size': 0.20, 'overall_score': 80.0, 'signal': '强烈买入'},
    ]

    path = visualizer.plot_portfolio_allocation(stocks, title="2026年投资组合")

    if path:
        print(f"✓ 组合配置图已保存: {path}")


def demo_risk_chart():
    """演示 6: 风险分析图"""
    print("\n" + "=" * 80)
    print("演示 6: 风险分析图")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    visualizer = create_visualizer()

    risk_data = {
        '杠杆风险': 0.25,
        '行业风险': 0.35,
        '公司风险': 0.20,
        '流动性风险': 0.15,
        '政策风险': 0.30,
    }

    path = visualizer.plot_risk_analysis("600519", risk_data)

    if path:
        print(f"✓ 风险分析图已保存: {path}")


def demo_full_report():
    """演示 7: 完整分析报告可视化"""
    print("\n" + "=" * 80)
    print("演示 7: 完整分析报告可视化（使用模拟数据）")
    print("=" * 80)

    if not MATPLOTLIB_AVAILABLE:
        print("⚠ matplotlib 不可用，跳过此演示")
        return

    # 创建模拟的分析上下文
    from dataclasses import dataclass
    from typing import Optional
    from enum import Enum

    class MockSignal(Enum):
        BUY = "买入"

    class MockRiskLevel(Enum):
        LOW = "低"

    @dataclass
    class MockMetrics:
        current_price: float = 1800.0
        pe_ratio: float = 35.5
        pb_ratio: float = 12.3
        roe: float = 0.32
        gross_margin: float = 0.92
        debt_ratio: float = 0.25

    @dataclass
    class MockValuation:
        intrinsic_value: float = 2200.0
        fair_price: float = 2000.0
        margin_of_safety: float = 11.11
        valuation_score: float = 7.5

    @dataclass
    class MockMoat:
        overall_score: float = 9.0
        brand_strength: float = 0.95
        cost_advantage: float = 0.7

    @dataclass
    class MockRisk:
        overall_risk_level: MockRiskLevel = MockRiskLevel.LOW
        leverage_risk: float = 0.25
        industry_risk: float = 0.35
        company_risk: float = 0.20
        ability_circle_match: float = 0.8

    @dataclass
    class MockBuySignal:
        confidence_score: float = 0.75

    @dataclass
    class MockContext:
        stock_code: str = "600519"
        overall_score: float = 78.5
        final_signal: MockSignal = MockSignal.BUY
        financial_metrics: Optional[MockMetrics] = None
        valuation: Optional[MockValuation] = None
        competitive_moat: Optional[MockMoat] = None
        risk_assessment: Optional[MockRisk] = None
        buy_signal: Optional[MockBuySignal] = None

    # 创建模拟上下文
    context = MockContext(
        financial_metrics=MockMetrics(),
        valuation=MockValuation(),
        competitive_moat=MockMoat(),
        risk_assessment=MockRisk(),
        buy_signal=MockBuySignal(),
    )

    visualizer = create_visualizer()
    charts = visualizer.generate_analysis_report(context, output_dir="charts/600519")

    print(f"\n生成的图表 ({len(charts)} 张):")
    for name, path in charts.items():
        print(f"  {name}: {path}")


def check_dependencies():
    """检查依赖"""
    print("\n" + "=" * 80)
    print("依赖检查")
    print("=" * 80)

    print(f"matplotlib: {'✓ 可用' if MATPLOTLIB_AVAILABLE else '✗ 不可用'}")

    if not MATPLOTLIB_AVAILABLE:
        print("\n安装 matplotlib: pip install matplotlib")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 可视化分析演示")
    print("=" * 80)

    check_dependencies()

    if not MATPLOTLIB_AVAILABLE:
        print("\n⚠ 请安装 matplotlib 后再运行演示")
        print("pip install matplotlib")
        return

    try:
        demo_radar_chart()
        demo_valuation_chart()
        demo_financial_chart()
        demo_signal_gauge()
        demo_portfolio_chart()
        demo_risk_chart()
        demo_full_report()

        print("\n" + "=" * 80)
        print("演示完成！图表已保存到 charts/ 目录")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"演示失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
