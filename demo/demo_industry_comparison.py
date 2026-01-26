"""
行业对比分析演示脚本
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.analysis.industry_comparator import IndustryComparator
from src.data import MultiSourceDataProvider
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 行业对比分析演示")
    print("=" * 80)

    # 初始化分析器
    provider = MultiSourceDataProvider()
    comparator = IndustryComparator(data_provider=provider)

    # 1. 显示所有可用行业
    print("\n" + "-" * 80)
    print("1. 可用行业列表")
    print("-" * 80)

    industries = comparator.get_available_industries()
    for i, industry in enumerate(industries, 1):
        stocks = comparator.get_industry_stocks(industry)
        print(f"{i}. {industry:15} (共 {len(stocks)} 只股票: {', '.join(stocks)})")

    # 2. 分析单个行业
    print("\n" + "-" * 80)
    print("2. 白酒行业分析")
    print("-" * 80)

    white_wine_metrics = comparator.analyze_industry("白酒")
    if white_wine_metrics:
        print(f"行业: {white_wine_metrics.industry_name}")
        print(f"股票数: {len(white_wine_metrics.stock_codes)}")
        if white_wine_metrics.avg_pe_ratio:
            print(f"平均 PE 比率: {white_wine_metrics.avg_pe_ratio:.2f}")
        if white_wine_metrics.avg_pb_ratio:
            print(f"平均 PB 比率: {white_wine_metrics.avg_pb_ratio:.2f}")
        if white_wine_metrics.avg_roe:
            print(f"平均 ROE: {white_wine_metrics.avg_roe:.2%}")
        if white_wine_metrics.avg_gross_margin:
            print(f"平均毛利率: {white_wine_metrics.avg_gross_margin:.2%}")
        if white_wine_metrics.median_pe_ratio:
            print(f"中位数 PE 比率: {white_wine_metrics.median_pe_ratio:.2f}")
    else:
        print("无法获取白酒行业数据")

    # 3. 股票与行业对比
    print("\n" + "-" * 80)
    print("3. 茅台（600519）与白酒行业对比")
    print("-" * 80)

    comparison = comparator.compare_stock_with_industry("600519", "白酒")
    if comparison and comparison.metrics and comparison.industry_metrics:
        print(f"股票代码: {comparison.stock_code}")
        print(f"所属行业: {comparison.industry}")

        print("\n股票指标:")
        if comparison.metrics.pe_ratio:
            print(f"  PE 比率: {comparison.metrics.pe_ratio:.2f}")
        if comparison.metrics.pb_ratio:
            print(f"  PB 比率: {comparison.metrics.pb_ratio:.2f}")
        if comparison.metrics.roe:
            print(f"  ROE: {comparison.metrics.roe:.2%}")
        if comparison.metrics.gross_margin:
            print(f"  毛利率: {comparison.metrics.gross_margin:.2%}")

        print("\n行业对比:")
        if comparison.pe_vs_industry_avg:
            print(f"  PE 相对于行业平均: {comparison.pe_vs_industry_avg:.2f}x")
        if comparison.pb_vs_industry_avg:
            print(f"  PB 相对于行业平均: {comparison.pb_vs_industry_avg:.2f}x")
        if comparison.roe_vs_industry_avg:
            print(f"  ROE 相对于行业平均: {comparison.roe_vs_industry_avg:.2f}x")

        print("\n百分位排名（0-100）:")
        if comparison.pe_percentile is not None:
            print(f"  PE 百分位: {comparison.pe_percentile:.1f}% (越低越好)")
        if comparison.pb_percentile is not None:
            print(f"  PB 百分位: {comparison.pb_percentile:.1f}% (越低越好)")
        if comparison.roe_percentile is not None:
            print(f"  ROE 百分位: {comparison.roe_percentile:.1f}% (越高越好)")

        print("\n综合评分:")
        print(f"  竞争力评分: {comparison.competitiveness_score:.1f}/10")
        print(f"  估值评分: {comparison.valuation_score:.1f}/10")
        print(f"  成长评分: {comparison.growth_score:.1f}/10")
    else:
        print("无法进行对比分析")

    # 4. 行业内股票排名
    print("\n" + "-" * 80)
    print("4. 白酒行业内股票排名")
    print("-" * 80)

    rankings = comparator.rank_stocks_in_industry("白酒")
    if rankings:
        print("排名 | 股票代码 | 综合评分")
        print("-" * 40)
        for rank, (code, score, metrics) in enumerate(rankings, 1):
            print(f"{rank:3} | {code:8} | {score:8.2f}")
    else:
        print("无法获取排名数据")

    # 5. 多行业对比
    print("\n" + "-" * 80)
    print("5. 多行业对比分析")
    print("-" * 80)

    selected_industries = ["白酒", "家电", "银行"]
    industry_results = comparator.compare_multiple_industries(selected_industries)

    if industry_results:
        print("行业名称 | 股票数 | 平均PE | 平均PB | 平均ROE")
        print("-" * 60)
        for industry_name, metrics in industry_results.items():
            pe_str = f"{metrics.avg_pe_ratio:.2f}" if metrics.avg_pe_ratio else "N/A"
            pb_str = f"{metrics.avg_pb_ratio:.2f}" if metrics.avg_pb_ratio else "N/A"
            roe_str = f"{metrics.avg_roe:.2%}" if metrics.avg_roe else "N/A"
            print(f"{industry_name:8} | {len(metrics.stock_codes):6} | {pe_str:6} | {pb_str:6} | {roe_str}")
    else:
        print("无法获取行业对比数据")

    # 6. 对比多个行业中的股票
    print("\n" + "-" * 80)
    print("6. 跨行业股票对比")
    print("-" * 80)

    stocks_to_compare = [
        ("600519", "白酒"),      # 茅台
        ("000651", "家电"),      # 格力
        ("600036", "银行"),      # 招商银行
    ]

    print("股票代码 | 所属行业 | PE相对行业 | ROE相对行业 | 竞争力评分")
    print("-" * 65)

    for stock_code, industry in stocks_to_compare:
        comparison = comparator.compare_stock_with_industry(stock_code, industry)
        if comparison:
            pe_str = f"{comparison.pe_vs_industry_avg:.2f}x" if comparison.pe_vs_industry_avg else "N/A"
            roe_str = f"{comparison.roe_vs_industry_avg:.2f}x" if comparison.roe_vs_industry_avg else "N/A"
            print(f"{stock_code:8} | {industry:8} | {pe_str:10} | {roe_str:10} | {comparison.competitiveness_score:8.1f}")
        else:
            print(f"{stock_code:8} | {industry:8} | N/A        | N/A        | N/A")

    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

