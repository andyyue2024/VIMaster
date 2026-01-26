"""
股权思维 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext

logger = logging.getLogger(__name__)


class EquityThinkingAgent(BaseAgent):
    """
    Agent 1: 股权思维 Agent
    将股票视为企业所有权，关注企业长期经营利润的增长
    """

    def __init__(self):
        super().__init__(
            name="股权思维Agent",
            description="企业所有权分析与长期利润增长评估"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        分析股权思维指标
        评估企业的长期盈利能力和增长潜力
        """
        if not context.financial_metrics:
            logger.warning(f"股票 {context.stock_code} 缺少财务指标数据")
            return context

        metrics = context.financial_metrics

        # 评估盈利能力
        profit_score = 0.0
        if metrics.roe and metrics.roe > 0.15:  # ROE > 15% 表示优秀
            profit_score += 7
        elif metrics.roe and metrics.roe > 0.10:  # ROE > 10% 表示良好
            profit_score += 5
        else:
            profit_score += 2

        # 评估增长潜力
        growth_score = 0.0
        if metrics.profit_growth and metrics.profit_growth > 0.15:  # 利润增长 > 15%
            growth_score += 7
        elif metrics.profit_growth and metrics.profit_growth > 0.05:
            growth_score += 5
        else:
            growth_score += 2

        # 评估现金流质量
        cash_flow_score = 0.0
        if metrics.free_cash_flow and metrics.free_cash_flow > 0:
            cash_flow_score += 7
        else:
            cash_flow_score += 2

        # 综合股权思维得分
        equity_thinking_score = (profit_score + growth_score + cash_flow_score) / 3

        # 记录分析结果
        analysis_log = f"""
[股权思维分析]
- 盈利能力评分: {profit_score:.1f}/10 (ROE: {metrics.roe or 'N/A'})
- 增长潜力评分: {growth_score:.1f}/10 (利润增长: {metrics.profit_growth or 'N/A'})
- 现金流质量: {cash_flow_score:.1f}/10
- 综合评分: {equity_thinking_score:.1f}/10
"""
        logger.info(analysis_log)

        # 更新上下文（为后续Agent提供基础信息）
        context.overall_score += equity_thinking_score / 9  # 9个Agent，均分

        return context
