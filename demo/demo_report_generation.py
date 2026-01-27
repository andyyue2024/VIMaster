"""
报告生成演示脚本
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.reports import (
    ReportManager,
    ReportTemplate,
    StockReportData,
    PortfolioReportData,
    REPORTLAB_AVAILABLE,
    OPENPYXL_AVAILABLE,
)


def demo_template_customization():
    """演示 1: 模板自定义"""
    print("\n" + "=" * 80)
    print("演示 1: 报告模板自定义")
    print("=" * 80)

    # 创建自定义模板
    template = ReportTemplate(
        name="custom_template",
        title="我的投资分析报告",
        subtitle="专业价值投资分析",
        author="投资研究团队",
        primary_color="#2e7d32",  # 绿色主题
        secondary_color="#81c784",
        include_summary=True,
        include_financials=True,
        include_valuation=True,
        include_risk=True,
        footer_text="此报告仅供参考，不构成投资建议",
    )

    print(f"模板名称: {template.name}")
    print(f"标题: {template.title}")
    print(f"主色调: {template.primary_color}")

    # 保存模板
    template.save("config/custom_template.json")
    print("✓ 自定义模板已保存到 config/custom_template.json")


def demo_single_stock_report():
    """演示 2: 单只股票报告生成"""
    print("\n" + "=" * 80)
    print("演示 2: 单只股票报告生成")
    print("=" * 80)

    # 构建测试数据
    data = StockReportData(
        stock_code="600519",
        stock_name="贵州茅台",
        current_price=1800.00,
        pe_ratio=35.5,
        pb_ratio=12.3,
        roe=0.32,
        gross_margin=0.92,
        debt_ratio=0.25,
        free_cash_flow=50_000_000_000,
        intrinsic_value=2200.00,
        fair_price=2000.00,
        margin_of_safety=11.11,
        valuation_score=7.5,
        moat_score=9.0,
        brand_strength=0.95,
        cost_advantage=0.7,
        risk_level="低",
        leverage_risk=0.2,
        buy_signal="买入",
        sell_signal="持有",
        final_signal="买入",
        overall_score=78.5,
        ml_score=8.2,
        decision="买入",
        position_size=0.15,
        stop_loss=1530.00,
        take_profit=2700.00,
    )

    manager = ReportManager()

    # 生成 PDF
    if REPORTLAB_AVAILABLE:
        success = manager.generate_pdf(data, "reports/demo_stock_report.pdf")
        if success:
            print("✓ PDF 报告已生成: reports/demo_stock_report.pdf")
    else:
        print("⚠ reportlab 不可用，跳过 PDF 生成")

    # 生成 Excel
    if OPENPYXL_AVAILABLE:
        success = manager.generate_excel(data, "reports/demo_stock_report.xlsx")
        if success:
            print("✓ Excel 报告已生成: reports/demo_stock_report.xlsx")
    else:
        print("⚠ openpyxl 不可用，跳过 Excel 生成")


def demo_portfolio_report():
    """演示 3: 投资组合报告生成"""
    print("\n" + "=" * 80)
    print("演示 3: 投资组合报告生成")
    print("=" * 80)

    # 构建测试数据
    stocks = [
        StockReportData(
            stock_code="600519",
            stock_name="贵州茅台",
            current_price=1800.00,
            final_signal="买入",
            overall_score=78.5,
            margin_of_safety=11.11,
            ml_score=8.2,
            decision="买入",
        ),
        StockReportData(
            stock_code="000858",
            stock_name="五粮液",
            current_price=160.00,
            final_signal="持有",
            overall_score=65.0,
            margin_of_safety=5.5,
            ml_score=6.8,
            decision="持有",
        ),
        StockReportData(
            stock_code="000651",
            stock_name="格力电器",
            current_price=45.00,
            final_signal="买入",
            overall_score=72.3,
            margin_of_safety=18.5,
            ml_score=7.5,
            decision="买入",
        ),
    ]

    portfolio_data = PortfolioReportData(
        report_id="DEMO-2026-001",
        generated_at="2026-01-27 15:30",
        stocks=stocks,
        total_stocks=3,
        strong_buy_count=0,
        buy_count=2,
        hold_count=1,
        sell_count=0,
        strong_sell_count=0,
        strategy="平衡型",
        expected_return=0.12,
        risk_score=4.5,
    )

    manager = ReportManager()

    # 生成 PDF
    if REPORTLAB_AVAILABLE:
        success = manager.generate_portfolio_pdf(portfolio_data, "reports/demo_portfolio_report.pdf")
        if success:
            print("✓ PDF 组合报告已生成: reports/demo_portfolio_report.pdf")
    else:
        print("⚠ reportlab 不可用，跳过 PDF 生成")

    # 生成 Excel
    if OPENPYXL_AVAILABLE:
        success = manager.generate_portfolio_excel(portfolio_data, "reports/demo_portfolio_report.xlsx")
        if success:
            print("✓ Excel 组合报告已生成: reports/demo_portfolio_report.xlsx")
    else:
        print("⚠ openpyxl 不可用，跳过 Excel 生成")


def demo_custom_template_report():
    """演示 4: 使用自定义模板生成报告"""
    print("\n" + "=" * 80)
    print("演示 4: 使用自定义模板生成报告")
    print("=" * 80)

    # 加载自定义模板
    try:
        template = ReportTemplate.load("config/custom_template.json")
        print(f"✓ 已加载模板: {template.name}")
    except FileNotFoundError:
        print("⚠ 自定义模板不存在，使用默认模板")
        template = ReportTemplate(
            title="自定义报告",
            primary_color="#1565c0",
        )

    manager = ReportManager(template=template)

    data = StockReportData(
        stock_code="600036",
        stock_name="招商银行",
        current_price=35.00,
        pe_ratio=8.5,
        pb_ratio=1.2,
        roe=0.18,
        final_signal="强烈买入",
        overall_score=82.0,
        ml_score=8.8,
    )

    if REPORTLAB_AVAILABLE:
        success = manager.generate_pdf(data, "reports/custom_template_report.pdf")
        if success:
            print("✓ 自定义模板 PDF 报告已生成: reports/custom_template_report.pdf")


def check_dependencies():
    """检查依赖"""
    print("\n" + "=" * 80)
    print("依赖检查")
    print("=" * 80)

    print(f"reportlab (PDF): {'✓ 可用' if REPORTLAB_AVAILABLE else '✗ 不可用'}")
    print(f"openpyxl (Excel): {'✓ 可用' if OPENPYXL_AVAILABLE else '✗ 不可用'}")

    if not REPORTLAB_AVAILABLE:
        print("\n安装 reportlab: pip install reportlab")
    if not OPENPYXL_AVAILABLE:
        print("安装 openpyxl: pip install openpyxl")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 报告生成演示")
    print("=" * 80)

    check_dependencies()

    if not REPORTLAB_AVAILABLE and not OPENPYXL_AVAILABLE:
        print("\n⚠ 请安装至少一个报告生成依赖后再运行演示")
        return

    demo_template_customization()
    demo_single_stock_report()
    demo_portfolio_report()
    demo_custom_template_report()

    print("\n" + "=" * 80)
    print("演示完成！报告已保存到 reports/ 目录")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
