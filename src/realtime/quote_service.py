"""
实时行情推送模块 - 支持实时数据订阅和推送
"""
import logging
import threading
import time
import queue
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)

# 尝试导入 websockets（可选依赖）
try:
    import asyncio
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets 不可用，WebSocket 推送功能将被禁用")


class QuoteEventType(Enum):
    """行情事件类型"""
    PRICE_UPDATE = "price_update"       # 价格更新
    VOLUME_UPDATE = "volume_update"     # 成交量更新
    TRADE = "trade"                     # 成交
    ORDER_BOOK = "order_book"           # 订单簿
    TICK = "tick"                       # Tick 数据
    KLINE = "kline"                     # K线数据
    ALERT = "alert"                     # 价格提醒
    SIGNAL = "signal"                   # 交易信号


@dataclass
class QuoteData:
    """行情数据"""
    stock_code: str
    stock_name: str = ""
    event_type: QuoteEventType = QuoteEventType.PRICE_UPDATE
    timestamp: str = ""

    # 价格数据
    price: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    pre_close: Optional[float] = None

    # 变动
    change: Optional[float] = None
    change_percent: Optional[float] = None

    # 成交
    volume: Optional[int] = None
    amount: Optional[float] = None

    # 买卖盘
    bid_price: Optional[float] = None
    bid_volume: Optional[int] = None
    ask_price: Optional[float] = None
    ask_volume: Optional[int] = None

    # 扩展数据
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "price": self.price,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "pre_close": self.pre_close,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "amount": self.amount,
            "bid_price": self.bid_price,
            "bid_volume": self.bid_volume,
            "ask_price": self.ask_price,
            "ask_volume": self.ask_volume,
            "extra": self.extra,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "QuoteData":
        return QuoteData(
            stock_code=data.get("stock_code", ""),
            stock_name=data.get("stock_name", ""),
            event_type=QuoteEventType(data.get("event_type", "price_update")),
            timestamp=data.get("timestamp", ""),
            price=data.get("price"),
            open=data.get("open"),
            high=data.get("high"),
            low=data.get("low"),
            close=data.get("close"),
            pre_close=data.get("pre_close"),
            change=data.get("change"),
            change_percent=data.get("change_percent"),
            volume=data.get("volume"),
            amount=data.get("amount"),
            extra=data.get("extra", {}),
        )


# 回调函数类型
QuoteCallback = Callable[[QuoteData], None]


class QuoteSubscriber:
    """行情订阅者"""

    def __init__(self, subscriber_id: str, callback: QuoteCallback):
        self.subscriber_id = subscriber_id
        self.callback = callback
        self.subscribed_stocks: Set[str] = set()
        self.created_at = datetime.now()

    def on_quote(self, quote: QuoteData) -> None:
        """收到行情推送"""
        try:
            self.callback(quote)
        except Exception as e:
            logger.error(f"订阅者 {self.subscriber_id} 处理行情失败: {e}")


class QuotePublisher:
    """行情发布器"""

    def __init__(self):
        self.subscribers: Dict[str, QuoteSubscriber] = {}
        self.stock_subscribers: Dict[str, Set[str]] = {}  # stock_code -> subscriber_ids
        self._lock = threading.Lock()

    def subscribe(self, subscriber_id: str, stock_codes: List[str], callback: QuoteCallback) -> bool:
        """订阅行情"""
        with self._lock:
            subscriber = QuoteSubscriber(subscriber_id, callback)
            subscriber.subscribed_stocks = set(stock_codes)
            self.subscribers[subscriber_id] = subscriber

            for code in stock_codes:
                if code not in self.stock_subscribers:
                    self.stock_subscribers[code] = set()
                self.stock_subscribers[code].add(subscriber_id)

            logger.info(f"订阅者 {subscriber_id} 订阅了 {len(stock_codes)} 只股票")
            return True

    def unsubscribe(self, subscriber_id: str) -> bool:
        """取消订阅"""
        with self._lock:
            subscriber = self.subscribers.pop(subscriber_id, None)
            if subscriber:
                for code in subscriber.subscribed_stocks:
                    if code in self.stock_subscribers:
                        self.stock_subscribers[code].discard(subscriber_id)
                logger.info(f"订阅者 {subscriber_id} 已取消订阅")
                return True
            return False

    def add_stock(self, subscriber_id: str, stock_code: str) -> bool:
        """添加订阅股票"""
        with self._lock:
            subscriber = self.subscribers.get(subscriber_id)
            if subscriber:
                subscriber.subscribed_stocks.add(stock_code)
                if stock_code not in self.stock_subscribers:
                    self.stock_subscribers[stock_code] = set()
                self.stock_subscribers[stock_code].add(subscriber_id)
                return True
            return False

    def remove_stock(self, subscriber_id: str, stock_code: str) -> bool:
        """移除订阅股票"""
        with self._lock:
            subscriber = self.subscribers.get(subscriber_id)
            if subscriber:
                subscriber.subscribed_stocks.discard(stock_code)
                if stock_code in self.stock_subscribers:
                    self.stock_subscribers[stock_code].discard(subscriber_id)
                return True
            return False

    def publish(self, quote: QuoteData) -> int:
        """发布行情"""
        with self._lock:
            subscriber_ids = self.stock_subscribers.get(quote.stock_code, set()).copy()

        count = 0
        for sid in subscriber_ids:
            subscriber = self.subscribers.get(sid)
            if subscriber:
                subscriber.on_quote(quote)
                count += 1

        return count

    def get_subscriber_count(self) -> int:
        """获取订阅者数量"""
        return len(self.subscribers)

    def get_stock_subscriber_count(self, stock_code: str) -> int:
        """获取股票订阅者数量"""
        return len(self.stock_subscribers.get(stock_code, set()))


class QuoteDataSource(ABC):
    """行情数据源抽象基类"""

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def subscribe(self, stock_codes: List[str]) -> bool:
        pass

    @abstractmethod
    def unsubscribe(self, stock_codes: List[str]) -> bool:
        pass

    @abstractmethod
    def get_quote(self, stock_code: str) -> Optional[QuoteData]:
        pass


class SimulatedQuoteSource(QuoteDataSource):
    """模拟行情数据源（用于测试）"""

    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.subscribed_stocks: Set[str] = set()
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[QuoteData], None]] = None
        self._base_prices: Dict[str, float] = {}

    def set_callback(self, callback: Callable[[QuoteData], None]) -> None:
        self._callback = callback

    def connect(self) -> bool:
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("模拟行情源已连接")
        return True

    def disconnect(self) -> None:
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("模拟行情源已断开")

    def subscribe(self, stock_codes: List[str]) -> bool:
        self.subscribed_stocks.update(stock_codes)
        # 初始化基准价格
        import random
        for code in stock_codes:
            if code not in self._base_prices:
                self._base_prices[code] = random.uniform(10, 200)
        return True

    def unsubscribe(self, stock_codes: List[str]) -> bool:
        for code in stock_codes:
            self.subscribed_stocks.discard(code)
        return True

    def get_quote(self, stock_code: str) -> Optional[QuoteData]:
        if stock_code not in self._base_prices:
            return None
        return self._generate_quote(stock_code)

    def _generate_quote(self, stock_code: str) -> QuoteData:
        """生成模拟行情"""
        import random

        base_price = self._base_prices.get(stock_code, 100)
        # 随机波动 ±2%
        change_pct = random.uniform(-0.02, 0.02)
        new_price = base_price * (1 + change_pct)
        self._base_prices[stock_code] = new_price

        return QuoteData(
            stock_code=stock_code,
            stock_name=f"模拟股票{stock_code}",
            event_type=QuoteEventType.PRICE_UPDATE,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            price=round(new_price, 2),
            open=round(base_price * 0.99, 2),
            high=round(max(base_price, new_price) * 1.01, 2),
            low=round(min(base_price, new_price) * 0.99, 2),
            close=round(new_price, 2),
            pre_close=round(base_price, 2),
            change=round(new_price - base_price, 2),
            change_percent=round(change_pct * 100, 2),
            volume=random.randint(10000, 1000000),
            amount=round(new_price * random.randint(10000, 1000000), 2),
        )

    def _run_loop(self) -> None:
        """运行循环"""
        while self.running:
            for code in list(self.subscribed_stocks):
                quote = self._generate_quote(code)
                if self._callback:
                    self._callback(quote)
            time.sleep(self.update_interval)


class RealTimeQuoteService:
    """实时行情服务"""

    def __init__(self, data_source: Optional[QuoteDataSource] = None):
        self.publisher = QuotePublisher()
        self.data_source = data_source or SimulatedQuoteSource()
        self.running = False
        self._message_queue: queue.Queue = queue.Queue()

        # 设置数据源回调
        if hasattr(self.data_source, 'set_callback'):
            self.data_source.set_callback(self._on_quote_received)

    def start(self) -> bool:
        """启动服务"""
        if self.running:
            return True

        self.running = True
        connected = self.data_source.connect()

        if connected:
            logger.info("实时行情服务已启动")
        else:
            logger.error("实时行情服务启动失败")
            self.running = False

        return connected

    def stop(self) -> None:
        """停止服务"""
        self.running = False
        self.data_source.disconnect()
        logger.info("实时行情服务已停止")

    def subscribe(self, subscriber_id: str, stock_codes: List[str], callback: QuoteCallback) -> bool:
        """订阅行情"""
        # 向数据源订阅
        self.data_source.subscribe(stock_codes)
        # 注册订阅者
        return self.publisher.subscribe(subscriber_id, stock_codes, callback)

    def unsubscribe(self, subscriber_id: str) -> bool:
        """取消订阅"""
        return self.publisher.unsubscribe(subscriber_id)

    def add_stock(self, subscriber_id: str, stock_code: str) -> bool:
        """添加订阅股票"""
        self.data_source.subscribe([stock_code])
        return self.publisher.add_stock(subscriber_id, stock_code)

    def remove_stock(self, subscriber_id: str, stock_code: str) -> bool:
        """移除订阅股票"""
        return self.publisher.remove_stock(subscriber_id, stock_code)

    def get_current_quote(self, stock_code: str) -> Optional[QuoteData]:
        """获取当前行情"""
        return self.data_source.get_quote(stock_code)

    def _on_quote_received(self, quote: QuoteData) -> None:
        """收到行情数据"""
        self.publisher.publish(quote)

    def get_stats(self) -> Dict[str, Any]:
        """获取服务统计"""
        return {
            "running": self.running,
            "subscriber_count": self.publisher.get_subscriber_count(),
            "subscribed_stocks": len(self.data_source.subscribed_stocks) if hasattr(self.data_source, 'subscribed_stocks') else 0,
        }


class PriceAlertManager:
    """价格提醒管理器"""

    def __init__(self, quote_service: RealTimeQuoteService):
        self.quote_service = quote_service
        self.alerts: Dict[str, List[Dict[str, Any]]] = {}  # stock_code -> alerts
        self._lock = threading.Lock()
        self._subscriber_id = "price_alert_manager"
        self._subscribed = False

    def add_alert(
        self,
        stock_code: str,
        condition: str,  # "above" or "below"
        price: float,
        callback: Callable[[str, float, str], None],
        one_time: bool = True
    ) -> str:
        """添加价格提醒"""
        import uuid
        alert_id = str(uuid.uuid4())[:8]

        with self._lock:
            if stock_code not in self.alerts:
                self.alerts[stock_code] = []

            self.alerts[stock_code].append({
                "alert_id": alert_id,
                "condition": condition,
                "price": price,
                "callback": callback,
                "one_time": one_time,
                "triggered": False,
            })

        # 确保订阅了该股票
        if not self._subscribed:
            self.quote_service.subscribe(self._subscriber_id, [stock_code], self._on_quote)
            self._subscribed = True
        else:
            self.quote_service.add_stock(self._subscriber_id, stock_code)

        logger.info(f"已添加价格提醒: {stock_code} {condition} {price}")
        return alert_id

    def remove_alert(self, alert_id: str) -> bool:
        """移除价格提醒"""
        with self._lock:
            for stock_code, alerts in self.alerts.items():
                for alert in alerts:
                    if alert["alert_id"] == alert_id:
                        alerts.remove(alert)
                        logger.info(f"已移除价格提醒: {alert_id}")
                        return True
        return False

    def _on_quote(self, quote: QuoteData) -> None:
        """收到行情"""
        if quote.price is None:
            return

        with self._lock:
            alerts = self.alerts.get(quote.stock_code, [])
            triggered_alerts = []

            for alert in alerts:
                if alert["triggered"]:
                    continue

                should_trigger = False
                if alert["condition"] == "above" and quote.price >= alert["price"]:
                    should_trigger = True
                elif alert["condition"] == "below" and quote.price <= alert["price"]:
                    should_trigger = True

                if should_trigger:
                    try:
                        alert["callback"](quote.stock_code, quote.price, alert["condition"])
                    except Exception as e:
                        logger.error(f"价格提醒回调失败: {e}")

                    if alert["one_time"]:
                        triggered_alerts.append(alert)
                    else:
                        alert["triggered"] = True

            # 移除一次性提醒
            for alert in triggered_alerts:
                alerts.remove(alert)


# WebSocket 服务器（可选）
if WEBSOCKETS_AVAILABLE:
    class WebSocketQuoteServer:
        """WebSocket 行情推送服务器"""

        def __init__(self, quote_service: RealTimeQuoteService, host: str = "localhost", port: int = 8765):
            self.quote_service = quote_service
            self.host = host
            self.port = port
            self.clients: Set = set()
            self.client_subscriptions: Dict[Any, Set[str]] = {}
            self._server = None
            self._loop = None

        async def handler(self, websocket, path):
            """处理 WebSocket 连接"""
            self.clients.add(websocket)
            self.client_subscriptions[websocket] = set()
            client_id = f"ws_{id(websocket)}"

            logger.info(f"WebSocket 客户端连接: {client_id}")

            try:
                async for message in websocket:
                    await self._handle_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.clients.discard(websocket)
                self.client_subscriptions.pop(websocket, None)
                logger.info(f"WebSocket 客户端断开: {client_id}")

        async def _handle_message(self, websocket, message: str):
            """处理客户端消息"""
            try:
                data = json.loads(message)
                action = data.get("action")

                if action == "subscribe":
                    stocks = data.get("stocks", [])
                    self.client_subscriptions[websocket].update(stocks)
                    await websocket.send(json.dumps({
                        "type": "subscribed",
                        "stocks": list(self.client_subscriptions[websocket])
                    }))

                elif action == "unsubscribe":
                    stocks = data.get("stocks", [])
                    for s in stocks:
                        self.client_subscriptions[websocket].discard(s)
                    await websocket.send(json.dumps({
                        "type": "unsubscribed",
                        "stocks": stocks
                    }))

                elif action == "get_quote":
                    stock_code = data.get("stock_code")
                    quote = self.quote_service.get_current_quote(stock_code)
                    if quote:
                        await websocket.send(quote.to_json())

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))

        async def broadcast_quote(self, quote: QuoteData):
            """广播行情到所有订阅客户端"""
            message = quote.to_json()
            for client, subscriptions in list(self.client_subscriptions.items()):
                if quote.stock_code in subscriptions:
                    try:
                        await client.send(message)
                    except Exception:
                        pass

        def start(self):
            """启动服务器"""
            self._loop = asyncio.new_event_loop()

            async def run_server():
                self._server = await websockets.serve(self.handler, self.host, self.port)
                logger.info(f"WebSocket 服务器启动: ws://{self.host}:{self.port}")
                await self._server.wait_closed()

            threading.Thread(target=lambda: self._loop.run_until_complete(run_server()), daemon=True).start()

        def stop(self):
            """停止服务器"""
            if self._server:
                self._server.close()
            if self._loop:
                self._loop.stop()


# 便捷函数
def create_quote_service(simulated: bool = True, update_interval: float = 1.0) -> RealTimeQuoteService:
    """创建行情服务"""
    if simulated:
        source = SimulatedQuoteSource(update_interval=update_interval)
    else:
        source = SimulatedQuoteSource(update_interval=update_interval)  # TODO: 接入真实数据源
    return RealTimeQuoteService(data_source=source)
