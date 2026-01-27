"""desktop 包初始化"""
from src.desktop.app import (
    run_desktop_app,
    PYQT_AVAILABLE,
)

# 仅在 PyQt6 可用时导出类
if PYQT_AVAILABLE:
    from src.desktop.app import (
        MainWindow,
        StockAnalysisPanel,
        PortfolioPanel,
        HistoryPanel,
        SettingsPanel,
        AnalysisWorker,
        SignalLabel,
        ScoreBar,
    )

    __all__ = [
        "run_desktop_app",
        "PYQT_AVAILABLE",
        "MainWindow",
        "StockAnalysisPanel",
        "PortfolioPanel",
        "HistoryPanel",
        "SettingsPanel",
        "AnalysisWorker",
        "SignalLabel",
        "ScoreBar",
    ]
else:
    __all__ = [
        "run_desktop_app",
        "PYQT_AVAILABLE",
    ]
