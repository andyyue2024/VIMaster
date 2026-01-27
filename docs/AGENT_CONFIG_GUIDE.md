# Agent 参数化配置指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现支持 **Agent 参数化配置**，允许通过 JSON 配置文件或代码动态调整各个分析 Agent 的行为参数，包括：

- 财务分析阈值（ROE、毛利率、负债率等）
- 估值参数（折现率、PE/PB 合理值、权重）
- 风险管理限制（仓位、止损止盈）
- 买卖信号触发条件
- ML 评分权重

---

## 🚀 快速开始

### 使用默认配置
```python
from src.agents import get_agent_config

config = get_agent_config()
print(config.financial.roe_excellent)  # 0.20
print(config.valuation.discount_rate)  # 0.10
```

### 从 JSON 文件加载配置
```python
from src.agents import load_agent_config

config = load_agent_config("config/agent_config.json")
```

### 修改配置
```python
from src.agents import AgentConfig, set_agent_config

config = AgentConfig()
config.financial.roe_excellent = 0.25  # 提高 ROE 标准
config.valuation.discount_rate = 0.12  # 提高折现率
set_agent_config(config)
```

### 保存配置
```python
from src.agents import save_agent_config

save_agent_config("config/my_config.json")
```

---

## 🎯 配置项详解

### 1. 财务分析配置 (FinancialAnalysisConfig)

```python
@dataclass
class FinancialAnalysisConfig:
    # ROE 阈值
    roe_excellent: float = 0.20   # 优秀 ROE (20%)
    roe_good: float = 0.15        # 良好 ROE (15%)
    roe_minimum: float = 0.10     # 最低 ROE (10%)

    # 毛利率阈值
    gross_margin_excellent: float = 0.40
    gross_margin_good: float = 0.25
    gross_margin_minimum: float = 0.15

    # 负债率阈值
    debt_ratio_safe: float = 0.40
    debt_ratio_warning: float = 0.60
    debt_ratio_danger: float = 0.80

    # 自由现金流
    require_positive_fcf: bool = True
    fcf_growth_weight: float = 0.3

    # 评分权重（总和应为 1.0）
    weight_roe: float = 0.30
    weight_gross_margin: float = 0.20
    weight_debt_ratio: float = 0.20
    weight_fcf: float = 0.30
```

### 2. 估值配置 (ValuationConfig)

```python
@dataclass
class ValuationConfig:
    # DCF 参数
    discount_rate: float = 0.10         # 10% 折现率
    terminal_growth_rate: float = 0.03  # 3% 永续增长
    projection_years: int = 10          # 预测 10 年

    # PE 估值
    pe_ratio_low: float = 10.0
    pe_ratio_fair: float = 15.0
    pe_ratio_high: float = 25.0

    # PB 估值
    pb_ratio_low: float = 1.0
    pb_ratio_fair: float = 2.0
    pb_ratio_high: float = 5.0

    # 估值方法权重（总和应为 1.0）
    weight_dcf: float = 0.40
    weight_pe: float = 0.30
    weight_pb: float = 0.30
```

### 3. 风险管理配置 (RiskManagementConfig)

```python
@dataclass
class RiskManagementConfig:
    # 仓位限制
    max_single_position: float = 0.20   # 单股最大 20%
    max_industry_exposure: float = 0.40 # 行业最大 40%
    min_cash_reserve: float = 0.10      # 最低 10% 现金

    # 风险等级阈值（0-10 分）
    low_risk_threshold: float = 3.0
    medium_risk_threshold: float = 6.0
    high_risk_threshold: float = 8.0

    # 止损止盈
    default_stop_loss: float = 0.15      # 15% 止损
    default_take_profit: float = 0.50    # 50% 止盈
    trailing_stop_enabled: bool = True
    trailing_stop_distance: float = 0.10
```

### 4. 买入信号配置 (BuySignalConfig)

```python
@dataclass
class BuySignalConfig:
    pessimism_threshold: float = 0.7    # 悲观情绪阈值
    price_drop_trigger: float = 0.20    # 价格下跌 20% 触发
    volume_spike_ratio: float = 2.0     # 成交量放大 2 倍

    strong_buy_score: float = 8.0
    buy_score: float = 6.0
    hold_score: float = 4.0

    require_valuation_support: bool = True
    require_moat_support: bool = True
    min_financial_score: float = 5.0
```

### 5. 卖出信号配置 (SellSignalConfig)

```python
@dataclass
class SellSignalConfig:
    roe_decline_trigger: float = 0.30   # ROE 下降 30% 触发
    margin_decline_trigger: float = 0.25
    debt_increase_trigger: float = 0.50

    overvalued_pe_ratio: float = 40.0
    overvalued_pb_ratio: float = 8.0
    overvalued_margin: float = -0.30    # 负安全边际 30%

    strong_sell_score: float = 8.0
    sell_score: float = 6.0
```

### 6. ML 评分配置 (MLScoringConfig)

```python
@dataclass
class MLScoringConfig:
    enabled: bool = True
    model_path: Optional[str] = None
    weight_in_decision: float = 0.2    # ML 分占 20% 权重

    # 默认模型权重
    weight_pe: float = -0.25
    weight_pb: float = -0.15
    weight_roe: float = 0.35
    weight_gross_margin: float = 0.20
    weight_fcf: float = 0.30
    weight_debt: float = -0.25
```

---

## 📄 配置文件示例

完整配置文件位于 `config/agent_config.json`：

```json
{
  "financial": {
    "roe_excellent": 0.20,
    "roe_good": 0.15,
    "roe_minimum": 0.10,
    "weight_roe": 0.30,
    "weight_gross_margin": 0.20
  },
  "valuation": {
    "discount_rate": 0.10,
    "pe_ratio_fair": 15.0,
    "weight_dcf": 0.40
  },
  "risk_management": {
    "max_single_position": 0.20,
    "default_stop_loss": 0.15
  },
  "debug_mode": false,
  "version": "1.0"
}
```

---

## 🔧 在 CLI 中使用配置

### 方式 1: 代码中加载

```python
from src.app import ValueInvestingApp

app = ValueInvestingApp(config_path="../config/agent_config.json")
app.analyze_single_stock("600519")
```

### 方式 2: 运行时修改
```python
from src.agents import AgentConfigManager

# 修改单个参数
AgentConfigManager.update_config(debug_mode=True)

# 修改子配置
cfg = AgentConfigManager.get_financial_config()
cfg.roe_excellent = 0.25
```

---

## 📊 配置对分析的影响

| 配置项 | 调高影响 | 调低影响 |
|--------|---------|---------|
| `roe_excellent` | 更严格筛选高 ROE | 更宽松，更多股票通过 |
| `discount_rate` | 内在价值降低 | 内在价值升高 |
| `max_single_position` | 允许更集中 | 更分散 |
| `default_stop_loss` | 更宽松止损 | 更严格止损 |

---

## 🧪 测试

```bash
pytest tests/unit/test_agent_config.py -v
```

---

## 📚 文件清单

| 文件 | 说明 |
|------|------|
| `src/agents/agent_config.py` | 配置定义和管理器 (400+ 行) |
| `config/agent_config.json` | 默认配置文件 |
| `tests/unit/test_agent_config.py` | 单元测试 (150+ 行) |

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
