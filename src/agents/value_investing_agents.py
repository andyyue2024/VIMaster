"""
价值投资 Agent 实现
包含 9 个核心 Agent：
1. 股权思维 Agent - 企业所有权与长期增长分析
2. 护城河 Agent - 竞争优势分析
3. 财务分析 Agent - 财务指标评估
4. 估值 Agent - 内在价值与合理价格评估
5. 安全边际 Agent - 价格与价值差异分析
6. 买入点 Agent - 买入时机识别
7. 卖出纪律 Agent - 卖出信号识别
8. 风险管理 Agent - 风险评估与规避
9. 心理纪律 Agent - 行为纪律与决策检查清单
"""
import logging
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.models.data_models import (
    StockAnalysisContext, CompetitiveModality, ValuationAnalysis,
    BuySignalAnalysis, SellSignalAnalysis, RiskAssessment, RiskLevel,
    InvestmentSignal, InvestmentDecision, FinancialMetrics
)
from src.data.akshare_provider import AkshareDataProvider, DataValidator

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


class MoatAgent(BaseAgent):
    """
    Agent 2: 护城河 Agent
    分析企业的竞争优势（品牌、成本、网络效应、转换成本等）
    """

    def __init__(self):
        super().__init__(
            name="护城河Agent",
            description="竞争优势分析"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        分析企业护城河
        """
        metrics = context.financial_metrics

        # 初始化护城河分析
        moat = CompetitiveModality()

        if metrics:
            # 通过毛利率判断品牌强度和成本优势
            if metrics.gross_margin and metrics.gross_margin > 0.40:  # 毛利率 > 40%
                moat.brand_strength = 0.8
                moat.cost_advantage = 0.7
            elif metrics.gross_margin and metrics.gross_margin > 0.20:
                moat.brand_strength = 0.5
                moat.cost_advantage = 0.5
            else:
                moat.brand_strength = 0.2
                moat.cost_advantage = 0.2

            # 通过ROE判断整体竞争优势
            if metrics.roe and metrics.roe > 0.20:  # ROE > 20% 表示强劲护城河
                moat.overall_score = 9.0
            elif metrics.roe and metrics.roe > 0.15:
                moat.overall_score = 7.0
            elif metrics.roe and metrics.roe > 0.10:
                moat.overall_score = 5.0
            else:
                moat.overall_score = 3.0

            # 根据行业特性判断网络效应和转换成本
            industry_info = AkshareDataProvider.get_industry_info(context.stock_code)
            if industry_info:
                industry = industry_info.get('industry', '').lower()
                if any(word in industry for word in ['互联网', '电商', '社交', '平台']):
                    moat.network_effect = 0.8
                    moat.switching_cost = 0.7
                elif any(word in industry for word in ['消费', '食品', '饮料']):
                    moat.brand_strength = 0.8
                    moat.switching_cost = 0.6
                else:
                    moat.network_effect = 0.3
                    moat.switching_cost = 0.3

        moat.description = f"品牌强度: {moat.brand_strength:.1f}/1.0, 成本优势: {moat.cost_advantage:.1f}/1.0, 网络效应: {moat.network_effect:.1f}/1.0, 转换成本: {moat.switching_cost:.1f}/1.0"

        analysis_log = f"""
[护城河分析]
- 品牌强度: {moat.brand_strength:.1f}/1.0
- 成本优势: {moat.cost_advantage:.1f}/1.0
- 网络效应: {moat.network_effect:.1f}/1.0
- 转换成本: {moat.switching_cost:.1f}/1.0
- 综合护城河: {moat.overall_score:.1f}/10.0
"""
        logger.info(analysis_log)

        context.competitive_moat = moat
        context.overall_score += moat.overall_score / 90  # 归一化到0-1

        return context


class FinancialAnalysisAgent(BaseAgent):
    """
    Agent 3: 财务分析 Agent
    评估财务状况：ROE、毛利率、自由现金流、负债率
    """

    def __init__(self):
        super().__init__(
            name="财务分析Agent",
            description="财务指标评估（ROE、毛利率、自由现金流、负债率）"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        分析财务指标
        """
        if not context.financial_metrics:
            logger.warning(f"股票 {context.stock_code} 缺少财务指标数据")
            return context

        metrics = context.financial_metrics
        financial_score = 0.0

        # ROE 评估
        roe_score = 0.0
        if metrics.roe:
            if metrics.roe > 0.20:
                roe_score = 10.0
            elif metrics.roe > 0.15:
                roe_score = 8.0
            elif metrics.roe > 0.10:
                roe_score = 6.0
            elif metrics.roe > 0.05:
                roe_score = 4.0
            else:
                roe_score = 2.0

        # 毛利率评估
        margin_score = 0.0
        if metrics.gross_margin:
            if metrics.gross_margin > 0.50:
                margin_score = 10.0
            elif metrics.gross_margin > 0.40:
                margin_score = 8.0
            elif metrics.gross_margin > 0.20:
                margin_score = 6.0
            else:
                margin_score = 3.0

        # 自由现金流评估
        fcf_score = 0.0
        if metrics.free_cash_flow and metrics.free_cash_flow > 0:
            fcf_score = 8.0
        elif metrics.free_cash_flow and metrics.free_cash_flow > -1000000000:  # 近 10 亿
            fcf_score = 5.0
        else:
            fcf_score = 2.0

        # 负债率评估
        debt_score = 0.0
        if metrics.debt_ratio:
            if metrics.debt_ratio < 0.30:
                debt_score = 10.0
            elif metrics.debt_ratio < 0.50:
                debt_score = 8.0
            elif metrics.debt_ratio < 0.70:
                debt_score = 5.0
            else:
                debt_score = 2.0
        else:
            debt_score = 5.0  # 默认分

        financial_score = (roe_score + margin_score + fcf_score + debt_score) / 4

        analysis_log = f"""
[财务分析]
- ROE评分: {roe_score:.1f}/10 (ROE: {metrics.roe or 'N/A'})
- 毛利率评分: {margin_score:.1f}/10 (毛利率: {metrics.gross_margin or 'N/A'})
- 自由现金流: {fcf_score:.1f}/10
- 负债率评分: {debt_score:.1f}/10 (负债率: {metrics.debt_ratio or 'N/A'})
- 综合财务评分: {financial_score:.1f}/10
"""
        logger.info(analysis_log)

        context.overall_score += financial_score / 90

        return context


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


class RiskManagementAgent(BaseAgent):
    """
    Agent 8: 风险管理 Agent
    评估风险：能力圈、杠杆、行业风险、公司风险
    """

    def __init__(self):
        super().__init__(
            name="风险管理Agent",
            description="风险评估与规避"
        )

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        风险评估
        """
        risk_assessment = RiskAssessment(stock_code=context.stock_code)

        if context.financial_metrics:
            metrics = context.financial_metrics

            # 能力圈匹配度（由用户定义，这里基于行业评分）
            risk_assessment.ability_circle_match = context.overall_score / 10

            # 杠杆风险
            if metrics.debt_ratio and metrics.debt_ratio < 0.30:
                risk_assessment.leverage_risk = 0.2
            elif metrics.debt_ratio and metrics.debt_ratio < 0.50:
                risk_assessment.leverage_risk = 0.4
            elif metrics.debt_ratio and metrics.debt_ratio < 0.70:
                risk_assessment.leverage_risk = 0.6
            else:
                risk_assessment.leverage_risk = 0.8

        # 行业风险（简化评估）
        if context.competitive_moat:
            moat_score = context.competitive_moat.overall_score / 10
            risk_assessment.industry_risk = 1 - moat_score  # 护城河强则风险低
        else:
            risk_assessment.industry_risk = 0.5

        # 公司风险（基于综合评分）
        risk_assessment.company_risk = 1 - (context.overall_score / 10)

        # 综合风险等级
        overall_risk = (
            risk_assessment.leverage_risk * 0.3 +
            risk_assessment.industry_risk * 0.3 +
            risk_assessment.company_risk * 0.4
        )

        if overall_risk < 0.3:
            risk_assessment.overall_risk_level = RiskLevel.LOW
        elif overall_risk < 0.5:
            risk_assessment.overall_risk_level = RiskLevel.MEDIUM
        elif overall_risk < 0.7:
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
            risk_assessment.risk_mitigation_strategies.append("设置止损点，控制风险")

        analysis_log = f"""
[风险管理分析]
- 能力圈匹配度: {risk_assessment.ability_circle_match:.2f}/1.0
- 杠杆风险: {risk_assessment.leverage_risk:.2f}/1.0
- 行业风险: {risk_assessment.industry_risk:.2f}/1.0
- 公司风险: {risk_assessment.company_risk:.2f}/1.0
- 综合风险等级: {risk_assessment.overall_risk_level.value}
- 风险缓解策略: {', '.join(risk_assessment.risk_mitigation_strategies) if risk_assessment.risk_mitigation_strategies else '无'}
"""
        logger.info(analysis_log)

        context.risk_assessment = risk_assessment

        return context


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
