"""
演示脚本 - 展示系统的各项功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.data_models import (
    StockAnalysisContext, FinancialMetrics, CompetitiveModality,
    ValuationAnalysis, BuySignalAnalysis, InvestmentSignal
)
from src.schedulers.workflow_scheduler import WorkflowScheduler, AnalysisManager, ExecutionMode
from src.agents.value_investing_agents import (
    EquityThinkingAgent, MoatAgent, FinancialAnalysisAgent,
    ValuationAgent, SafetyMarginAgent
)


def demo_data_models():
    """演示：数据模型"""
    print("\n" + "="*80)
    print("演示 1: 数据模型")
    print("="*80)

    # 创建财务指标
    metrics = FinancialMetrics(
        stock_code="600519",
        pe_ratio=25.0,
        pb_ratio=10.0,
        roe=0.20,
        gross_margin=0.60,
        current_price=1000.0,
        earnings_per_share=40.0,
        debt_ratio=0.25,
        profit_growth=0.15
    )

    print(f"\n财务指标 - {metrics.stock_code}")
    print(f"  PE比率:     {metrics.pe_ratio}")
    print(f"  PB比率:     {metrics.pb_ratio}")
    print(f"  ROE:        {metrics.roe}")
    print(f"  毛利率:     {metrics.gross_margin}")
    print(f"  当前价格:   {metrics.current_price}")
    print(f"  负债率:     {metrics.debt_ratio}")

    # 创建竞争优势
    moat = CompetitiveModality(
        brand_strength=0.8,
        cost_advantage=0.7,
        network_effect=0.6,
        switching_cost=0.5,
        overall_score=8.0
    )

    print(f"\n竞争优势 (护城河)")
    print(f"  品牌强度:   {moat.brand_strength}/1.0")
    print(f"  成本优势:   {moat.cost_advantage}/1.0")
    print(f"  网络效应:   {moat.network_effect}/1.0")
    print(f"  转换成本:   {moat.switching_cost}/1.0")
    print(f"  综合强度:   {moat.overall_score}/10")


def demo_single_agents():
    """演示：单个 Agent"""
    print("\n" + "="*80)
    print("演示 2: 单个 Agent 分析")
    print("="*80)

    # 创建分析上下文
    context = StockAnalysisContext(
        stock_code="600519",
        stock_name="贵州茅台"
    )

    context.financial_metrics = FinancialMetrics(
        stock_code="600519",
        pe_ratio=25.0,
        pb_ratio=10.0,
        roe=0.20,
        gross_margin=0.60,
        current_price=1000.0,
        earnings_per_share=40.0,
        debt_ratio=0.25,
        profit_growth=0.15,
        free_cash_flow=1000000000
    )

    # 执行股权思维 Agent
    print("\n执行: 股权思维 Agent")
    agent1 = EquityThinkingAgent()
    context = agent1.execute(context)
    print(f"  综合评分: {context.overall_score:.2f}")

    # 执行护城河 Agent
    print("\n执行: 护城河 Agent")
    agent2 = MoatAgent()
    context = agent2.execute(context)
    if context.competitive_moat:
        print(f"  护城河强度: {context.competitive_moat.overall_score:.1f}/10")

    # 执行财务分析 Agent
    print("\n执行: 财务分析 Agent")
    agent3 = FinancialAnalysisAgent()
    context = agent3.execute(context)
    print(f"  综合评分: {context.overall_score:.2f}")

    # 执行估值 Agent
    print("\n执行: 估值 Agent")
    agent4 = ValuationAgent()
    context = agent4.execute(context)
    if context.valuation:
        print(f"  内在价值: {context.valuation.intrinsic_value:.2f}")
        print(f"  合理价格: {context.valuation.fair_price:.2f}")
        print(f"  估值评分: {context.valuation.valuation_score:.1f}/10")

    # 执行安全边际 Agent
    print("\n执行: 安全边际 Agent")
    agent5 = SafetyMarginAgent()
    context = agent5.execute(context)
    if context.valuation:
        print(f"  安全边际: {context.valuation.margin_of_safety:.2f}%")
        print(f"  安全边际OK: {context.safety_margin_ok}")


def demo_workflow():
    """演示：完整工作流"""
    print("\n" + "="*80)
    print("演示 3: 完整工作流")
    print("="*80)

    # 创建调度器
    scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
    scheduler.register_agents()

    print(f"\n已注册 {len(scheduler.agents)} 个 Agent:")
    for i, agent in enumerate(scheduler.agents, 1):
        print(f"  {i}. {agent.name}")

    # 演示数据流转（不调用实际 API）
    print("\n执行分析流程（使用 Mock 数据）...")

    context = StockAnalysisContext(
        stock_code="600519",
        stock_name="贵州茅台"
    )

    context.financial_metrics = FinancialMetrics(
        stock_code="600519",
        pe_ratio=25.0,
        pb_ratio=10.0,
        roe=0.20,
        gross_margin=0.60,
        current_price=1000.0,
        earnings_per_share=40.0,
        debt_ratio=0.25,
        profit_growth=0.15,
        free_cash_flow=1000000000
    )

    # 执行完整流程
    result = scheduler._execute_sequential(context)

    print(f"\n分析完成！")
    print(f"  综合评分: {result.overall_score:.2f}/100")
    print(f"  最终信号: {result.final_signal.value}")

    if result.investment_decision:
        print(f"  建议仓位: {result.investment_decision.position_size:.2%}")
        print(f"  执行价格: {result.investment_decision.action_price}")

    print(f"\n分析摘要: {result.analysis_summary}")


def demo_analysis_manager():
    """演示：分析管理器"""
    print("\n" + "="*80)
    print("演示 4: 分析管理器")
    print("="*80)

    manager = AnalysisManager()

    print(f"\n分析管理器已初始化")
    print(f"  注册Agent数: {len(manager.scheduler.agents)}")

    print("\n支持的方法:")
    print("  1. analyze_single_stock(stock_code)")
    print("  2. analyze_portfolio(stock_codes)")
    print("  3. get_investment_recommendations(stock_codes, signal)")

    print("\n工作流摘要:")
    print(manager.scheduler.get_execution_summary())


def demo_investment_signals():
    """演示：投资信号"""
    print("\n" + "="*80)
    print("演示 5: 投资信号说明")
    print("="*80)

    signals = [
        (InvestmentSignal.STRONG_BUY, "🟢🟢 强烈买入", "综合评分 ≥80，多项指标优秀"),
        (InvestmentSignal.BUY, "🟢 买入", "综合评分 ≥70，安全边际充足"),
        (InvestmentSignal.HOLD, "🟡 持有", "综合评分 50-70，中等风险"),
        (InvestmentSignal.SELL, "🔴 卖出", "综合评分 <50，或基本面恶化"),
        (InvestmentSignal.STRONG_SELL, "🔴🔴 强烈卖出", "基本面严重恶化，严重高估"),
    ]

    for signal, emoji_name, description in signals:
        print(f"\n{emoji_name}")
        print(f"  代码: {signal.value}")
        print(f"  说明: {description}")


def demo_architecture():
    """演示：系统架构"""
    print("\n" + "="*80)
    print("演示 6: 系统架构")
    print("="*80)

    print("""
三层分层架构：

┌─────────────────────────────────────────┐
│         应用层 (Application Layer)       │
│      CLI接口 / 报告生成 / 用户交互      │
│  ├─ CLI命令: analyze, portfolio, buy    │
│  ├─ 交互模式: 实时命令输入              │
│  └─ 报告输出: 结构化分析报告            │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│         调度层 (Scheduler Layer)         │
│   WorkflowScheduler / AnalysisManager   │
│  ├─ Agent编排: 顺序/并行执行            │
│  ├─ 依赖管理: 确保正确执行顺序         │
│  └─ 结果聚合: 综合多Agent分析结果      │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│      数据模型层 (Data Model Layer)       │
│   DataModels / AkshareDataProvider     │
│  ├─ 数据模型: StockAnalysisContext     │
│  ├─ 数据获取: akshare API集成          │
│  └─ 数据验证: DataValidator            │
└─────────────────────────────────────────┘


9个核心Agent执行流程：

┌─ 数据准备
│  ├─ 步骤1: 股权思维Agent
│  ├─ 步骤2: 护城河Agent      (可并行)
│  └─ 步骤3: 财务分析Agent    (可并行)
│
├─ 估值与交易分析
│  ├─ 步骤4: 估值Agent
│  ├─ 步骤5: 安全边际Agent
│  ├─ 步骤6: 买入点Agent
│  └─ 步骤7: 卖出纪律Agent
│
└─ 风险与决策
   ├─ 步骤8: 风险管理Agent
   └─ 步骤9: 心理纪律Agent
    """)


def main():
    """主演示程序"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "价值投资分析系统 (VIMaster) - 功能演示".center(78) + "║")
    print("╚" + "="*78 + "╝")

    print("\n本演示展示系统的以下功能:")
    print("  1. 数据模型演示")
    print("  2. 单个Agent分析演示")
    print("  3. 完整工作流演示")
    print("  4. 分析管理器演示")
    print("  5. 投资信号说明")
    print("  6. 系统架构说明")

    # 运行演示
    demo_data_models()
    demo_single_agents()
    demo_workflow()
    demo_analysis_manager()
    demo_investment_signals()
    demo_architecture()

    print("\n" + "="*80)
    print("演示完成！")
    print("="*80)
    print("\n了解更多信息，请参考:")
    print("  - README.md: 项目文档和使用说明")
    print("  - src/app.py: 应用层实现")
    print("  - tests/: 测试用例和示例")
    print("\n运行程序:")
    print("  python run.py          # 交互模式")
    print("  python run.py analyze 600519  # 分析单只股票")
    print("\n运行测试:")
    print("  pytest tests/          # 运行全部测试")
    print("  pytest tests/unit -v   # 单元测试")
    print("  pytest tests/integration -v  # 集成测试")
    print()


if __name__ == "__main__":
    main()
