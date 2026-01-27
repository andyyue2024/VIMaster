"""
实时行情功能单元测试
"""
import sys
from pathlib import Path
import time
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.realtime import (
    QuoteEventType,
    QuoteData,
    QuotePublisher,
    QuoteSubscriber,
    SimulatedQuoteSource,
    RealTimeQuoteService,
    PriceAlertManager,
    create_quote_service,
)


class TestQuoteData:
    """行情数据测试"""

    def test_quote_creation(self):
        """测试行情数据创建"""
        quote = QuoteData(
            stock_code="600519",
            price=1800.00,
            change_percent=2.5,
        )

        assert quote.stock_code == "600519"
        assert quote.price == 1800.00
        assert quote.change_percent == 2.5

    def test_quote_to_dict(self):
        """测试转换为字典"""
        quote = QuoteData(
            stock_code="600519",
            price=1800.00,
            event_type=QuoteEventType.PRICE_UPDATE,
        )

        data = quote.to_dict()

        assert data["stock_code"] == "600519"
        assert data["price"] == 1800.00
        assert data["event_type"] == "price_update"

    def test_quote_to_json(self):
        """测试转换为 JSON"""
        quote = QuoteData(stock_code="600519", price=100.0)

        json_str = quote.to_json()

        assert "600519" in json_str
        assert "100.0" in json_str

    def test_quote_from_dict(self):
        """测试从字典创建"""
        data = {
            "stock_code": "000858",
            "price": 160.0,
            "event_type": "trade",
        }

        quote = QuoteData.from_dict(data)

        assert quote.stock_code == "000858"
        assert quote.price == 160.0
        assert quote.event_type == QuoteEventType.TRADE


class TestQuotePublisher:
    """行情发布器测试"""

    def test_subscribe(self):
        """测试订阅"""
        publisher = QuotePublisher()

        def callback(quote):
            pass

        result = publisher.subscribe("sub1", ["600519", "000858"], callback)

        assert result is True
        assert publisher.get_subscriber_count() == 1

    def test_unsubscribe(self):
        """测试取消订阅"""
        publisher = QuotePublisher()

        publisher.subscribe("sub1", ["600519"], lambda q: None)
        result = publisher.unsubscribe("sub1")

        assert result is True
        assert publisher.get_subscriber_count() == 0

    def test_publish(self):
        """测试发布"""
        publisher = QuotePublisher()
        received = []

        def callback(quote):
            received.append(quote)

        publisher.subscribe("sub1", ["600519"], callback)

        quote = QuoteData(stock_code="600519", price=100.0)
        count = publisher.publish(quote)

        assert count == 1
        assert len(received) == 1
        assert received[0].stock_code == "600519"

    def test_publish_to_multiple_subscribers(self):
        """测试发布到多个订阅者"""
        publisher = QuotePublisher()
        received_a = []
        received_b = []

        publisher.subscribe("sub_a", ["600519"], lambda q: received_a.append(q))
        publisher.subscribe("sub_b", ["600519"], lambda q: received_b.append(q))

        quote = QuoteData(stock_code="600519", price=100.0)
        count = publisher.publish(quote)

        assert count == 2
        assert len(received_a) == 1
        assert len(received_b) == 1

    def test_add_remove_stock(self):
        """测试添加/移除订阅股票"""
        publisher = QuotePublisher()

        publisher.subscribe("sub1", ["600519"], lambda q: None)

        publisher.add_stock("sub1", "000858")
        assert publisher.get_stock_subscriber_count("000858") == 1

        publisher.remove_stock("sub1", "000858")
        assert publisher.get_stock_subscriber_count("000858") == 0


class TestSimulatedQuoteSource:
    """模拟行情源测试"""

    def test_connect_disconnect(self):
        """测试连接断开"""
        source = SimulatedQuoteSource(update_interval=0.1)

        result = source.connect()
        assert result is True
        assert source.running is True

        source.disconnect()
        assert source.running is False

    def test_subscribe(self):
        """测试订阅"""
        source = SimulatedQuoteSource()

        result = source.subscribe(["600519", "000858"])

        assert result is True
        assert "600519" in source.subscribed_stocks
        assert "000858" in source.subscribed_stocks

    def test_get_quote(self):
        """测试获取行情"""
        source = SimulatedQuoteSource()
        source.subscribe(["600519"])

        quote = source.get_quote("600519")

        assert quote is not None
        assert quote.stock_code == "600519"
        assert quote.price is not None

    def test_callback(self):
        """测试回调"""
        source = SimulatedQuoteSource(update_interval=0.1)
        received = []

        source.set_callback(lambda q: received.append(q))
        source.subscribe(["600519"])
        source.connect()

        time.sleep(0.3)

        source.disconnect()

        assert len(received) > 0


class TestRealTimeQuoteService:
    """实时行情服务测试"""

    def test_service_lifecycle(self):
        """测试服务生命周期"""
        service = create_quote_service(simulated=True)

        result = service.start()
        assert result is True
        assert service.running is True

        service.stop()
        assert service.running is False

    def test_subscribe(self):
        """测试订阅"""
        service = create_quote_service(simulated=True)
        received = []

        service.start()
        service.subscribe("test_sub", ["600519"], lambda q: received.append(q))

        time.sleep(1.5)

        service.stop()

        assert len(received) > 0

    def test_get_stats(self):
        """测试获取统计"""
        service = create_quote_service(simulated=True)

        service.start()
        service.subscribe("sub1", ["600519"], lambda q: None)
        service.subscribe("sub2", ["000858"], lambda q: None)

        stats = service.get_stats()

        assert stats["running"] is True
        assert stats["subscriber_count"] == 2

        service.stop()


class TestPriceAlertManager:
    """价格提醒管理器测试"""

    def test_add_alert(self):
        """测试添加提醒"""
        service = create_quote_service(simulated=True)
        manager = PriceAlertManager(service)

        service.start()

        alert_id = manager.add_alert(
            "600519",
            "above",
            100.0,
            lambda c, p, t: None,
        )

        assert alert_id is not None
        assert len(alert_id) == 8

        service.stop()

    def test_remove_alert(self):
        """测试移除提醒"""
        service = create_quote_service(simulated=True)
        manager = PriceAlertManager(service)

        service.start()

        alert_id = manager.add_alert("600519", "above", 100.0, lambda c, p, t: None)
        result = manager.remove_alert(alert_id)

        assert result is True

        service.stop()

    def test_alert_trigger(self):
        """测试提醒触发"""
        service = create_quote_service(simulated=True, update_interval=0.1)
        manager = PriceAlertManager(service)
        triggered = []

        def on_alert(stock_code, price, condition):
            triggered.append((stock_code, price, condition))

        service.start()

        # 设置一个很容易触发的阈值
        manager.add_alert("600519", "above", 0.01, on_alert)  # 几乎任何价格都会触发

        time.sleep(1)

        service.stop()

        # 应该触发了提醒
        assert len(triggered) > 0
