"""
Agent 参数化配置系统 - 支持 YAML/JSON/Dict 配置各 Agent 行为参数
"""
import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# ============================================================================
# 各 Agent 配置数据类
# ============================================================================


@dataclass
class FinancialAnalysisConfig:
    """财务分析 Agent 配置"""
    # ROE 阈值
    roe_excellent: float = 0.20  # 优秀 ROE
    roe_good: float = 0.15  # 良好 ROE
    roe_minimum: float = 0.10  # 最低可接受 ROE

    # 毛利率阈值
    gross_margin_excellent: float = 0.40
    gross_margin_good: float = 0.25
    gross_margin_minimum: float = 0.15

    # 负债率阈值
    debt_ratio_safe: float = 0.40
    debt_ratio_warning: float = 0.60
    debt_ratio_danger: float = 0.80

    # 自由现金流
    require_positive_fcf: bool = True
    fcf_growth_weight: float = 0.3

    # 评分权重
    weight_roe: float = 0.30
    weight_gross_margin: float = 0.20
    weight_debt_ratio: float = 0.20
    weight_fcf: float = 0.30


@dataclass
class MoatAnalysisConfig:
    """护城河分析 Agent 配置"""
    # 各维度权重
    weight_brand: float = 0.25
    weight_cost_advantage: float = 0.20
    weight_network_effect: float = 0.20
    weight_switching_cost: float = 0.20
    weight_scale: float = 0.15

    # 评分阈值
    strong_moat_threshold: float = 7.0
    moderate_moat_threshold: float = 5.0
    weak_moat_threshold: float = 3.0

    # 行业调整因子
    industry_adjustment_enabled: bool = True
    tech_industry_network_boost: float = 1.2
    consumer_industry_brand_boost: float = 1.3


@dataclass
class ValuationConfig:
    """估值分析 Agent 配置"""
    # DCF 参数
    discount_rate: float = 0.10  # 折现率
    terminal_growth_rate: float = 0.03  # 永续增长率
    projection_years: int = 10  # 预测年数

    # PE 估值
    pe_ratio_low: float = 10.0
    pe_ratio_fair: float = 15.0
    pe_ratio_high: float = 25.0

    # PB 估值
    pb_ratio_low: float = 1.0
    pb_ratio_fair: float = 2.0
    pb_ratio_high: float = 5.0

    # 估值方法权重
    weight_dcf: float = 0.40
    weight_pe: float = 0.30
    weight_pb: float = 0.30


@dataclass
class SafetyMarginConfig:
    """安全边际 Agent 配置"""
    # 安全边际阈值
    excellent_margin: float = 0.40  # 40% 以上为极佳
    good_margin: float = 0.25  # 25% 以上为良好
    minimum_margin: float = 0.15  # 最低要求 15%

    # 风险调整
    high_risk_extra_margin: float = 0.10  # 高风险股票额外要求
    low_risk_reduce_margin: float = 0.05  # 低风险股票可降低要求

    # 评分权重
    weight_margin_size: float = 0.60
    weight_margin_stability: float = 0.40


@dataclass
class BuySignalConfig:
    """买入信号 Agent 配置"""
    # 触发条件阈值
    pessimism_threshold: float = 0.7  # 悲观情绪阈值
    price_drop_trigger: float = 0.20  # 价格下跌触发点
    volume_spike_ratio: float = 2.0  # 成交量异常倍数

    # 信号强度
    strong_buy_score: float = 8.0
    buy_score: float = 6.0
    hold_score: float = 4.0

    # 确认条件
    require_valuation_support: bool = True
    require_moat_support: bool = True
    min_financial_score: float = 5.0


@dataclass
class SellSignalConfig:
    """卖出信号 Agent 配置"""
    # 基本面恶化阈值
    roe_decline_trigger: float = 0.30  # ROE 下降 30% 触发
    margin_decline_trigger: float = 0.25  # 毛利率下降 25% 触发
    debt_increase_trigger: float = 0.50  # 负债率上升 50% 触发

    # 估值过高阈值
    overvalued_pe_ratio: float = 40.0
    overvalued_pb_ratio: float = 8.0
    overvalued_margin: float = -0.30  # 负安全边际 30%

    # 信号强度
    strong_sell_score: float = 8.0
    sell_score: float = 6.0


@dataclass
class RiskManagementConfig:
    """风险管理 Agent 配置"""
    # 仓位限制
    max_single_position: float = 0.20  # 单只股票最大仓位
    max_industry_exposure: float = 0.40  # 单一行业最大敞口
    min_cash_reserve: float = 0.10  # 最低现金储备

    # 风险等级阈值
    low_risk_threshold: float = 3.0
    medium_risk_threshold: float = 6.0
    high_risk_threshold: float = 8.0

    # 止损止盈
    default_stop_loss: float = 0.15  # 默认止损比例
    default_take_profit: float = 0.50  # 默认止盈比例
    trailing_stop_enabled: bool = True
    trailing_stop_distance: float = 0.10


@dataclass
class PsychologyDisciplineConfig:
    """心理纪律 Agent 配置"""
    # 决策延迟
    cooling_off_period_days: int = 3  # 冷静期天数
    require_checklist: bool = True  # 是否要求清单确认

    # 信念强度
    high_conviction_threshold: float = 0.8
    medium_conviction_threshold: float = 0.5

    # 纪律检查
    check_diversification: bool = True
    check_position_sizing: bool = True
    check_emotional_state: bool = True


@dataclass
class MLScoringConfig:
    """机器学习评分配置"""
    enabled: bool = True
    model_path: Optional[str] = None  # 自定义模型路径
    weight_in_decision: float = 0.2  # ML 分在最终决策中的权重

    # 特征权重（用于默认模型）
    weight_pe: float = -0.25
    weight_pb: float = -0.15
    weight_roe: float = 0.35
    weight_gross_margin: float = 0.20
    weight_fcf: float = 0.30
    weight_debt: float = -0.25


# ============================================================================
# 全局 Agent 配置
# ============================================================================


@dataclass
class AgentConfig:
    """全部 Agent 的统一配置"""
    # 各 Agent 子配置
    financial: FinancialAnalysisConfig = field(default_factory=FinancialAnalysisConfig)
    moat: MoatAnalysisConfig = field(default_factory=MoatAnalysisConfig)
    valuation: ValuationConfig = field(default_factory=ValuationConfig)
    safety_margin: SafetyMarginConfig = field(default_factory=SafetyMarginConfig)
    buy_signal: BuySignalConfig = field(default_factory=BuySignalConfig)
    sell_signal: SellSignalConfig = field(default_factory=SellSignalConfig)
    risk_management: RiskManagementConfig = field(default_factory=RiskManagementConfig)
    psychology: PsychologyDisciplineConfig = field(default_factory=PsychologyDisciplineConfig)
    ml_scoring: MLScoringConfig = field(default_factory=MLScoringConfig)

    # 全局设置
    debug_mode: bool = False
    log_level: str = "INFO"
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def save(self, path: str) -> None:
        """保存配置到 JSON 文件"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"配置已保存到 {path}")

    @staticmethod
    def load(path: str) -> "AgentConfig":
        """从 JSON 文件加载配置"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AgentConfig.from_dict(data)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AgentConfig":
        """从字典创建配置"""
        config = AgentConfig()

        # 解析各子配置
        if "financial" in data:
            config.financial = FinancialAnalysisConfig(**data["financial"])
        if "moat" in data:
            config.moat = MoatAnalysisConfig(**data["moat"])
        if "valuation" in data:
            config.valuation = ValuationConfig(**data["valuation"])
        if "safety_margin" in data:
            config.safety_margin = SafetyMarginConfig(**data["safety_margin"])
        if "buy_signal" in data:
            config.buy_signal = BuySignalConfig(**data["buy_signal"])
        if "sell_signal" in data:
            config.sell_signal = SellSignalConfig(**data["sell_signal"])
        if "risk_management" in data:
            config.risk_management = RiskManagementConfig(**data["risk_management"])
        if "psychology" in data:
            config.psychology = PsychologyDisciplineConfig(**data["psychology"])
        if "ml_scoring" in data:
            config.ml_scoring = MLScoringConfig(**data["ml_scoring"])

        # 全局设置
        config.debug_mode = data.get("debug_mode", False)
        config.log_level = data.get("log_level", "INFO")
        config.version = data.get("version", "1.0")

        return config


# ============================================================================
# 配置管理器（单例）
# ============================================================================


class AgentConfigManager:
    """Agent 配置管理器 - 单例模式"""

    _instance: Optional["AgentConfigManager"] = None
    _config: AgentConfig = AgentConfig()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls) -> AgentConfig:
        """获取当前配置"""
        return cls._config

    @classmethod
    def set_config(cls, config: AgentConfig) -> None:
        """设置配置"""
        cls._config = config
        logger.info("Agent 配置已更新")

    @classmethod
    def update_config(cls, **kwargs) -> None:
        """部分更新配置"""
        for key, value in kwargs.items():
            if hasattr(cls._config, key):
                setattr(cls._config, key, value)
        logger.info(f"Agent 配置已部分更新: {list(kwargs.keys())}")

    @classmethod
    def load_from_file(cls, path: str) -> AgentConfig:
        """从文件加载配置"""
        config = AgentConfig.load(path)
        cls._config = config
        logger.info(f"Agent 配置已从 {path} 加载")
        return config

    @classmethod
    def save_to_file(cls, path: str) -> None:
        """保存当前配置到文件"""
        cls._config.save(path)

    @classmethod
    def reset_to_default(cls) -> None:
        """重置为默认配置"""
        cls._config = AgentConfig()
        logger.info("Agent 配置已重置为默认值")

    @classmethod
    def get_financial_config(cls) -> FinancialAnalysisConfig:
        return cls._config.financial

    @classmethod
    def get_moat_config(cls) -> MoatAnalysisConfig:
        return cls._config.moat

    @classmethod
    def get_valuation_config(cls) -> ValuationConfig:
        return cls._config.valuation

    @classmethod
    def get_safety_margin_config(cls) -> SafetyMarginConfig:
        return cls._config.safety_margin

    @classmethod
    def get_buy_signal_config(cls) -> BuySignalConfig:
        return cls._config.buy_signal

    @classmethod
    def get_sell_signal_config(cls) -> SellSignalConfig:
        return cls._config.sell_signal

    @classmethod
    def get_risk_management_config(cls) -> RiskManagementConfig:
        return cls._config.risk_management

    @classmethod
    def get_psychology_config(cls) -> PsychologyDisciplineConfig:
        return cls._config.psychology

    @classmethod
    def get_ml_config(cls) -> MLScoringConfig:
        return cls._config.ml_scoring


# ============================================================================
# 便捷函数
# ============================================================================


def get_agent_config() -> AgentConfig:
    """获取全局 Agent 配置"""
    return AgentConfigManager.get_config()


def set_agent_config(config: AgentConfig) -> None:
    """设置全局 Agent 配置"""
    AgentConfigManager.set_config(config)


def load_agent_config(path: str) -> AgentConfig:
    """从文件加载 Agent 配置"""
    return AgentConfigManager.load_from_file(path)


def save_agent_config(path: str) -> None:
    """保存 Agent 配置到文件"""
    AgentConfigManager.save_to_file(path)


def reset_agent_config() -> None:
    """重置 Agent 配置为默认值"""
    AgentConfigManager.reset_to_default()
