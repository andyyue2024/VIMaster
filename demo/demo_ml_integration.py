"""
机器学习模型集成演示：使用基本面指标为股票打分并对组合排序
"""
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.ml import StockMLScorer
from src.data import MultiSourceDataProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_single_stock():
    print("\n" + "=" * 80)
    print("演示 1: 单只股票 ML 评分")
    print("=" * 80)

    provider = MultiSourceDataProvider()
    fm = provider.get_financial_metrics("600519")
    if not fm:
        print("无法获取财务指标")
        return

    scorer = StockMLScorer()
    result = scorer.score_stock("600519", {
        "pe_ratio": fm.pe_ratio,
        "pb_ratio": fm.pb_ratio,
        "roe": fm.roe,
        "gross_margin": fm.gross_margin,
        "free_cash_flow": fm.free_cash_flow,
        "debt_ratio": fm.debt_ratio,
    })

    print(f"股票: {result['stock_code']}")
    print(f"ML评分: {result['ml_score']:.2f} / 10")
    print("特征: ")
    for k, v in result['features'].items():
        print(f"  {k:15}: {v}")


def demo_portfolio():
    print("\n" + "=" * 80)
    print("演示 2: 投资组合 ML 排序")
    print("=" * 80)

    provider = MultiSourceDataProvider()
    codes = ["600519", "000858", "000651", "600036"]
    items = []
    for code in codes:
        fm = provider.get_financial_metrics(code)
        if not fm:
            continue
        items.append((code, {
            "pe_ratio": fm.pe_ratio,
            "pb_ratio": fm.pb_ratio,
            "roe": fm.roe,
            "gross_margin": fm.gross_margin,
            "free_cash_flow": fm.free_cash_flow,
            "debt_ratio": fm.debt_ratio,
        }))

    scorer = StockMLScorer()
    results = scorer.score_portfolio(items)
    results.sort(key=lambda r: r['ml_score'], reverse=True)

    print("\n组合评分排序：")
    for r in results:
        print(f"  {r['stock_code']}: {r['ml_score']:.2f}")


def main():
    print("\n" + "=" * 80)
    print("VIMaster - 机器学习模型集成演示")
    print("=" * 80)
    try:
        demo_single_stock()
        demo_portfolio()
        print("\n演示完成！\n")
    except Exception as e:
        logger.error(f"演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
