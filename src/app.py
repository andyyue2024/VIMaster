"""
应用层 - 命令行接口 (CLI) 和主程序入口
"""
import logging
import sys
from typing import List, Optional, Dict
from src.schedulers.workflow_scheduler import AnalysisManager
from src.models.data_models import InvestmentSignal
from src.ml import StockMLScorer
from src.agents.agent_config import AgentConfigManager, load_agent_config
from src.reports import ReportManager, StockReportData, PortfolioReportData, ReportTemplate
from src.storage import AnalysisRepository
from src.community import create_community_service, CommunityService
from src.visualization import create_visualizer, StockVisualizer, check_visualization_available
# LLM 大师 Agents
from src.agents.llm import (
    LLMConfigManager,
    get_all_master_agents,
    get_master_agent_by_name,
)
from src.agents.llm.master_agents import run_all_masters_analysis, get_master_consensus
# LLM 专家 Agents
from src.agents.llm.expert_agents import (
    get_all_expert_agents,
    get_expert_agent_by_name,
    run_all_experts_analysis,
    get_expert_consensus,
)
import os
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValueInvestingApp:
    """价值投资分析应用"""

    def __init__(self, config_path: str = None):
        # 加载 Agent 配置（如果指定）
        if config_path and os.path.exists(config_path):
            load_agent_config(config_path)
            logger.info(f"已加载 Agent 配置: {config_path}")

        self.manager = AnalysisManager()
        self.ml_scorer = StockMLScorer()
        self.report_manager = ReportManager()
        self.visualizer = create_visualizer() if check_visualization_available() else None
        logger.info("价值投资分析应用已初始化")

    def analyze_single_stock(self, stock_code: str) -> None:
        """分析单只股票并打印结果"""
        logger.info(f"分析股票: {stock_code}")

        context = self.manager.analyze_single_stock(stock_code)
        if context:
            self._print_stock_report(context)
            # ML 评分（如果能获取财务指标）
            try:
                fm = context.financial_metrics
                if fm:
                    ml_result = self.ml_scorer.score_stock(stock_code, {
                        "pe_ratio": fm.pe_ratio,
                        "pb_ratio": fm.pb_ratio,
                        "roe": fm.roe,
                        "gross_margin": fm.gross_margin,
                        "free_cash_flow": fm.free_cash_flow,
                        "debt_ratio": fm.debt_ratio,
                    })
                    print("\n[ML评分] 综合机器学习分数 (0-10):", ml_result["ml_score"])
                else:
                    logger.info("缺少财务指标，跳过 ML 评分")
            except Exception as e:
                logger.warning(f"ML 评分失败: {e}")
        else:
            print(f"[!] 无法分析股票 {stock_code}，请检查代码是否正确")

    def analyze_with_masters(self, stock_code: str, master_names: List[str] = None) -> None:
        """
        使用 LLM 大师 Agent 分析股票

        Args:
            stock_code: 股票代码
            master_names: 指定的大师名称列表，为空则使用所有大师
        """
        logger.info(f"使用 LLM 大师分析股票: {stock_code}")

        # 首先获取基础分析数据
        context = self.manager.analyze_single_stock(stock_code)
        if not context:
            print(f"[!] 无法获取股票 {stock_code} 的基础数据")
            return

        # 运行大师分析
        if master_names:
            for name in master_names:
                agent = get_master_agent_by_name(name)
                if agent:
                    try:
                        logger.info(f"运行 {agent.name} 分析...")
                        context = agent.execute(context)
                    except Exception as e:
                        logger.error(f"{agent.name} 分析失败: {e}")
                        print(f"⚠ {agent.name} 分析失败: {e}")
                else:
                    print(f"⚠ 未找到大师: {name}")
        else:
            try:
                context = run_all_masters_analysis(context)
            except Exception as e:
                logger.error(f"大师分析失败: {e}")
                print(f"⚠ 大师分析失败: {e}")
                return

        # 打印大师分析结果
        self._print_llm_analysis(context, "master")

    def analyze_with_experts(self, stock_code: str, expert_names: List[str] = None) -> None:
        """
        使用 LLM 专家 Agent 分析股票

        Args:
            stock_code: 股票代码
            expert_names: 指定的专家名称列表，为空则使用所有专家
        """
        logger.info(f"使用 LLM 专家分析股票: {stock_code}")

        # 首先获取基础分析数据
        context = self.manager.analyze_single_stock(stock_code)
        if not context:
            print(f"[!] 无法获取股票 {stock_code} 的基础数据")
            return

        # 运行专家分析
        if expert_names:
            for name in expert_names:
                agent = get_expert_agent_by_name(name)
                if agent:
                    try:
                        logger.info(f"运行 {agent.name} 分析...")
                        context = agent.execute(context)
                    except Exception as e:
                        logger.error(f"{agent.name} 分析失败: {e}")
                        print(f"⚠ {agent.name} 分析失败: {e}")
                else:
                    print(f"⚠ 未找到专家: {name}")
        else:
            try:
                context = run_all_experts_analysis(context)
            except Exception as e:
                logger.error(f"专家分析失败: {e}")
                print(f"⚠ 专家分析失败: {e}")
                return

        # 打印专家分析结果
        self._print_llm_analysis(context, "expert")

    def _print_llm_analysis(self, context, analysis_type: str = "master") -> None:
        """打印 LLM 分析结果"""
        if analysis_type == "master":
            title = "投资大师"
            signals = getattr(context, 'master_signals', {})
            get_consensus = get_master_consensus
        else:
            title = "分析专家"
            signals = getattr(context, 'expert_signals', {})
            get_consensus = get_expert_consensus

        print("\n" + "="*80)
        print(f"{title}分析报告 - {context.stock_code}")
        print("="*80)

        if not signals:
            print(f"\n⚠ 没有{title}分析数据")
            return

        # 打印每位大师/专家的分析
        for key, signal in signals.items():
            signal_emoji = {
                "bullish": "🟢",
                "bearish": "🔴",
                "neutral": "🟡",
            }.get(signal.signal, "⚪")

            print(f"\n【{signal.agent_name}】 {signal_emoji} {signal.signal.upper()}")
            print(f"  信心度: {signal.confidence:.1f}%")
            reasoning = signal.reasoning if isinstance(signal.reasoning, str) else str(signal.reasoning)
            print(f"  分析理由: {reasoning[:300]}...")

        # 打印共识
        consensus = get_consensus(context)
        print("\n" + "-"*80)
        print(f"【{title}共识】")
        print(f"  共识信号: {consensus['consensus'].upper()}")
        print(f"  看涨: {consensus['bullish_count']} | 中性: {consensus['neutral_count']} | 看跌: {consensus['bearish_count']}")
        print(f"  平均信心度: {consensus['average_confidence']:.1f}%")
        print("="*80)

    def analyze_multiple_stocks(self, stock_codes: List[str]) -> None:
        """分析多只股票并生成报告"""
        logger.info(f"分析 {len(stock_codes)} 只股票")

        report = self.manager.analyze_portfolio(stock_codes)
        self._print_portfolio_report(report)

    def get_buy_recommendations(self, stock_codes: List[str]) -> None:
        """获取买入推荐"""
        recommendations = self.manager.get_investment_recommendations(stock_codes, InvestmentSignal.STRONG_BUY)
        if recommendations:
            print("\n" + "="*60)
            print("强烈买入推荐")
            print("="*60)
            for stock in recommendations:
                print(f"股票: {stock.stock_code}")
                if stock.financial_metrics:
                    print(f"  当前价格: {stock.financial_metrics.current_price}")
                if stock.valuation:
                    print(f"  合理价格: {stock.valuation.fair_price:.2f}")
                    print(f"  安全边际: {stock.valuation.margin_of_safety:.2f}%")
                if stock.investment_decision:
                    print(f"  建议买入价: {stock.investment_decision.action_price}")
                print()
        else:
            print("没有强烈买入推荐")

    def visualize_stock(self, stock_code: str, output_dir: str = "charts") -> Dict[str, str]:
        """
        生成股票分析可视化图表

        Args:
            stock_code: 股票代码
            output_dir: 输出目录

        Returns:
            生成的图表路径字典
        """
        if not self.visualizer:
            print("⚠ 可视化功能不可用，请安装 matplotlib: pip install matplotlib")
            return {}

        logger.info(f"生成 {stock_code} 可视化图表...")

        # 获取分析结果
        context = self.manager.analyze_single_stock(stock_code)
        if not context:
            print(f"[!] 无法获取 {stock_code} 的分析数据")
            return {}

        # 生成图表
        charts = self.visualizer.generate_analysis_report(context, output_dir=output_dir)

        if charts:
            print(f"\n✓ 已生成 {len(charts)} 张图表:")
            for name, path in charts.items():
                print(f"  {name}: {path}")
        else:
            print("未能生成图表")

        return charts

    def generate_stock_report(self, stock_code: str, output_dir: str = "reports", formats: List[str] = None) -> Dict[str, bool]:
        """生成单只股票的分析报告"""
        if formats is None:
            formats = ["pdf", "excel"]

        logger.info(f"生成股票 {stock_code} 报告...")

        # 获取分析结果
        context = self.manager.analyze_single_stock(stock_code)
        if not context:
            logger.error(f"无法获取股票 {stock_code} 的分析数据")
            return {}

        # 构建报告数据
        report_data = self._context_to_report_data(context)

        # 生成报告
        results = {}
        os.makedirs(output_dir, exist_ok=True)

        if "pdf" in formats:
            pdf_path = os.path.join(output_dir, f"{stock_code}_report.pdf")
            results["pdf"] = self.report_manager.generate_pdf(report_data, pdf_path)
            if results["pdf"]:
                print(f"✓ PDF 报告已生成: {pdf_path}")

        if "excel" in formats:
            excel_path = os.path.join(output_dir, f"{stock_code}_report.xlsx")
            results["excel"] = self.report_manager.generate_excel(report_data, excel_path)
            if results["excel"]:
                print(f"✓ Excel 报告已生成: {excel_path}")

        return results

    def generate_portfolio_report(self, stock_codes: List[str], output_dir: str = "reports", formats: List[str] = None) -> Dict[str, bool]:
        """生成投资组合报告"""
        if formats is None:
            formats = ["pdf", "excel"]

        logger.info(f"生成投资组合报告，包含 {len(stock_codes)} 只股票...")

        # 获取分析结果
        report = self.manager.analyze_portfolio(stock_codes)
        if not report:
            logger.error("无法获取组合分析数据")
            return {}

        # 构建报告数据
        portfolio_data = PortfolioReportData(
            report_id=report.report_id,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total_stocks=report.total_stocks_analyzed,
            strong_buy_count=report.strong_buy_count,
            buy_count=report.buy_count,
            hold_count=report.hold_count,
            sell_count=report.sell_count,
            strong_sell_count=report.strong_sell_count,
        )

        for stock in report.stocks:
            portfolio_data.stocks.append(self._context_to_report_data(stock))

        # 生成报告
        results = {}
        os.makedirs(output_dir, exist_ok=True)

        if "pdf" in formats:
            pdf_path = os.path.join(output_dir, "portfolio_report.pdf")
            results["pdf"] = self.report_manager.generate_portfolio_pdf(portfolio_data, pdf_path)
            if results["pdf"]:
                print(f"✓ PDF 组合报告已生成: {pdf_path}")

        if "excel" in formats:
            excel_path = os.path.join(output_dir, "portfolio_report.xlsx")
            results["excel"] = self.report_manager.generate_portfolio_excel(portfolio_data, excel_path)
            if results["excel"]:
                print(f"✓ Excel 组合报告已生成: {excel_path}")

        return results

    def _context_to_report_data(self, context) -> StockReportData:
        """将分析上下文转换为报告数据"""
        data = StockReportData(stock_code=context.stock_code)

        if context.financial_metrics:
            fm = context.financial_metrics
            data.current_price = fm.current_price
            data.pe_ratio = fm.pe_ratio
            data.pb_ratio = fm.pb_ratio
            data.roe = fm.roe
            data.gross_margin = fm.gross_margin
            data.debt_ratio = fm.debt_ratio
            data.free_cash_flow = fm.free_cash_flow

        if context.valuation:
            val = context.valuation
            data.intrinsic_value = val.intrinsic_value
            data.fair_price = val.fair_price
            data.margin_of_safety = val.margin_of_safety
            data.valuation_score = val.valuation_score

        if context.competitive_moat:
            moat = context.competitive_moat
            data.moat_score = moat.overall_score
            data.brand_strength = moat.brand_strength
            data.cost_advantage = moat.cost_advantage

        if context.risk_assessment:
            risk = context.risk_assessment
            data.risk_level = risk.overall_risk_level.value if risk.overall_risk_level else ""
            data.leverage_risk = risk.leverage_risk

        if context.buy_signal:
            data.buy_signal = context.buy_signal.buy_signal.value if context.buy_signal.buy_signal else ""

        if context.sell_signal:
            data.sell_signal = context.sell_signal.sell_signal.value if context.sell_signal.sell_signal else ""

        data.final_signal = context.final_signal.value if context.final_signal else ""
        data.overall_score = context.overall_score

        if context.investment_decision:
            dec = context.investment_decision
            data.decision = dec.decision.value if dec.decision else ""
            data.position_size = dec.position_size
            data.stop_loss = dec.stop_loss_price
            data.take_profit = dec.take_profit_price

        return data

    def _print_stock_report(self, context) -> None:
        """打印单只股票的详细报告"""
        print("\n" + "="*80)
        print(f"价值投资分析报告 - {context.stock_code}")
        print("="*80)

        # 财务指标
        if context.financial_metrics:
            print("\n【财务指标】")
            metrics = context.financial_metrics
            print(f"  当前价格:     {metrics.current_price or 'N/A'}")
            print(f"  PE比率:       {metrics.pe_ratio or 'N/A'}")
            print(f"  PB比率:       {metrics.pb_ratio or 'N/A'}")
            print(f"  ROE:          {metrics.roe or 'N/A'}")
            print(f"  毛利率:       {metrics.gross_margin or 'N/A'}")
            print(f"  自由现金流:   {metrics.free_cash_flow or 'N/A'}")
            print(f"  负债率:       {metrics.debt_ratio or 'N/A'}")

        # 竞争优势
        if context.competitive_moat:
            print("\n【竞争优势（护城河）】")
            moat = context.competitive_moat
            print(f"  护城河强度:   {moat.overall_score:.1f}/10")
            print(f"  品牌强度:     {moat.brand_strength:.1f}/1.0")
            print(f"  成本优势:     {moat.cost_advantage:.1f}/1.0")
            print(f"  网络效应:     {moat.network_effect:.1f}/1.0")
            print(f"  转换成本:     {moat.switching_cost:.1f}/1.0")

        # 估值分析
        if context.valuation:
            print("\n【估值分析】")
            valuation = context.valuation
            print(f"  内在价值:     {valuation.intrinsic_value:.2f}")
            print(f"  合理价格:     {valuation.fair_price:.2f}")
            print(f"  安全边际:     {valuation.margin_of_safety:.2f}%")
            print(f"  估值评分:     {valuation.valuation_score:.1f}/10")

        # 买入信号
        if context.buy_signal:
            print("\n【买入分析】")
            buy = context.buy_signal
            print(f"  市场极度悲观: {buy.is_extreme_pessimism}")
            print(f"  暂时性困难:   {buy.has_temporary_difficulty}")
            print(f"  市场误解:     {buy.is_market_misunderstanding}")
            print(f"  买入信号:     {buy.buy_signal.value}")
            print(f"  置信度:       {buy.confidence_score:.2f}")

        # 卖出信号
        if context.sell_signal:
            print("\n【卖出分析】")
            sell = context.sell_signal
            print(f"  基本面恶化:   {sell.fundamental_deterioration}")
            print(f"  严重高估:     {sell.is_severely_overvalued}")
            print(f"  卖出信号:     {sell.sell_signal.value}")
            print(f"  置信度:       {sell.confidence_score:.2f}")

        # 风险评估
        if context.risk_assessment:
            print("\n【风险评估】")
            risk = context.risk_assessment
            print(f"  风险等级:     {risk.overall_risk_level.value}")
            print(f"  能力圈匹配:   {risk.ability_circle_match:.2f}")
            print(f"  杠杆风险:     {risk.leverage_risk:.2f}")
            print(f"  行业风险:     {risk.industry_risk:.2f}")
            print(f"  公司风险:     {risk.company_risk:.2f}")
            if risk.risk_mitigation_strategies:
                print(f"  风险策略:     {', '.join(risk.risk_mitigation_strategies)}")

        # 投资决策
        if context.investment_decision:
            print("\n【投资决策】")
            decision = context.investment_decision
            print(f"  最终建议:     {decision.decision.value}")
            print(f"  信念强度:     {decision.conviction_level:.2f}")
            print(f"  执行价格:     {decision.action_price}")
            print(f"  止损价:       {decision.stop_loss_price}")
            print(f"  止盈价:       {decision.take_profit_price}")
            print(f"  建议仓位:     {decision.position_size:.2%}")
            print(f"  决策清单通过: {'YES' if decision.checklist_passed else 'NO'}")

        # 综合评分
        print("\n【综合评估】")
        print(f"  综合评分:     {context.overall_score:.2f}/100")
        print(f"  最终信号:     {context.final_signal.value}")
        if context.analysis_summary:
            print(f"  分析摘要:     {context.analysis_summary}")

        print("="*80)

    def _print_portfolio_report(self, report) -> None:
        """打印投资组合报告"""
        print("\n" + "="*80)
        print(f"投资组合分析报告 - {report.report_id}")
        print("="*80)

        print(f"\n分析统计:")
        print(f"  总分析股票数: {report.total_stocks_analyzed}")
        print(f"  强烈买入:     {report.strong_buy_count}")
        print(f"  买入:         {report.buy_count}")
        print(f"  持有:         {report.hold_count}")
        print(f"  卖出:         {report.sell_count}")
        print(f"  强烈卖出:     {report.strong_sell_count}")

        print(f"\n股票明细:")
        print("-"*80)

        for stock in report.stocks:
            signal_emoji = {
                InvestmentSignal.STRONG_BUY: "[++]",
                InvestmentSignal.BUY: "[+]",
                InvestmentSignal.HOLD: "[=]",
                InvestmentSignal.SELL: "[-]",
                InvestmentSignal.STRONG_SELL: "[--]",
            }.get(stock.final_signal, "[?]")

            print(f"\n{stock.stock_code} {signal_emoji} {stock.final_signal.value}")
            print(f"  综合评分: {stock.overall_score:.2f}/100")

            if stock.financial_metrics:
                print(f"  当前价: {stock.financial_metrics.current_price}")

            # 打印 ML 分（如果已计算并存在字段）
            ml_score = getattr(stock, "ml_score", None) if hasattr(stock, "ml_score") else stock.__dict__.get("ml_score") if hasattr(stock, "__dict__") else None
            if ml_score is not None:
                print(f"  ML评分: {ml_score:.2f} / 10")

            if stock.valuation:
                print(f"  合理价: {stock.valuation.fair_price:.2f}, 安全边际: {stock.valuation.margin_of_safety:.2f}%")

            if stock.investment_decision:
                print(f"  建议仓位: {stock.investment_decision.position_size:.2%}")

        print("\n" + "="*80)

    def run_interactive_mode(self) -> None:
        """交互模式"""
        print("\n价值投资分析系统 (交互模式)")
        print("="*60)
        print("命令:")
        print("  1. analyze <股票代码>     - 分析单只股票")
        print("  2. masters <股票代码>     - 使用投资大师 LLM 分析")
        print("  3. experts <股票代码>     - 使用分析专家 LLM 分析")
        print("  4. portfolio <股票1> <股票2> ... - 分析股票组合")
        print("  5. buy <股票1> <股票2> ... - 获取买入推荐")
        print("  6. help              - 显示帮助")
        print("  7. exit              - 退出程序")
        print("="*60)

        while True:
            try:
                cmd = input("\n请输入命令: ").strip()

                if not cmd:
                    continue

                parts = cmd.split()
                command = parts[0].lower()

                if command == "analyze" and len(parts) > 1:
                    stock_code = parts[1]
                    self.analyze_single_stock(stock_code)

                elif command == "masters" and len(parts) > 1:
                    stock_code = parts[1]
                    master_names = parts[2:] if len(parts) > 2 else None
                    self.analyze_with_masters(stock_code, master_names)

                elif command == "experts" and len(parts) > 1:
                    stock_code = parts[1]
                    expert_names = parts[2:] if len(parts) > 2 else None
                    self.analyze_with_experts(stock_code, expert_names)

                elif command == "portfolio" and len(parts) > 1:
                    stock_codes = parts[1:]
                    self.analyze_multiple_stocks(stock_codes)

                elif command == "buy" and len(parts) > 1:
                    stock_codes = parts[1:]
                    self.get_buy_recommendations(stock_codes)

                elif command == "help":
                    print(self._get_help_text())

                elif command == "exit":
                    print("感谢使用！再见！")
                    break

                else:
                    print("命令不识别，请使用 'help' 查看帮助")

            except KeyboardInterrupt:
                print("\n已取消")
                break
            except Exception as e:
                logger.error(f"执行命令出错: {str(e)}")
                print(f"✗ 执行出错: {str(e)}")

    def _get_help_text(self) -> str:
        """获取帮助文本"""
        return """
价值投资分析系统 - 帮助文档
=====================================

本系统基于价值投资理论，通过 9 个分析 Agent 评估股票的投资价值。

核心 Agent:
  1. 股权思维 Agent    - 评估企业盈利能力和增长潜力
  2. 护城河 Agent      - 分析企业竞争优势
  3. 财务分析 Agent    - 评估财务指标（ROE、毛利率等）
  4. 估值 Agent        - 计算内在价值和合理价格
  5. 安全边际 Agent    - 分析价格与价值的差异
  6. 买入点 Agent      - 识别买入时机
  7. 卖出纪律 Agent    - 识别卖出信号
  8. 风险管理 Agent    - 评估投资风险
  9. 心理纪律 Agent    - 生成投资决策和仓位建议

LLM 投资大师 Agent（基于大语言模型）:
  • Ben Graham Agent          - 本杰明·格雷厄姆（价值投资之父）
  • Philip Fisher Agent       - 菲利普·费雪（成长型投资大师）
  • Charlie Munger Agent      - 查理·芒格（多元思维模型）
  • Warren Buffett Agent      - 沃伦·巴菲特（股神）
  • Stanley Druckenmiller Agent - 斯坦利·德鲁肯米勒（宏观对冲大师）
  • Cathie Wood Agent         - 凯西·伍德（创新投资女王）
  • Bill Ackman Agent         - 比尔·阿克曼（激进投资家）

LLM 分析专家 Agent（基于大语言模型）:
  • Fundamentals Agent        - 基本面分析（盈利、增长、财务健康、估值比率）
  • Sentiment Agent           - 市场情绪分析（内部交易、新闻情绪）
  • Valuation Expert Agent    - 估值专家（DCF、所有者收益估值）
  • Technical Agent           - 技术分析（趋势、动量、均值回归、波动率）
  • Risk Manager Agent        - 风险管理（头寸限制、风险指标）
  • Portfolio Manager Agent   - 投资组合经理（综合决策、订单生成）

推荐信号说明:
  🟢🟢 强烈买入 - 强烈推荐买入
  🟢  买入    - 推荐买入
  🟡  持有    - 观望
  🔴  卖出    - 建议卖出
  🔴🔴 强烈卖出 - 强烈建议卖出

示例用法:
  analyze 600519               - 分析贵州茅台
  masters 600519               - 使用所有投资大师分析贵州茅台
  masters 600519 buffett munger - 只使用巴菲特和芒格分析
  experts 600519               - 使用所有分析专家分析
  experts 600519 technical sentiment - 只使用技术分析和情绪分析
  portfolio 600519 000858      - 分析多只股票
  buy 600519 000858            - 查找买入推荐
  exit                         - 退出程序
"""


def main():
    """主程序入口"""
    if len(sys.argv) > 1:
        # 命令行模式
        app = ValueInvestingApp()
        command = sys.argv[1].lower()

        if command == "analyze" and len(sys.argv) > 2:
            app.analyze_single_stock(sys.argv[2])

        elif command == "masters" and len(sys.argv) > 2:
            stock_code = sys.argv[2]
            master_names = sys.argv[3:] if len(sys.argv) > 3 else None
            app.analyze_with_masters(stock_code, master_names)

        elif command == "experts" and len(sys.argv) > 2:
            stock_code = sys.argv[2]
            expert_names = sys.argv[3:] if len(sys.argv) > 3 else None
            app.analyze_with_experts(stock_code, expert_names)

        elif command == "portfolio" and len(sys.argv) > 2:
            app.analyze_multiple_stocks(sys.argv[2:])

        elif command == "buy" and len(sys.argv) > 2:
            app.get_buy_recommendations(sys.argv[2:])

        elif command == "help":
            app_temp = ValueInvestingApp()
            print(app_temp._get_help_text())

        else:
            print("用法: python main.py <command> [arguments]")
            print("  analyze <股票代码>")
            print("  masters <股票代码> [大师名称...]")
            print("  experts <股票代码> [专家名称...]")
            print("  portfolio <股票1> <股票2> ...")
            print("  buy <股票1> <股票2> ...")
            print("  help")
    else:
        # 交互模式
        app = ValueInvestingApp()
        app.run_interactive_mode()


if __name__ == "__main__":
    main()
