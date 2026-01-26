"""
卖出纪律 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext, SellSignalAnalysis, InvestmentSignal

logger = logging.getLogger(__name__)


class SellSignalAgent(BaseAgent):
    """
    Agent 7: 卖出纪律 Agent
    识别卖出信号：基本面恶化、严重高估、存在更好机会
    """

    def __init__(self):
        super().__init__(
            name="卖出纪律Agent",
            description="卖出信号识别"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        卖出信号分析
        """
        sell_signal = SellSignalAnalysis(stock_code=context.stock_code)

        if not context.valuation or not context.financial_metrics:
            context.sell_signal = sell_signal
            return context

        valuation = context.valuation
        metrics = context.financial_metrics

        # 判断基本面恶化
        if metrics.profit_growth and metrics.profit_growth < -0.20:
            sell_signal.fundamental_deterioration = True

        # 判断严重高估
        if metrics.pe_ratio and metrics.pe_ratio > 30:
            sell_signal.is_severely_overvalued = True
        elif valuation.valuation_score and valuation.valuation_score < 2:
            sell_signal.is_severely_overvalued = True

        # 判断是否存在更好机会（当前投资分数较低且有负面信号）
        if context.overall_score < 4 and sell_signal.fundamental_deterioration:
            sell_signal.better_opportunity_exists = True

        # 综合卖出信号
        sell_factors = sum([
            sell_signal.fundamental_deterioration,
            sell_signal.is_severely_overvalued,
            sell_signal.better_opportunity_exists
        ])

        # 确定卖出信号
        if sell_factors >= 2:
            sell_signal.sell_signal = InvestmentSignal.STRONG_SELL
            sell_signal.confidence_score = 0.9
        elif sell_factors >= 1:
            sell_signal.sell_signal = InvestmentSignal.SELL
            sell_signal.confidence_score = 0.7
        else:
            sell_signal.sell_signal = InvestmentSignal.HOLD
            sell_signal.confidence_score = 0.0

        if metrics.current_price:
            sell_signal.recommended_sell_price = metrics.current_price

        analysis_log = f"""
[卖出纪律分析]
- 基本面恶化: {sell_signal.fundamental_deterioration}
- 严重高估: {sell_signal.is_severely_overvalued}
- 更好机会: {sell_signal.better_opportunity_exists}
- 卖出信号: {sell_signal.sell_signal.value}
- 置信度: {sell_signal.confidence_score:.2f}
"""
        logger.info(analysis_log)

        context.sell_signal = sell_signal

        return context
