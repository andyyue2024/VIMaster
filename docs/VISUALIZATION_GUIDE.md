# 可视化分析功能指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持 **可视化分析结果** 功能，包括：

- 📊 **评分雷达图** - 多维度评分可视化
- 📈 **估值对比图** - 当前价格 vs 合理价格 vs 内在价值
- 💹 **财务指标图** - ROE、毛利率、PE/PB、负债率
- 🎯 **信号仪表盘** - 直观的买卖信号展示
- 🥧 **组合配置图** - 投资组合仓位分布
- ⚠️ **风险分析图** - 多维度风险可视化

---

## 🚀 快速开始

### 安装依赖

```bash
pip install matplotlib
```

### 基本使用

```python
from src.visualization import create_visualizer

# 创建可视化器
visualizer = create_visualizer()

# 绘制雷达图
scores = {'财务': 8, '估值': 7, '护城河': 9}
visualizer.plot_score_radar("600519", scores)

# 绘制估值对比
visualizer.plot_valuation_comparison("600519", 1800, 2000, 2200)
```

### 集成使用

```python
from src.app import ValueInvestingApp

app = ValueInvestingApp()

# 分析并生成可视化图表
app.visualize_stock("600519")
# 输出: ✓ 已生成 5 张图表
```

---

## 🎯 图表类型

### 1️⃣ 评分雷达图

多维度评分可视化，直观展示股票各方面表现。

```python
scores = {
    '护城河': 9.0,
    '财务健康': 8.5,
    '估值吸引力': 7.0,
    '成长性': 6.5,
    '风险控制': 8.0,
}

visualizer.plot_score_radar("600519", scores)
```

**输出**: `charts/600519_radar.png`

### 2️⃣ 估值对比图

对比当前价格、合理价格和内在价值。

```python
visualizer.plot_valuation_comparison(
    stock_code="600519",
    current_price=1800.0,
    fair_price=2000.0,
    intrinsic_value=2200.0,
)
```

**输出**: `charts/600519_valuation.png`

### 3️⃣ 财务指标图

四象限展示核心财务指标。

```python
metrics = {
    'roe': 0.32,           # ROE
    'gross_margin': 0.92,  # 毛利率
    'pe_ratio': 35.5,      # PE
    'pb_ratio': 12.3,      # PB
    'debt_ratio': 0.25,    # 负债率
}

visualizer.plot_financial_metrics("600519", metrics)
```

**输出**: `charts/600519_financial.png`

### 4️⃣ 信号仪表盘

直观的投资信号展示。

```python
visualizer.plot_signal_gauge(
    stock_code="600519",
    overall_score=78.5,
    signal="买入",
)
```

**输出**: `charts/600519_gauge.png`

### 5️⃣ 投资组合配置图

组合仓位分布和评分对比。

```python
stocks = [
    {'stock_code': '600519', 'position_size': 0.30, 'overall_score': 78.5, 'signal': '买入'},
    {'stock_code': '000858', 'position_size': 0.25, 'overall_score': 65.0, 'signal': '持有'},
]

visualizer.plot_portfolio_allocation(stocks, title="我的投资组合")
```

**输出**: `charts/portfolio_allocation.png`

### 6️⃣ 风险分析图

多维度风险可视化。

```python
risk_data = {
    '杠杆风险': 0.25,
    '行业风险': 0.35,
    '公司风险': 0.20,
    '流动性风险': 0.15,
}

visualizer.plot_risk_analysis("600519", risk_data)
```

**输出**: `charts/600519_risk.png`

---

## 🔧 API 参考

### StockVisualizer

```python
class StockVisualizer:
    def __init__(self, config=None, output_dir="charts")
    
    # 雷达图
    def plot_score_radar(stock_code, scores, title=None, save_path=None) -> str
    
    # 估值对比
    def plot_valuation_comparison(stock_code, current_price, fair_price, intrinsic_value) -> str
    
    # 财务指标
    def plot_financial_metrics(stock_code, metrics, save_path=None) -> str
    
    # 信号仪表盘
    def plot_signal_gauge(stock_code, overall_score, signal, save_path=None) -> str
    
    # 组合配置
    def plot_portfolio_allocation(stocks, title="投资组合", save_path=None) -> str
    
    # 风险分析
    def plot_risk_analysis(stock_code, risk_data, save_path=None) -> str
    
    # 完整报告
    def generate_analysis_report(context, output_dir=None) -> Dict[str, str]
```

### ChartConfig

```python
@dataclass
class ChartConfig:
    width: int = 12
    height: int = 8
    dpi: int = 100
    style: str = "seaborn-v0_8-whitegrid"
    title_fontsize: int = 14
    label_fontsize: int = 10
    colors: List[str] = None
```

---

## 🎨 自定义样式

```python
from src.visualization import ChartConfig, StockVisualizer

config = ChartConfig(
    width=16,
    height=10,
    dpi=150,
    title_fontsize=18,
    colors=['#e74c3c', '#3498db', '#2ecc71'],
)

visualizer = StockVisualizer(config=config)
```

---

## 📂 文件清单

| 文件 | 说明 |
|------|------|
| `src/visualization/charts.py` | 核心实现 (450+ 行) |
| `src/visualization/__init__.py` | 包导出 |
| `demo/demo_visualization.py` | 演示脚本 |
| `tests/unit/test_visualization.py` | 单元测试 |

---

## ⚙️ 依赖

```bash
pip install matplotlib
```

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
