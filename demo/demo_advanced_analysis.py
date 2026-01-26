"""
综合分析功能演示脚本
展示行业对比、历史估值对比和投资组合优化建议
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.analysis import (
    ComprehensiveAnalyzer,
    ValuationAnalyzer,
    PortfolioOptimizer,
    PortfolioStrategy,
)
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_single_stock_comprehensive():
    """演示1: 单只股票综合分析"""
    print("\n" + "=" * 80)
    print("演示 1: 单只股票综合分析（包含行业对比、历史估值、风险评估）")
    print("=" * 80)

    analyzer = ComprehensiveAnalyzer()

    # 分析茅台
    result = analyzer.analyze_stock_comprehensive("600519", industry="白酒")

    if result:
        print("\n【基础分析】")
        basic = result.get("basic_analysis", {})
        print(f"股票代码: {basic.get('stock_code')}")
        print(f"综合评分: {basic.get('overall_score'):.1f}")
        print(f"投资信号: {basic.get('final_signal')}")

        if "financial_metrics" in basic:
            print("\n【财务指标】")
            fm = basic["financial_metrics"]
            print(f"  当前价格: {fm.get('current_price')}")
            print(f"  PE比率: {fm.get('pe_ratio')}")
            print(f"  ROE: {fm.get('roe'):.2%}" if fm.get('roe') else "  ROE: N/A")

        if "valuation_history" in result:
            print("\n【历史估值分析】")
            vh = result["valuation_history"]
            print(f"  当前PE: {vh.get('current_pe'):.2f}")
            print(f"  历史平均PE: {vh.get('historical_avg_pe'):.2f}")
            print(f"  PE相对历史平均: {vh.get('pe_vs_avg'):.2f}x")
            print(f"  估值百分位: {vh.get('valuation_percentile'):.1f}%")
            print(f"  估值信号: {vh.get('valuation_signal')}")

        if "industry_comparison" in result:
            print("\n【行业对比分析】")
            ic = result["industry_comparison"]
            print(f"  PE百分位: {ic.get('pe_percentile'):.1f}%")
            print(f"  ROE百分位: {ic.get('roe_percentile'):.1f}%")
            print(f"  竞争力评分: {ic.get('competitiveness_score'):.1f}/10")
    else:
        print("无法分析股票")


def demo_valuation_history():
    """演示2: 历史估值对比分析"""
    print("\n" + "=" * 80)
    print("演示 2: 历史估值对比分析")
    print("=" * 80)

    analyzer = ValuationAnalyzer()

    stocks = ["600519", "000858", "000651"]

    print("\n对比多只股票的历史估值...")
    comparisons = analyzer.compare_stocks_valuation(stocks, days=365)

    if comparisons:
        print("\n股票代码 | 当前PE | 历史平均PE | PE倍数 | 估值百分位 | 估值信号")
        print("-" * 70)
        for comp in comparisons:
            print(f"{comp.stock_code:8} | {comp.current_pe:6.2f} | {comp.historical_avg_pe:10.2f} | "
                  f"{comp.pe_vs_avg:6.2f}x | {comp.valuation_percentile:10.1f}% | {comp.valuation_signal}")
    else:
        print("无法获取估值数据")


def demo_portfolio_optimization():
    """演示3: 投资组合优化建议"""
    print("\n" + "=" * 80)
    print("演示 3: 投资组合优化建议（多种策略）")
    print("=" * 80)

    analyzer = ComprehensiveAnalyzer()
    optimizer = PortfolioOptimizer()

    # 候选股票
    stock_codes = ["600519", "000858", "000651", "600036", "300059"]

    strategies = [
        PortfolioStrategy.VALUE,      # 价值型
        PortfolioStrategy.GROWTH,     # 成长型
        PortfolioStrategy.BALANCED,   # 平衡型
    ]

    for strategy in strategies:
        print(f"\n【{strategy.value}投资组合】")
        print("-" * 60)

        result = analyzer.analyze_portfolio_comprehensive(stock_codes, strategy=strategy)

        if result and "portfolio_recommendation" in result:
            rec = result["portfolio_recommendation"]
            print(f"总结: {rec.get('summary')}")
            print(f"预期收益率: {rec.get('expected_return'):.2%}")
            print(f"风险评分: {rec.get('risk_score'):.1f}/10")
            print(f"现金配置: {rec.get('cash_weight'):.0%}")

            print("\n持仓配置:")
            for pos in rec.get("positions", []):
                print(f"  {pos['stock_code']:8} | 仓位: {pos['weight']:6.2%} | 风险: {pos['risk_level']:4} | {pos['reason']}")
        else:
            print("无法生成投资组合建议")


def demo_investment_recommendations():
    """演示4: 综合投资建议"""
    print("\n" + "=" * 80)
    print("演示 4: 综合投资建议（买入/持有/卖出）")
    print("=" * 80)

    analyzer = ComprehensiveAnalyzer()

    stocks = ["600519", "000858", "000651", "600036", "300059", "601398"]

    recommendations = analyzer.generate_investment_recommendations(stocks)

    if recommendations:
        print(f"\n总分析股票数: {recommendations.get('total_stocks')}")

        buy = recommendations.get("buy_stocks", {})
        print(f"\n【买入建议】({buy.get('count')}只)")
        print(buy.get('summary'))
        for stock in buy.get("stocks", [])[:3]:
            print(f"  {stock.get('stock_code')}: 综合评分 {stock.get('basic_analysis', {}).get('overall_score', 0):.1f}")

        hold = recommendations.get("hold_stocks", {})
        print(f"\n【持有建议】({hold.get('count')}只)")
        print(hold.get('summary'))

        sell = recommendations.get("sell_stocks", {})
        print(f"\n【卖出建议】({sell.get('count')}只)")
        print(sell.get('summary'))
    else:
        print("无法生成投资建议")


def demo_industry_comparison_detailed():
    """演示5: 详细的行业对比分析"""
    print("\n" + "=" * 80)
    print("演示 5: 详细的行业对比分析")
    print("=" * 80)

    analyzer = ComprehensiveAnalyzer()

    industries = ["白酒", "家电", "银行"]

    result = analyzer.compare_industries_with_stocks(industries)

    if result:
        for industry_name, industry_data in result.get("industries", {}).items():
            print(f"\n【{industry_name}行业】")
            print("-" * 60)

            metrics = industry_data.get("metrics", {})
            print(f"行业指标:")
            print(f"  平均PE: {metrics.get('avg_pe_ratio', 'N/A')}")
            print(f"  平均ROE: {metrics.get('avg_roe', 'N/A')}")

            print(f"\n代表股票:")
            for stock in industry_data.get("stocks", [])[:2]:
                code = stock.get("stock_code")
                score = stock.get("basic_analysis", {}).get("overall_score", 0)
                print(f"  {code}: 综合评分 {score:.1f}")
    else:
        print("无法进行行业对比分析")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 增强分析功能演示")
    print("行业对比分析 + 历史估值对比 + 投资组合优化")
    print("=" * 80)

    try:
        # 演示1: 单只股票综合分析
        demo_single_stock_comprehensive()

        # 演示2: 历史估值对比
        demo_valuation_history()

        # 演示3: 投资组合优化
        demo_portfolio_optimization()

        # 演示4: 综合投资建议
        demo_investment_recommendations()

        # 演示5: 行业对比分析
        demo_industry_comparison_detailed()

        print("\n" + "=" * 80)
        print("演示完成！")
        print("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"演示出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
