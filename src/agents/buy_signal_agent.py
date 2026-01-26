"""
买入点 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext, BuySignalAnalysis, InvestmentSignal

logger = logging.getLogger(__name__)


class BuySignalAgent(BaseAgent):
    """
    Agent 6: 买入点 Agent
    识别买入时机：市场极度悲观、公司遭遇暂时困难、市场误解
    """

    def __init__(self):
        super().__init__(
            name="买入点Agent",
            description="买入时机识别"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        买入点分析
        """
        buy_signal = BuySignalAnalysis(stock_code=context.stock_code)

        if not context.valuation or not context.financial_metrics:
            context.buy_signal = buy_signal
            return context

        valuation = context.valuation
        metrics = context.financial_metrics

        # 判断市场极度悲观（PE很低）
        if metrics.pe_ratio and metrics.pe_ratio < 10:
            buy_signal.is_extreme_pessimism = True

        # 判断公司遭遇暂时困难（但基本面良好）
        if metrics.profit_growth and metrics.profit_growth < -0.10 and context.overall_score > 5:
            buy_signal.has_temporary_difficulty = True

        # 判断市场误解（价格相对于基本面显著低估）
        if context.safety_margin_ok and valuation.margin_of_safety and valuation.margin_of_safety > 15:
            buy_signal.is_market_misunderstanding = True

        # 综合买入信号
        buy_factors = sum([
            buy_signal.is_extreme_pessimism,
            buy_signal.has_temporary_difficulty,
            buy_signal.is_market_misunderstanding,
            context.safety_margin_ok
        ])

        if metrics.current_price and valuation.fair_price:
            buy_signal.price_to_fair_ratio = metrics.current_price / valuation.fair_price

        # 确定买入信号
        if buy_factors >= 3 and valuation.valuation_score >= 8:
            buy_signal.buy_signal = InvestmentSignal.STRONG_BUY
            buy_signal.confidence_score = 0.9
            buy_signal.recommended_buy_price = metrics.current_price
        elif buy_factors >= 2 and valuation.valuation_score >= 7:
            buy_signal.buy_signal = InvestmentSignal.BUY
            buy_signal.confidence_score = 0.7
            buy_signal.recommended_buy_price = metrics.current_price
        elif buy_factors >= 1 and context.safety_margin_ok:
            buy_signal.buy_signal = InvestmentSignal.HOLD
            buy_signal.confidence_score = 0.5
        else:
            buy_signal.buy_signal = InvestmentSignal.HOLD
            buy_signal.confidence_score = 0.0

        analysis_log = f"""
[买入点分析]
- 市场极度悲观: {buy_signal.is_extreme_pessimism}
- 暂时性困难: {buy_signal.has_temporary_difficulty}
- 市场误解: {buy_signal.is_market_misunderstanding}
- 价格/合理价比率: {buy_signal.price_to_fair_ratio or 'N/A'}
- 买入信号: {buy_signal.buy_signal.value}
- 置信度: {buy_signal.confidence_score:.2f}
"""
        logger.info(analysis_log)

        context.buy_signal = buy_signal

        return context
