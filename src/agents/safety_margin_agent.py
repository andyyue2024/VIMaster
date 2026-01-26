"""
安全边际 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext

logger = logging.getLogger(__name__)


class SafetyMarginAgent(BaseAgent):
    """
    Agent 5: 安全边际 Agent
    分析价格与内在价值的差异，确定安全边际
    """

    def __init__(self):
        super().__init__(
            name="安全边际Agent",
            description="价格与价值差异分析"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        安全边际分析
        """
        if not context.valuation or not context.financial_metrics:
            return context

        valuation = context.valuation
        metrics = context.financial_metrics

        if not valuation.fair_price or not metrics.current_price:
            return context

        # 计算安全边际
        margin = (valuation.fair_price - metrics.current_price) / valuation.fair_price
        valuation.margin_of_safety = margin * 100

        # 判断是否存在安全边际
        if margin >= 0.20:  # 安全边际 >= 20%
            context.safety_margin_ok = True
            margin_score = 10.0
        elif margin >= 0.10:  # 安全边际 >= 10%
            context.safety_margin_ok = True
            margin_score = 7.0
        elif margin >= 0:  # 安全边际 >= 0
            context.safety_margin_ok = True
            margin_score = 5.0
        else:
            context.safety_margin_ok = False
            margin_score = 1.0

        analysis_log = f"""
[安全边际分析]
- 合理价格: {valuation.fair_price:.2f}
- 当前价格: {metrics.current_price:.2f}
- 安全边际: {valuation.margin_of_safety:.2f}%
- 安全边际评分: {margin_score:.1f}/10
"""
        logger.info(analysis_log)

        context.overall_score += margin_score / 90

        return context
