"""agents 包初始化"""
from src.agents.base_agent import BaseAgent
from src.agents.equity_thinking_agent import EquityThinkingAgent
from src.agents.moat_agent import MoatAgent
from src.agents.financial_analysis_agent import FinancialAnalysisAgent
from src.agents.valuation_agent import ValuationAgent
from src.agents.safety_margin_agent import SafetyMarginAgent
from src.agents.buy_signal_agent import BuySignalAgent
from src.agents.sell_signal_agent import SellSignalAgent
from src.agents.risk_management_agent import RiskManagementAgent
from src.agents.behavioral_discipline_agent import BehavioralDisciplineAgent

# LLM 大师 Agents
from src.agents.llm import (
    LLMBaseAgent,
    LLMConfig,
    LLMProvider,
    LLMConfigManager,
    BenGrahamAgent,
    PhilipFisherAgent,
    CharlieMungerAgent,
    WarrenBuffettAgent,
    StanleyDruckenmillerAgent,
    CathieWoodAgent,
    BillAckmanAgent,
    get_all_master_agents,
    get_master_agent_by_name,
    # 专家 Agents
    FundamentalsAgent,
    SentimentAgent,
    ValuationExpertAgent,
    TechnicalAgent,
    RiskManagerAgent,
    PortfolioManagerAgent,
    get_all_expert_agents,
    get_expert_agent_by_name,
)

__all__ = [
    # 基础 Agent
    "BaseAgent",
    "EquityThinkingAgent", "MoatAgent", "FinancialAnalysisAgent",
    "ValuationAgent", "SafetyMarginAgent", "BuySignalAgent",
    "SellSignalAgent", "RiskManagementAgent", "BehavioralDisciplineAgent",
    # LLM 配置
    "LLMBaseAgent", "LLMConfig", "LLMProvider", "LLMConfigManager",
    # 大师 Agents
    "BenGrahamAgent", "PhilipFisherAgent", "CharlieMungerAgent",
    "WarrenBuffettAgent", "StanleyDruckenmillerAgent", "CathieWoodAgent",
    "BillAckmanAgent", "get_all_master_agents", "get_master_agent_by_name",
    # 专家 Agents
    "FundamentalsAgent", "SentimentAgent", "ValuationExpertAgent",
    "TechnicalAgent", "RiskManagerAgent", "PortfolioManagerAgent",
    "get_all_expert_agents", "get_expert_agent_by_name",
]
