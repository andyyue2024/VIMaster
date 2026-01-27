"""
财务分析 Agent - 支持参数化配置
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext
from src.agents.agent_config import AgentConfigManager

logger = logging.getLogger(__name__)


class FinancialAnalysisAgent(BaseAgent):
    """
    Agent 3: 财务分析 Agent
    评估财务状况：ROE、毛利率、自由现金流、负债率
    支持通过 AgentConfigManager 动态配置阈值和权重
    """

    def __init__(self):
        super().__init__(
            name="财务分析Agent",
            description="财务指标评估（ROE、毛利率、自由现金流、负债率）"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        分析财务指标（使用配置化阈值）
        """
        if not context.financial_metrics:
            logger.warning(f"股票 {context.stock_code} 缺少财务指标数据")
            return context

        # 获取配置
        cfg = AgentConfigManager.get_financial_config()

        metrics = context.financial_metrics
        financial_score = 0.0

        # ROE 评估（使用配置阈值）
        roe_score = 0.0
        if metrics.roe:
            if metrics.roe > cfg.roe_excellent:
                roe_score = 10.0
            elif metrics.roe > cfg.roe_good:
                roe_score = 8.0
            elif metrics.roe > cfg.roe_minimum:
                roe_score = 6.0
            elif metrics.roe > 0.05:
                roe_score = 4.0
            else:
                roe_score = 2.0

        # 毛利率评估（使用配置阈值）
        margin_score = 0.0
        if metrics.gross_margin:
            if metrics.gross_margin > cfg.gross_margin_excellent:
                margin_score = 10.0
            elif metrics.gross_margin > cfg.gross_margin_good:
                margin_score = 8.0
            elif metrics.gross_margin > cfg.gross_margin_minimum:
                margin_score = 6.0
            else:
                margin_score = 3.0

        # 自由现金流评估
        fcf_score = 0.0
        if metrics.free_cash_flow and metrics.free_cash_flow > 0:
            fcf_score = 8.0
        elif metrics.free_cash_flow and metrics.free_cash_flow > -1000000000:
            fcf_score = 5.0
        else:
            if cfg.require_positive_fcf:
                fcf_score = 2.0
            else:
                fcf_score = 4.0

        # 负债率评估（使用配置阈值）
        debt_score = 0.0
        if metrics.debt_ratio:
            if metrics.debt_ratio < cfg.debt_ratio_safe:
                debt_score = 10.0
            elif metrics.debt_ratio < cfg.debt_ratio_warning:
                debt_score = 6.0
            elif metrics.debt_ratio < cfg.debt_ratio_danger:
                debt_score = 4.0
            else:
                debt_score = 2.0
        else:
            debt_score = 5.0

        # 加权计算（使用配置权重）
        financial_score = (
            roe_score * cfg.weight_roe +
            margin_score * cfg.weight_gross_margin +
            fcf_score * cfg.weight_fcf +
            debt_score * cfg.weight_debt_ratio
        )

        analysis_log = f"""
[财务分析]
- ROE评分: {roe_score:.1f}/10 (ROE: {metrics.roe or 'N/A'}, 阈值: >{cfg.roe_excellent})
- 毛利率评分: {margin_score:.1f}/10 (毛利率: {metrics.gross_margin or 'N/A'})
- 自由现金流: {fcf_score:.1f}/10
- 负债率评分: {debt_score:.1f}/10 (负债率: {metrics.debt_ratio or 'N/A'})
- 综合财务评分: {financial_score:.1f}/10
"""
        logger.info(analysis_log)

        context.overall_score += financial_score / 90

        return context
