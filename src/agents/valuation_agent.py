"""
估值 Agent - 支持参数化配置
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext, ValuationAnalysis
from src.agents.agent_config import AgentConfigManager

logger = logging.getLogger(__name__)


class ValuationAgent(BaseAgent):
    """
    Agent 4: 估值 Agent
    综合DCF、PE、PB等方法评估内在价值
    支持通过 AgentConfigManager 动态配置参数
    """

    def __init__(self):
        super().__init__(
            name="估值Agent",
            description="内在价值评估（DCF、PE、PB）"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        估值分析（使用配置化参数）
        """
        if not context.financial_metrics:
            return context

        # 获取配置
        cfg = AgentConfigManager.get_valuation_config()

        metrics = context.financial_metrics
        valuation = ValuationAnalysis(stock_code=context.stock_code)

        # PE 估值（使用配置的合理 PE）
        if metrics.pe_ratio and metrics.pe_ratio > 0:
            fair_pe = cfg.pe_ratio_fair
            valuation.pe_valuation = metrics.current_price / metrics.pe_ratio * fair_pe if metrics.pe_ratio != 0 else metrics.current_price

        # PB 估值（使用配置的合理 PB）
        if metrics.pb_ratio and metrics.pb_ratio > 0:
            fair_pb = cfg.pb_ratio_fair
            valuation.pb_valuation = metrics.current_price / metrics.pb_ratio * fair_pb if metrics.pb_ratio != 0 else metrics.current_price

        # DCF 简化估值（使用配置的折现率和增长率）
        if metrics.earnings_per_share and metrics.earnings_per_share > 0:
            growth_rate = cfg.terminal_growth_rate
            discount_rate = cfg.discount_rate
            # 简化 DCF：未来 EPS × 合理 PE
            future_eps = metrics.earnings_per_share * (1 + growth_rate)
            # 折现因子近似
            discount_factor = 1 / (1 + discount_rate)
            valuation.dcf_value = future_eps * cfg.pe_ratio_fair * discount_factor

        # 加权综合估值（使用配置权重）
        pe_val = valuation.pe_valuation or 0
        pb_val = valuation.pb_valuation or 0
        dcf_val = valuation.dcf_value or 0

        total_weight = 0
        weighted_sum = 0
        if pe_val > 0:
            weighted_sum += pe_val * cfg.weight_pe
            total_weight += cfg.weight_pe
        if pb_val > 0:
            weighted_sum += pb_val * cfg.weight_pb
            total_weight += cfg.weight_pb
        if dcf_val > 0:
            weighted_sum += dcf_val * cfg.weight_dcf
            total_weight += cfg.weight_dcf

        if total_weight > 0:
            valuation.intrinsic_value = weighted_sum / total_weight
            valuation.fair_price = valuation.intrinsic_value
        else:
            valuation.intrinsic_value = metrics.current_price
            valuation.fair_price = metrics.current_price

        # 估值评分
        if metrics.current_price and valuation.fair_price:
            ratio = metrics.current_price / valuation.fair_price
            if ratio < 0.70:
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
- PE估值: {valuation.pe_valuation or 'N/A'} (权重: {cfg.weight_pe})
- PB估值: {valuation.pb_valuation or 'N/A'} (权重: {cfg.weight_pb})
- DCF估值: {valuation.dcf_value or 'N/A'} (权重: {cfg.weight_dcf})
- 估值评分: {valuation.valuation_score:.1f}/10
"""
        logger.info(analysis_log)

        context.valuation = valuation
        context.overall_score += valuation.valuation_score / 90

        return context
