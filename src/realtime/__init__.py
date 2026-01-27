"""realtime 包初始化"""
from src.realtime.quote_service import (
    QuoteEventType,
    QuoteData,
    QuoteCallback,
    QuoteSubscriber,
    QuotePublisher,
    QuoteDataSource,
    SimulatedQuoteSource,
    RealTimeQuoteService,
    PriceAlertManager,
    create_quote_service,
    WEBSOCKETS_AVAILABLE,
)

# 可选导出 WebSocket 服务器
if WEBSOCKETS_AVAILABLE:
    from src.realtime.quote_service import WebSocketQuoteServer
    __all__ = [
        "QuoteEventType",
        "QuoteData",
        "QuoteCallback",
        "QuoteSubscriber",
        "QuotePublisher",
        "QuoteDataSource",
        "SimulatedQuoteSource",
        "RealTimeQuoteService",
        "PriceAlertManager",
        "WebSocketQuoteServer",
        "create_quote_service",
        "WEBSOCKETS_AVAILABLE",
    ]
else:
    __all__ = [
        "QuoteEventType",
        "QuoteData",
        "QuoteCallback",
        "QuoteSubscriber",
        "QuotePublisher",
        "QuoteDataSource",
        "SimulatedQuoteSource",
        "RealTimeQuoteService",
        "PriceAlertManager",
        "create_quote_service",
        "WEBSOCKETS_AVAILABLE",
    ]
