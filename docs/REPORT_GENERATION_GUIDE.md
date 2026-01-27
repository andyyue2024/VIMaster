# 报告生成功能指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持完整的 **报告生成功能**，包括：

- 📄 **PDF 格式报告** - 专业排版，适合打印和分享
- 📊 **Excel 格式报告** - 结构化数据，方便后续分析
- 🎨 **模板自定义** - 完全可配置的报告样式

---

## 🚀 快速开始

### 安装依赖（可选）

```bash
# PDF 生成（需要 reportlab）
pip install reportlab

# Excel 生成（需要 openpyxl）
pip install openpyxl
```

### 生成单只股票报告

```python
from src.app import ValueInvestingApp

app = ValueInvestingApp()

# 生成 PDF 和 Excel 报告
results = app.generate_stock_report("600519", output_dir="reports")
# 输出: ✓ PDF 报告已生成: reports/600519_report.pdf
# 输出: ✓ Excel 报告已生成: reports/600519_report.xlsx
```

### 生成投资组合报告

```python
app = ValueInvestingApp()

results = app.generate_portfolio_report(
    ["600519", "000858", "000651"],
    output_dir="reports"
)
```

---

## 🎨 模板自定义

### 创建自定义模板

```python
from src.reports import ReportTemplate

template = ReportTemplate(
    name="my_template",
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

# 保存模板
template.save("config/my_template.json")
```

### 使用自定义模板

```python
from src.reports import ReportManager, ReportTemplate

# 加载模板
template = ReportTemplate.load("config/my_template.json")

# 创建报告管理器
manager = ReportManager(template=template)

# 生成报告
manager.generate_pdf(data, "reports/custom_report.pdf")
```

---

## 📄 模板配置项

### 基本信息

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `name` | str | "default" | 模板名称 |
| `title` | str | "VIMaster..." | 报告标题 |
| `subtitle` | str | "" | 副标题 |
| `author` | str | "VIMaster 系统" | 作者 |

### 页面设置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `page_size` | str | "A4" | 页面大小 (A4/letter) |
| `margin_top` | float | 2.0 | 上边距 (cm) |
| `margin_bottom` | float | 2.0 | 下边距 (cm) |
| `margin_left` | float | 2.5 | 左边距 (cm) |
| `margin_right` | float | 2.0 | 右边距 (cm) |

### 样式设置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `primary_color` | str | "#1a5f7a" | 主色调 |
| `secondary_color` | str | "#57c5b6" | 辅助色 |
| `text_color` | str | "#333333" | 文字颜色 |

### 内容设置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `include_summary` | bool | True | 包含摘要 |
| `include_financials` | bool | True | 包含财务指标 |
| `include_valuation` | bool | True | 包含估值分析 |
| `include_moat` | bool | True | 包含护城河 |
| `include_risk` | bool | True | 包含风险评估 |
| `include_signals` | bool | True | 包含买卖信号 |
| `include_ml_score` | bool | True | 包含 ML 评分 |

### 页脚设置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `footer_text` | str | "本报告由..." | 页脚文字 |
| `show_page_numbers` | bool | True | 显示页码 |
| `show_generation_time` | bool | True | 显示生成时间 |

---

## 📊 报告内容

### 单只股票报告

PDF 和 Excel 报告包含以下内容：

1. **投资摘要**
   - 综合评分
   - 最终信号
   - 投资决策
   - ML 评分

2. **财务指标**
   - 当前价格
   - PE/PB 比率
   - ROE
   - 毛利率
   - 负债率

3. **估值分析**
   - 内在价值
   - 合理价格
   - 安全边际
   - 估值评分

4. **风险评估**
   - 风险等级
   - 杠杆风险
   - 止损/止盈价

### 投资组合报告

1. **组合统计**
   - 分析股票数
   - 各信号数量统计

2. **股票明细**
   - 代码/名称
   - 信号/评分
   - 安全边际
   - ML 评分

---

## 🔧 API 参考

### ReportManager

```python
class ReportManager:
    def __init__(self, template: Optional[ReportTemplate] = None)
    
    def set_template(self, template: ReportTemplate) -> None
    def load_template(self, path: str) -> None
    
    # 单只股票报告
    def generate_pdf(self, data: StockReportData, output_path: str) -> bool
    def generate_excel(self, data: StockReportData, output_path: str) -> bool
    
    # 投资组合报告
    def generate_portfolio_pdf(self, data: PortfolioReportData, output_path: str) -> bool
    def generate_portfolio_excel(self, data: PortfolioReportData, output_path: str) -> bool
    
    # 批量生成
    def generate_all(self, data: StockReportData, output_dir: str, base_name: str) -> Dict[str, bool]
```

### StockReportData

```python
@dataclass
class StockReportData:
    stock_code: str
    stock_name: str = ""
    
    # 财务指标
    current_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    gross_margin: Optional[float] = None
    debt_ratio: Optional[float] = None
    
    # 估值
    intrinsic_value: Optional[float] = None
    fair_price: Optional[float] = None
    margin_of_safety: Optional[float] = None
    
    # 评分和信号
    overall_score: Optional[float] = None
    ml_score: Optional[float] = None
    final_signal: str = ""
    decision: str = ""
```

---

## 🎯 使用场景

### 场景 1: 日常分析报告

```python
app = ValueInvestingApp()
app.generate_stock_report("600519")
```

### 场景 2: 周度组合报告

```python
app = ValueInvestingApp()
app.generate_portfolio_report(
    ["600519", "000858", "000651", "600036"],
    output_dir="reports/weekly"
)
```

### 场景 3: 自定义模板报告

```python
from src.reports import ReportManager, ReportTemplate

template = ReportTemplate(
    title="VIP 客户投资报告",
    primary_color="#4a148c",  # 紫色主题
)

manager = ReportManager(template=template)
manager.generate_pdf(data, "reports/vip_report.pdf")
```

---

## 📚 文件清单

| 文件 | 说明 |
|------|------|
| `src/reports/report_generator.py` | 核心实现 (600+ 行) |
| `src/reports/__init__.py` | 包导出 |
| `config/report_template.json` | 默认模板配置 |
| `demo_report_generation.py` | 演示脚本 |
| `tests/unit/test_report_generator.py` | 单元测试 |

---

## ⚙️ 依赖说明

| 依赖 | 用途 | 安装命令 |
|------|------|---------|
| reportlab | PDF 生成 | `pip install reportlab` |
| openpyxl | Excel 生成 | `pip install openpyxl` |

两个依赖都是可选的，系统会自动检测并只启用可用的格式。

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
