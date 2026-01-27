"""
投资大师 LLM Agents - 基于 masters 目录下的提示词文件
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.agents.llm.llm_base_agent import LLMBaseAgent
from src.models.data_models import StockAnalysisContext, InvestmentSignal

logger = logging.getLogger(__name__)


# ============================================================================
# 大师投资信号数据结构
# ============================================================================


@dataclass
class MasterInvestmentSignal:
    """大师投资信号"""
    agent_name: str
    signal: str  # bullish, bearish, neutral
    confidence: float  # 0-100
    reasoning: str
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


def load_master_prompt(filename: str) -> str:
    """从 masters 目录加载提示词"""
    # 获取 masters 目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    masters_dir = os.path.join(os.path.dirname(current_dir), "masters")

    filepath = os.path.join(masters_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    else:
        logger.warning(f"Master 文件不存在: {filepath}")
        return ""


# ============================================================================
# Ben Graham Agent (master2.txt)
# ============================================================================


class BenGrahamAgent(LLMBaseAgent):
    """
    本杰明·格雷厄姆 Agent - 价值投资之父

    投资理念：
    - 严格秉承安全边际原则
    - 关注盈利稳定性
    - 评估财务实力（低负债、充足流动性）
    - 使用格雷厄姆数、净净价值法衡量折扣
    """

    def __init__(self):
        system_prompt = load_master_prompt("master2.txt")
        super().__init__(
            name="BenGrahamAgent",
            description="本杰明·格雷厄姆价值投资分析 - 安全边际与财务稳健",
            system_prompt=system_prompt,
            master_file="master2.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请严格按照本杰明·格雷厄姆的价值投资原则进行分析，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        # 存储大师分析结果
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["ben_graham"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Philip Fisher Agent (master3.txt)
# ============================================================================


class PhilipFisherAgent(LLMBaseAgent):
    """
    菲利普·费雪 Agent - 成长型投资大师

    投资理念：
    - 长期投资优质企业
    - 深入的"闲聊法"基本面分析
    - 投资组合管理与耐心持有
    - "十不"投资原则
    """

    def __init__(self):
        system_prompt = load_master_prompt("master3.txt")
        super().__init__(
            name="PhilipFisherAgent",
            description="菲利普·费雪成长型投资分析 - 优质企业长期持有",
            system_prompt=system_prompt,
            master_file="master3.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请依据你的成长型投资原则进行全面分析，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["philip_fisher"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Charlie Munger Agent (master4.txt)
# ============================================================================


class CharlieMungerAgent(LLMBaseAgent):
    """
    查理·芒格 Agent - 多元思维模型

    投资理念：
    - 以公平价格买入卓越企业
    - 多学科思维模型
    - 关注企业护城河
    - 重视管理层诚信
    - "总是反过来想"
    """

    def __init__(self):
        system_prompt = load_master_prompt("master4.txt")
        super().__init__(
            name="CharlieMungerAgent",
            description="查理·芒格多元思维投资分析 - 卓越企业与护城河",
            system_prompt=system_prompt,
            master_file="master4.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请运用多学科思维模型，按照查理·芒格的投资原则进行分析，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["charlie_munger"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Warren Buffett Agent (master5.txt)
# ============================================================================


class WarrenBuffettAgent(LLMBaseAgent):
    """
    沃伦·巴菲特 Agent - 股神

    投资理念：
    - 能力圈原则
    - 安全边际（>30%）
    - 经济护城河
    - 优质管理层
    - 财务实力（低负债、高 ROE）
    - 长期投资
    """

    def __init__(self):
        system_prompt = load_master_prompt("master5.txt")
        super().__init__(
            name="WarrenBuffettAgent",
            description="沃伦·巴菲特价值投资分析 - 能力圈与经济护城河",
            system_prompt=system_prompt,
            master_file="master5.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请严格依据沃伦·巴菲特的投资原则进行分析，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["warren_buffett"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Stanley Druckenmiller Agent (master6.txt)
# ============================================================================


class StanleyDruckenmillerAgent(LLMBaseAgent):
    """
    斯坦利·德鲁肯米勒 Agent - 宏观对冲大师

    投资理念：
    - 寻找不对称风险回报机会
    - 重视增长态势与市场趋势
    - 保护资本，避免重大回撤
    - 接受高估值的行业领导者
    - 坚定信心时大胆投资
    - 逻辑改变时果断止损
    """

    def __init__(self):
        system_prompt = load_master_prompt("master6.txt")
        super().__init__(
            name="StanleyDruckenmillerAgent",
            description="斯坦利·德鲁肯米勒宏观投资分析 - 不对称风险回报",
            system_prompt=system_prompt,
            master_file="master6.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请依据你的投资原则，重点关注风险回报比和增长趋势，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["stanley_druckenmiller"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Cathie Wood Agent (master7.txt)
# ============================================================================


class CathieWoodAgent(LLMBaseAgent):
    """
    凯西·伍德 Agent - 创新投资女王

    投资理念：
    - 寻找颠覆性创新公司
    - 关注指数级增长潜力和巨大 TAM
    - 聚焦科技、医疗保健等未来行业
    - 考虑多年时间跨度的突破
    - 接受高波动性追求高回报
    - 评估管理层愿景和研发投入
    """

    def __init__(self):
        system_prompt = load_master_prompt("master7.txt")
        super().__init__(
            name="CathieWoodAgent",
            description="凯西·伍德创新投资分析 - 颠覆性技术与指数增长",
            system_prompt=system_prompt,
            master_file="master7.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请依据你的创新投资原则，重点关注颠覆性技术和增长潜力，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["cathie_wood"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# Bill Ackman Agent (master8.txt)
# ============================================================================


class BillAckmanAgent(LLMBaseAgent):
    """
    比尔·阿克曼 Agent - 激进投资家

    投资理念：
    - 寻找具有持久竞争优势的高质量企业
    - 优先考虑持续自由现金流和增长潜力
    - 强调财务纪律（合理杠杆、有效资本配置）
    - 重视估值（内在价值和安全边际）
    - 长期集中投资
    - 必要时采取积极行动释放价值
    """

    def __init__(self):
        system_prompt = load_master_prompt("master8.txt")
        super().__init__(
            name="BillAckmanAgent",
            description="比尔·阿克曼激进投资分析 - 价值释放与积极行动",
            system_prompt=system_prompt,
            master_file="master8.txt",
        )

    def _build_user_message(self, context: StockAnalysisContext) -> str:
        analysis_data = self._prepare_analysis_data(context)
        return f"""请分析股票 {context.stock_code}（{context.stock_name}）的投资价值。

分析数据：
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

请依据你的投资原则进行分析，评估是否值得投资，并以 JSON 格式返回投资信号。"""

    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        if not hasattr(context, 'master_signals'):
            context.master_signals = {}

        context.master_signals["bill_ackman"] = MasterInvestmentSignal(
            agent_name=self.name,
            signal=signal.get("signal", "neutral"),
            confidence=signal.get("confidence", 50.0),
            reasoning=signal.get("reasoning", ""),
            analysis_data=signal.get("analysis_data"),
        )

        return context


# ============================================================================
# 便捷函数
# ============================================================================


# 所有大师 Agent 类
MASTER_AGENT_CLASSES = [
    BenGrahamAgent,
    PhilipFisherAgent,
    CharlieMungerAgent,
    WarrenBuffettAgent,
    StanleyDruckenmillerAgent,
    CathieWoodAgent,
    BillAckmanAgent,
]


def get_all_master_agents() -> List[LLMBaseAgent]:
    """获取所有大师 Agent 实例"""
    return [cls() for cls in MASTER_AGENT_CLASSES]


def get_master_agent_by_name(name: str) -> Optional[LLMBaseAgent]:
    """根据名称获取大师 Agent"""
    name_lower = name.lower().replace("_", "").replace(" ", "")

    name_mapping = {
        "bengraham": BenGrahamAgent,
        "bengrahamagent": BenGrahamAgent,
        "graham": BenGrahamAgent,
        "philipfisher": PhilipFisherAgent,
        "philipfisheragent": PhilipFisherAgent,
        "fisher": PhilipFisherAgent,
        "charliemunger": CharlieMungerAgent,
        "charliemungeragent": CharlieMungerAgent,
        "munger": CharlieMungerAgent,
        "warrenbuffett": WarrenBuffettAgent,
        "warrenbuffettagent": WarrenBuffettAgent,
        "buffett": WarrenBuffettAgent,
        "stanleydruckenmiller": StanleyDruckenmillerAgent,
        "stanleydruckenmilleragent": StanleyDruckenmillerAgent,
        "druckenmiller": StanleyDruckenmillerAgent,
        "cathiewood": CathieWoodAgent,
        "cathiewoodagent": CathieWoodAgent,
        "wood": CathieWoodAgent,
        "billackman": BillAckmanAgent,
        "billackmanagent": BillAckmanAgent,
        "ackman": BillAckmanAgent,
    }

    if name_lower in name_mapping:
        return name_mapping[name_lower]()

    return None


def run_all_masters_analysis(context: StockAnalysisContext) -> StockAnalysisContext:
    """
    运行所有大师 Agent 分析

    Args:
        context: 股票分析上下文

    Returns:
        包含所有大师分析结果的上下文
    """
    agents = get_all_master_agents()

    for agent in agents:
        try:
            logger.info(f"运行 {agent.name} 分析...")
            context = agent.execute(context)
        except Exception as e:
            logger.error(f"{agent.name} 分析失败: {e}")

    return context


def get_master_consensus(context: StockAnalysisContext) -> Dict[str, Any]:
    """
    获取大师共识

    Args:
        context: 包含大师分析结果的上下文

    Returns:
        共识分析结果
    """
    if not hasattr(context, 'master_signals') or not context.master_signals:
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

    for name, signal in context.master_signals.items():
        if signal.signal == "bullish":
            bullish += 1
        elif signal.signal == "bearish":
            bearish += 1
        else:
            neutral += 1

        total_confidence += signal.confidence
        details.append({
            "master": name,
            "signal": signal.signal,
            "confidence": signal.confidence,
            "reasoning": signal.reasoning,
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
