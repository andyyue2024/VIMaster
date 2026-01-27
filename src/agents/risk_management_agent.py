"""
风险管理 Agent - 支持参数化配置
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext, RiskAssessment, RiskLevel
from src.agents.agent_config import AgentConfigManager

logger = logging.getLogger(__name__)


class RiskManagementAgent(BaseAgent):
    """
    Agent 8: 风险管理 Agent
    评估风险：能力圈、杠杆、行业风险、公司风险
    支持通过 AgentConfigManager 动态配置参数
    """

    def __init__(self):
        super().__init__(
            name="风险管理Agent",
            description="风险评估与规避"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        风险评估（使用配置化阈值）
        """
        # 获取配置
        cfg = AgentConfigManager.get_risk_management_config()

        risk_assessment = RiskAssessment(stock_code=context.stock_code)

        if context.financial_metrics:
            metrics = context.financial_metrics

            # 能力圈匹配度
            risk_assessment.ability_circle_match = context.overall_score / 10

            # 杠杆风险（基于负债率阈值）
            if metrics.debt_ratio and metrics.debt_ratio < 0.30:
                risk_assessment.leverage_risk = 0.2
            elif metrics.debt_ratio and metrics.debt_ratio < 0.50:
                risk_assessment.leverage_risk = 0.4
            elif metrics.debt_ratio and metrics.debt_ratio < 0.70:
                risk_assessment.leverage_risk = 0.6
            else:
                risk_assessment.leverage_risk = 0.8

        # 行业风险
        if context.competitive_moat:
            moat_score = context.competitive_moat.overall_score / 10
            risk_assessment.industry_risk = 1 - moat_score
        else:
            risk_assessment.industry_risk = 0.5

        # 公司风险
        risk_assessment.company_risk = 1 - (context.overall_score / 10)

        # 综合风险等级（使用配置化阈值）
        overall_risk = (
            risk_assessment.leverage_risk * 0.3 +
            risk_assessment.industry_risk * 0.3 +
            risk_assessment.company_risk * 0.4
        )

        # 转换为 0-10 分数并使用配置阈值
        risk_score = overall_risk * 10
        if risk_score < cfg.low_risk_threshold:
            risk_assessment.overall_risk_level = RiskLevel.LOW
        elif risk_score < cfg.medium_risk_threshold:
            risk_assessment.overall_risk_level = RiskLevel.MEDIUM
        elif risk_score < cfg.high_risk_threshold:
            risk_assessment.overall_risk_level = RiskLevel.HIGH
        else:
            risk_assessment.overall_risk_level = RiskLevel.VERY_HIGH

        # 风险缓解策略
        risk_assessment.risk_mitigation_strategies = []
        if risk_assessment.ability_circle_match < 0.5:
            risk_assessment.risk_mitigation_strategies.append("加强行业研究，确保在能力圈内")
        if risk_assessment.leverage_risk > 0.6:
            risk_assessment.risk_mitigation_strategies.append("警惕公司高负债率，降低仓位")
        if risk_assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            risk_assessment.risk_mitigation_strategies.append(
                f"设置止损点 {cfg.default_stop_loss:.0%}，控制风险"
            )

        analysis_log = f"""
[风险管理分析]
- 能力圈匹配度: {risk_assessment.ability_circle_match:.2f}/1.0
- 杠杆风险: {risk_assessment.leverage_risk:.2f}/1.0
- 行业风险: {risk_assessment.industry_risk:.2f}/1.0
- 公司风险: {risk_assessment.company_risk:.2f}/1.0
- 综合风险等级: {risk_assessment.overall_risk_level.value}
- 止损设置: {cfg.default_stop_loss:.0%}, 止盈设置: {cfg.default_take_profit:.0%}
- 风险缓解策略: {', '.join(risk_assessment.risk_mitigation_strategies) if risk_assessment.risk_mitigation_strategies else '无'}
"""
        logger.info(analysis_log)

        context.risk_assessment = risk_assessment

        return context
