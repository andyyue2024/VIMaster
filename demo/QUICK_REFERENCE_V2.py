"""
增强分析功能 - 快速参考指南
"""

# ============================================================================
# VIMaster v2.0 - 增强分析功能快速参考
# ============================================================================

# 导入模块
from src.analysis import (
    ValuationAnalyzer,           # 历史估值分析器
    PortfolioOptimizer,          # 投资组合优化器
    ComprehensiveAnalyzer,       # 综合分析器
    PortfolioStrategy,           # 投资策略枚举
)

# ============================================================================
# 1. 历史估值对比分析
# ============================================================================

# 初始化
analyzer = ValuationAnalyzer()

# 1.1 分析历史估值趋势
trend = analyzer.analyze_valuation_history("600519", days=365)
# 返回: avg_pe_ratio, min_pe_ratio, max_pe_ratio, median_pe_ratio, std_dev_pe

# 1.2 对比当前与历史估值
comparison = analyzer.compare_valuation_history("600519")
# 返回: current_pe, historical_avg_pe, pe_vs_avg, valuation_percentile, valuation_signal

# 1.3 对比多只股票
stocks = ["600519", "000858", "000651"]
comparisons = analyzer.compare_stocks_valuation(stocks, days=365)

# 1.4 获取估值统计
stats = analyzer.get_valuation_statistics("600519")

# ============================================================================
# 2. 投资组合优化
# ============================================================================

# 初始化
optimizer = PortfolioOptimizer()

# 2.1 5 种投资策略
# PortfolioStrategy.VALUE        # 价值型 - 低估值、安全
# PortfolioStrategy.GROWTH       # 成长型 - 高成长、高风险
# PortfolioStrategy.BALANCED     # 平衡型 - 均衡配置
# PortfolioStrategy.INCOME       # 收益型 - 高分红、稳定
# PortfolioStrategy.CONSERVATIVE # 保守型 - 极低风险

# 2.2 生成投资组合
recommendation = optimizer.generate_portfolio_recommendation(
    stock_analyses,                              # 股票分析结果列表
    strategy=PortfolioStrategy.BALANCED,         # 选择策略
    portfolio_size=5                             # 组合中的股票数
)

# 2.3 查看组合信息
print(f"策略: {recommendation.strategy.value}")
print(f"预期收益率: {recommendation.expected_return:.2%}")
print(f"风险评分: {recommendation.risk_score:.1f}/10")
print(f"现金配置: {recommendation.cash_weight:.0%}")

for position in recommendation.positions:
    print(f"{position.stock_code}: 仓位 {position.weight:.2%}")

# 2.4 计算组合指标
metrics = optimizer.calculate_portfolio_metrics(positions)
# 返回: total_weight, average_score, average_risk, diversification

# ============================================================================
# 3. 综合分析（推荐使用）
# ============================================================================

# 初始化
analyzer = ComprehensiveAnalyzer()

# 3.1 单只股票综合分析
result = analyzer.analyze_stock_comprehensive(
    "600519",
    industry="白酒"  # 可选
)

# 包含: 基础分析 + 历史估值 + 行业对比

# 3.2 投资组合综合分析
portfolio_result = analyzer.analyze_portfolio_comprehensive(
    ["600519", "000858", "000651"],
    strategy=PortfolioStrategy.BALANCED
)

# 3.3 生成投资建议
recommendations = analyzer.generate_investment_recommendations(
    ["600519", "000858", "000651", "600036"]
)

# 返回: buy_stocks, hold_stocks, sell_stocks
print(f"买入建议: {recommendations['buy_stocks']['count']}只")
print(f"持有建议: {recommendations['hold_stocks']['count']}只")
print(f"卖出建议: {recommendations['sell_stocks']['count']}只")

# 3.4 行业对比分析
industry_result = analyzer.compare_industries_with_stocks(
    ["白酒", "家电", "银行"]
)

# ============================================================================
# 常见应用场景
# ============================================================================

# 场景 1: 寻找被低估的股票
def find_undervalued_stocks(stocks):
    analyzer = ValuationAnalyzer()
    undervalued = []

    for code in stocks:
        comp = analyzer.compare_valuation_history(code)
        if comp and comp.valuation_percentile < 30:  # 历史底部 30%
            undervalued.append(code)

    return undervalued

# 场景 2: 构建适合自己的投资组合
def build_portfolio(stocks, risk_tolerance):
    analyzer = ComprehensiveAnalyzer()

    if risk_tolerance == "conservative":
        strategy = PortfolioStrategy.CONSERVATIVE
    elif risk_tolerance == "moderate":
        strategy = PortfolioStrategy.BALANCED
    else:
        strategy = PortfolioStrategy.GROWTH

    portfolio = analyzer.analyze_portfolio_comprehensive(stocks, strategy)
    return portfolio

# 场景 3: 行业对比选股
def select_best_stock_in_industry(industry):
    analyzer = ComprehensiveAnalyzer()

    # 对比该行业的所有股票
    from src.analysis import IndustryComparator
    comparator = IndustryComparator()

    stocks = comparator.get_industry_stocks(industry)
    rankings = comparator.rank_stocks_in_industry(industry)

    # 返回评分最高的股票
    return rankings[0] if rankings else None

# 场景 4: 监控投资组合
def monitor_portfolio(portfolio_stocks):
    analyzer = ComprehensiveAnalyzer()

    for code in portfolio_stocks:
        result = analyzer.analyze_stock_comprehensive(code)

        signal = result["valuation_history"]["valuation_signal"]
        if signal == "卖出":
            print(f"⚠️  建议卖出: {code}")
        elif signal == "买入":
            print(f"✓ 增持机会: {code}")

# ============================================================================
# 关键指标速查
# ============================================================================

# 历史估值指标
# - PE vs 历史平均: 0.8 表示低 20%，1.2 表示高 20%
# - 估值百分位: 0% 最便宜，100% 最贵
# - 估值信号: 买入/持有/卖出

# 投资组合指标
# - 预期收益率: 0-20%，越高越好
# - 风险评分: 0-10，越低越安全
# - 多样化评分: 0-10，越高越分散

# 投资策略选择
# - 价值型 (VALUE): 追求安全边际大的股票
# - 成长型 (GROWTH): 追求资本增值
# - 平衡型 (BALANCED): 风险和收益均衡
# - 收益型 (INCOME): 追求稳定分红
# - 保守型 (CONSERVATIVE): 极低风险，高现金比例

# ============================================================================
# 最佳实践
# ============================================================================

# ✓ 结合多个分析维度
# ✓ 根据风险承受能力选择策略
# ✓ 定期重新评估投资组合
# ✓ 关注买卖信号和风险评分
# ✓ 保持适当的多样化

# ============================================================================
# 更多文档
# ============================================================================

# 详细使用指南: ADVANCED_ANALYSIS_GUIDE.md
# 完整演示脚本: demo_advanced_analysis.py
# 单元测试: tests/unit/test_advanced_analysis.py
