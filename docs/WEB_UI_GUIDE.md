# Web UI 界面指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持 **Web UI 界面**，提供现代化的浏览器访问体验：

- 🏠 **首页仪表盘** - 快速分析、统计概览
- 📊 **股票分析** - 单股详细分析
- 📈 **投资组合** - 批量分析多只股票
- 📜 **历史记录** - 查看分析历史
- ⚙️ **系统设置** - 配置参数

---

## 🚀 快速开始

### 安装依赖

```bash
pip install flask flask-cors
```

### 启动服务

```bash
python run_web.py --port 8080
```

### 访问界面

打开浏览器访问：
```
http://localhost:8080
```

---

## 🎯 功能页面

### 1️⃣ 首页

- **快速分析** - 输入股票代码立即分析
- **统计概览** - 总分析次数、信号分布
- **功能入口** - 快速跳转各功能模块

**访问地址**: `http://localhost:8080/`

### 2️⃣ 股票分析页面

- 输入股票代码进行深度分析
- 显示 9 大 Agent 分析结果
- 财务指标、估值、护城河、风险评估
- 投资决策建议

**访问地址**: `http://localhost:8080/analyze`

**URL 参数**:
```
http://localhost:8080/analyze?code=600519
```

### 3️⃣ 投资组合页面

- 批量输入多只股票代码
- 预设组合（价值投资、银行股、消费股）
- 组合汇总统计
- 按评分排序的股票列表

**访问地址**: `http://localhost:8080/portfolio`

### 4️⃣ 历史记录页面

- 查看所有分析历史
- 搜索特定股票
- 重新分析功能

**访问地址**: `http://localhost:8080/history`

### 5️⃣ 设置页面

- 通用设置（数据源、缓存、线程数）
- Agent 配置（权重参数）
- 通知设置（邮件通知）
- 关于信息

**访问地址**: `http://localhost:8080/settings`

---

## 📡 API 接口

Web UI 提供以下 API 接口：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/analyze` | POST | 分析单只股票 |
| `/api/analyze/batch` | POST | 批量分析 |
| `/api/history` | GET | 获取历史记录 |
| `/api/stats` | GET | 获取统计信息 |

### 分析股票

```bash
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "600519"}'
```

### 批量分析

```bash
curl -X POST http://localhost:8080/api/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"stock_codes": ["600519", "000858"]}'
```

---

## 🎨 界面预览

### 首页
```
┌─────────────────────────────────────────────────┐
│  🎯 VIMaster - 价值投资分析系统                  │
├─────────────────────────────────────────────────┤
│  [快速分析] 输入股票代码: [600519] [分析]        │
├─────────────────────────────────────────────────┤
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐            │
│  │ 100 │  │  50 │  │  30 │  │  20 │            │
│  │总分析│  │ 买入│  │ 持有│  │ 卖出│            │
│  └─────┘  └─────┘  └─────┘  └─────┘            │
└─────────────────────────────────────────────────┘
```

### 分析结果
```
┌─────────────────────────────────────────────────┐
│  600519                         [买入] 78.5分   │
├─────────────────────────────────────────────────┤
│  当前价格: ¥1800    合理价格: ¥2000             │
│  安全边际: 11.11%   护城河: 9.0/10              │
├─────────────────────────────────────────────────┤
│  [财务指标]  [估值分析]  [护城河]  [风险评估]    │
│  PE: 35.5   内在价值:¥2200  品牌:0.95  风险:低  │
│  ROE: 32%   估值评分:7.5   成本:0.70           │
├─────────────────────────────────────────────────┤
│  投资决策: 买入 | 仓位: 10% | 止损: ¥1620       │
└─────────────────────────────────────────────────┘
```

---

## 🛠 技术栈

| 技术 | 用途 |
|------|------|
| Flask | Web 框架 |
| Bootstrap 5 | UI 框架 |
| Bootstrap Icons | 图标库 |
| JavaScript | 前端交互 |

---

## 📂 文件结构

```
src/web/
├── app.py              # Flask 应用
├── __init__.py         # 包导出
├── templates/          # HTML 模板
│   ├── index.html      # 首页
│   ├── analyze.html    # 分析页面
│   ├── portfolio.html  # 组合页面
│   ├── history.html    # 历史页面
│   ├── settings.html   # 设置页面
│   ├── 404.html        # 404 错误页
│   └── 500.html        # 500 错误页
└── static/             # 静态文件
    ├── css/
    │   └── style.css   # 自定义样式
    └── js/
        └── main.js     # JavaScript
```

---

## ⚙️ 启动参数

```bash
python run_web.py --help

options:
  --host HOST   监听地址 (默认: 0.0.0.0)
  --port PORT   监听端口 (默认: 8080)
  --debug       调试模式
```

---

## 🔧 生产部署

### Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 "src.web:create_web_app()"
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask flask-cors gunicorn
EXPOSE 8080
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "src.web:create_web_app()"]
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name vimaster.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📱 响应式设计

Web UI 完全支持响应式布局：

- 💻 桌面端 - 多栏布局
- 📱 平板端 - 自适应布局
- 📲 手机端 - 单栏布局

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
