"""
专家 LLM Agents - 基于 experts 目录下的提示词文件

这些 Agent 专注于特定的分析领域：
- 基本面分析
- 市场情绪分析
- 估值分析
- 技术分析
- 风险管理
- 投资组合管理
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.agents.llm.llm_base_agent import LLMBaseAgent
from src.models.data_models import StockAnalysisContext

logger = logging.getLogger(__name__)


# ============================================================================
# 专家投资信号数据结构
# ============================================================================


@dataclass
class ExpertInvestmentSignal:
    """专家投资信号"""
    agent_name: str
    signal: str  # bullish, bearish, neutral
    confidence: float  # 0-100
    reasoning: Any  # 可以是字符串或复杂结构
    analysis_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "signal": self.signal,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "analysis_data": self.analysis_data,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================================
# 工具函数
# ============================================================================


def load_expert_prompt(filename: str) -> str:
    """从 experts 目录加载提示词"""
    # 获取 experts 目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    experts_dir = os.path.join(os.path.dirname(current_dir), "experts")

    filepath = os.path.join(experts_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    else:
        logger.warning(f"Expert 文件不存在: {filepath}")
        return ""


# ============================================================================
# Fundamentals Agent (master11.txt)
# ============================================================================


class FundamentalsAgent(LLMBaseAgent):
    """
    基本面分析 Agent - 分析财务指标

    分析领域：
    - 盈利能力（ROE、净利润率、营业利润率）
    - 增长情况（营收增长、盈利增长、账面价值增长）
    - 财务健康（流动比率、负债权益比、自由现金流）
    - 估值比率（PE、PB、PS）
    """

    def __init__(self):
        system_prompt = load_expert_prompt("master11.txt")
        super().__init__(
            name="FundamentalsAgent",
            description="基本面分析专家 - 财务指标与基础数据分析",
            system_prompt=system_prompt,
            master_file="master11.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的基本面数据。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请从盈利能力、增长情况、财务健康状况、估值比率四个维度进行分析，并生成交易信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'expert_signals'):
            context.expert_signals = {}

        context.expert_signals["fundamentals"] = ExpertInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Sentiment Agent (master12.txt)
# ============================================================================


class SentimentAgent(LLMBaseAgent):
    """
    市场情绪分析 Agent - 分析内部交易和新闻情绪

    分析领域：
    - 内部交易信息（大股东、高管交易）
    - 公司新闻情绪（正面/负面/中性）
    - 综合情绪信号
    """

    def __init__(self):
        system_prompt = load_expert_prompt("master12.txt")
        super().__init__(
            name="SentimentAgent",
            description="市场情绪分析专家 - 内部交易与新闻情绪分析",
            system_prompt=system_prompt,
            master_file="master12.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的市场情绪。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请综合内部交易信息和公司新闻情绪，生成交易信号。内部交易权重0.3，新闻情绪权重0.7。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'expert_signals'):
            context.expert_signals = {}

        context.expert_signals["sentiment"] = ExpertInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Valuation Agent (master13.txt)
# ============================================================================


class ValuationExpertAgent(LLMBaseAgent):
    """
    估值分析 Agent - 计算内在价值

    分析领域：
    - DCF 现金流折现估值
    - 所有者收益估值
    - 估值差距分析
    """

    def __init__(self):
        system_prompt = load_expert_prompt("master13.txt")
        super().__init__(
            name="ValuationExpertAgent",
            description="估值分析专家 - DCF与所有者收益估值",
            system_prompt=system_prompt,
            master_file="master13.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请计算股票 {context.stock_code}（{context.stock_name}）的内在价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请使用DCF和所有者收益两种方法进行估值，计算估值差距并生成交易信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'expert_signals'):
            context.expert_signals = {}

        context.expert_signals["valuation_expert"] = ExpertInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Technical Agent (master14.txt)
# ============================================================================


class TechnicalAgent(LLMBaseAgent):
    """
    技术分析 Agent - 分析技术指标

    分析领域：
    - 趋势跟踪（移动平均、趋势线）
    - 均值回归（布林带、超买超卖）
    - 动量分析（RSI、MACD）
    - 波动率分析
    - 统计套利
    """

    def __init__(self):
        system_prompt = load_expert_prompt("master14.txt")
        super().__init__(
            name="TechnicalAgent",
            description="技术分析专家 - 多策略技术指标分析",
            system_prompt=system_prompt,
            master_file="master14.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请对股票 {context.stock_code}（{context.stock_name}）进行技术分析。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请综合趋势跟踪(25%)、均值回归(20%)、动量(25%)、波动率(15%)、统计套利(15%)五种策略进行分析。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'expert_signals'):
            context.expert_signals = {}

        context.expert_signals["technical"] = ExpertInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("strategy_signals") if "strategy_signals" in signal else signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Risk Manager Agent (master15.txt)
# ============================================================================


class RiskManagerAgent(LLMBaseAgent):
    """
    风险管理 Agent - 计算风险指标和头寸限制

    分析领域：
    - 投资组合价值计算
    - 头寸限制计算
    - 保证金要求
    - 风险控制
    """

    def __init__(self):
        system_prompt = load_expert_prompt("master15.txt")
        super().__init__(
            name="RiskManagerAgent",
            description="风险管理专家 - 风险指标与头寸限制",
            system_prompt=system_prompt,
            master_file="master15.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        # 添加投资组合信息（如果有）
        portfolio_info = {
            "total_portfolio_value": 1000000,  # 默认100万
            "cash": 200000,  # 默认20万现金
            "current_position": 0,
        }
        analysis_data["portfolio"] = portfolio_info

        return f"""请为股票 {context.stock_code}（{context.stock_name}）计算风险指标和头寸限制。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请计算头寸限制和风险指标。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'expert_signals'):
            context.expert_signals = {}

        context.expert_signals["risk_manager"] = ExpertInvestmentSignal(
            agent_name=self.name,
            signal="neutral",  # 风险管理通常不产生买卖信号
            confidence=signal.get("confidence", 100.0) if "confidence" in signal else 100.0,
            reasoning=signal.get("reasoning", signal),
            analysis_data={
                "remaining_position_limit": signal.get("remaining_position_limit"),
                "current_price": signal.get("current_price"),
            },
        )

        return context


# ============================================================================
# Portfolio Manager Agent (master16.txt)
# ============================================================================


class PortfolioManagerAgent(LLMBaseAgent):
    """
    投资组合经理 Agent - 综合决策与订单生成

    职责：
    - 综合分析所有交易信号
    - 执行多头/空头交易规则
    - 生成最终交易决策
    - 风险管理与头寸控制
    """

    def __init__(self):
        system_prompt = load_expert_prompt("master16.txt")
        super().__init__(
            name="PortfolioManagerAgent",
            description="投资组合经理 - 综合决策与订单生成",
            system_prompt=system_prompt,
            master_file="master16.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)

        # 收集所有专家信号
        signals_by_ticker = {}
        if hasattr(context, 'expert_signals') and context.expert_signals:
            for expert_name, signal in context.expert_signals.items():
                if expert_name not in ["risk_manager", "portfolio_manager"]:
                    signals_by_ticker[expert_name] = {
                        "signal": signal.signal,
                        "confidence": signal.confidence,
                    }

        # 添加大师信号（如果有）
        if hasattr(context, 'master_signals') and context.master_signals:
            for master_name, signal in context.master_signals.items():
                signals_by_ticker[f"master_{master_name}"] = {
                    "signal": signal.signal,
                    "confidence": signal.confidence,
                }

        # 投资组合信息
        portfolio_info = {
            "cash": 200000,
            "positions": {},
            "current_prices": {context.stock_code: analysis_data.get("financial_metrics", {}).get("current_price", 0)},
            "max_shares": {context.stock_code: 1000},
            "margin_requirement": 0.5,
        }

        return f"""请为股票 {context.stock_code}（{context.stock_name}）做出最终交易决策。

股票分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

各专家/大师交易信号：
{json.dumps(signals_by_ticker, ensure_ascii=False, indent=2)}

投资组合信息：
{json.dumps(portfolio_info, ensure_ascii=False, indent=2)}

请综合所有信号，按照交易规则做出最终决策。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'expert_signals'):
            context.expert_signals = {}

        # 从 decisions 中提取当前股票的决策
        decisions = signal.get("decisions", {})
        stock_decision = decisions.get(context.stock_code, signal)

        action = stock_decision.get("action", "hold")
        signal_mapping = {
            "buy": "bullish",
            "cover": "bullish",
            "sell": "bearish",
            "short": "bearish",
            "hold": "neutral",
        }

        context.expert_signals["portfolio_manager"] = ExpertInvestmentSignal(
            agent_name=self.name,
            signal=signal_mapping.get(action, "neutral"),
            confidence=stock_decision.get("confidence", 50.0),
            reasoning=stock_decision.get("reasoning", ""),
            analysis_data={
                "action": action,
                "quantity": stock_decision.get("quantity", 0),
                "decisions": decisions,
            },
        )

        return context


# ============================================================================
# 便捷函数
# ============================================================================


# 所有专家 Agent 类
EXPERT_AGENT_CLASSES = [
    FundamentalsAgent,
    SentimentAgent,
    ValuationExpertAgent,
    TechnicalAgent,
    RiskManagerAgent,
    PortfolioManagerAgent,
]


def get_all_expert_agents() -> List[LLMBaseAgent]:
    """获取所有专家 Agent 实例"""
    return [cls() for cls in EXPERT_AGENT_CLASSES]


def get_expert_agent_by_name(name: str) -> Optional[LLMBaseAgent]:
    """根据名称获取专家 Agent"""
    name_lower = name.lower().replace("_", "").replace(" ", "")

    name_mapping = {
        "fundamentals": FundamentalsAgent,
        "fundamental": FundamentalsAgent,
        "sentiment": SentimentAgent,
        "valuationexpert": ValuationExpertAgent,
        "valuation": ValuationExpertAgent,
        "technical": TechnicalAgent,
        "tech": TechnicalAgent,
        "riskmanager": RiskManagerAgent,
        "risk": RiskManagerAgent,
        "portfoliomanager": PortfolioManagerAgent,
        "portfolio": PortfolioManagerAgent,
        "pm": PortfolioManagerAgent,
    }

    if name_lower in name_mapping:
        return name_mapping[name_lower]()

    return None


def run_all_experts_analysis(context: StockAnalysisContext) -> StockAnalysisContext:
    """
    运行所有专家 Agent 分析

    Args:
        context: 股票分析上下文

    Returns:
        包含所有专家分析结果的上下文
    """
    agents = get_all_expert_agents()

    for agent in agents:
        try:
            logger.info(f"运行 {agent.name} 分析...")
            context = agent.execute(context)
        except Exception as e:
            logger.error(f"{agent.name} 分析失败: {e}")

    return context


def get_expert_consensus(context: StockAnalysisContext) -> Dict[str, Any]:
    """
    获取专家共识

    Args:
        context: 包含专家分析结果的上下文

    Returns:
        共识分析结果
    """
    if not hasattr(context, 'expert_signals') or not context.expert_signals:
        return {
            "consensus": "unknown",
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
            "average_confidence": 0.0,
            "details": [],
        }

    bullish = 0
    bearish = 0
    neutral = 0
    total_confidence = 0.0
    details = []

    # 排除风险管理和组合管理的信号（它们不产生方向性信号）
    excluded = ["risk_manager"]

    for name, signal in context.expert_signals.items():
        if name in excluded:
            continue

        if signal.signal == "bullish":
            bullish += 1
        elif signal.signal == "bearish":
            bearish += 1
        else:
            neutral += 1

        total_confidence += signal.confidence
        details.append({
            "expert": name,
            "signal": signal.signal,
            "confidence": signal.confidence,
            "reasoning": signal.reasoning if isinstance(signal.reasoning, str) else str(signal.reasoning)[:200],
        })

    total = bullish + bearish + neutral
    avg_confidence = total_confidence / total if total > 0 else 0.0

    # 判断共识
    if bullish > bearish and bullish > neutral:
        consensus = "bullish"
    elif bearish > bullish and bearish > neutral:
        consensus = "bearish"
    else:
        consensus = "neutral"

    return {
        "consensus": consensus,
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": neutral,
        "average_confidence": avg_confidence,
        "details": details,
    }
