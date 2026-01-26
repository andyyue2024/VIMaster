"""
心理纪律 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext, InvestmentDecision, InvestmentSignal, RiskLevel

logger = logging.getLogger(__name__)


class BehavioralDisciplineAgent(BaseAgent):
    """
    Agent 9: 心理纪律 Agent
    生成行为纪律和投资决策检查清单
    """

    def __init__(self):
        super().__init__(
            name="心理纪律Agent",
            description="行为纪律与投资决策检查清单"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        生成投资决策和行为纪律建议
        """
        decision = InvestmentDecision(stock_code=context.stock_code)

        # 基于各Agent的分析结果生成综合决策
        final_signal = InvestmentSignal.HOLD
        conviction_level = 0.0

        # 综合买入和卖出信号
        if context.sell_signal and context.sell_signal.sell_signal != InvestmentSignal.HOLD:
            final_signal = context.sell_signal.sell_signal
            conviction_level = context.sell_signal.confidence_score
        elif context.buy_signal and context.buy_signal.buy_signal != InvestmentSignal.HOLD:
            final_signal = context.buy_signal.buy_signal
            conviction_level = context.buy_signal.confidence_score
        else:
            final_signal = InvestmentSignal.HOLD
            conviction_level = 0.0

        decision.decision = final_signal
        decision.conviction_level = conviction_level

        # 设置交易价格
        if context.financial_metrics:
            decision.action_price = context.financial_metrics.current_price

            # 根据风险等级设置止损和止盈
            if context.risk_assessment:
                if context.risk_assessment.overall_risk_level == RiskLevel.LOW:
                    decision.stop_loss_price = context.financial_metrics.current_price * 0.85
                    decision.take_profit_price = context.financial_metrics.current_price * 1.30
                elif context.risk_assessment.overall_risk_level == RiskLevel.MEDIUM:
                    decision.stop_loss_price = context.financial_metrics.current_price * 0.90
                    decision.take_profit_price = context.financial_metrics.current_price * 1.20
                elif context.risk_assessment.overall_risk_level == RiskLevel.HIGH:
                    decision.stop_loss_price = context.financial_metrics.current_price * 0.92
                    decision.take_profit_price = context.financial_metrics.current_price * 1.15
                else:
                    decision.stop_loss_price = context.financial_metrics.current_price * 0.95
                    decision.take_profit_price = context.financial_metrics.current_price * 1.10

        # 仓位大小（基于风险等级）
        if context.risk_assessment:
            if context.risk_assessment.overall_risk_level == RiskLevel.LOW:
                decision.position_size = 0.8
            elif context.risk_assessment.overall_risk_level == RiskLevel.MEDIUM:
                decision.position_size = 0.6
            elif context.risk_assessment.overall_risk_level == RiskLevel.HIGH:
                decision.position_size = 0.4
            else:
                decision.position_size = 0.2

        # 投资决策检查清单
        checklist_items = [
            context.safety_margin_ok,  # 1. 有安全边际吗？
            context.overall_score >= 5,  # 2. 综合评分达到及格线吗？
            context.financial_metrics and context.financial_metrics.roe and context.financial_metrics.roe > 0.10,  # 3. ROE > 10%？
            context.competitive_moat and context.competitive_moat.overall_score >= 5,  # 4. 有护城河吗？
            not (context.risk_assessment and context.risk_assessment.overall_risk_level == RiskLevel.VERY_HIGH),  # 5. 风险可控吗？
        ]

        decision.checklist_passed = all(checklist_items)

        analysis_log = f"""
[心理纪律分析]
- 最终决策: {decision.decision.value}
- 信念强度: {decision.conviction_level:.2f}
- 建议执行价: {decision.action_price or 'N/A'}
- 止损价: {decision.stop_loss_price or 'N/A'}
- 止盈价: {decision.take_profit_price or 'N/A'}
- 建议仓位: {decision.position_size:.2f}
- 决策检查清单通过: {decision.checklist_passed}
"""
        logger.info(analysis_log)

        context.investment_decision = decision
        context.final_signal = final_signal

        return context
