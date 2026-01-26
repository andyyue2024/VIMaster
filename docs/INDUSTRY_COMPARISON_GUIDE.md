# 行业对比分析功能文档

**日期**: 2026年1月26日  
**版本**: v1.0  
**状态**: ✅ **完成并可用**

---

## 📋 概述

VIMaster 现已支持完整的行业对比分析功能，可以：
- 分析整个行业的财务指标
- 将单只股票与所在行业进行对比
- 对行业内的股票进行排名
- 对比多个行业的整体特征
- 进行跨行业的股票对比

---

## 🚀 快速开始

### 基础使用

```python
from src.analysis.industry_comparator import IndustryComparator

# 初始化分析器
comparator = IndustryComparator()

# 1. 查看可用行业
industries = comparator.get_available_industries()
print(industries)

# 2. 分析单个行业
industry_metrics = comparator.analyze_industry("白酒")
print(f"平均 PE: {industry_metrics.avg_pe_ratio}")

# 3. 对比单只股票与行业
comparison = comparator.compare_stock_with_industry("600519", "白酒")
print(f"PE 相对于行业: {comparison.pe_vs_industry_avg:.2f}x")

# 4. 行业内股票排名
rankings = comparator.rank_stocks_in_industry("白酒")
for code, score, metrics in rankings:
    print(f"{code}: {score:.2f}")

# 5. 多行业对比
results = comparator.compare_multiple_industries(["白酒", "家电", "银行"])
```

### 使用多源数据提供者

```python
from src.analysis.industry_comparator import IndustryComparator
from src.data import MultiSourceDataProvider

# 创建多源提供者（支持 TuShare、BaoStock、AkShare 自动降级）
provider = MultiSourceDataProvider(tushare_token="your_token")

# 使用多源提供者初始化分析器
comparator = IndustryComparator(data_provider=provider)

# 现在可以获取更完整的行业数据
industry_metrics = comparator.analyze_industry("白酒")
```

---

## 📊 支持的行业

| 行业 | 代表股票 | 股票数 |
|------|--------|--------|
| **白酒** | 600519（茅台）、000858（五粮液） | 3 |
| **家电** | 000651（格力）、000333（美的） | 3 |
| **银行** | 600036（招商）、600000（浦发） | 3 |
| **食品饮料** | 000858（五粮液）、601933（永辉） | 3 |
| **房地产** | 600048（保利）、601766（中国中车） | 3 |
| **消费** | 600688（上海石化）、000651（格力） | 3 |
| **医药** | 601858（中国神华）、601889（伊利） | 3 |
| **科技** | 603290（斯达）、002594（比亚迪） | 3 |

### 添加自定义行业

```python
# 扩展 INDUSTRY_STOCKS
comparator.INDUSTRY_STOCKS["新能源"] = ["601696", "600519", "603459"]
```

---

## 🎯 核心功能详解

### 1. 行业分析（analyze_industry）

```python
industry_metrics = comparator.analyze_industry("白酒")

# 返回的指标
print(f"行业名称: {industry_metrics.industry_name}")
print(f"股票数: {len(industry_metrics.stock_codes)}")
print(f"平均 PE: {industry_metrics.avg_pe_ratio}")
print(f"平均 PB: {industry_metrics.avg_pb_ratio}")
print(f"平均 ROE: {industry_metrics.avg_roe}")
print(f"平均毛利率: {industry_metrics.avg_gross_margin}")
print(f"平均负债率: {industry_metrics.avg_debt_ratio}")
print(f"中位数 PE: {industry_metrics.median_pe_ratio}")
```

**返回值**:
- `industry_name` (str): 行业名称
- `stock_codes` (List[str]): 行业内的股票代码
- `avg_pe_ratio` (float): 平均 PE 比率
- `avg_pb_ratio` (float): 平均 PB 比率
- `avg_roe` (float): 平均 ROE
- `avg_gross_margin` (float): 平均毛利率
- `avg_debt_ratio` (float): 平均负债率
- `median_pe_ratio` (float): 中位数 PE
- `median_pb_ratio` (float): 中位数 PB
- `median_roe` (float): 中位数 ROE

### 2. 股票与行业对比（compare_stock_with_industry）

```python
comparison = comparator.compare_stock_with_industry("600519", "白酒")

# 返回的对比数据
print(f"股票: {comparison.stock_code}")
print(f"行业: {comparison.industry}")

# 相对于行业平均值的倍数
print(f"PE 相对行业: {comparison.pe_vs_industry_avg:.2f}x")
print(f"PB 相对行业: {comparison.pb_vs_industry_avg:.2f}x")
print(f"ROE 相对行业: {comparison.roe_vs_industry_avg:.2f}x")

# 百分位排名（0-100）
print(f"PE 百分位: {comparison.pe_percentile:.1f}%（越低越好）")
print(f"ROE 百分位: {comparison.roe_percentile:.1f}%（越高越好）")

# 综合评分
print(f"竞争力评分: {comparison.competitiveness_score:.1f}/10")
print(f"估值评分: {comparison.valuation_score:.1f}/10")
print(f"成长评分: {comparison.growth_score:.1f}/10")
```

**对比指标说明**:
- `pe_vs_industry_avg`: PE 相对于行业平均的倍数（<1 表示低估，>1 表示高估）
- `pb_vs_industry_avg`: PB 相对于行业平均的倍数
- `roe_vs_industry_avg`: ROE 相对于行业平均的倍数（>1 表示强于行业）
- `pe_percentile`: PE 在行业中的百分位（0-100，越低越好）
- `pb_percentile`: PB 在行业中的百分位（0-100，越低越好）
- `roe_percentile`: ROE 在行业中的百分位（0-100，越高越好）

**评分解释**:
- `competitiveness_score`: 竞争力评分（基于 ROE）
- `valuation_score`: 估值评分（基于 PE 和 PB）
- `growth_score`: 成长评分（基于 ROE 相对行业的表现）

### 3. 行业内排名（rank_stocks_in_industry）

```python
rankings = comparator.rank_stocks_in_industry("白酒")

for rank, (stock_code, score, metrics) in enumerate(rankings, 1):
    print(f"{rank}. {stock_code}: 评分 {score:.2f}")
```

**排名算法**:
```
综合评分 = 竞争力评分 × 0.4 + 估值评分 × 0.3 + 成长评分 × 0.3
```

### 4. 多行业对比（compare_multiple_industries）

```python
results = comparator.compare_multiple_industries(["白酒", "家电", "银行"])

for industry_name, metrics in results.items():
    print(f"行业: {industry_name}")
    print(f"  平均 PE: {metrics.avg_pe_ratio:.2f}")
    print(f"  平均 ROE: {metrics.avg_roe:.2%}")
```

### 5. 数据缓存

```python
# 第一次调用会从数据源获取
metrics1 = comparator.analyze_industry("白酒")

# 第二次调用会从缓存返回（无网络请求）
metrics2 = comparator.analyze_industry("白酒")

assert metrics1 is metrics2  # 同一对象
```

---

## 📈 分析示例

### 案例 1：寻找被低估的蓝筹股

```python
comparator = IndustryComparator()

# 分析银行行业
bank_metrics = comparator.analyze_industry("银行")

# 对比每只股票
for code in ["600036", "600000", "601398"]:
    comparison = comparator.compare_stock_with_industry(code, "银行")
    
    if comparison and comparison.pe_percentile < 30:  # PE 在行业底部
        print(f"潜在低估股票: {code}")
        print(f"  PE 百分位: {comparison.pe_percentile:.1f}%")
        print(f"  ROE: {comparison.roe_percentile:.1f}%")
```

### 案例 2：找出行业龙头

```python
# 排名行业内的股票
rankings = comparator.rank_stocks_in_industry("白酒")

# 获取前三名
top_3 = rankings[:3]

for rank, (code, score, metrics) in enumerate(top_3, 1):
    print(f"第 {rank} 名: {code} (评分: {score:.2f})")
```

### 案例 3：跨行业对比

```python
# 对比来自不同行业的股票
stocks = [
    ("600519", "白酒"),      # 茅台
    ("000651", "家电"),      # 格力
    ("600036", "银行"),      # 招商银行
]

results = []
for code, industry in stocks:
    comparison = comparator.compare_stock_with_industry(code, industry)
    if comparison:
        results.append((code, comparison.competitiveness_score))

# 按竞争力评分排名
results.sort(key=lambda x: x[1], reverse=True)
for code, score in results:
    print(f"{code}: 竞争力 {score:.1f}/10")
```

---

## 🔧 API 参考

### IndustryComparator

#### `__init__(data_provider: Optional[MultiSourceDataProvider] = None)`

初始化行业对比分析器。

```python
# 使用默认的 AkShare
comparator = IndustryComparator()

# 使用自定义的多源提供者
provider = MultiSourceDataProvider(tushare_token="xxx")
comparator = IndustryComparator(data_provider=provider)
```

#### `get_available_industries() -> List[str]`

获取所有可用的行业。

```python
industries = comparator.get_available_industries()
# 返回: ["白酒", "家电", "银行", ...]
```

#### `get_industry_stocks(industry: str) -> List[str]`

获取指定行业的股票代码。

```python
stocks = comparator.get_industry_stocks("白酒")
# 返回: ["600519", "000858", "600989"]
```

#### `analyze_industry(industry: str) -> Optional[IndustryMetrics]`

分析整个行业的财务指标。

```python
metrics = comparator.analyze_industry("白酒")
```

#### `compare_stock_with_industry(stock_code: str, industry: str) -> Optional[StockIndustryComparison]`

将股票与所在行业进行对比。

```python
comparison = comparator.compare_stock_with_industry("600519", "白酒")
```

#### `rank_stocks_in_industry(industry: str) -> List[tuple]`

对行业内的股票进行排名。

```python
rankings = comparator.rank_stocks_in_industry("白酒")
# 返回: [(code, score, metrics), ...]
```

#### `compare_multiple_industries(industries: List[str]) -> Dict[str, IndustryMetrics]`

对比多个行业。

```python
results = comparator.compare_multiple_industries(["白酒", "家电"])
```

---

## 📊 数据模型

### IndustryMetrics

```python
@dataclass
class IndustryMetrics:
    industry_name: str              # 行业名称
    stock_codes: List[str]          # 股票代码列表
    avg_pe_ratio: Optional[float]   # 平均 PE
    avg_pb_ratio: Optional[float]   # 平均 PB
    avg_roe: Optional[float]        # 平均 ROE
    avg_gross_margin: Optional[float]  # 平均毛利率
    avg_debt_ratio: Optional[float]    # 平均负债率
    median_pe_ratio: Optional[float]   # 中位数 PE
    median_pb_ratio: Optional[float]   # 中位数 PB
    median_roe: Optional[float]        # 中位数 ROE
    stocks_metrics: Dict[str, FinancialMetrics]  # 所有股票指标
```

### StockIndustryComparison

```python
@dataclass
class StockIndustryComparison:
    stock_code: str                 # 股票代码
    stock_name: str                 # 股票名称
    industry: str                   # 所属行业
    metrics: Optional[FinancialMetrics]      # 股票财务指标
    industry_metrics: Optional[IndustryMetrics]  # 行业指标
    
    pe_percentile: Optional[float]           # PE 百分位
    pb_percentile: Optional[float]           # PB 百分位
    roe_percentile: Optional[float]          # ROE 百分位
    gross_margin_percentile: Optional[float] # 毛利率百分位
    
    pe_vs_industry_avg: Optional[float]      # PE 相对行业
    pb_vs_industry_avg: Optional[float]      # PB 相对行业
    roe_vs_industry_avg: Optional[float]     # ROE 相对行业
    
    competitiveness_score: float             # 竞争力评分
    valuation_score: float                   # 估值评分
    growth_score: float                      # 成长评分
```

---

## 🎯 最佳实践

### 1. 缓存优化

```python
# 使用缓存避免重复查询
comparator = IndustryComparator()

# 第一次查询会加载数据
metrics = comparator.analyze_industry("白酒")

# 后续查询使用缓存
for code in ["600519", "000858"]:
    comparison = comparator.compare_stock_with_industry(code, "白酒")
```

### 2. 错误处理

```python
import logging

logger = logging.getLogger(__name__)

try:
    comparison = comparator.compare_stock_with_industry("600519", "白酒")
    if comparison:
        print(f"对比成功: PE 倍数 {comparison.pe_vs_industry_avg:.2f}")
    else:
        logger.warning("对比返回 None")
except Exception as e:
    logger.error(f"对比异常: {str(e)}")
```

### 3. 批量分析

```python
# 分析多个行业
industries = comparator.get_available_industries()

for industry in industries:
    metrics = comparator.analyze_industry(industry)
    if metrics:
        print(f"{industry}: 平均 PE = {metrics.avg_pe_ratio:.2f}")
```

### 4. 性能优化

```python
from concurrent.futures import ThreadPoolExecutor

# 并发分析多个股票与行业的对比
stocks = [("600519", "白酒"), ("000651", "家电"), ("600036", "银行")]

with ThreadPoolExecutor(max_workers=3) as executor:
    comparisons = [
        executor.submit(comparator.compare_stock_with_industry, code, industry)
        for code, industry in stocks
    ]
    results = [f.result() for f in comparisons]
```

---

## 🐛 故障排除

### 问题 1：无法获取行业数据

**症状**: `analyze_industry()` 返回 None

**原因**: 
- 数据源不可用
- 股票代码无效
- 网络连接问题

**解决**:
```python
# 检查数据源状态
if isinstance(comparator.data_provider, MultiSourceDataProvider):
    comparator.data_provider.print_source_stats()

# 手动添加数据源
from src.data import AkshareDataProvider
comparator.data_provider = AkshareDataProvider
```

### 问题 2：对比结果为 None

**症状**: `compare_stock_with_industry()` 返回 None

**原因**: 股票或行业不存在，或数据获取失败

**解决**:
```python
# 验证股票代码
stocks = comparator.get_industry_stocks("白酒")
if "600519" in stocks:
    comparison = comparator.compare_stock_with_industry("600519", "白酒")
```

### 问题 3：百分位计算不准确

**症状**: 百分位值不合理（如负数或 > 100）

**原因**: 数据不足或计算精度问题

**解决**:
```python
# 检查行业内的股票数量
industry_metrics = comparator.analyze_industry("白酒")
if len(industry_metrics.stocks_metrics) < 3:
    print("警告: 股票数量过少，百分位计算可能不准确")
```

---

## 📈 性能指标

| 操作 | 耗时 | 备注 |
|------|------|------|
| 分析行业（首次） | 2-5 秒 | 取决于数据源 |
| 分析行业（缓存） | < 1 ms | 从缓存返回 |
| 股票对比 | 1-3 秒 | 包括行业分析 |
| 排名 5 只股票 | 5-10 秒 | 并发查询可优化 |
| 对比 3 个行业 | 10-15 秒 | 可并发执行 |

---

## 🚀 运行演示

```bash
python demo_industry_comparison.py
```

---

**完成状态**: 🟢 **完成并可用**  
**版本**: v1.0  
**最后更新**: 2026年1月26日

