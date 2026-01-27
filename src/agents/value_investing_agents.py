"""
历史兼容性：将旧的 value_investing_agents 重导向到新的模块（按 agent 拆分）
原始实现已拆分为多个文件（equity_thinking_agent.py 等）。
此文件保留为向后兼容的导出。
"""
from src.agents.equity_thinking_agent import EquityThinkingAgent
from src.agents.moat_agent import MoatAgent
from src.agents.financial_analysis_agent import FinancialAnalysisAgent
from src.agents.valuation_agent import ValuationAgent
from src.agents.safety_margin_agent import SafetyMarginAgent
from src.agents.buy_signal_agent import BuySignalAgent
from src.agents.sell_signal_agent import SellSignalAgent
from src.agents.risk_management_agent import RiskManagementAgent
from src.agents.behavioral_discipline_agent import BehavioralDisciplineAgent
from src.agents.agent_config import (
    AgentConfig,
    AgentConfigManager,
    get_agent_config,
    set_agent_config,
    load_agent_config,
    save_agent_config,
    reset_agent_config,
    FinancialAnalysisConfig,
    MoatAnalysisConfig,
    ValuationConfig,
    SafetyMarginConfig,
    BuySignalConfig,
    SellSignalConfig,
    RiskManagementConfig,
    PsychologyDisciplineConfig,
    MLScoringConfig,
)

__all__ = [
    "EquityThinkingAgent", "MoatAgent", "FinancialAnalysisAgent",
    "ValuationAgent", "SafetyMarginAgent", "BuySignalAgent",
    "SellSignalAgent", "RiskManagementAgent", "BehavioralDisciplineAgent",
    # Agent 配置
    "AgentConfig",
    "AgentConfigManager",
    "get_agent_config",
    "set_agent_config",
    "load_agent_config",
    "save_agent_config",
    "reset_agent_config",
    "FinancialAnalysisConfig",
    "MoatAnalysisConfig",
    "ValuationConfig",
    "SafetyMarginConfig",
    "BuySignalConfig",
    "SellSignalConfig",
    "RiskManagementConfig",
    "PsychologyDisciplineConfig",
    "MLScoringConfig",
]
