"""
数据模型层 - 核心数据结构定义
定义价值投资分析所需的所有数据模型
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class InvestmentSignal(Enum):
    """投资信号枚举"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class FinancialMetrics:
    """财务指标数据模型"""
    stock_code: str
    pe_ratio: Optional[float] = None  # 市盈率
    pb_ratio: Optional[float] = None  # 市净率
    roe: Optional[float] = None  # 股东权益回报率
    gross_margin: Optional[float] = None  # 毛利率
    free_cash_flow: Optional[float] = None  # 自由现金流
    debt_ratio: Optional[float] = None  # 负债率
    current_price: Optional[float] = None  # 当前股价
    earnings_per_share: Optional[float] = None  # 每股收益
    book_value_per_share: Optional[float] = None  # 每股净资产
    revenue_growth: Optional[float] = None  # 收入增长率
    profit_growth: Optional[float] = None  # 利润增长率
    dividend_yield: Optional[float] = None  # 分红收益率
    update_time: datetime = field(default_factory=datetime.now)


@dataclass
class CompetitiveModality:
    """竞争优势（护城河）数据模型"""
    brand_strength: float = 0.0  # 品牌强度 (0-1)
    cost_advantage: float = 0.0  # 成本优势 (0-1)
    network_effect: float = 0.0  # 网络效应 (0-1)
    switching_cost: float = 0.0  # 转换成本 (0-1)
    overall_score: float = 0.0  # 综合护城河强度 (0-10)
    description: str = ""


@dataclass
class ValuationAnalysis:
    """估值分析数据模型"""
    stock_code: str
    intrinsic_value: Optional[float] = None  # 内在价值
    dcf_value: Optional[float] = None  # DCF估值
    pe_valuation: Optional[float] = None  # PE相对估值
    pb_valuation: Optional[float] = None  # PB相对估值
    margin_of_safety: Optional[float] = None  # 安全边际 (百分比)
    current_price: Optional[float] = None  # 当前价格
    fair_price: Optional[float] = None  # 合理价格
    valuation_score: float = 0.0  # 估值评分 (0-10)
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class BuySignalAnalysis:
    """买入点分析数据模型"""
    stock_code: str
    is_extreme_pessimism: bool = False  # 市场极度悲观
    has_temporary_difficulty: bool = False  # 公司遭遇暂时困难
    is_market_misunderstanding: bool = False  # 市场误解
    price_to_fair_ratio: Optional[float] = None  # 当前价/合理价
    buy_signal: InvestmentSignal = InvestmentSignal.HOLD
    recommended_buy_price: Optional[float] = None  # 推荐买入价
    confidence_score: float = 0.0  # 置信度 (0-1)
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class SellSignalAnalysis:
    """卖出点分析数据模型"""
    stock_code: str
    fundamental_deterioration: bool = False  # 基本面恶化
    is_severely_overvalued: bool = False  # 严重高估
    better_opportunity_exists: bool = False  # 存在更好机会
    sell_signal: InvestmentSignal = InvestmentSignal.HOLD
    recommended_sell_price: Optional[float] = None  # 推荐卖出价
    confidence_score: float = 0.0  # 置信度 (0-1)
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class RiskAssessment:
    """风险评估数据模型"""
    stock_code: str
    ability_circle_match: float = 0.0  # 能力圈匹配度 (0-1)
    leverage_risk: float = 0.0  # 杠杆风险 (0-1)
    industry_risk: float = 0.0  # 行业风险 (0-1)
    company_risk: float = 0.0  # 公司风险 (0-1)
    overall_risk_level: RiskLevel = RiskLevel.HIGH
    risk_mitigation_strategies: List[str] = field(default_factory=list)
    assessment_date: datetime = field(default_factory=datetime.now)


@dataclass
class InvestmentDecision:
    """行为纪律 - 投资决策数据模型"""
    stock_code: str
    decision: InvestmentSignal = InvestmentSignal.HOLD
    action_price: Optional[float] = None  # 执行价格
    stop_loss_price: Optional[float] = None  # 止损价格
    take_profit_price: Optional[float] = None  # 止盈价格
    position_size: float = 0.0  # 仓位大小 (0-1)
    conviction_level: float = 0.0  # 信念强度 (0-1)
    checklist_passed: bool = False  # 决策检查清单通过
    decision_date: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class StockAnalysisContext:
    """股票分析上下文 - 贯穿整个分析流程"""
    stock_code: str
    stock_name: str = ""
    analysis_date: datetime = field(default_factory=datetime.now)

    # 第一层：数据准备
    financial_metrics: Optional[FinancialMetrics] = None

    # 第二层：基础分析
    competitive_moat: Optional[CompetitiveModality] = None  # 护城河

    # 第三层：财务分析（已通过 financial_metrics 包含）

    # 第四层：估值分析
    valuation: Optional[ValuationAnalysis] = None

    # 第五层：安全边际
    safety_margin_ok: bool = False

    # 第六层：交易点分析
    buy_signal: Optional[BuySignalAnalysis] = None
    sell_signal: Optional[SellSignalAnalysis] = None

    # 第七层：风险管理
    risk_assessment: Optional[RiskAssessment] = None

    # 第八层：行为纪律
    investment_decision: Optional[InvestmentDecision] = None

    # 综合评分
    overall_score: float = 0.0  # 综合评分 (0-100)
    final_signal: InvestmentSignal = InvestmentSignal.HOLD
    analysis_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "analysis_date": self.analysis_date.isoformat(),
            "financial_metrics": self.financial_metrics.__dict__ if self.financial_metrics else None,
            "competitive_moat": self.competitive_moat.__dict__ if self.competitive_moat else None,
            "valuation": self.valuation.__dict__ if self.valuation else None,
            "buy_signal": self.buy_signal.__dict__ if self.buy_signal else None,
            "sell_signal": self.sell_signal.__dict__ if self.sell_signal else None,
            "risk_assessment": self.risk_assessment.__dict__ if self.risk_assessment else None,
            "investment_decision": self.investment_decision.__dict__ if self.investment_decision else None,
            "overall_score": self.overall_score,
            "final_signal": self.final_signal.value,
            "analysis_summary": self.analysis_summary,
        }


@dataclass
class AnalysisReport:
    """分析报告数据模型"""
    report_id: str
    stocks: List[StockAnalysisContext] = field(default_factory=list)
    report_date: datetime = field(default_factory=datetime.now)
    total_stocks_analyzed: int = 0
    strong_buy_count: int = 0
    buy_count: int = 0
    hold_count: int = 0
    sell_count: int = 0
    strong_sell_count: int = 0

    def generate_summary(self) -> str:
        """生成报告摘要"""
        return f"""
=== 价值投资分析报告 ===
报告日期: {self.report_date.strftime('%Y-%m-%d %H:%M:%S')}
分析股票数: {self.total_stocks_analyzed}

推荐结果统计:
- 强烈买入: {self.strong_buy_count}
- 买入: {self.buy_count}
- 持有: {self.hold_count}
- 卖出: {self.sell_count}
- 强烈卖出: {self.strong_sell_count}
"""
