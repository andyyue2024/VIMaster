"""
投资组合优化模块 - 根据分析结果生成投资组合建议
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class PortfolioStrategy(Enum):
    """投资组合策略"""
    GROWTH = "成长型"  # 高成长，高风险
    VALUE = "价值型"  # 低估值，低风险
    BALANCED = "平衡型"  # 均衡配置
    INCOME = "收益型"  # 高分红，稳定收益
    CONSERVATIVE = "保守型"  # 极低风险


@dataclass
class PortfolioPosition:
    """投资组合持仓"""
    stock_code: str
    stock_name: str
    weight: float  # 仓位权重（0-1）
    target_price: Optional[float] = None  # 目标价格
    stop_loss_price: Optional[float] = None  # 止损价格
    take_profit_price: Optional[float] = None  # 止盈价格

    # 风险指标
    risk_level: str = "中等"  # 低、中、高
    volatility: Optional[float] = None  # 波动率

    # 理由
    reason: str = ""  # 选中理由


@dataclass
class PortfolioRecommendation:
    """投资组合建议"""
    strategy: PortfolioStrategy
    positions: List[PortfolioPosition] = field(default_factory=list)

    # 组合指标
    total_weight: float = 0.0  # 总权重（应该等于1.0）
    expected_return: Optional[float] = None  # 预期收益率
    risk_score: float = 5.0  # 风险评分（0-10）
    diversification_score: float = 5.0  # 多样化评分（0-10）

    # 现金配置
    cash_weight: float = 0.0  # 现金比例

    # 建议
    summary: str = ""  # 总结意见

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        positions_data = [
            {
                "stock_code": p.stock_code,
                "weight": p.weight,
                "risk_level": p.risk_level,
                "reason": p.reason,
            }
            for p in self.positions
        ]

        return {
            "strategy": self.strategy.value,
            "positions": positions_data,
            "total_weight": self.total_weight,
            "expected_return": self.expected_return,
            "risk_score": self.risk_score,
            "cash_weight": self.cash_weight,
            "summary": self.summary,
        }


class PortfolioOptimizer:
    """投资组合优化器"""

    def __init__(self):
        """初始化投资组合优化器"""
        pass

    def generate_portfolio_recommendation(
        self,
        stock_analyses: List[Dict[str, Any]],
        strategy: PortfolioStrategy = PortfolioStrategy.BALANCED,
        portfolio_size: int = 5
    ) -> Optional[PortfolioRecommendation]:
        """
        生成投资组合建议
        Args:
            stock_analyses: 股票分析结果列表
            strategy: 投资策略
            portfolio_size: 组合中的股票数量
        Returns:
            PortfolioRecommendation 对象
        """
        try:
            logger.info(f"生成投资组合建议: 策略={strategy.value}, 股票数={portfolio_size}")

            if not stock_analyses or len(stock_analyses) < portfolio_size:
                logger.warning(f"股票数量不足，需要至少 {portfolio_size} 只")
                return None

            # 筛选和排名股票
            selected_stocks = self._select_stocks(stock_analyses, strategy, portfolio_size)
            if not selected_stocks:
                logger.warning("无法筛选出合适的股票")
                return None

            # 创建组合建议
            recommendation = PortfolioRecommendation(strategy=strategy)

            # 分配权重
            self._allocate_weights(recommendation, selected_stocks, strategy)

            # 计算组合指标
            self._calculate_portfolio_metrics(recommendation, selected_stocks)

            # 生成建议总结
            self._generate_summary(recommendation)

            return recommendation
        except Exception as e:
            logger.error(f"生成投资组合建议失败: {str(e)}")
            return None

    def optimize_portfolio_rebalance(
        self,
        current_portfolio: List[Dict[str, Any]],
        stock_analyses: List[Dict[str, Any]]
    ) -> Optional[PortfolioRecommendation]:
        """
        优化现有投资组合的再平衡
        Args:
            current_portfolio: 当前投资组合
            stock_analyses: 股票分析结果
        Returns:
            优化后的投资组合建议
        """
        try:
            logger.info("优化投资组合再平衡")

            # 评估现有组合中的股票
            rebalanced_stocks = []
            for stock in current_portfolio:
                # 查找对应的分析结果
                analysis = next(
                    (a for a in stock_analyses
                     if a.get("stock_code") == stock.get("stock_code")),
                    None
                )

                if analysis:
                    rebalanced_stocks.append({
                        **stock,
                        **analysis,
                    })

            # 评估是否需要调整
            adjustment_recommendation = self._evaluate_rebalance_need(rebalanced_stocks)

            return adjustment_recommendation
        except Exception as e:
            logger.error(f"优化投资组合再平衡失败: {str(e)}")
            return None

    def calculate_portfolio_metrics(
        self,
        positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        计算投资组合的主要指标
        Args:
            positions: 持仓列表
        Returns:
            指标字典
        """
        try:
            total_weight = sum(p.get("weight", 0) for p in positions)

            # 计算加权评分
            weighted_scores = []
            for p in positions:
                weight = p.get("weight", 0)
                score = p.get("overall_score", 5.0)
                weighted_scores.append(weight * score)

            avg_score = sum(weighted_scores) / total_weight if total_weight > 0 else 5.0

            # 风险评分
            risk_scores = [p.get("risk_level", 5.0) for p in positions]
            avg_risk = statistics.mean(risk_scores) if risk_scores else 5.0

            return {
                "total_weight": total_weight,
                "average_score": avg_score,
                "average_risk": avg_risk,
                "position_count": len(positions),
                "diversification": self._calculate_diversification(positions),
            }
        except Exception as e:
            logger.error(f"计算投资组合指标失败: {str(e)}")
            return {}

    # 辅助方法

    def _select_stocks(
        self,
        stock_analyses: List[Dict[str, Any]],
        strategy: PortfolioStrategy,
        portfolio_size: int
    ) -> List[Dict[str, Any]]:
        """根据策略筛选股票"""
        filtered = []

        for analysis in stock_analyses:
            # 基于策略的筛选
            if strategy == PortfolioStrategy.VALUE:
                # 价值型：选择被低估、安全边际大的股票
                if self._is_value_stock(analysis):
                    filtered.append(analysis)
            elif strategy == PortfolioStrategy.GROWTH:
                # 成长型：选择高成长、高ROE的股票
                if self._is_growth_stock(analysis):
                    filtered.append(analysis)
            elif strategy == PortfolioStrategy.INCOME:
                # 收益型：选择高分红、稳定的股票
                if self._is_income_stock(analysis):
                    filtered.append(analysis)
            else:  # BALANCED 和 CONSERVATIVE
                # 平衡型和保守型：选择综合评分好的股票
                if analysis.get("overall_score", 0) >= 5.0:
                    filtered.append(analysis)

        # 排序并取前 portfolio_size 个
        filtered.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        return filtered[:portfolio_size]

    def _allocate_weights(
        self,
        recommendation: PortfolioRecommendation,
        selected_stocks: List[Dict[str, Any]],
        strategy: PortfolioStrategy
    ) -> None:
        """分配权重"""
        total_stocks = len(selected_stocks)
        if total_stocks == 0:
            return

        # 基于策略的权重分配方式
        if strategy == PortfolioStrategy.GROWTH:
            # 成长型：高风险股票权重高
            for i, stock in enumerate(selected_stocks):
                weight = (total_stocks - i) / (total_stocks * (total_stocks + 1) / 2)
                cash_weight = 0.1
        elif strategy == PortfolioStrategy.VALUE:
            # 价值型：均匀分配，保留现金
            weight = 0.8 / total_stocks
            cash_weight = 0.2
        elif strategy == PortfolioStrategy.INCOME:
            # 收益型：均匀分配，保留现金
            weight = 0.85 / total_stocks
            cash_weight = 0.15
        else:  # BALANCED, CONSERVATIVE
            # 平衡型和保守型：均匀分配
            weight = 0.9 / total_stocks if strategy == PortfolioStrategy.BALANCED else 0.8 / total_stocks
            cash_weight = 0.1 if strategy == PortfolioStrategy.BALANCED else 0.2

        # 创建持仓
        for i, stock in enumerate(selected_stocks):
            if strategy == PortfolioStrategy.GROWTH:
                # 成长型：不同权重
                w = (total_stocks - i) / (total_stocks * (total_stocks + 1) / 2)
            else:
                w = weight

            position = PortfolioPosition(
                stock_code=stock.get("stock_code", ""),
                stock_name=stock.get("stock_code", ""),
                weight=w,
                risk_level=self._get_risk_level(stock),
                reason=self._get_selection_reason(stock, strategy),
            )

            recommendation.positions.append(position)

        recommendation.cash_weight = cash_weight
        recommendation.total_weight = 1.0

    def _calculate_portfolio_metrics(
        self,
        recommendation: PortfolioRecommendation,
        selected_stocks: List[Dict[str, Any]]
    ) -> None:
        """计算投资组合指标"""
        # 预期收益率（结合 ML 分作为额外信号）
        weighted_returns = []
        for stock in selected_stocks:
            base_score = stock.get("overall_score", 5.0)
            ml_score = stock.get("ml_score", 5.0)  # 新增：ML 信号（0-10）
            combined = (base_score / 10.0) * 0.6 + (ml_score / 10.0) * 0.4  # 60% 基础、40% ML
            estimated_return = (combined - 0.5) * 0.2  # 基线 0.5，范围约 -10%~+10%
            weight = next((p.weight for p in recommendation.positions
                         if p.stock_code == stock.get("stock_code")), 0.1)
            weighted_returns.append(weight * estimated_return)

        recommendation.expected_return = sum(weighted_returns) if weighted_returns else 0.0

        # 风险评分（保持原逻辑）
        risk_scores = [
            next((p.weight for p in recommendation.positions
                 if p.stock_code == stock.get("stock_code")), 0.1) *
            stock.get("risk_level", 5.0)
            for stock in selected_stocks
        ]
        recommendation.risk_score = sum(risk_scores) if risk_scores else 5.0

        # 多样化评分
        recommendation.diversification_score = min(10.0, len(selected_stocks))

    def _generate_summary(self, recommendation: PortfolioRecommendation) -> None:
        """生成建议总结"""
        if recommendation.strategy == PortfolioStrategy.GROWTH:
            recommendation.summary = f"成长型组合：配置{len(recommendation.positions)}只高成长股票，预期收益较高但风险也较高"
        elif recommendation.strategy == PortfolioStrategy.VALUE:
            recommendation.summary = f"价值型组合：配置{len(recommendation.positions)}只被低估股票，风险较低"
        elif recommendation.strategy == PortfolioStrategy.INCOME:
            recommendation.summary = f"收益型组合：配置{len(recommendation.positions)}只高分红股票，强调稳定收益"
        elif recommendation.strategy == PortfolioStrategy.BALANCED:
            recommendation.summary = f"平衡型组合：配置{len(recommendation.positions)}只综合评分良好的股票，风险适中"
        else:  # CONSERVATIVE
            recommendation.summary = f"保守型组合：配置{len(recommendation.positions)}只低风险股票，保留{recommendation.cash_weight:.0%}现金防御"

    def _is_value_stock(self, analysis: Dict[str, Any]) -> bool:
        """判断是否为价值股"""
        return (
            analysis.get("valuation", {}).get("margin_of_safety", 0) > 15 and
            analysis.get("overall_score", 0) > 5.0
        )

    def _is_growth_stock(self, analysis: Dict[str, Any]) -> bool:
        """判断是否为成长股"""
        return (
            analysis.get("financial_metrics", {}).get("profit_growth", 0) > 0.15 and
            analysis.get("financial_metrics", {}).get("roe", 0) > 0.15
        )

    def _is_income_stock(self, analysis: Dict[str, Any]) -> bool:
        """判断是否为收益股"""
        return analysis.get("financial_metrics", {}).get("dividend_yield", 0) > 0.02

    def _get_risk_level(self, analysis: Dict[str, Any]) -> str:
        """获取风险等级"""
        risk_assessment = analysis.get("risk_assessment", {})
        level = risk_assessment.get("overall_risk_level", "")

        if "低" in str(level):
            return "低"
        elif "高" in str(level):
            return "高"
        else:
            return "中等"

    def _get_selection_reason(
        self,
        analysis: Dict[str, Any],
        strategy: PortfolioStrategy
    ) -> str:
        """获取选中理由"""
        if strategy == PortfolioStrategy.VALUE:
            return f"被低估，安全边际{analysis.get('valuation', {}).get('margin_of_safety', 0):.1f}%"
        elif strategy == PortfolioStrategy.GROWTH:
            return f"成长性强，利润增长{analysis.get('financial_metrics', {}).get('profit_growth', 0):.1%}"
        elif strategy == PortfolioStrategy.INCOME:
            return f"分红稳定，分红收益率{analysis.get('financial_metrics', {}).get('dividend_yield', 0):.2%}"
        else:
            return f"综合评分{analysis.get('overall_score', 0):.1f}分"

    def _calculate_diversification(self, positions: List[Dict[str, Any]]) -> float:
        """计算多样化程度"""
        if not positions:
            return 0.0

        weights = [p.get("weight", 0) for p in positions]
        # Herfindahl指数
        herfindahl = sum(w ** 2 for w in weights)
        # 转换为0-10分
        diversification = max(0, 10 - herfindahl * 100)
        return min(10, diversification)

    def _evaluate_rebalance_need(
        self,
        rebalanced_stocks: List[Dict[str, Any]]
    ) -> Optional[PortfolioRecommendation]:
        """评估是否需要再平衡"""
        if not rebalanced_stocks:
            return None

        # 检查是否有股票信号改变
        needs_rebalance = False
        for stock in rebalanced_stocks:
            signal = stock.get("investment_decision", {}).get("decision", "")
            if "卖出" in str(signal):
                needs_rebalance = True
                break

        if needs_rebalance:
            logger.info("检测到需要再平衡组合")

        return None
