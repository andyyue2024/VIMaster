"""
综合分析模块 - 整合所有分析功能
"""
import logging
from typing import List, Dict, Any, Optional
from src.analysis.industry_comparator import IndustryComparator
from src.analysis.valuation_history_analyzer import ValuationAnalyzer
from src.analysis.portfolio_optimizer import PortfolioOptimizer, PortfolioStrategy
from src.schedulers.workflow_scheduler import AnalysisManager

logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """综合分析器 - 整合行业对比、历史估值和投资组合优化"""

    def __init__(self):
        """初始化综合分析器"""
        self.industry_comparator = IndustryComparator()
        self.valuation_analyzer = ValuationAnalyzer()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.analysis_manager = AnalysisManager()

    def analyze_stock_comprehensive(
        self,
        stock_code: str,
        industry: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        进行股票综合分析
        Args:
            stock_code: 股票代码
            industry: 行业（如果为None则自动获取）
        Returns:
            综合分析结果
        """
        try:
            logger.info(f"进行 {stock_code} 的综合分析")

            # 1. 基础分析（价值投资分析）
            context = self.analysis_manager.analyze_single_stock(stock_code)
            if not context:
                logger.warning(f"无法分析股票 {stock_code}")
                return None

            result = {
                "stock_code": stock_code,
                "basic_analysis": self._context_to_dict(context),
            }

            # 2. 历史估值分析
            valuation_comparison = self.valuation_analyzer.compare_valuation_history(stock_code)
            if valuation_comparison:
                result["valuation_history"] = valuation_comparison.to_dict()

            # 3. 行业对比分析
            if industry:
                industry_comparison = self.industry_comparator.compare_stock_with_industry(
                    stock_code, industry
                )
                if industry_comparison:
                    result["industry_comparison"] = industry_comparison.to_dict()

            return result
        except Exception as e:
            logger.error(f"综合分析 {stock_code} 失败: {str(e)}")
            return None

    def analyze_portfolio_comprehensive(
        self,
        stock_codes: List[str],
        strategy: PortfolioStrategy = PortfolioStrategy.BALANCED
    ) -> Optional[Dict[str, Any]]:
        """
        进行投资组合综合分析和优化
        Args:
            stock_codes: 股票代码列表
            strategy: 投资策略
        Returns:
            投资组合分析和建议
        """
        try:
            logger.info(f"进行投资组合综合分析: {len(stock_codes)} 只股票, 策略: {strategy.value}")

            # 1. 分析所有股票
            stock_analyses = []
            for code in stock_codes:
                analysis = self.analyze_stock_comprehensive(code)
                if analysis:
                    stock_analyses.append(analysis)

            if not stock_analyses:
                logger.warning("无法分析任何股票")
                return None

            # 2. 生成投资组合建议
            recommendation = self.portfolio_optimizer.generate_portfolio_recommendation(
                stock_analyses,
                strategy=strategy,
                portfolio_size=min(5, len(stock_analyses))
            )

            if not recommendation:
                logger.warning("无法生成投资组合建议")
                return None

            # 3. 计算投资组合指标
            metrics = self.portfolio_optimizer.calculate_portfolio_metrics(
                [
                    {
                        "stock_code": p.stock_code,
                        "weight": p.weight,
                        "overall_score": next(
                            (a.get("basic_analysis", {}).get("overall_score", 5.0)
                             for a in stock_analyses if a.get("stock_code") == p.stock_code),
                            5.0
                        ),
                        "risk_level": 5.0,
                    }
                    for p in recommendation.positions
                ]
            )

            return {
                "stock_analyses": stock_analyses,
                "portfolio_recommendation": recommendation.to_dict(),
                "portfolio_metrics": metrics,
            }
        except Exception as e:
            logger.error(f"投资组合综合分析失败: {str(e)}")
            return None

    def compare_industries_with_stocks(
        self,
        industries: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        对比多个行业及其代表股票
        Args:
            industries: 行业列表
        Returns:
            行业对比分析
        """
        try:
            logger.info(f"对比行业: {industries}")

            # 1. 对比行业
            industry_results = self.industry_comparator.compare_multiple_industries(industries)
            if not industry_results:
                logger.warning("无法对比行业")
                return None

            # 2. 分析每个行业的代表股票
            industry_analyses = {}
            for industry in industries:
                stocks = self.industry_comparator.get_industry_stocks(industry)
                if stocks:
                    # 分析前三只股票
                    stock_analyses = []
                    for code in stocks[:3]:
                        analysis = self.analyze_stock_comprehensive(code, industry)
                        if analysis:
                            stock_analyses.append(analysis)

                    industry_analyses[industry] = {
                        "stocks": stock_analyses,
                        "metrics": industry_results.get(industry, {}).to_dict()
                                  if industry_results.get(industry) else {},
                    }

            return {
                "industries": industry_analyses,
                "industry_count": len(industry_analyses),
            }
        except Exception as e:
            logger.error(f"行业对比分析失败: {str(e)}")
            return None

    def generate_investment_recommendations(
        self,
        stock_codes: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        生成综合投资建议
        Args:
            stock_codes: 股票代码列表
        Returns:
            投资建议
        """
        try:
            logger.info(f"生成综合投资建议: {len(stock_codes)} 只股票")

            # 分类股票
            buy_stocks = []
            hold_stocks = []
            sell_stocks = []

            # 分析每只股票
            for code in stock_codes:
                analysis = self.analyze_stock_comprehensive(code)
                if analysis:
                    signal = analysis.get("basic_analysis", {}).get("investment_decision", {}).get("decision", "")

                    if "强烈买入" in str(signal) or "买入" in str(signal):
                        buy_stocks.append(analysis)
                    elif "卖出" in str(signal):
                        sell_stocks.append(analysis)
                    else:
                        hold_stocks.append(analysis)

            # 生成建议
            recommendations = {
                "buy_stocks": {
                    "count": len(buy_stocks),
                    "stocks": buy_stocks,
                    "summary": f"建议购买 {len(buy_stocks)} 只股票，这些股票具有良好的投资机会"
                },
                "hold_stocks": {
                    "count": len(hold_stocks),
                    "stocks": hold_stocks,
                    "summary": f"建议持有 {len(hold_stocks)} 只股票，继续观察其表现"
                },
                "sell_stocks": {
                    "count": len(sell_stocks),
                    "stocks": sell_stocks,
                    "summary": f"建议卖出 {len(sell_stocks)} 只股票，这些股票可能被高估或基本面恶化"
                },
                "total_stocks": len(stock_codes),
            }

            return recommendations
        except Exception as e:
            logger.error(f"生成综合投资建议失败: {str(e)}")
            return None

    # 辅助方法

    @staticmethod
    def _context_to_dict(context) -> Dict[str, Any]:
        """将分析上下文转换为字典"""
        try:
            result = {
                "stock_code": context.stock_code,
                "overall_score": context.overall_score,
                "final_signal": context.final_signal.value if context.final_signal else "未评级",
            }

            if context.financial_metrics:
                result["financial_metrics"] = {
                    "current_price": context.financial_metrics.current_price,
                    "pe_ratio": context.financial_metrics.pe_ratio,
                    "pb_ratio": context.financial_metrics.pb_ratio,
                    "roe": context.financial_metrics.roe,
                    "gross_margin": context.financial_metrics.gross_margin,
                    "free_cash_flow": context.financial_metrics.free_cash_flow,
                    "debt_ratio": context.financial_metrics.debt_ratio,
                }

            if context.competitive_moat:
                result["competitive_moat"] = {
                    "overall_score": context.competitive_moat.overall_score,
                    "brand_strength": context.competitive_moat.brand_strength,
                    "cost_advantage": context.competitive_moat.cost_advantage,
                }

            if context.valuation:
                result["valuation"] = {
                    "intrinsic_value": context.valuation.intrinsic_value,
                    "fair_price": context.valuation.fair_price,
                    "margin_of_safety": context.valuation.margin_of_safety,
                    "valuation_score": context.valuation.valuation_score,
                }

            if context.investment_decision:
                result["investment_decision"] = {
                    "decision": context.investment_decision.decision.value,
                    "conviction_level": context.investment_decision.conviction_level,
                    "position_size": context.investment_decision.position_size,
                    "stop_loss_price": context.investment_decision.stop_loss_price,
                    "take_profit_price": context.investment_decision.take_profit_price,
                }

            if context.risk_assessment:
                result["risk_assessment"] = {
                    "overall_risk_level": context.risk_assessment.overall_risk_level.value,
                    "ability_circle_match": context.risk_assessment.ability_circle_match,
                    "leverage_risk": context.risk_assessment.leverage_risk,
                }

            return result
        except Exception as e:
            logger.error(f"转换上下文失败: {str(e)}")
            return {}
