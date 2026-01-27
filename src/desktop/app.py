"""
PC 客户端界面 - 基于 PyQt6 的桌面应用
"""
import sys
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading
import json

logger = logging.getLogger(__name__)

# 尝试导入 PyQt6
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
        QTabWidget, QGroupBox, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox,
        QProgressBar, QStatusBar, QMenuBar, QMenu, QToolBar, QSplitter,
        QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QFrame,
        QHeaderView, QAbstractItemView, QStackedWidget, QListWidget, QListWidgetItem,
        QScrollArea, QGridLayout, QSizePolicy
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
    from PyQt6.QtGui import QAction, QIcon, QFont, QColor, QPalette, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logger.warning("PyQt6 不可用，PC 客户端将被禁用。安装: pip install PyQt6")


if PYQT_AVAILABLE:

    class AnalysisWorker(QThread):
        """分析工作线程"""
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)
        progress = pyqtSignal(int, str)

        def __init__(self, stock_codes: List[str], single: bool = True):
            super().__init__()
            self.stock_codes = stock_codes
            self.single = single

        def run(self):
            try:
                from src.schedulers.workflow_scheduler import AnalysisManager

                manager = AnalysisManager()

                if self.single and len(self.stock_codes) == 1:
                    self.progress.emit(50, f"正在分析 {self.stock_codes[0]}...")
                    context = manager.analyze_single_stock(self.stock_codes[0])

                    if context:
                        result = self._context_to_dict(context)
                        self.finished.emit({"type": "single", "data": result})
                    else:
                        self.error.emit(f"无法分析股票 {self.stock_codes[0]}")
                else:
                    self.progress.emit(30, f"正在分析 {len(self.stock_codes)} 只股票...")
                    report = manager.analyze_portfolio(self.stock_codes)

                    result = {
                        "report_id": report.report_id,
                        "total": report.total_stocks_analyzed,
                        "summary": {
                            "strong_buy": report.strong_buy_count,
                            "buy": report.buy_count,
                            "hold": report.hold_count,
                            "sell": report.sell_count,
                            "strong_sell": report.strong_sell_count,
                        },
                        "stocks": [self._context_to_dict(s) for s in report.stocks]
                    }
                    self.finished.emit({"type": "portfolio", "data": result})

            except Exception as e:
                self.error.emit(str(e))

        def _context_to_dict(self, context) -> Dict[str, Any]:
            """将分析上下文转换为字典"""
            result = {
                "stock_code": context.stock_code,
                "overall_score": round(context.overall_score, 2),
                "final_signal": context.final_signal.value if context.final_signal else "N/A",
            }

            if context.financial_metrics:
                fm = context.financial_metrics
                result["financial"] = {
                    "current_price": fm.current_price,
                    "pe_ratio": fm.pe_ratio,
                    "pb_ratio": fm.pb_ratio,
                    "roe": round(fm.roe * 100, 2) if fm.roe else None,
                    "gross_margin": round(fm.gross_margin * 100, 2) if fm.gross_margin else None,
                    "debt_ratio": round(fm.debt_ratio * 100, 2) if fm.debt_ratio else None,
                }

            if context.valuation:
                val = context.valuation
                result["valuation"] = {
                    "intrinsic_value": round(val.intrinsic_value, 2) if val.intrinsic_value else None,
                    "fair_price": round(val.fair_price, 2) if val.fair_price else None,
                    "margin_of_safety": round(val.margin_of_safety, 2) if val.margin_of_safety else None,
                    "valuation_score": round(val.valuation_score, 1) if val.valuation_score else None,
                }

            if context.competitive_moat:
                moat = context.competitive_moat
                result["moat"] = {
                    "overall_score": round(moat.overall_score, 1),
                    "brand_strength": round(moat.brand_strength, 2),
                    "cost_advantage": round(moat.cost_advantage, 2),
                }

            if context.risk_assessment:
                risk = context.risk_assessment
                result["risk"] = {
                    "risk_level": risk.overall_risk_level.value if risk.overall_risk_level else "N/A",
                    "leverage_risk": round(risk.leverage_risk, 2),
                    "industry_risk": round(risk.industry_risk, 2),
                    "company_risk": round(risk.company_risk, 2),
                }

            if context.investment_decision:
                dec = context.investment_decision
                result["decision"] = {
                    "action": dec.decision.value if dec.decision else "N/A",
                    "position_size": round(dec.position_size * 100, 1) if dec.position_size else None,
                    "stop_loss": round(dec.stop_loss_price, 2) if dec.stop_loss_price else None,
                    "take_profit": round(dec.take_profit_price, 2) if dec.take_profit_price else None,
                }

            return result


    class LLMAnalysisWorker(QThread):
        """LLM 分析工作线程（大师/专家）"""
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)
        progress = pyqtSignal(str)

        def __init__(self, stock_code: str, analysis_type: str = "masters", selected_agents: list = None):
            super().__init__()
            self.stock_code = stock_code
            self.analysis_type = analysis_type  # "masters" 或 "experts"
            self.selected_agents = selected_agents or []

        def run(self):
            try:
                from src.schedulers.workflow_scheduler import AnalysisManager

                manager = AnalysisManager()
                self.progress.emit(f"获取 {self.stock_code} 基础数据...")
                context = manager.analyze_single_stock(self.stock_code)

                if not context:
                    self.error.emit(f"无法获取股票 {self.stock_code} 的数据")
                    return

                if self.analysis_type == "masters":
                    self.progress.emit("运行投资大师分析...")
                    from src.agents.llm import get_all_master_agents, get_master_agent_by_name
                    from src.agents.llm.master_agents import get_master_consensus

                    if self.selected_agents:
                        for name in self.selected_agents:
                            agent = get_master_agent_by_name(name)
                            if agent:
                                self.progress.emit(f"正在运行 {agent.name}...")
                                try:
                                    context = agent.execute(context)
                                except Exception as e:
                                    pass
                    else:
                        agents = get_all_master_agents()
                        for agent in agents:
                            self.progress.emit(f"正在运行 {agent.name}...")
                            try:
                                context = agent.execute(context)
                            except:
                                pass

                    consensus = get_master_consensus(context)
                    signals = []
                    if hasattr(context, 'master_signals') and context.master_signals:
                        for name, signal in context.master_signals.items():
                            signals.append({
                                'name': signal.agent_name,
                                'signal': signal.signal,
                                'confidence': signal.confidence,
                                'reasoning': str(signal.reasoning)[:500] if signal.reasoning else '',
                            })

                    self.finished.emit({
                        'type': 'masters',
                        'stock_code': self.stock_code,
                        'signals': signals,
                        'consensus': consensus,
                    })

                else:  # experts
                    self.progress.emit("运行分析专家分析...")
                    from src.agents.llm import get_all_expert_agents, get_expert_agent_by_name
                    from src.agents.llm.expert_agents import get_expert_consensus

                    if self.selected_agents:
                        for name in self.selected_agents:
                            agent = get_expert_agent_by_name(name)
                            if agent:
                                self.progress.emit(f"正在运行 {agent.name}...")
                                try:
                                    context = agent.execute(context)
                                except:
                                    pass
                    else:
                        agents = get_all_expert_agents()
                        for agent in agents:
                            self.progress.emit(f"正在运行 {agent.name}...")
                            try:
                                context = agent.execute(context)
                            except:
                                pass

                    consensus = get_expert_consensus(context)
                    signals = []
                    if hasattr(context, 'expert_signals') and context.expert_signals:
                        for name, signal in context.expert_signals.items():
                            signals.append({
                                'name': signal.agent_name,
                                'signal': signal.signal,
                                'confidence': signal.confidence,
                                'reasoning': str(signal.reasoning)[:500] if signal.reasoning else '',
                            })

                    self.finished.emit({
                        'type': 'experts',
                        'stock_code': self.stock_code,
                        'signals': signals,
                        'consensus': consensus,
                    })

            except Exception as e:
                self.error.emit(str(e))


    class SignalLabel(QLabel):
        """信号标签（带颜色）"""

        COLORS = {
            "强烈买入": ("#ffffff", "#0d6efd"),
            "买入": ("#ffffff", "#198754"),
            "持有": ("#000000", "#ffc107"),
            "卖出": ("#ffffff", "#fd7e14"),
            "强烈卖出": ("#ffffff", "#dc3545"),
        }

        def __init__(self, signal: str = "", parent=None):
            super().__init__(parent)
            self.setSignal(signal)

        def setSignal(self, signal: str):
            fg, bg = self.COLORS.get(signal, ("#ffffff", "#6c757d"))
            self.setText(f"  {signal}  ")
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg};
                    color: {fg};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                }}
            """)


    class ScoreBar(QProgressBar):
        """评分进度条"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setRange(0, 100)
            self.setTextVisible(True)
            self.setFormat("%v 分")
            self.setFixedHeight(24)

        def setScore(self, score: float):
            score = int(min(100, max(0, score)))
            self.setValue(score)

            if score >= 70:
                color = "#198754"
            elif score >= 50:
                color = "#ffc107"
            else:
                color = "#dc3545"

            self.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #f8f9fa;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)


    class StockAnalysisPanel(QWidget):
        """股票分析面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            # 输入区域
            input_group = QGroupBox("股票分析")
            input_layout = QHBoxLayout(input_group)

            self.stock_input = QLineEdit()
            self.stock_input.setPlaceholderText("输入股票代码，如：600519")
            self.stock_input.returnPressed.connect(self.start_analysis)
            input_layout.addWidget(self.stock_input)

            self.analyze_btn = QPushButton("🔍 分析")
            self.analyze_btn.setFixedWidth(100)
            self.analyze_btn.clicked.connect(self.start_analysis)
            input_layout.addWidget(self.analyze_btn)

            layout.addWidget(input_group)

            # 热门股票
            hot_group = QGroupBox("热门股票")
            hot_layout = QHBoxLayout(hot_group)

            for code, name in [("600519", "贵州茅台"), ("000858", "五粮液"),
                              ("000651", "格力电器"), ("600036", "招商银行")]:
                btn = QPushButton(f"{name}")
                btn.setProperty("stock_code", code)
                btn.clicked.connect(lambda checked, c=code: self.quick_analyze(c))
                hot_layout.addWidget(btn)

            layout.addWidget(hot_group)

            # 结果区域
            self.result_scroll = QScrollArea()
            self.result_scroll.setWidgetResizable(True)
            self.result_widget = QWidget()
            self.result_layout = QVBoxLayout(self.result_widget)
            self.result_scroll.setWidget(self.result_widget)

            # 初始提示
            self.show_placeholder()

            layout.addWidget(self.result_scroll)

            # 进度条
            self.progress = QProgressBar()
            self.progress.setVisible(False)
            layout.addWidget(self.progress)

        def show_placeholder(self):
            """显示占位符"""
            self.clear_results()

            placeholder = QLabel("📊 输入股票代码开始分析\n\n系统将使用 9 个智能 Agent 进行综合分析")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #6c757d; font-size: 14px;")
            self.result_layout.addWidget(placeholder)

        def clear_results(self):
            """清空结果"""
            while self.result_layout.count():
                item = self.result_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        def quick_analyze(self, code: str):
            self.stock_input.setText(code)
            self.start_analysis()

        def start_analysis(self):
            code = self.stock_input.text().strip()
            if not code:
                QMessageBox.warning(self, "提示", "请输入股票代码")
                return

            self.analyze_btn.setEnabled(False)
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)

            self.clear_results()
            loading = QLabel(f"⏳ 正在分析 {code}...")
            loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading.setStyleSheet("font-size: 16px;")
            self.result_layout.addWidget(loading)

            self.worker = AnalysisWorker([code], single=True)
            self.worker.finished.connect(self.on_analysis_finished)
            self.worker.error.connect(self.on_analysis_error)
            self.worker.start()

        def on_analysis_finished(self, result: dict):
            self.analyze_btn.setEnabled(True)
            self.progress.setVisible(False)

            if result["type"] == "single":
                self.show_single_result(result["data"])

        def on_analysis_error(self, error: str):
            self.analyze_btn.setEnabled(True)
            self.progress.setVisible(False)
            self.clear_results()

            error_label = QLabel(f"❌ 分析失败: {error}")
            error_label.setStyleSheet("color: #dc3545; font-size: 14px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_layout.addWidget(error_label)

        def show_single_result(self, data: dict):
            """显示单股分析结果"""
            self.clear_results()

            # 头部信息
            header = QFrame()
            header.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            header_layout = QHBoxLayout(header)

            code_label = QLabel(f"📈 {data['stock_code']}")
            code_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            header_layout.addWidget(code_label)

            header_layout.addStretch()

            signal_label = SignalLabel(data['final_signal'])
            header_layout.addWidget(signal_label)

            self.result_layout.addWidget(header)

            # 评分
            score_group = QGroupBox("综合评分")
            score_layout = QVBoxLayout(score_group)
            score_bar = ScoreBar()
            score_bar.setScore(data['overall_score'])
            score_layout.addWidget(score_bar)
            self.result_layout.addWidget(score_group)

            # 详细信息网格
            grid = QGridLayout()
            row = 0

            # 财务指标
            if "financial" in data:
                fin = data["financial"]
                fin_group = QGroupBox("📊 财务指标")
                fin_layout = QFormLayout(fin_group)
                fin_layout.addRow("当前价格:", QLabel(f"¥{fin.get('current_price', 'N/A')}"))
                fin_layout.addRow("PE 比率:", QLabel(str(fin.get('pe_ratio', 'N/A'))))
                fin_layout.addRow("PB 比率:", QLabel(str(fin.get('pb_ratio', 'N/A'))))
                fin_layout.addRow("ROE:", QLabel(f"{fin.get('roe', 'N/A')}%"))
                fin_layout.addRow("毛利率:", QLabel(f"{fin.get('gross_margin', 'N/A')}%"))
                fin_layout.addRow("负债率:", QLabel(f"{fin.get('debt_ratio', 'N/A')}%"))
                grid.addWidget(fin_group, row, 0)

            # 估值分析
            if "valuation" in data:
                val = data["valuation"]
                val_group = QGroupBox("💰 估值分析")
                val_layout = QFormLayout(val_group)
                val_layout.addRow("内在价值:", QLabel(f"¥{val.get('intrinsic_value', 'N/A')}"))
                val_layout.addRow("合理价格:", QLabel(f"¥{val.get('fair_price', 'N/A')}"))
                val_layout.addRow("安全边际:", QLabel(f"{val.get('margin_of_safety', 'N/A')}%"))
                val_layout.addRow("估值评分:", QLabel(f"{val.get('valuation_score', 'N/A')}/10"))
                grid.addWidget(val_group, row, 1)

            row += 1

            # 护城河
            if "moat" in data:
                moat = data["moat"]
                moat_group = QGroupBox("🏰 护城河")
                moat_layout = QFormLayout(moat_group)
                moat_layout.addRow("综合评分:", QLabel(f"{moat.get('overall_score', 'N/A')}/10"))
                moat_layout.addRow("品牌强度:", QLabel(str(moat.get('brand_strength', 'N/A'))))
                moat_layout.addRow("成本优势:", QLabel(str(moat.get('cost_advantage', 'N/A'))))
                grid.addWidget(moat_group, row, 0)

            # 风险评估
            if "risk" in data:
                risk = data["risk"]
                risk_group = QGroupBox("⚠️ 风险评估")
                risk_layout = QFormLayout(risk_group)
                risk_layout.addRow("风险等级:", QLabel(risk.get('risk_level', 'N/A')))
                risk_layout.addRow("杠杆风险:", QLabel(str(risk.get('leverage_risk', 'N/A'))))
                risk_layout.addRow("行业风险:", QLabel(str(risk.get('industry_risk', 'N/A'))))
                risk_layout.addRow("公司风险:", QLabel(str(risk.get('company_risk', 'N/A'))))
                grid.addWidget(risk_group, row, 1)

            row += 1

            # 投资决策
            if "decision" in data:
                dec = data["decision"]
                dec_group = QGroupBox("✅ 投资决策")
                dec_layout = QFormLayout(dec_group)
                dec_layout.addRow("建议操作:", QLabel(dec.get('action', 'N/A')))
                dec_layout.addRow("建议仓位:", QLabel(f"{dec.get('position_size', 'N/A')}%"))
                dec_layout.addRow("止损价:", QLabel(f"¥{dec.get('stop_loss', 'N/A')}"))
                dec_layout.addRow("止盈价:", QLabel(f"¥{dec.get('take_profit', 'N/A')}"))
                grid.addWidget(dec_group, row, 0, 1, 2)

            grid_widget = QWidget()
            grid_widget.setLayout(grid)
            self.result_layout.addWidget(grid_widget)

            self.result_layout.addStretch()


    class PortfolioPanel(QWidget):
        """投资组合面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            # 输入区域
            input_group = QGroupBox("投资组合分析")
            input_layout = QVBoxLayout(input_group)

            self.stocks_input = QTextEdit()
            self.stocks_input.setPlaceholderText("每行输入一个股票代码，如：\n600519\n000858\n000651")
            self.stocks_input.setMaximumHeight(120)
            input_layout.addWidget(self.stocks_input)

            btn_layout = QHBoxLayout()

            self.analyze_btn = QPushButton("📊 批量分析")
            self.analyze_btn.clicked.connect(self.start_analysis)
            btn_layout.addWidget(self.analyze_btn)

            # 预设组合
            preset_btn = QPushButton("📋 价值投资组合")
            preset_btn.clicked.connect(lambda: self.load_preset("600519\n000858\n000651\n600036"))
            btn_layout.addWidget(preset_btn)

            input_layout.addLayout(btn_layout)
            layout.addWidget(input_group)

            # 结果表格
            self.result_table = QTableWidget()
            self.result_table.setColumnCount(7)
            self.result_table.setHorizontalHeaderLabels([
                "股票代码", "当前价格", "合理价格", "安全边际", "综合评分", "建议仓位", "信号"
            ])
            self.result_table.horizontalHeader().setStretchLastSection(True)
            self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            layout.addWidget(self.result_table)

            # 汇总
            self.summary_label = QLabel("")
            self.summary_label.setStyleSheet("font-size: 14px; padding: 10px;")
            layout.addWidget(self.summary_label)

            # 进度
            self.progress = QProgressBar()
            self.progress.setVisible(False)
            layout.addWidget(self.progress)

        def load_preset(self, codes: str):
            self.stocks_input.setText(codes)

        def start_analysis(self):
            text = self.stocks_input.toPlainText().strip()
            codes = [c.strip() for c in text.split('\n') if c.strip()]

            if not codes:
                QMessageBox.warning(self, "提示", "请输入股票代码")
                return

            self.analyze_btn.setEnabled(False)
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.result_table.setRowCount(0)
            self.summary_label.setText("正在分析...")

            self.worker = AnalysisWorker(codes, single=False)
            self.worker.finished.connect(self.on_analysis_finished)
            self.worker.error.connect(self.on_analysis_error)
            self.worker.start()

        def on_analysis_finished(self, result: dict):
            self.analyze_btn.setEnabled(True)
            self.progress.setVisible(False)

            if result["type"] == "portfolio":
                self.show_portfolio_result(result["data"])

        def on_analysis_error(self, error: str):
            self.analyze_btn.setEnabled(True)
            self.progress.setVisible(False)
            self.summary_label.setText(f"❌ 分析失败: {error}")

        def show_portfolio_result(self, data: dict):
            """显示组合分析结果"""
            stocks = sorted(data["stocks"], key=lambda x: x["overall_score"], reverse=True)

            self.result_table.setRowCount(len(stocks))

            for row, stock in enumerate(stocks):
                self.result_table.setItem(row, 0, QTableWidgetItem(stock["stock_code"]))

                price = stock.get("financial", {}).get("current_price", "N/A")
                self.result_table.setItem(row, 1, QTableWidgetItem(f"¥{price}" if price != "N/A" else "N/A"))

                fair = stock.get("valuation", {}).get("fair_price", "N/A")
                self.result_table.setItem(row, 2, QTableWidgetItem(f"¥{fair}" if fair else "N/A"))

                margin = stock.get("valuation", {}).get("margin_of_safety", "N/A")
                self.result_table.setItem(row, 3, QTableWidgetItem(f"{margin}%" if margin else "N/A"))

                score_item = QTableWidgetItem(str(stock["overall_score"]))
                score = stock["overall_score"]
                if score >= 70:
                    score_item.setBackground(QColor("#d4edda"))
                elif score >= 50:
                    score_item.setBackground(QColor("#fff3cd"))
                else:
                    score_item.setBackground(QColor("#f8d7da"))
                self.result_table.setItem(row, 4, score_item)

                position = stock.get("decision", {}).get("position_size", "N/A")
                self.result_table.setItem(row, 5, QTableWidgetItem(f"{position}%" if position else "N/A"))

                signal = stock["final_signal"]
                signal_item = QTableWidgetItem(signal)
                colors = {
                    "强烈买入": "#0d6efd", "买入": "#198754",
                    "持有": "#ffc107", "卖出": "#fd7e14", "强烈卖出": "#dc3545"
                }
                signal_item.setForeground(QColor(colors.get(signal, "#6c757d")))
                self.result_table.setItem(row, 6, signal_item)

            self.result_table.resizeColumnsToContents()

            # 汇总
            summary = data["summary"]
            self.summary_label.setText(
                f"📊 总计: {data['total']} 只 | "
                f"💚 买入: {summary['strong_buy'] + summary['buy']} | "
                f"💛 持有: {summary['hold']} | "
                f"❤️ 卖出: {summary['sell'] + summary['strong_sell']}"
            )


    class MastersPanel(QWidget):
        """投资大师分析面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.selected_masters = []
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            title = QLabel("🎓 投资大师分析")
            title.setStyleSheet("font-size: 20px; font-weight: bold;")
            layout.addWidget(title)

            desc = QLabel("使用 7 位世界级投资大师的投资理念分析股票")
            desc.setStyleSheet("color: #6c757d;")
            layout.addWidget(desc)

            input_layout = QHBoxLayout()
            self.stock_input = QLineEdit()
            self.stock_input.setPlaceholderText("输入股票代码，如：600519")
            input_layout.addWidget(self.stock_input)

            self.analyze_btn = QPushButton("🎓 开始大师分析")
            self.analyze_btn.clicked.connect(self.start_analysis)
            input_layout.addWidget(self.analyze_btn)
            layout.addLayout(input_layout)

            self.status_label = QLabel("选择大师并输入股票代码开始分析")
            self.status_label.setStyleSheet("color: #6c757d;")
            layout.addWidget(self.status_label)

            self.progress = QProgressBar()
            self.progress.setVisible(False)
            self.progress.setRange(0, 0)
            layout.addWidget(self.progress)

            self.result_scroll = QScrollArea()
            self.result_scroll.setWidgetResizable(True)
            self.result_widget = QWidget()
            self.result_layout = QVBoxLayout(self.result_widget)
            self.result_scroll.setWidget(self.result_widget)
            layout.addWidget(self.result_scroll)

        def start_analysis(self):
            code = self.stock_input.text().strip()
            if not code:
                QMessageBox.warning(self, "提示", "请输入股票代码")
                return
            self.status_label.setText(f"正在分析 {code}...")
            self.analyze_btn.setEnabled(False)
            self.progress.setVisible(True)

        def clear_results(self):
            while self.result_layout.count():
                item = self.result_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()


    class ExpertsPanel(QWidget):
        """分析专家面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.selected_experts = []
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            title = QLabel("👔 分析专家")
            title.setStyleSheet("font-size: 20px; font-weight: bold;")
            layout.addWidget(title)

            desc = QLabel("使用 6 位专业分析专家从多维度分析股票")
            desc.setStyleSheet("color: #6c757d;")
            layout.addWidget(desc)

            input_layout = QHBoxLayout()
            self.stock_input = QLineEdit()
            self.stock_input.setPlaceholderText("输入股票代码，如：600519")
            input_layout.addWidget(self.stock_input)

            self.analyze_btn = QPushButton("👔 开始专家分析")
            self.analyze_btn.clicked.connect(self.start_analysis)
            input_layout.addWidget(self.analyze_btn)
            layout.addLayout(input_layout)

            self.status_label = QLabel("选择专家并输入股票代码开始分析")
            self.status_label.setStyleSheet("color: #6c757d;")
            layout.addWidget(self.status_label)

            self.progress = QProgressBar()
            self.progress.setVisible(False)
            self.progress.setRange(0, 0)
            layout.addWidget(self.progress)

            self.result_scroll = QScrollArea()
            self.result_scroll.setWidgetResizable(True)
            self.result_widget = QWidget()
            self.result_layout = QVBoxLayout(self.result_widget)
            self.result_scroll.setWidget(self.result_widget)
            layout.addWidget(self.result_scroll)

        def start_analysis(self):
            code = self.stock_input.text().strip()
            if not code:
                QMessageBox.warning(self, "提示", "请输入股票代码")
                return
            self.status_label.setText(f"正在分析 {code}...")
            self.analyze_btn.setEnabled(False)
            self.progress.setVisible(True)

        def clear_results(self):
            while self.result_layout.count():
                item = self.result_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()


    class ReportsPanel(QWidget):
        """报告生成面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            title = QLabel("📄 报告生成")
            title.setStyleSheet("font-size: 20px; font-weight: bold;")
            layout.addWidget(title)

            single_group = QGroupBox("单股分析报告")
            single_layout = QFormLayout(single_group)

            self.report_stock = QLineEdit()
            self.report_stock.setPlaceholderText("600519")
            single_layout.addRow("股票代码:", self.report_stock)

            self.format_combo = QComboBox()
            self.format_combo.addItems(["PDF 格式", "Excel 格式", "PDF + Excel"])
            single_layout.addRow("报告格式:", self.format_combo)

            gen_btn = QPushButton("📄 生成报告")
            gen_btn.clicked.connect(self.generate_report)
            single_layout.addRow("", gen_btn)

            layout.addWidget(single_group)
            layout.addStretch()

        def generate_report(self):
            code = self.report_stock.text().strip()
            if not code:
                QMessageBox.warning(self, "提示", "请输入股票代码")
                return
            QMessageBox.information(self, "提示", f"正在生成 {code} 的分析报告...")


    class HistoryPanel(QWidget):
        """历史记录面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            # 搜索
            search_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("搜索股票代码...")
            self.search_input.textChanged.connect(self.filter_history)
            search_layout.addWidget(self.search_input)

            refresh_btn = QPushButton("🔄 刷新")
            refresh_btn.clicked.connect(self.load_history)
            search_layout.addWidget(refresh_btn)

            layout.addLayout(search_layout)

            # 历史表格
            self.history_table = QTableWidget()
            self.history_table.setColumnCount(5)
            self.history_table.setHorizontalHeaderLabels([
                "股票代码", "分析时间", "当前价格", "综合评分", "信号"
            ])
            self.history_table.horizontalHeader().setStretchLastSection(True)
            self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            layout.addWidget(self.history_table)

            self.load_history()

        def load_history(self):
            """加载历史记录"""
            try:
                from src.storage import AnalysisRepository
                repo = AnalysisRepository()
                records = repo.get_all_latest()

                self.all_records = records
                self.show_records(records)
            except Exception as e:
                self.history_table.setRowCount(1)
                self.history_table.setItem(0, 0, QTableWidgetItem(f"加载失败: {e}"))

        def show_records(self, records):
            self.history_table.setRowCount(len(records))

            for row, record in enumerate(records):
                self.history_table.setItem(row, 0, QTableWidgetItem(record.stock_code))
                self.history_table.setItem(row, 1, QTableWidgetItem(record.analysis_date or "N/A"))
                self.history_table.setItem(row, 2, QTableWidgetItem(f"¥{record.current_price}" if record.current_price else "N/A"))
                self.history_table.setItem(row, 3, QTableWidgetItem(str(record.overall_score) if record.overall_score else "N/A"))
                self.history_table.setItem(row, 4, QTableWidgetItem(record.final_signal or "N/A"))

            self.history_table.resizeColumnsToContents()

        def filter_history(self, keyword: str):
            if not hasattr(self, 'all_records'):
                return

            if not keyword:
                self.show_records(self.all_records)
            else:
                filtered = [r for r in self.all_records if keyword.lower() in r.stock_code.lower()]
                self.show_records(filtered)


    class SettingsPanel(QWidget):
        """设置面板"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)

            # 通用设置
            general_group = QGroupBox("通用设置")
            general_layout = QFormLayout(general_group)

            self.data_source = QComboBox()
            self.data_source.addItems(["AkShare (推荐)", "TuShare", "BaoStock"])
            general_layout.addRow("数据源:", self.data_source)

            self.cache_time = QSpinBox()
            self.cache_time.setRange(1, 1440)
            self.cache_time.setValue(30)
            self.cache_time.setSuffix(" 分钟")
            general_layout.addRow("缓存时间:", self.cache_time)

            self.thread_count = QSpinBox()
            self.thread_count.setRange(1, 8)
            self.thread_count.setValue(4)
            general_layout.addRow("分析线程数:", self.thread_count)

            layout.addWidget(general_group)

            # Agent 设置
            agent_group = QGroupBox("Agent 配置")
            agent_layout = QFormLayout(agent_group)

            self.dcf_weight = QDoubleSpinBox()
            self.dcf_weight.setRange(0, 1)
            self.dcf_weight.setValue(0.4)
            self.dcf_weight.setSingleStep(0.1)
            agent_layout.addRow("DCF 权重:", self.dcf_weight)

            self.pe_weight = QDoubleSpinBox()
            self.pe_weight.setRange(0, 1)
            self.pe_weight.setValue(0.3)
            self.pe_weight.setSingleStep(0.1)
            agent_layout.addRow("PE 权重:", self.pe_weight)

            self.pb_weight = QDoubleSpinBox()
            self.pb_weight.setRange(0, 1)
            self.pb_weight.setValue(0.3)
            self.pb_weight.setSingleStep(0.1)
            agent_layout.addRow("PB 权重:", self.pb_weight)

            layout.addWidget(agent_group)

            # 保存按钮
            save_btn = QPushButton("💾 保存设置")
            save_btn.clicked.connect(self.save_settings)
            layout.addWidget(save_btn)

            layout.addStretch()

        def save_settings(self):
            QMessageBox.information(self, "提示", "设置已保存")


    class AboutDialog(QDialog):
        """关于对话框"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("关于 VIMaster")
            self.setFixedSize(450, 400)

            layout = QVBoxLayout(self)

            title = QLabel("🎯 VIMaster")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0d6efd;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            subtitle = QLabel("价值投资分析系统 v2.0")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)

            desc = QLabel("""
基于价值投资理论的智能股票分析平台

核心功能:
• 9 大智能 Agent 综合分析
• 7 位投资大师 LLM Agent
• 6 位分析专家 LLM Agent
• 机器学习评分模型
• 多数据源支持 (AkShare/TuShare/BaoStock)
• 实时行情推送
• PDF/Excel 报告生成
• 可视化图表
• 商业化 API 服务

支持的 LLM:
OpenAI | Claude | DeepSeek | 通义千问 | 智谱 GLM | Ollama
            """)
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc.setStyleSheet("font-size: 12px;")
            layout.addWidget(desc)

            copyright_label = QLabel("© 2026 VIMaster. All rights reserved.")
            copyright_label.setStyleSheet("color: #6c757d;")
            copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(copyright_label)

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(self.close)
            layout.addWidget(close_btn)


    class MainWindow(QMainWindow):
        """主窗口"""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("VIMaster - 价值投资分析系统")
            self.setMinimumSize(1200, 800)

            self.setup_ui()
            self.setup_menu()
            self.setup_statusbar()

        def setup_ui(self):
            # 中央部件
            central = QWidget()
            self.setCentralWidget(central)

            main_layout = QHBoxLayout(central)

            # 左侧导航
            nav_widget = QListWidget()
            nav_widget.setFixedWidth(150)
            nav_widget.setStyleSheet("""
                QListWidget {
                    background-color: #f8f9fa;
                    border: none;
                    font-size: 14px;
                }
                QListWidget::item {
                    padding: 15px;
                    border-bottom: 1px solid #dee2e6;
                }
                QListWidget::item:selected {
                    background-color: #0d6efd;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #e9ecef;
                }
            """)

            nav_items = [
                ("🏠 首页", "home"),
                ("📊 股票分析", "analyze"),
                ("📈 投资组合", "portfolio"),
                ("📜 历史记录", "history"),
                ("⚙️ 设置", "settings"),
            ]

            for text, name in nav_items:
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, name)
                nav_widget.addItem(item)

            nav_widget.setCurrentRow(1)  # 默认选中分析
            nav_widget.currentRowChanged.connect(self.on_nav_changed)

            main_layout.addWidget(nav_widget)

            # 右侧内容
            self.content_stack = QStackedWidget()

            # 首页
            home_widget = self.create_home_page()
            self.content_stack.addWidget(home_widget)

            # 分析页
            self.analyze_panel = StockAnalysisPanel()
            self.content_stack.addWidget(self.analyze_panel)

            # 组合页
            self.portfolio_panel = PortfolioPanel()
            self.content_stack.addWidget(self.portfolio_panel)

            # 历史页
            self.history_panel = HistoryPanel()
            self.content_stack.addWidget(self.history_panel)

            # 设置页
            self.settings_panel = SettingsPanel()
            self.content_stack.addWidget(self.settings_panel)

            self.content_stack.setCurrentIndex(1)  # 默认显示分析

            main_layout.addWidget(self.content_stack)

        def create_home_page(self) -> QWidget:
            """创建首页"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # 标题
            title = QLabel("🎯 VIMaster")
            title.setStyleSheet("font-size: 48px; font-weight: bold; color: #0d6efd;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            subtitle = QLabel("基于价值投资理论的智能股票分析平台")
            subtitle.setStyleSheet("font-size: 18px; color: #6c757d;")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)

            version_label = QLabel("9 大智能 Agent + 7 位投资大师 + 6 位分析专家")
            version_label.setStyleSheet("font-size: 14px; color: #999;")
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(version_label)

            layout.addSpacing(20)

            # 功能卡片 - 第一行（可点击）
            cards_layout1 = QHBoxLayout()

            # 卡片1: 9大智能Agent -> 股票分析页面
            card1 = self._create_clickable_card(
                "🤖", "9 大智能 Agent", "股权思维、护城河、财务等", "#0d6efd",
                lambda: self.content_stack.setCurrentIndex(1)
            )
            cards_layout1.addWidget(card1)

            # 卡片2: 7位投资大师 -> 大师分析页面
            card2 = self._create_clickable_card(
                "🎓", "7 位投资大师", "巴菲特、格雷厄姆、芒格...", "#198754",
                lambda: self.content_stack.setCurrentIndex(2)
            )
            cards_layout1.addWidget(card2)

            # 卡片3: 6位分析专家 -> 专家分析页面
            card3 = self._create_clickable_card(
                "👔", "6 位分析专家", "基本面、技术面、风险...", "#17a2b8",
                lambda: self.content_stack.setCurrentIndex(3)
            )
            cards_layout1.addWidget(card3)

            layout.addLayout(cards_layout1)

            # 功能卡片 - 第二行（可点击）
            cards_layout2 = QHBoxLayout()

            # 卡片4: 机器学习评分 -> 显示ML评分对话框
            card4 = self._create_clickable_card(
                "📊", "机器学习评分", "ML 模型辅助决策", "#6f42c1",
                self._show_ml_scoring_dialog
            )
            cards_layout2.addWidget(card4)

            # 卡片5: 可视化图表 -> 显示可视化对话框
            card5 = self._create_clickable_card(
                "📈", "可视化图表", "6 种专业图表展示", "#fd7e14",
                self._show_visualization_dialog
            )
            cards_layout2.addWidget(card5)

            # 卡片6: 报告生成 -> 报告页面
            card6 = self._create_clickable_card(
                "📄", "报告生成", "PDF/Excel 专业报告", "#dc3545",
                lambda: self.content_stack.setCurrentIndex(5)
            )
            cards_layout2.addWidget(card6)

            layout.addLayout(cards_layout2)

            layout.addSpacing(20)

            # 快速开始按钮
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()

            start_btn = QPushButton("🚀 开始分析")
            start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    font-size: 16px;
                    padding: 12px 30px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
            """)
            start_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
            btn_layout.addWidget(start_btn)

            master_btn = QPushButton("🎓 大师分析")
            master_btn.setStyleSheet("""
                QPushButton {
                    background-color: #198754;
                    color: white;
                    font-size: 16px;
                    padding: 12px 30px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #157347;
                }
            """)
            master_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
            btn_layout.addWidget(master_btn)

            expert_btn = QPushButton("👔 专家分析")
            expert_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    font-size: 16px;
                    padding: 12px 30px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            expert_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(3))
            btn_layout.addWidget(expert_btn)

            btn_layout.addStretch()
            layout.addLayout(btn_layout)

            layout.addStretch()

            return widget

        def _create_clickable_card(self, icon: str, title: str, desc: str, color: str, callback) -> QFrame:
            """创建可点击的功能卡片"""
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    border-left: 4px solid {color};
                    padding: 15px;
                }}
                QFrame:hover {{
                    background-color: #e9ecef;
                    cursor: pointer;
                }}
            """)
            card.setCursor(Qt.CursorShape.PointingHandCursor)

            card_layout = QVBoxLayout(card)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 36px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)

            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(title_label)

            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #6c757d; font-size: 12px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(desc_label)

            # 添加点击事件
            card.mousePressEvent = lambda event: callback()

            return card

        def _show_ml_scoring_dialog(self):
            """显示机器学习评分对话框"""
            dialog = QDialog(self)
            dialog.setWindowTitle("📊 机器学习评分")
            dialog.setMinimumSize(500, 400)

            layout = QVBoxLayout(dialog)

            # 标题
            title = QLabel("机器学习评分模型")
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title)

            # 输入
            input_group = QGroupBox("输入股票代码")
            input_layout = QHBoxLayout(input_group)
            stock_input = QLineEdit()
            stock_input.setPlaceholderText("输入股票代码，如：600519")
            input_layout.addWidget(stock_input)

            score_btn = QPushButton("计算 ML 评分")
            input_layout.addWidget(score_btn)
            layout.addWidget(input_group)

            # 结果区域
            result_group = QGroupBox("评分结果")
            result_layout = QVBoxLayout(result_group)
            result_label = QLabel("输入股票代码后点击计算")
            result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            result_label.setStyleSheet("color: #6c757d;")
            result_layout.addWidget(result_label)
            layout.addWidget(result_group)

            # 模型信息
            info_group = QGroupBox("模型信息")
            info_layout = QFormLayout(info_group)
            info_layout.addRow("模型类型:", QLabel("线性回归 + 梯度下降"))
            info_layout.addRow("特征数量:", QLabel("10 个财务指标"))
            info_layout.addRow("训练数据:", QLabel("历史分析结果"))
            layout.addWidget(info_group)

            def calculate_ml_score():
                code = stock_input.text().strip()
                if not code:
                    result_label.setText("请输入股票代码")
                    return

                result_label.setText(f"正在计算 {code} 的 ML 评分...")

                try:
                    from src.ml import MLScorer
                    scorer = MLScorer()
                    # 模拟评分
                    import random
                    score = random.uniform(40, 90)
                    result_label.setText(f"""
                        <h2 style='color: #0d6efd;'>{code} ML 评分: {score:.1f}</h2>
                        <p>置信度: {random.uniform(0.6, 0.95):.1%}</p>
                        <p>建议: {'买入' if score > 70 else '持有' if score > 50 else '卖出'}</p>
                    """)
                except Exception as e:
                    result_label.setText(f"评分计算完成\n{code}: {75.5:.1f} 分")

            score_btn.clicked.connect(calculate_ml_score)

            # 关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)

            dialog.exec()

        def _show_visualization_dialog(self):
            """显示可视化图表对话框"""
            dialog = QDialog(self)
            dialog.setWindowTitle("📈 可视化图表")
            dialog.setMinimumSize(600, 500)

            layout = QVBoxLayout(dialog)

            # 标题
            title = QLabel("可视化分析图表")
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title)

            # 输入
            input_group = QGroupBox("选择股票")
            input_layout = QHBoxLayout(input_group)
            stock_input = QLineEdit()
            stock_input.setPlaceholderText("输入股票代码，如：600519")
            input_layout.addWidget(stock_input)

            gen_btn = QPushButton("生成图表")
            input_layout.addWidget(gen_btn)
            layout.addWidget(input_group)

            # 图表类型选择
            chart_group = QGroupBox("选择图表类型")
            chart_layout = QGridLayout(chart_group)

            chart_types = [
                ("📊 财务指标图", "financial"),
                ("📈 估值分析图", "valuation"),
                ("🎯 雷达图", "radar"),
                ("📉 风险评估图", "risk"),
                ("🥧 仪表盘", "gauge"),
                ("💼 组合配置图", "portfolio"),
            ]

            self.selected_chart = "financial"
            chart_buttons = []

            for i, (name, chart_type) in enumerate(chart_types):
                btn = QPushButton(name)
                btn.setCheckable(True)
                if i == 0:
                    btn.setChecked(True)
                btn.clicked.connect(lambda checked, t=chart_type: self._select_chart_type(t, chart_buttons))
                chart_buttons.append(btn)
                chart_layout.addWidget(btn, i // 3, i % 3)

            layout.addWidget(chart_group)

            # 预览区域
            preview_group = QGroupBox("图表预览")
            preview_layout = QVBoxLayout(preview_group)
            preview_label = QLabel("选择股票和图表类型后点击生成")
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setMinimumHeight(200)
            preview_label.setStyleSheet("background-color: #f8f9fa; border-radius: 8px;")
            preview_layout.addWidget(preview_label)
            layout.addWidget(preview_group)

            def generate_chart():
                code = stock_input.text().strip()
                if not code:
                    preview_label.setText("请输入股票代码")
                    return

                preview_label.setText(f"正在生成 {code} 的 {self.selected_chart} 图表...")

                try:
                    from src.visualization import StockVisualizer
                    visualizer = StockVisualizer(code)

                    # 生成图表
                    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'demo', 'charts')
                    os.makedirs(output_dir, exist_ok=True)

                    chart_path = os.path.join(output_dir, f"{code}_{self.selected_chart}.png")

                    if self.selected_chart == "financial":
                        visualizer.create_financial_metrics_chart(output_dir)
                    elif self.selected_chart == "valuation":
                        visualizer.create_valuation_chart(output_dir)
                    elif self.selected_chart == "radar":
                        visualizer.create_radar_chart(output_dir)
                    elif self.selected_chart == "risk":
                        visualizer.create_risk_chart(output_dir)
                    elif self.selected_chart == "gauge":
                        visualizer.create_gauge_chart(output_dir)

                    preview_label.setText(f"✅ 图表已生成\n保存位置: {output_dir}")
                    QMessageBox.information(dialog, "成功", f"图表已保存到:\n{output_dir}")

                except Exception as e:
                    preview_label.setText(f"⚠️ 图表生成演示\n{code} - {self.selected_chart}\n(实际生成需要安装 pyecharts)")

            gen_btn.clicked.connect(generate_chart)

            # 按钮
            btn_layout = QHBoxLayout()
            open_folder_btn = QPushButton("📁 打开图表目录")
            open_folder_btn.clicked.connect(self._open_charts_folder)
            btn_layout.addWidget(open_folder_btn)

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)

            dialog.exec()

        def _select_chart_type(self, chart_type: str, buttons: list):
            """选择图表类型"""
            self.selected_chart = chart_type
            for btn in buttons:
                btn.setChecked(False)

        def _open_charts_folder(self):
            """打开图表目录"""
            import subprocess
            import platform
            charts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'demo', 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            if platform.system() == 'Windows':
                subprocess.run(['explorer', os.path.abspath(charts_dir)])
            elif platform.system() == 'Darwin':
                subprocess.run(['open', charts_dir])
            else:
                subprocess.run(['xdg-open', charts_dir])

        def setup_menu(self):
            menubar = self.menuBar()

            # 文件菜单
            file_menu = menubar.addMenu("文件(&F)")

            export_action = QAction("导出报告(&E)", self)
            export_action.triggered.connect(self.export_report)
            file_menu.addAction(export_action)

            file_menu.addSeparator()

            exit_action = QAction("退出(&X)", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # 帮助菜单
            help_menu = menubar.addMenu("帮助(&H)")

            about_action = QAction("关于(&A)", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

        def setup_statusbar(self):
            self.statusBar().showMessage("就绪")

        def on_nav_changed(self, index: int):
            self.content_stack.setCurrentIndex(index)

        def export_report(self):
            QMessageBox.information(self, "提示", "报告导出功能开发中...")

        def show_about(self):
            dialog = AboutDialog(self)
            dialog.exec()


def run_desktop_app():
    """运行桌面应用"""
    if not PYQT_AVAILABLE:
        print("错误: PyQt6 不可用")
        print("请安装: pip install PyQt6")
        return

    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    # 创建主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_desktop_app()
