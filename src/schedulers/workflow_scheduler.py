"""
调度层 - 工作流引擎
负责 Agent 的编排、依赖管理和结果聚合
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from src.models.data_models import (
    StockAnalysisContext, AnalysisReport, InvestmentSignal, FinancialMetrics
)
from src.agents.base_agent import BaseAgent
from src.agents.value_investing_agents import (
    EquityThinkingAgent, MoatAgent, FinancialAnalysisAgent,
    ValuationAgent, SafetyMarginAgent, BuySignalAgent,
    SellSignalAgent, RiskManagementAgent, BehavioralDisciplineAgent
)
from src.data.akshare_provider import AkshareDataProvider

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行（当前版本仅支持部分并行）


class WorkflowScheduler:
    """
    工作流调度器
    负责 Agent 的执行编排和工作流管理
    """

    def __init__(self, execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL):
        self.execution_mode = execution_mode
        self.agents: List[BaseAgent] = []
        self.execution_history: List[Dict[str, Any]] = []

    def register_agents(self) -> None:
        """注册所有价值投资 Agent"""
        self.agents = [
            EquityThinkingAgent(),
            MoatAgent(),
            FinancialAnalysisAgent(),
            ValuationAgent(),
            SafetyMarginAgent(),
            BuySignalAgent(),
            SellSignalAgent(),
            RiskManagementAgent(),
            BehavioralDisciplineAgent(),
        ]
        logger.info(f"已注册 {len(self.agents)} 个 Agent")

    def analyze_stock(self, stock_code: str, stock_name: str = "") -> Optional[StockAnalysisContext]:
        """
        分析单只股票的完整工作流

        Args:
            stock_code: 股票代码
            stock_name: 股票名称（可选）

        Returns:
            分析上下文或 None
        """
        logger.info(f"开始分析股票: {stock_code} {stock_name}")

        # 初始化分析上下文
        context = StockAnalysisContext(
            stock_code=stock_code,
            stock_name=stock_name,
        )

        # 步骤 1: 数据准备
        logger.info(f"步骤 1: 获取财务数据")
        metrics = AkshareDataProvider.get_financial_metrics(stock_code)
        if not metrics:
            logger.error(f"无法获取股票 {stock_code} 的财务数据")
            return None

        context.financial_metrics = metrics
        context.stock_name = metrics.stock_code  # 更新股票名称

        # 步骤 2-9: 执行 Agent 分析
        try:
            if self.execution_mode == ExecutionMode.SEQUENTIAL:
                context = self._execute_sequential(context)
            else:
                context = self._execute_with_dependencies(context)

            # 最终综合评估
            context = self._finalize_analysis(context)

            logger.info(f"股票 {stock_code} 分析完成，综合评分: {context.overall_score:.2f}/100")
            return context

        except Exception as e:
            logger.error(f"分析失败: {str(e)}", exc_info=True)
            return None

    def _execute_sequential(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        顺序执行所有 Agent

        执行顺序：
        1. 股权思维 Agent
        2. 护城河 Agent
        3. 财务分析 Agent
        4. 估值 Agent
        5. 安全边际 Agent
        6. 买入点 Agent
        7. 卖出纪律 Agent
        8. 风险管理 Agent
        9. 心理纪律 Agent
        """
        for agent in self.agents:
            try:
                context = agent.execute(context)
                self._record_execution(agent, "success", context)
            except Exception as e:
                logger.error(f"Agent {agent.name} 执行失败: {str(e)}")
                self._record_execution(agent, "failed", context, error=str(e))

        return context

    def _execute_with_dependencies(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        考虑依赖关系的执行策略
        当前版本简化为顺序执行，可扩展为真正的并行执行
        """
        # 基础分析阶段（可并行）
        base_agents = [self.agents[0], self.agents[1], self.agents[2]]  # 股权思维、护城河、财务分析
        for agent in base_agents:
            context = agent.execute(context)

        # 估值与交易阶段（依赖基础分析）
        valuation_agents = [self.agents[3], self.agents[4], self.agents[5], self.agents[6]]  # 估值、安全边际、买入点、卖出点
        for agent in valuation_agents:
            context = agent.execute(context)

        # 风险与决策阶段（依赖前面所有分析）
        risk_agents = [self.agents[7], self.agents[8]]  # 风险管理、心理纪律
        for agent in risk_agents:
            context = agent.execute(context)

        return context

    def _record_execution(self, agent: BaseAgent, status: str, context: StockAnalysisContext, error: str = "") -> None:
        """记录 Agent 执行历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent.name,
            "status": status,
            "execution_time": agent.execution_time,
            "stock_code": context.stock_code,
            "error": error,
        }
        self.execution_history.append(record)

    def _finalize_analysis(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        最终化分析结果
        生成综合评分和分析摘要
        """
        # 规范化综合评分到 0-100
        context.overall_score = min(100, max(0, context.overall_score * 10))

        # 生成分析摘要
        summary_parts = []

        if context.financial_metrics:
            summary_parts.append(f"财务状况: ROE={context.financial_metrics.roe or 'N/A'}, PE={context.financial_metrics.pe_ratio or 'N/A'}")

        if context.competitive_moat:
            summary_parts.append(f"竞争优势: 护城河强度={context.competitive_moat.overall_score:.1f}/10")

        if context.valuation:
            summary_parts.append(f"估值分析: 内在价值={context.valuation.intrinsic_value or 'N/A':.2f}, 安全边际={context.valuation.margin_of_safety or 'N/A':.2f}%")

        if context.investment_decision:
            summary_parts.append(f"投资建议: {context.investment_decision.decision.value}")

        if context.risk_assessment:
            summary_parts.append(f"风险等级: {context.risk_assessment.overall_risk_level.value}")

        context.analysis_summary = " | ".join(summary_parts)

        return context

    def analyze_stocks(self, stock_codes: List[str]) -> AnalysisReport:
        """
        分析多只股票，生成综合报告

        Args:
            stock_codes: 股票代码列表

        Returns:
            分析报告
        """
        logger.info(f"开始分析 {len(stock_codes)} 只股票")

        report = AnalysisReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        for stock_code in stock_codes:
            context = self.analyze_stock(stock_code)
            if context:
                report.stocks.append(context)
                report.total_stocks_analyzed += 1

                # 统计信号
                signal = context.final_signal
                if signal == InvestmentSignal.STRONG_BUY:
                    report.strong_buy_count += 1
                elif signal == InvestmentSignal.BUY:
                    report.buy_count += 1
                elif signal == InvestmentSignal.HOLD:
                    report.hold_count += 1
                elif signal == InvestmentSignal.SELL:
                    report.sell_count += 1
                elif signal == InvestmentSignal.STRONG_SELL:
                    report.strong_sell_count += 1

        logger.info(f"分析完成: {report.total_stocks_analyzed}/{len(stock_codes)} 只股票")
        return report

    def get_execution_summary(self) -> str:
        """获取执行摘要"""
        summary = f"""
=== 工作流执行摘要 ===
执行模式: {self.execution_mode.value}
注册Agent数: {len(self.agents)}
执行历史记录: {len(self.execution_history)}

Agent列表:
"""
        for agent in self.agents:
            summary += f"  - {agent.name}: {agent.description}\n"

        return summary


class AnalysisManager:
    """
    分析管理器
    提供高级分析接口
    """

    def __init__(self):
        self.scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
        self.scheduler.register_agents()

    def analyze_single_stock(self, stock_code: str) -> Optional[StockAnalysisContext]:
        """分析单只股票"""
        return self.scheduler.analyze_stock(stock_code)

    def analyze_portfolio(self, stock_codes: List[str]) -> AnalysisReport:
        """分析股票组合"""
        return self.scheduler.analyze_stocks(stock_codes)

    def get_investment_recommendations(self, stock_codes: List[str], signal: InvestmentSignal) -> List[StockAnalysisContext]:
        """
        获取特定信号的投资建议

        Args:
            stock_codes: 股票代码列表
            signal: 投资信号（STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL）

        Returns:
            符合条件的股票分析列表
        """
        report = self.scheduler.analyze_stocks(stock_codes)
        return [stock for stock in report.stocks if stock.final_signal == signal]
