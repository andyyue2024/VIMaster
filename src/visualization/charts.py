"""
可视化模块 - 支持分析结果图表展示
"""
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# 尝试导入可视化库（可选依赖）
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib 不可用，图表功能将被禁用")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class ChartConfig:
    """图表配置"""
    width: int = 12
    height: int = 8
    dpi: int = 100
    style: str = "seaborn-v0_8-whitegrid"
    title_fontsize: int = 14
    label_fontsize: int = 10
    colors: List[str] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]


class StockVisualizer:
    """股票分析可视化器"""

    def __init__(self, config: Optional[ChartConfig] = None, output_dir: str = "charts"):
        self.config = config or ChartConfig()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _check_available(self) -> bool:
        """检查可视化库是否可用"""
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib 不可用，无法生成图表")
            return False
        return True

    def plot_score_radar(
        self,
        stock_code: str,
        scores: Dict[str, float],
        title: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        绘制评分雷达图

        Args:
            stock_code: 股票代码
            scores: 各维度评分 {"财务": 8, "估值": 7, ...}
            title: 图表标题
            save_path: 保存路径
        """
        if not self._check_available():
            return None

        labels = list(scores.keys())
        values = list(scores.values())
        num_vars = len(labels)

        # 计算角度
        angles = [n / float(num_vars) * 2 * 3.14159 for n in range(num_vars)]
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        ax.plot(angles, values, 'o-', linewidth=2, color=self.config.colors[0])
        ax.fill(angles, values, alpha=0.25, color=self.config.colors[0])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=self.config.label_fontsize)
        ax.set_ylim(0, 10)

        ax.set_title(title or f"{stock_code} 综合评分", fontsize=self.config.title_fontsize, pad=20)

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_code}_radar.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"雷达图已保存: {save_path}")
        return save_path

    def plot_valuation_comparison(
        self,
        stock_code: str,
        current_price: float,
        fair_price: float,
        intrinsic_value: float,
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        绘制估值对比图
        """
        if not self._check_available():
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['当前价格', '合理价格', '内在价值']
        values = [current_price, fair_price, intrinsic_value]
        colors = ['#d62728', '#2ca02c', '#1f77b4']

        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='black')

        # 添加数值标签
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                   f'¥{val:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        # 添加安全边际区域
        if current_price < fair_price:
            margin = (fair_price - current_price) / fair_price * 100
            ax.axhline(y=current_price, color='red', linestyle='--', alpha=0.5)
            ax.text(2.3, current_price, f'安全边际: {margin:.1f}%', fontsize=10, color='green')

        ax.set_ylabel('价格 (元)', fontsize=12)
        ax.set_title(f'{stock_code} 估值分析', fontsize=self.config.title_fontsize)
        ax.set_ylim(0, max(values) * 1.2)

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_code}_valuation.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"估值对比图已保存: {save_path}")
        return save_path

    def plot_financial_metrics(
        self,
        stock_code: str,
        metrics: Dict[str, float],
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        绘制财务指标柱状图
        """
        if not self._check_available():
            return None

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # ROE
        ax1 = axes[0, 0]
        roe = metrics.get('roe', 0) * 100
        ax1.bar(['ROE'], [roe], color=self.config.colors[0], width=0.5)
        ax1.axhline(y=15, color='green', linestyle='--', label='优秀线 (15%)')
        ax1.set_ylabel('%')
        ax1.set_title('净资产收益率 (ROE)')
        ax1.legend()

        # 毛利率
        ax2 = axes[0, 1]
        gross_margin = metrics.get('gross_margin', 0) * 100
        ax2.bar(['毛利率'], [gross_margin], color=self.config.colors[1], width=0.5)
        ax2.axhline(y=30, color='green', linestyle='--', label='优秀线 (30%)')
        ax2.set_ylabel('%')
        ax2.set_title('毛利率')
        ax2.legend()

        # PE/PB
        ax3 = axes[1, 0]
        pe = metrics.get('pe_ratio', 0)
        pb = metrics.get('pb_ratio', 0)
        x = ['PE', 'PB']
        ax3.bar(x, [pe, pb], color=[self.config.colors[2], self.config.colors[3]], width=0.5)
        ax3.set_title('估值指标')

        # 负债率
        ax4 = axes[1, 1]
        debt_ratio = metrics.get('debt_ratio', 0) * 100
        ax4.bar(['负债率'], [debt_ratio], color=self.config.colors[4], width=0.5)
        ax4.axhline(y=60, color='red', linestyle='--', label='警戒线 (60%)')
        ax4.set_ylabel('%')
        ax4.set_title('资产负债率')
        ax4.legend()

        fig.suptitle(f'{stock_code} 财务指标分析', fontsize=self.config.title_fontsize)

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_code}_financial.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"财务指标图已保存: {save_path}")
        return save_path

    def plot_signal_gauge(
        self,
        stock_code: str,
        overall_score: float,
        signal: str,
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        绘制信号仪表盘
        """
        if not self._check_available():
            return None

        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': 'polar'})

        # 仪表盘范围 0-100
        score = min(100, max(0, overall_score))

        # 颜色区间
        colors_map = {
            (0, 30): '#d62728',    # 红色 - 卖出
            (30, 50): '#ff7f0e',   # 橙色 - 观望
            (50, 70): '#bcbd22',   # 黄色 - 持有
            (70, 85): '#2ca02c',   # 绿色 - 买入
            (85, 100): '#1f77b4',  # 蓝色 - 强烈买入
        }

        # 绘制背景扇形
        theta_range = 3.14159  # 半圆
        for (low, high), color in colors_map.items():
            theta_start = (1 - high/100) * theta_range
            theta_end = (1 - low/100) * theta_range
            theta = [theta_start + i * (theta_end - theta_start) / 50 for i in range(51)]
            r = [1] * 51
            ax.fill_between(theta, 0, r, color=color, alpha=0.3)

        # 绘制指针
        pointer_angle = (1 - score/100) * theta_range
        ax.annotate('', xy=(pointer_angle, 0.9), xytext=(pointer_angle, 0),
                   arrowprops=dict(arrowstyle='->', color='black', lw=3))

        ax.set_ylim(0, 1.2)
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_yticklabels([])
        ax.set_xticklabels([])

        # 添加刻度标签
        for score_val in [0, 25, 50, 75, 100]:
            angle = (1 - score_val/100) * theta_range
            ax.text(angle, 1.1, str(score_val), ha='center', va='center', fontsize=10)

        # 信号颜色
        signal_colors = {
            '强烈买入': '#1f77b4',
            '买入': '#2ca02c',
            '持有': '#bcbd22',
            '卖出': '#ff7f0e',
            '强烈卖出': '#d62728',
        }
        signal_color = signal_colors.get(signal, '#7f7f7f')

        ax.text(0.5, -0.15, f'评分: {score:.1f}', transform=ax.transAxes,
               ha='center', fontsize=18, fontweight='bold')
        ax.text(0.5, -0.25, f'信号: {signal}', transform=ax.transAxes,
               ha='center', fontsize=16, color=signal_color, fontweight='bold')

        ax.set_title(f'{stock_code} 投资信号', fontsize=self.config.title_fontsize, pad=20)

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_code}_gauge.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"信号仪表盘已保存: {save_path}")
        return save_path

    def plot_portfolio_allocation(
        self,
        stocks: List[Dict[str, Any]],
        title: str = "投资组合配置",
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        绘制投资组合配置饼图
        """
        if not self._check_available():
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 饼图 - 仓位分布
        labels = [s.get('stock_code', '') for s in stocks]
        sizes = [s.get('position_size', 0) * 100 for s in stocks]
        colors = self.config.colors[:len(stocks)]

        wedges, texts, autotexts = ax1.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, pctdistance=0.75
        )
        ax1.set_title('仓位分布', fontsize=self.config.title_fontsize)

        # 柱状图 - 评分对比
        scores = [s.get('overall_score', 0) for s in stocks]
        signals = [s.get('signal', '') for s in stocks]

        signal_colors = {
            '强烈买入': '#1f77b4',
            '买入': '#2ca02c',
            '持有': '#bcbd22',
            '卖出': '#ff7f0e',
            '强烈卖出': '#d62728',
        }
        bar_colors = [signal_colors.get(sig, '#7f7f7f') for sig in signals]

        bars = ax2.bar(labels, scores, color=bar_colors, edgecolor='black')
        ax2.set_ylabel('综合评分')
        ax2.set_title('股票评分对比', fontsize=self.config.title_fontsize)
        ax2.set_ylim(0, 100)

        # 添加评分标签
        for bar, score in zip(bars, scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{score:.1f}', ha='center', va='bottom', fontsize=10)

        fig.suptitle(title, fontsize=self.config.title_fontsize + 2)

        if save_path is None:
            save_path = os.path.join(self.output_dir, "portfolio_allocation.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"组合配置图已保存: {save_path}")
        return save_path

    def plot_risk_analysis(
        self,
        stock_code: str,
        risk_data: Dict[str, float],
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        绘制风险分析图
        """
        if not self._check_available():
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        categories = list(risk_data.keys())
        values = list(risk_data.values())

        # 颜色根据风险等级
        colors = []
        for v in values:
            if v < 0.3:
                colors.append('#2ca02c')  # 低风险 - 绿色
            elif v < 0.6:
                colors.append('#ff7f0e')  # 中风险 - 橙色
            else:
                colors.append('#d62728')  # 高风险 - 红色

        bars = ax.barh(categories, values, color=colors, edgecolor='black', height=0.6)

        # 添加数值标签
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:.2f}', va='center', fontsize=10)

        ax.set_xlim(0, 1.2)
        ax.set_xlabel('风险系数')
        ax.set_title(f'{stock_code} 风险分析', fontsize=self.config.title_fontsize)

        # 添加风险区域标识
        ax.axvline(x=0.3, color='green', linestyle='--', alpha=0.5, label='低风险')
        ax.axvline(x=0.6, color='orange', linestyle='--', alpha=0.5, label='中风险')
        ax.legend(loc='lower right')

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_code}_risk.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        logger.info(f"风险分析图已保存: {save_path}")
        return save_path

    def generate_analysis_report(
        self,
        context,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        生成完整的可视化分析报告

        Args:
            context: StockAnalysisContext 分析上下文
            output_dir: 输出目录

        Returns:
            生成的图表路径字典
        """
        if not self._check_available():
            return {}

        stock_code = context.stock_code
        charts = {}
        save_dir = output_dir or os.path.join(self.output_dir, stock_code)
        os.makedirs(save_dir, exist_ok=True)

        # 1. 雷达图
        if context.competitive_moat and context.valuation:
            scores = {
                '护城河': context.competitive_moat.overall_score,
                '估值': context.valuation.valuation_score if context.valuation.valuation_score else 5,
            }
            if context.financial_metrics:
                scores['财务'] = min(10, (context.financial_metrics.roe or 0) * 30)
            if context.risk_assessment:
                scores['风险'] = 10 - context.risk_assessment.leverage_risk * 10
            if context.buy_signal:
                scores['买入'] = context.buy_signal.confidence_score * 10

            path = self.plot_score_radar(stock_code, scores,
                                        save_path=os.path.join(save_dir, "radar.png"))
            if path:
                charts['radar'] = path

        # 2. 估值对比图
        if context.financial_metrics and context.valuation:
            path = self.plot_valuation_comparison(
                stock_code,
                context.financial_metrics.current_price or 0,
                context.valuation.fair_price or 0,
                context.valuation.intrinsic_value or 0,
                save_path=os.path.join(save_dir, "valuation.png")
            )
            if path:
                charts['valuation'] = path

        # 3. 财务指标图
        if context.financial_metrics:
            fm = context.financial_metrics
            metrics = {
                'roe': fm.roe or 0,
                'gross_margin': fm.gross_margin or 0,
                'pe_ratio': fm.pe_ratio or 0,
                'pb_ratio': fm.pb_ratio or 0,
                'debt_ratio': fm.debt_ratio or 0,
            }
            path = self.plot_financial_metrics(stock_code, metrics,
                                              save_path=os.path.join(save_dir, "financial.png"))
            if path:
                charts['financial'] = path

        # 4. 信号仪表盘
        signal = context.final_signal.value if context.final_signal else "未知"
        path = self.plot_signal_gauge(stock_code, context.overall_score, signal,
                                      save_path=os.path.join(save_dir, "gauge.png"))
        if path:
            charts['gauge'] = path

        # 5. 风险分析图
        if context.risk_assessment:
            risk = context.risk_assessment
            risk_data = {
                '杠杆风险': risk.leverage_risk,
                '行业风险': risk.industry_risk,
                '公司风险': risk.company_risk,
                '能力圈匹配': 1 - risk.ability_circle_match,
            }
            path = self.plot_risk_analysis(stock_code, risk_data,
                                          save_path=os.path.join(save_dir, "risk.png"))
            if path:
                charts['risk'] = path

        logger.info(f"可视化报告已生成: {len(charts)} 张图表")
        return charts


# 便捷函数
def create_visualizer(output_dir: str = "charts") -> StockVisualizer:
    """创建可视化器"""
    return StockVisualizer(output_dir=output_dir)


def check_visualization_available() -> bool:
    """检查可视化功能是否可用"""
    return MATPLOTLIB_AVAILABLE
