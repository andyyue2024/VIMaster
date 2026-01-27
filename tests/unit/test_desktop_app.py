"""
PC 客户端模块单元测试
"""
import pytest
import sys
import os

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 检查 PyQt6 是否可用
from src.desktop.app import PYQT_AVAILABLE

# 如果 PyQt6 可用，跳过条件
pytestmark = pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt6 不可用")


class TestDesktopImports:
    """测试桌面应用模块导入"""

    def test_pyqt_availability_flag(self):
        """测试 PYQT_AVAILABLE 标志"""
        from src.desktop.app import PYQT_AVAILABLE
        assert isinstance(PYQT_AVAILABLE, bool)

    def test_import_main_window(self):
        """测试 MainWindow 导入"""
        from src.desktop.app import MainWindow
        assert MainWindow is not None

    def test_import_stock_analysis_panel(self):
        """测试 StockAnalysisPanel 导入"""
        from src.desktop.app import StockAnalysisPanel
        assert StockAnalysisPanel is not None

    def test_import_portfolio_panel(self):
        """测试 PortfolioPanel 导入"""
        from src.desktop.app import PortfolioPanel
        assert PortfolioPanel is not None

    def test_import_masters_panel(self):
        """测试 MastersPanel 导入"""
        from src.desktop.app import MastersPanel
        assert MastersPanel is not None

    def test_import_experts_panel(self):
        """测试 ExpertsPanel 导入"""
        from src.desktop.app import ExpertsPanel
        assert ExpertsPanel is not None

    def test_import_reports_panel(self):
        """测试 ReportsPanel 导入"""
        from src.desktop.app import ReportsPanel
        assert ReportsPanel is not None

    def test_import_history_panel(self):
        """测试 HistoryPanel 导入"""
        from src.desktop.app import HistoryPanel
        assert HistoryPanel is not None

    def test_import_settings_panel(self):
        """测试 SettingsPanel 导入"""
        from src.desktop.app import SettingsPanel
        assert SettingsPanel is not None

    def test_import_llm_analysis_worker(self):
        """测试 LLMAnalysisWorker 导入"""
        from src.desktop.app import LLMAnalysisWorker
        assert LLMAnalysisWorker is not None


class TestDesktopRunFunction:
    """测试桌面应用运行函数"""

    def test_run_desktop_app_exists(self):
        """测试 run_desktop_app 函数存在"""
        from src.desktop.app import run_desktop_app
        assert callable(run_desktop_app)


class TestPyQtAvailability:
    """测试 PyQt6 可用性（无需跳过）"""

    @pytest.mark.skipif(False, reason="始终运行")
    def test_pyqt_availability_is_boolean(self):
        """测试 PYQT_AVAILABLE 是布尔值"""
        from src.desktop.app import PYQT_AVAILABLE
        assert isinstance(PYQT_AVAILABLE, bool)

