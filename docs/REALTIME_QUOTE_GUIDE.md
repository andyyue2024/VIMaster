# 实时行情推送功能指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持 **实时行情推送** 功能，包括：

- 📡 **实时数据订阅** - 订阅多只股票的实时行情
- 🔔 **价格提醒** - 设置价格阈值自动提醒
- 🌐 **WebSocket 推送** - 支持 WebSocket 协议推送
- 📊 **多订阅者** - 支持多个订阅者同时订阅

---

## 🚀 快速开始

### 安装依赖（可选）

```bash
# WebSocket 支持（可选）
pip install websockets
```

### 基本使用

```python
from src.realtime import create_quote_service, QuoteData

# 创建行情服务
service = create_quote_service(simulated=True)

# 定义回调函数
def on_quote(quote: QuoteData):
    print(f"{quote.stock_code}: {quote.price:.2f} ({quote.change_percent:+.2f}%)")

# 启动服务
service.start()

# 订阅行情
service.subscribe("my_subscriber", ["600519", "000858"], on_quote)

# ... 行情会通过回调推送 ...

# 停止服务
service.stop()
```

---

## 🎯 核心功能

### 1️⃣ 行情订阅

```python
from src.realtime import create_quote_service

service = create_quote_service()
service.start()

# 订阅
service.subscribe("subscriber_id", ["600519", "000858"], callback)

# 动态添加股票
service.add_stock("subscriber_id", "000651")

# 动态移除股票
service.remove_stock("subscriber_id", "600519")

# 取消订阅
service.unsubscribe("subscriber_id")
```

### 2️⃣ 价格提醒

```python
from src.realtime import create_quote_service, PriceAlertManager

service = create_quote_service()
alert_manager = PriceAlertManager(service)

service.start()

def on_alert(stock_code, price, condition):
    print(f"🔔 {stock_code} 价格 {condition} 阈值，当前: {price}")

# 添加提醒：价格高于 100
alert_manager.add_alert("600519", "above", 100.0, on_alert)

# 添加提醒：价格低于 50
alert_manager.add_alert("600519", "below", 50.0, on_alert)

# 移除提醒
alert_manager.remove_alert(alert_id)
```

### 3️⃣ WebSocket 服务

```python
from src.realtime import create_quote_service, WebSocketQuoteServer

service = create_quote_service()
ws_server = WebSocketQuoteServer(service, host="localhost", port=8765)

service.start()
ws_server.start()

# 客户端连接: ws://localhost:8765
# 发送订阅: {"action": "subscribe", "stocks": ["600519"]}
```

---

## 📡 QuoteData 数据结构

```python
@dataclass
class QuoteData:
    stock_code: str           # 股票代码
    stock_name: str           # 股票名称
    event_type: QuoteEventType  # 事件类型
    timestamp: str            # 时间戳
    
    # 价格
    price: float              # 当前价
    open: float               # 开盘价
    high: float               # 最高价
    low: float                # 最低价
    close: float              # 收盘价
    pre_close: float          # 昨收价
    
    # 变动
    change: float             # 涨跌额
    change_percent: float     # 涨跌幅 (%)
    
    # 成交
    volume: int               # 成交量
    amount: float             # 成交额
    
    # 买卖盘
    bid_price: float          # 买一价
    ask_price: float          # 卖一价
```

### 事件类型

| 类型 | 说明 |
|------|------|
| `PRICE_UPDATE` | 价格更新 |
| `VOLUME_UPDATE` | 成交量更新 |
| `TRADE` | 成交 |
| `ORDER_BOOK` | 订单簿 |
| `TICK` | Tick 数据 |
| `KLINE` | K线数据 |
| `ALERT` | 价格提醒 |
| `SIGNAL` | 交易信号 |

---

## 🌐 WebSocket 协议

### 连接

```
ws://localhost:8765
```

### 消息格式

#### 订阅
```json
{
  "action": "subscribe",
  "stocks": ["600519", "000858"]
}
```

#### 取消订阅
```json
{
  "action": "unsubscribe",
  "stocks": ["600519"]
}
```

#### 获取当前行情
```json
{
  "action": "get_quote",
  "stock_code": "600519"
}
```

### 行情推送格式

```json
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "event_type": "price_update",
  "timestamp": "2026-01-27 15:30:00.123456",
  "price": 1800.50,
  "change_percent": 2.35,
  "volume": 1234567
}
```

---

## 🔧 API 参考

### RealTimeQuoteService

```python
class RealTimeQuoteService:
    def start(self) -> bool
    def stop(self) -> None
    
    def subscribe(self, subscriber_id: str, stock_codes: List[str], callback) -> bool
    def unsubscribe(self, subscriber_id: str) -> bool
    def add_stock(self, subscriber_id: str, stock_code: str) -> bool
    def remove_stock(self, subscriber_id: str, stock_code: str) -> bool
    
    def get_current_quote(self, stock_code: str) -> Optional[QuoteData]
    def get_stats(self) -> Dict[str, Any]
```

### PriceAlertManager

```python
class PriceAlertManager:
    def add_alert(
        self,
        stock_code: str,
        condition: str,  # "above" or "below"
        price: float,
        callback: Callable,
        one_time: bool = True
    ) -> str
    
    def remove_alert(self, alert_id: str) -> bool
```

### QuotePublisher

```python
class QuotePublisher:
    def subscribe(self, subscriber_id: str, stock_codes: List[str], callback) -> bool
    def unsubscribe(self, subscriber_id: str) -> bool
    def publish(self, quote: QuoteData) -> int  # 返回推送数量
    def get_subscriber_count(self) -> int
```

---

## 🎯 使用场景

### 场景 1: 实时监控

```python
def monitor_callback(quote):
    if quote.change_percent > 5:
        print(f"⚠️ {quote.stock_code} 涨幅超过5%!")
    elif quote.change_percent < -5:
        print(f"⚠️ {quote.stock_code} 跌幅超过5%!")

service.subscribe("monitor", ["600519", "000858"], monitor_callback)
```

### 场景 2: 价格突破提醒

```python
# 突破新高提醒
alert_manager.add_alert("600519", "above", 2000.0, on_breakthrough)

# 跌破支撑提醒
alert_manager.add_alert("600519", "below", 1700.0, on_breakdown)
```

### 场景 3: WebSocket 广播

```python
# 启动 WebSocket 服务
ws_server = WebSocketQuoteServer(service)
ws_server.start()

# 前端 JavaScript 连接
# const ws = new WebSocket("ws://localhost:8765");
# ws.send(JSON.stringify({action: "subscribe", stocks: ["600519"]}));
```

---

## ⚙️ 数据源配置

### 模拟数据源（默认）

```python
# 模拟行情，适合测试
service = create_quote_service(simulated=True, update_interval=1.0)
```

### 自定义数据源

```python
from src.realtime import QuoteDataSource, RealTimeQuoteService

class MyDataSource(QuoteDataSource):
    def connect(self) -> bool:
        # 连接到真实数据源
        pass
    
    def subscribe(self, stock_codes: List[str]) -> bool:
        # 订阅股票
        pass
    
    def get_quote(self, stock_code: str) -> Optional[QuoteData]:
        # 获取行情
        pass

source = MyDataSource()
service = RealTimeQuoteService(data_source=source)
```

---

## 📂 文件清单

| 文件 | 说明 |
|------|------|
| `src/realtime/quote_service.py` | 核心实现 (550+ 行) |
| `src/realtime/__init__.py` | 包导出 |
| `demo/demo_realtime_quote.py` | 演示脚本 |
| `tests/unit/test_realtime_quote.py` | 单元测试 |

---

## ⚙️ 依赖说明

| 依赖 | 用途 | 状态 |
|------|------|------|
| websockets | WebSocket 服务 | 可选 |

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
