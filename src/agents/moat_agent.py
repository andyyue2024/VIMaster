"""
护城河 Agent
"""
import logging
from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext
from src.data.akshare_provider import AkshareDataProvider

logger = logging.getLogger(__name__)


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
        moat = None
        try:
            from src.models.data_models import CompetitiveModality
            moat = CompetitiveModality()
        except Exception:
            logger.exception("无法导入 CompetitiveModality 类型，跳过护城河分析")

        if moat and metrics:
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

        if moat:
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
