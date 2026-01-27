"""
LLM Agent 模块 - 基于大语言模型的投资分析 Agent
"""
from src.agents.llm.llm_config import (
    LLMConfig,
    LLMProvider,
    LLMConfigManager,
    get_llm_config,
    set_llm_config,
    load_llm_config,
)
from src.agents.llm.llm_base_agent import LLMBaseAgent
from src.agents.llm.master_agents import (
    BenGrahamAgent,
    PhilipFisherAgent,
    CharlieMungerAgent,
    WarrenBuffettAgent,
    StanleyDruckenmillerAgent,
    CathieWoodAgent,
    BillAckmanAgent,
    get_all_master_agents,
    get_master_agent_by_name,
)
from src.agents.llm.expert_agents import (
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
    # 配置
    "LLMConfig",
    "LLMProvider",
    "LLMConfigManager",
    "get_llm_config",
    "set_llm_config",
    "load_llm_config",
    # 基类
    "LLMBaseAgent",
    # 大师 Agents
    "BenGrahamAgent",
    "PhilipFisherAgent",
    "CharlieMungerAgent",
    "WarrenBuffettAgent",
    "StanleyDruckenmillerAgent",
    "CathieWoodAgent",
    "BillAckmanAgent",
    "get_all_master_agents",
    "get_master_agent_by_name",
    # 专家 Agents
    "FundamentalsAgent",
    "SentimentAgent",
    "ValuationExpertAgent",
    "TechnicalAgent",
    "RiskManagerAgent",
    "PortfolioManagerAgent",
    "get_all_expert_agents",
    "get_expert_agent_by_name",
]
