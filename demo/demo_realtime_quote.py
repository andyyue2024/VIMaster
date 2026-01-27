"""
实时行情演示脚本
"""
import sys
from pathlib import Path
import time
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.realtime import (
    create_quote_service,
    RealTimeQuoteService,
    QuoteData,
    PriceAlertManager,
    WEBSOCKETS_AVAILABLE,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_subscription():
    """演示 1: 基本行情订阅"""
    print("\n" + "=" * 80)
    print("演示 1: 基本行情订阅")
    print("=" * 80)

    # 创建行情服务
    service = create_quote_service(simulated=True, update_interval=0.5)

    # 定义回调函数
    def on_quote(quote: QuoteData):
        print(f"  [{quote.timestamp[:19]}] {quote.stock_code}: "
              f"价格={quote.price:.2f}, 涨跌={quote.change_percent:.2f}%")

    # 启动服务
    service.start()

    # 订阅行情
    service.subscribe("demo_subscriber", ["600519", "000858"], on_quote)

    print("已订阅 600519, 000858，等待行情推送...")
    print("(显示 5 秒行情后停止)")

    time.sleep(5)

    # 停止服务
    service.stop()
    print("✓ 演示完成")


def demo_multiple_subscribers():
    """演示 2: 多个订阅者"""
    print("\n" + "=" * 80)
    print("演示 2: 多个订阅者")
    print("=" * 80)

    service = create_quote_service(simulated=True, update_interval=1.0)

    def subscriber_a(quote: QuoteData):
        print(f"  [订阅者A] {quote.stock_code}: {quote.price:.2f}")

    def subscriber_b(quote: QuoteData):
        print(f"  [订阅者B] {quote.stock_code}: 成交量={quote.volume}")

    service.start()

    # 不同订阅者订阅不同股票
    service.subscribe("subscriber_a", ["600519"], subscriber_a)
    service.subscribe("subscriber_b", ["000858"], subscriber_b)

    print("订阅者A 订阅 600519，订阅者B 订阅 000858")

    time.sleep(3)

    # 取消订阅者A
    service.unsubscribe("subscriber_a")
    print("\n订阅者A 已取消订阅，只有订阅者B 继续接收...")

    time.sleep(2)

    service.stop()
    print("✓ 演示完成")


def demo_price_alerts():
    """演示 3: 价格提醒"""
    print("\n" + "=" * 80)
    print("演示 3: 价格提醒")
    print("=" * 80)

    service = create_quote_service(simulated=True, update_interval=0.3)
    alert_manager = PriceAlertManager(service)

    def on_alert(stock_code: str, price: float, condition: str):
        print(f"  🔔 价格提醒触发: {stock_code} 价格 {condition} 阈值，当前价格={price:.2f}")

    service.start()

    # 获取当前价格作为参考
    quote = service.get_current_quote("600519")
    if quote and quote.price:
        # 设置提醒阈值为当前价格 ±1%
        alert_manager.add_alert("600519", "above", quote.price * 1.01, on_alert)
        alert_manager.add_alert("600519", "below", quote.price * 0.99, on_alert)
        print(f"已设置 600519 价格提醒: 高于 {quote.price * 1.01:.2f} 或 低于 {quote.price * 0.99:.2f}")
    else:
        # 没有当前价格，设置默认阈值
        alert_manager.add_alert("600519", "above", 100, on_alert)
        alert_manager.add_alert("600519", "below", 50, on_alert)
        print("已设置 600519 价格提醒: 高于 100 或 低于 50")

    print("等待价格波动触发提醒...")

    time.sleep(5)

    service.stop()
    print("✓ 演示完成")


def demo_dynamic_subscription():
    """演示 4: 动态添加/移除订阅"""
    print("\n" + "=" * 80)
    print("演示 4: 动态添加/移除订阅")
    print("=" * 80)

    service = create_quote_service(simulated=True, update_interval=0.5)

    received_stocks = set()

    def on_quote(quote: QuoteData):
        received_stocks.add(quote.stock_code)
        print(f"  收到: {quote.stock_code} = {quote.price:.2f}")

    service.start()

    # 初始订阅
    service.subscribe("demo", ["600519"], on_quote)
    print("初始订阅: 600519")
    time.sleep(2)

    # 动态添加
    service.add_stock("demo", "000858")
    print("\n动态添加: 000858")
    time.sleep(2)

    # 动态移除
    service.remove_stock("demo", "600519")
    print("\n动态移除: 600519")
    time.sleep(2)

    service.stop()
    print(f"\n共收到 {len(received_stocks)} 只股票的行情: {received_stocks}")
    print("✓ 演示完成")


def demo_service_stats():
    """演示 5: 服务统计"""
    print("\n" + "=" * 80)
    print("演示 5: 服务统计")
    print("=" * 80)

    service = create_quote_service(simulated=True)

    def dummy_callback(quote: QuoteData):
        pass

    service.start()

    service.subscribe("sub1", ["600519", "000858"], dummy_callback)
    service.subscribe("sub2", ["600519"], dummy_callback)
    service.subscribe("sub3", ["000651"], dummy_callback)

    stats = service.get_stats()

    print(f"服务状态: {'运行中' if stats['running'] else '已停止'}")
    print(f"订阅者数量: {stats['subscriber_count']}")
    print(f"订阅股票数: {stats['subscribed_stocks']}")

    service.stop()
    print("✓ 演示完成")


def demo_websocket_server():
    """演示 6: WebSocket 服务器"""
    print("\n" + "=" * 80)
    print("演示 6: WebSocket 服务器")
    print("=" * 80)

    if not WEBSOCKETS_AVAILABLE:
        print("⚠ websockets 不可用，跳过此演示")
        print("安装: pip install websockets")
        return

    from src.realtime import WebSocketQuoteServer

    service = create_quote_service(simulated=True, update_interval=1.0)
    ws_server = WebSocketQuoteServer(service, host="localhost", port=8765)

    service.start()
    ws_server.start()

    print("WebSocket 服务器已启动: ws://localhost:8765")
    print("\n使用方法:")
    print('  1. 连接: ws://localhost:8765')
    print('  2. 订阅: {"action": "subscribe", "stocks": ["600519"]}')
    print('  3. 获取: {"action": "get_quote", "stock_code": "600519"}')
    print("\n服务器运行 10 秒后自动停止...")

    time.sleep(10)

    ws_server.stop()
    service.stop()
    print("✓ 演示完成")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 实时行情推送演示")
    print("=" * 80)

    try:
        demo_basic_subscription()
        demo_multiple_subscribers()
        demo_price_alerts()
        demo_dynamic_subscription()
        demo_service_stats()
        demo_websocket_server()

        print("\n" + "=" * 80)
        print("所有演示完成！")
        print("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"演示失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
