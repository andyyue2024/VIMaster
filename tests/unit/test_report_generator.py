"""
报告生成单元测试
"""
import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.reports import (
    ReportTemplate,
    StockReportData,
    PortfolioReportData,
    ReportManager,
    REPORTLAB_AVAILABLE,
    OPENPYXL_AVAILABLE,
)


class TestReportTemplate:
    """报告模板测试"""

    def test_default_template(self):
        """测试默认模板创建"""
        template = ReportTemplate()

        assert template.name == "default"
        assert template.title == "VIMaster 价值投资分析报告"
        assert template.page_size == "A4"

    def test_custom_template(self):
        """测试自定义模板"""
        template = ReportTemplate(
            name="custom",
            title="自定义报告",
            primary_color="#ff0000",
        )

        assert template.name == "custom"
        assert template.primary_color == "#ff0000"

    def test_template_to_dict(self):
        """测试转换为字典"""
        template = ReportTemplate()
        data = template.to_dict()

        assert "name" in data
        assert "title" in data
        assert data["include_summary"] is True

    def test_template_save_and_load(self):
        """测试保存和加载"""
        template = ReportTemplate(name="test", title="测试报告")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "template.json")
            template.save(path)

            loaded = ReportTemplate.load(path)

            assert loaded.name == "test"
            assert loaded.title == "测试报告"


class TestStockReportData:
    """股票报告数据测试"""

    def test_default_data(self):
        """测试默认数据"""
        data = StockReportData(stock_code="600519")

        assert data.stock_code == "600519"
        assert data.current_price is None
        assert data.overall_score is None

    def test_full_data(self):
        """测试完整数据"""
        data = StockReportData(
            stock_code="600519",
            stock_name="贵州茅台",
            current_price=1800.00,
            pe_ratio=35.5,
            roe=0.32,
            overall_score=78.5,
            final_signal="买入",
        )

        assert data.stock_name == "贵州茅台"
        assert data.current_price == 1800.00
        assert data.roe == 0.32


class TestPortfolioReportData:
    """组合报告数据测试"""

    def test_default_data(self):
        """测试默认数据"""
        data = PortfolioReportData()

        assert data.total_stocks == 0
        assert len(data.stocks) == 0

    def test_with_stocks(self):
        """测试包含股票"""
        stocks = [
            StockReportData(stock_code="600519"),
            StockReportData(stock_code="000858"),
        ]

        data = PortfolioReportData(
            report_id="TEST-001",
            stocks=stocks,
            total_stocks=2,
            buy_count=1,
        )

        assert len(data.stocks) == 2
        assert data.total_stocks == 2
        assert data.buy_count == 1


class TestReportManager:
    """报告管理器测试"""

    def test_init_default_template(self):
        """测试默认模板初始化"""
        manager = ReportManager()

        assert manager.template is not None
        assert manager.template.name == "default"

    def test_init_custom_template(self):
        """测试自定义模板初始化"""
        template = ReportTemplate(name="custom")
        manager = ReportManager(template=template)

        assert manager.template.name == "custom"

    def test_set_template(self):
        """测试设置模板"""
        manager = ReportManager()
        new_template = ReportTemplate(name="new")
        manager.set_template(new_template)

        assert manager.template.name == "new"


class TestPDFGeneration:
    """PDF 生成测试"""

    def test_pdf_generator_available(self):
        """测试 PDF 生成器可用性"""
        if REPORTLAB_AVAILABLE:
            manager = ReportManager()
            assert manager.pdf_generator is not None
        else:
            print("跳过: reportlab 不可用")

    def test_generate_single_stock_pdf(self):
        """测试生成单股 PDF"""
        if not REPORTLAB_AVAILABLE:
            print("跳过: reportlab 不可用")
            return

        data = StockReportData(
            stock_code="600519",
            stock_name="贵州茅台",
            current_price=1800.00,
            overall_score=78.5,
        )

        manager = ReportManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.pdf")
            result = manager.generate_pdf(data, path)

            assert result is True
            assert os.path.exists(path)


class TestExcelGeneration:
    """Excel 生成测试"""

    def test_excel_generator_available(self):
        """测试 Excel 生成器可用性"""
        if OPENPYXL_AVAILABLE:
            manager = ReportManager()
            assert manager.excel_generator is not None
        else:
            print("跳过: openpyxl 不可用")

    def test_generate_single_stock_excel(self):
        """测试生成单股 Excel"""
        if not OPENPYXL_AVAILABLE:
            print("跳过: openpyxl 不可用")
            return

        data = StockReportData(
            stock_code="600519",
            stock_name="贵州茅台",
            current_price=1800.00,
            overall_score=78.5,
        )

        manager = ReportManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.xlsx")
            result = manager.generate_excel(data, path)

            assert result is True
            assert os.path.exists(path)

    def test_generate_portfolio_excel(self):
        """测试生成组合 Excel"""
        if not OPENPYXL_AVAILABLE:
            print("跳过: openpyxl 不可用")
            return

        stocks = [
            StockReportData(stock_code="600519", final_signal="买入"),
            StockReportData(stock_code="000858", final_signal="持有"),
        ]

        data = PortfolioReportData(
            report_id="TEST-001",
            stocks=stocks,
            total_stocks=2,
        )

        manager = ReportManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "portfolio.xlsx")
            result = manager.generate_portfolio_excel(data, path)

            assert result is True
            assert os.path.exists(path)
