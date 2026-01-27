# 商业化 API 服务指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持 **商业化 API 服务**，包括：

- 🔐 **API 密钥认证** - 安全的密钥管理
- 📊 **订阅计划** - 免费/基础/专业/企业版
- ⚡ **限流控制** - 基于计划的请求限制
- 📈 **使用量追踪** - 详细的 API 调用统计
- 💰 **计费支持** - 配额管理和升级

---

## 🚀 快速开始

### 安装依赖

```bash
pip install flask flask-cors
```

### 启动服务

```bash
python run_api.py --host 0.0.0.0 --port 5000
```

### 创建 API 密钥

```bash
curl -X POST http://localhost:5000/api/v1/keys \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "plan": "basic"}'
```

### 调用 API

```bash
curl http://localhost:5000/api/v1/analyze/600519 \
  -H "X-API-Key: vk_your_api_key"
```

---

## 📊 订阅计划

| 计划 | 日配额 | 每分钟限制 | 单次最大股票数 | 月费 |
|------|--------|------------|----------------|------|
| **免费版** | 100 | 10 | 5 | ¥0 |
| **基础版** | 1,000 | 60 | 20 | ¥99 |
| **专业版** | 10,000 | 300 | 50 | ¥299 |
| **企业版** | 100,000 | 1,000 | 200 | ¥999 |

### 功能对比

| 功能 | 免费 | 基础 | 专业 | 企业 |
|------|:----:|:----:|:----:|:----:|
| 基础分析 | ✅ | ✅ | ✅ | ✅ |
| 单股分析 | ✅ | ✅ | ✅ | ✅ |
| 组合分析 | ❌ | ✅ | ✅ | ✅ |
| 历史数据 | ❌ | ✅ | ✅ | ✅ |
| 实时数据 | ❌ | ❌ | ✅ | ✅ |
| 导出报告 | ❌ | ❌ | ✅ | ✅ |
| 优先支持 | ❌ | ❌ | ✅ | ✅ |
| SLA 保障 | ❌ | ❌ | ❌ | ✅ |
| 私有部署 | ❌ | ❌ | ❌ | ✅ |

---

## 🔐 API 认证

### 获取密钥

```http
POST /api/v1/keys
Content-Type: application/json

{
  "user_id": "your_user_id",
  "plan": "basic"
}
```

**响应:**
```json
{
  "key_id": "abc12345",
  "api_key": "vk_xxxxxxxxxxxx",
  "secret_key": "xxxxxxxxxxxxxxxx",
  "plan": "basic",
  "daily_quota": 1000,
  "message": "请妥善保存密钥，secret_key 仅显示一次"
}
```

### 使用密钥

在请求头中添加:
```
X-API-Key: vk_your_api_key
```

---

## 📡 API 接口

### 健康检查

```http
GET /api/v1/health
```

### 获取计划列表

```http
GET /api/v1/plans
```

### 获取密钥信息

```http
GET /api/v1/keys/info
X-API-Key: vk_xxx
```

**响应:**
```json
{
  "key_id": "abc12345",
  "plan": "basic",
  "plan_name": "基础版",
  "daily_quota": 1000,
  "used_today": 50,
  "remaining_today": 950,
  "features": ["基础分析", "单股分析", "组合分析"]
}
```

### 获取使用统计

```http
GET /api/v1/keys/usage?days=30
X-API-Key: vk_xxx
```

### 分析单只股票

```http
GET /api/v1/analyze/{stock_code}
X-API-Key: vk_xxx
```

**响应:**
```json
{
  "stock_code": "600519",
  "overall_score": 78.5,
  "final_signal": "买入",
  "financial_metrics": {
    "current_price": 1800.0,
    "pe_ratio": 35.5,
    "roe": 0.32
  },
  "valuation": {
    "intrinsic_value": 2200.0,
    "fair_price": 2000.0,
    "margin_of_safety": 11.11
  },
  "moat": {
    "overall_score": 9.0
  },
  "decision": {
    "action": "买入",
    "position_size": 0.1
  }
}
```

### 批量分析

```http
POST /api/v1/analyze/batch
X-API-Key: vk_xxx
Content-Type: application/json

{
  "stock_codes": ["600519", "000858", "000651"]
}
```

**响应:**
```json
{
  "report_id": "report_20260127_100000",
  "total_analyzed": 3,
  "summary": {
    "strong_buy": 1,
    "buy": 1,
    "hold": 1,
    "sell": 0,
    "strong_sell": 0
  },
  "stocks": [
    {"stock_code": "600519", "overall_score": 78.5, "signal": "买入"},
    {"stock_code": "000858", "overall_score": 65.0, "signal": "持有"},
    {"stock_code": "000651", "overall_score": 72.0, "signal": "买入"}
  ]
}
```

### 获取股票行情

```http
GET /api/v1/quote/{stock_code}
X-API-Key: vk_xxx
```

---

## ⚡ 限流规则

### 响应头

每个响应都包含限流信息:

```
X-Remaining-Quota: 950
X-Response-Time: 123.45ms
```

### 错误码

| HTTP 状态码 | 错误码 | 说明 |
|-------------|--------|------|
| 401 | MISSING_API_KEY | 缺少 API 密钥 |
| 401 | INVALID_API_KEY | 无效的 API 密钥 |
| 429 | RATE_LIMITED | 请求过于频繁 |

---

## 🔧 管理功能

### 升级计划

```python
from src.api import ApiKeyManager, PlanType

manager = ApiKeyManager()
manager.upgrade_plan("vk_xxx", PlanType.PRO)
```

### 撤销密钥

```python
manager.revoke_key("vk_xxx")
```

### 查看使用统计

```python
from src.api import UsageTracker

tracker = UsageTracker()
stats = tracker.get_usage_stats("key_id", days=30)
print(stats)
```

---

## 📂 文件清单

| 文件 | 说明 |
|------|------|
| `src/api/api_service.py` | 核心实现 (600+ 行) |
| `src/api/__init__.py` | 包导出 |
| `run_api.py` | 启动脚本 |
| `tests/unit/test_api_service.py` | 单元测试 |

---

## 📁 数据存储

API 数据存储在 `data/api` 目录:

```
data/api/
├── api_keys.json     # API 密钥
└── usage_*.json      # 使用记录
```

---

## ⚙️ 部署

### 开发环境

```bash
python run_api.py --debug
```

### 生产环境 (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.api:create_api_app()"
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask flask-cors gunicorn
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.api:create_api_app()"]
```

---

## 🔒 安全建议

1. **HTTPS** - 生产环境务必使用 HTTPS
2. **密钥保护** - 不要在代码中硬编码密钥
3. **日志脱敏** - 日志中隐藏敏感信息
4. **IP 白名单** - 企业版支持 IP 限制
5. **定期轮换** - 建议定期更换密钥

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
