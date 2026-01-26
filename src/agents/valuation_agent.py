"""
估值 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext, ValuationAnalysis

logger = logging.getLogger(__name__)


class ValuationAgent(BaseAgent):
    """
    Agent 4: 估值 Agent
    综合DCF、PE、PB等方法评估内在价值
    """

    def __init__(self):
        super().__init__(
            name="估值Agent",
            description="内在价值评估（DCF、PE、PB）"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        估值分析
        """
        if not context.financial_metrics:
            return context

        metrics = context.financial_metrics
        valuation = ValuationAnalysis(stock_code=context.stock_code)

        # PE 估值
        if metrics.pe_ratio and metrics.pe_ratio > 0:
            # 假设行业平均PE为20
            fair_pe = 20
            valuation.pe_valuation = metrics.current_price / metrics.pe_ratio * fair_pe if metrics.pe_ratio != 0 else metrics.current_price

        # PB 估值
        if metrics.pb_ratio and metrics.pb_ratio > 0:
            fair_pb = 3.0  # 假设行业平均PB为3
            valuation.pb_valuation = metrics.current_price / metrics.pb_ratio * fair_pb if metrics.pb_ratio != 0 else metrics.current_price

        # DCF 简化估值（基于EPS和合理PE）
        if metrics.earnings_per_share and metrics.earnings_per_share > 0:
            # 假设未来增长率10%，合理PE为15
            future_eps = metrics.earnings_per_share * 1.10
            valuation.dcf_value = future_eps * 15

        # 综合估值
        valuations = [v for v in [valuation.pe_valuation, valuation.pb_valuation, valuation.dcf_value] if v]
        if valuations:
            valuation.intrinsic_value = sum(valuations) / len(valuations)
            valuation.fair_price = valuation.intrinsic_value
        else:
            valuation.intrinsic_value = metrics.current_price
            valuation.fair_price = metrics.current_price

        # 估值评分
        if metrics.current_price and valuation.fair_price:
            ratio = metrics.current_price / valuation.fair_price
            if ratio < 0.70:  # 低估30%以上
                valuation.valuation_score = 10.0
            elif ratio < 0.85:
                valuation.valuation_score = 8.0
            elif ratio < 1.0:
                valuation.valuation_score = 7.0
            elif ratio < 1.15:
                valuation.valuation_score = 5.0
            elif ratio < 1.30:
                valuation.valuation_score = 3.0
            else:
                valuation.valuation_score = 1.0

        valuation.current_price = metrics.current_price

        analysis_log = f"""
[估值分析]
- 当前价格: {metrics.current_price or 'N/A'}
- 内在价值: {valuation.intrinsic_value:.2f}
- PE估值: {valuation.pe_valuation or 'N/A'}
- PB估值: {valuation.pb_valuation or 'N/A'}
- DCF估值: {valuation.dcf_value or 'N/A'}
- 估值评分: {valuation.valuation_score:.1f}/10
"""
        logger.info(analysis_log)

        context.valuation = valuation
        context.overall_score += valuation.valuation_score / 90

        return context
