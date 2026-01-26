# 增强分析功能 - 完整使用指南

**版本**: v2.0  
**日期**: 2026年1月26日  
**功能**: 行业对比分析 + 历史估值对比 + 投资组合优化

---

## 📋 概述

VIMaster 现已支持三大增强分析功能：

### 1. **行业对比分析** (已有)
- 分析行业财务指标
- 对比股票与行业
- 行业内股票排名

### 2. **历史估值对比** (新增)
- 分析历史估值趋势
- 对比当前与历史平均估值
- 生成估值买卖信号

### 3. **投资组合优化** (新增)
- 5 种投资策略选择
- 智能权重分配
- 风险管理建议

### 4. **综合分析** (新增)
- 整合所有分析功能
- 生成完整投资建议
- 支持多股票组合分析

---

## 🚀 快速开始

### 基础使用

```python
from src.analysis import ComprehensiveAnalyzer

# 初始化综合分析器
analyzer = ComprehensiveAnalyzer()

# 1. 单只股票综合分析
result = analyzer.analyze_stock_comprehensive("600519", industry="白酒")
print(result)

# 2. 投资组合分析（平衡型策略）
from src.analysis import PortfolioStrategy
portfolio_result = analyzer.analyze_portfolio_comprehensive(
    ["600519", "000858", "000651"],
    strategy=PortfolioStrategy.BALANCED
)
print(portfolio_result)

# 3. 生成投资建议
recommendations = analyzer.generate_investment_recommendations(
    ["600519", "000858", "000651", "600036"]
)
print(recommendations)
```

---

## 📊 三大功能详解

### 功能 1：历史估值对比分析

#### 1.1 分析历史估值趋势

```python
from src.analysis import ValuationAnalyzer

analyzer = ValuationAnalyzer()

# 分析 365 天的估值趋势
trend = analyzer.analyze_valuation_history("600519", days=365)

if trend:
    print(f"平均PE: {trend.avg_pe_ratio:.2f}")
    print(f"最低PE: {trend.min_pe_ratio:.2f}")
    print(f"最高PE: {trend.max_pe_ratio:.2f}")
    print(f"中位数PE: {trend.median_pe_ratio:.2f}")
    print(f"当前估值等级: {trend.current_valuation_grade}")
```

#### 1.2 对比当前与历史平均估值

```python
# 获取估值对比数据
comparison = analyzer.compare_valuation_history("600519", days=365)

if comparison:
    print(f"当前PE: {comparison.current_pe:.2f}")
    print(f"历史平均PE: {comparison.historical_avg_pe:.2f}")
    print(f"PE相对历史平均: {comparison.pe_vs_avg:.2f}x")
    print(f"估值百分位: {comparison.valuation_percentile:.1f}%")
    print(f"估值信号: {comparison.valuation_signal}")
    print(f"信号置信度: {comparison.signal_confidence:.0%}")
```

#### 1.3 对比多只股票

```python
# 对比多只股票的历史估值
stocks = ["600519", "000858", "000651"]
comparisons = analyzer.compare_stocks_valuation(stocks, days=365)

for comp in comparisons:
    print(f"{comp.stock_code}: PE倍数={comp.pe_vs_avg:.2f}x, 信号={comp.valuation_signal}")
```

### 功能 2：投资组合优化建议

#### 2.1 5 种投资策略

```python
from src.analysis import PortfolioStrategy

# 价值型：寻找被低估的股票，安全边际大
# 成长型：寻找高成长股票，追求资本增值
# 平衡型：兼顾成长和安全，风险适中
# 收益型：追求稳定分红，偏好高股息
# 保守型：极低风险，保留大量现金
```

#### 2.2 生成投资组合

```python
from src.analysis import PortfolioOptimizer, PortfolioStrategy

optimizer = PortfolioOptimizer()

# 生成价值型投资组合
stock_analyses = [...]  # 股票分析结果列表

recommendation = optimizer.generate_portfolio_recommendation(
    stock_analyses,
    strategy=PortfolioStrategy.VALUE,
    portfolio_size=5
)

if recommendation:
    print(f"策略: {recommendation.strategy.value}")
    print(f"预期收益率: {recommendation.expected_return:.2%}")
    print(f"风险评分: {recommendation.risk_score:.1f}/10")
    print(f"现金配置: {recommendation.cash_weight:.0%}")
    
    for pos in recommendation.positions:
        print(f"  {pos.stock_code}: 仓位 {pos.weight:.2%}, 风险 {pos.risk_level}")
```

#### 2.3 投资组合指标计算

```python
# 计算投资组合的主要指标
metrics = optimizer.calculate_portfolio_metrics(positions)

print(f"总权重: {metrics['total_weight']:.2%}")
print(f"平均得分: {metrics['average_score']:.1f}")
print(f"平均风险: {metrics['average_risk']:.1f}")
print(f"多样化评分: {metrics['diversification']:.1f}/10")
```

### 功能 3：综合分析

#### 3.1 单只股票综合分析

```python
from src.analysis import ComprehensiveAnalyzer

analyzer = ComprehensiveAnalyzer()

# 全面分析一只股票
result = analyzer.analyze_stock_comprehensive("600519", industry="白酒")

if result:
    print("【基础分析】")
    basic = result["basic_analysis"]
    print(f"综合评分: {basic['overall_score']:.1f}")
    
    print("【历史估值】")
    val = result.get("valuation_history", {})
    print(f"PE vs 历史平均: {val.get('pe_vs_avg', 'N/A'):.2f}x")
    
    print("【行业对比】")
    ind = result.get("industry_comparison", {})
    print(f"竞争力评分: {ind.get('competitiveness_score', 'N/A'):.1f}/10")
```

#### 3.2 投资组合综合分析

```python
# 分析多只股票并生成投资组合

from src.analysis import PortfolioStrategy

stocks = ["600519", "000858", "000651", "600036", "300059"]

# 平衡型策略
portfolio_result = analyzer.analyze_portfolio_comprehensive(
    stocks,
    strategy=PortfolioStrategy.BALANCED
)

if portfolio_result:
    rec = portfolio_result["portfolio_recommendation"]
    print(f"策略: {rec['strategy']}")
    print(f"建议: {rec['summary']}")
    print(f"预期收益: {rec['expected_return']:.2%}")
```

#### 3.3 生成投资建议

```python
# 生成买入/持有/卖出建议

stocks = ["600519", "000858", "000651", "600036"]

recommendations = analyzer.generate_investment_recommendations(stocks)

if recommendations:
    print(f"【买入建议】({recommendations['buy_stocks']['count']}只)")
    for stock in recommendations['buy_stocks']['stocks']:
        print(f"  {stock['stock_code']}: 评分 {stock['basic_analysis']['overall_score']:.1f}")
    
    print(f"\n【持有建议】({recommendations['hold_stocks']['count']}只)")
    print(f"【卖出建议】({recommendations['sell_stocks']['count']}只)")
```

---

## 🎯 使用案例

### 案例 1：寻找被低估的股票

```python
analyzer = ComprehensiveAnalyzer()

stocks = ["600519", "000858", "000651"]

for code in stocks:
    result = analyzer.analyze_stock_comprehensive(code)
    
    val = result.get("valuation_history", {})
    if val.get("valuation_signal") == "买入":
        print(f"找到低估机会: {code}")
        print(f"  当前PE: {val['current_pe']:.2f}")
        print(f"  历史平均PE: {val['historical_avg_pe']:.2f}")
```

### 案例 2：构建适合自己的投资组合

```python
from src.analysis import PortfolioStrategy

analyzer = ComprehensiveAnalyzer()

# 如果你是保守投资者
portfolio = analyzer.analyze_portfolio_comprehensive(
    stocks,
    strategy=PortfolioStrategy.CONSERVATIVE
)

# 如果你追求成长
portfolio = analyzer.analyze_portfolio_comprehensive(
    stocks,
    strategy=PortfolioStrategy.GROWTH
)
```

### 案例 3：行业对比选择最优股票

```python
analyzer = ComprehensiveAnalyzer()

# 对比白酒、家电、银行三个行业
result = analyzer.compare_industries_with_stocks(["白酒", "家电", "银行"])

# 选择各行业最具竞争力的股票
for industry, data in result["industries"].items():
    best_stock = data["stocks"][0]  # 排名第一的股票
    print(f"{industry}行业最优选择: {best_stock['stock_code']}")
```

---

## 📈 关键指标说明

### 估值相关指标

| 指标 | 说明 | 解释 |
|------|------|------|
| PE vs 历史平均 | 当前PE / 历史平均PE | < 1 低估，> 1 高估 |
| 估值百分位 | 当前估值在历史中的位置 | 0% 最便宜，100% 最贵 |
| 估值信号 | 基于历史对比的买卖信号 | 买入/持有/卖出 |

### 投资组合指标

| 指标 | 说明 | 范围 |
|------|------|------|
| 预期收益率 | 加权平均预期收益 | 0-20% |
| 风险评分 | 加权平均风险水平 | 0-10 |
| 多样化评分 | 组合多样化程度 | 0-10 |

---

## 🧪 测试

```bash
# 运行高级分析功能测试
pytest tests/unit/test_advanced_analysis.py -v

# 运行演示
python demo_advanced_analysis.py
```

---

## 📁 新增文件

```
src/analysis/
├── valuation_history_analyzer.py    # 历史估值分析
├── portfolio_optimizer.py           # 投资组合优化
└── comprehensive_analyzer.py        # 综合分析整合

tests/unit/
└── test_advanced_analysis.py        # 单元测试

demo_advanced_analysis.py            # 演示脚本
```

---

## 💡 最佳实践

### 1. 结合多个分析维度

```python
# 不要只看一个指标，结合多个维度分析
result = analyzer.analyze_stock_comprehensive(stock_code, industry)

# 查看基础分析、历史估值和行业对比
basic = result["basic_analysis"]
valuation = result["valuation_history"]
industry = result["industry_comparison"]
```

### 2. 根据风险承受能力选择策略

```python
# 保守投资者
portfolio = analyzer.analyze_portfolio_comprehensive(
    stocks,
    strategy=PortfolioStrategy.CONSERVATIVE  # 现金 20%，低风险股票 80%
)

# 激进投资者
portfolio = analyzer.analyze_portfolio_comprehensive(
    stocks,
    strategy=PortfolioStrategy.GROWTH  # 权重倾向于高成长股票
)
```

### 3. 定期重新评估

```python
# 每月重新分析一次，检查是否需要调整
for code in portfolio_codes:
    result = analyzer.analyze_stock_comprehensive(code)
    
    signal = result["valuation_history"]["valuation_signal"]
    if signal == "卖出":
        print(f"建议卖出: {code}")
```

---

## 🎬 运行演示

```bash
python demo_advanced_analysis.py
```

演示内容：
1. 单只股票综合分析
2. 历史估值对比
3. 投资组合优化（多种策略）
4. 综合投资建议
5. 行业对比分析

---

## ✨ 功能总结

| 功能 | 说明 | 新增 |
|------|------|------|
| 行业对比分析 | 对比同行业股票 | ✓ |
| 历史估值分析 | 分析估值变化趋势 | ✅ 新增 |
| 投资组合优化 | 生成投资组合建议 | ✅ 新增 |
| 综合分析整合 | 整合所有分析功能 | ✅ 新增 |

---

**项目状态**: 🟢 **完成并可用**  
**版本**: v2.0  
**最后更新**: 2026年1月26日

