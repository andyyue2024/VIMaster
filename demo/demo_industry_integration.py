"""
行业对比分析集成示例
展示如何在 ValueInvestingApp 中使用行业对比分析
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.analysis.industry_comparator import IndustryComparator
from src.data import MultiSourceDataProvider
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IndustryAnalysisHelper:
    """行业分析辅助类"""

    def __init__(self, data_provider=None):
        """
        初始化行业分析辅助
        Args:
            data_provider: 数据提供者（可选）
        """
        self.comparator = IndustryComparator(data_provider=data_provider)

    def get_stock_peer_comparison(self, stock_code: str, industry: str):
        """
        获取股票与同业对比
        Args:
            stock_code: 股票代码
            industry: 行业名称
        Returns:
            对比结果字典
        """
        try:
            comparison = self.comparator.compare_stock_with_industry(stock_code, industry)

            if comparison:
                return {
                    "success": True,
                    "stock_code": stock_code,
                    "industry": industry,
                    "pe_percentile": comparison.pe_percentile,
                    "pb_percentile": comparison.pb_percentile,
                    "roe_percentile": comparison.roe_percentile,
                    "pe_vs_industry": comparison.pe_vs_industry_avg,
                    "pb_vs_industry": comparison.pb_vs_industry_avg,
                    "roe_vs_industry": comparison.roe_vs_industry_avg,
                    "competitiveness_score": comparison.competitiveness_score,
                    "valuation_score": comparison.valuation_score,
                    "growth_score": comparison.growth_score,
                }
            else:
                return {
                    "success": False,
                    "message": f"无法对比 {stock_code} 与 {industry} 行业"
                }
        except Exception as e:
            logger.error(f"对比异常: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def get_industry_top_stocks(self, industry: str, top_n: int = 5):
        """
        获取行业内的顶级股票
        Args:
            industry: 行业名称
            top_n: 返回的数量
        Returns:
            顶级股票列表
        """
        try:
            rankings = self.comparator.rank_stocks_in_industry(industry)

            if rankings:
                top_stocks = []
                for rank, (code, score, metrics) in enumerate(rankings[:top_n], 1):
                    top_stocks.append({
                        "rank": rank,
                        "stock_code": code,
                        "score": score,
                        "pe_ratio": metrics.pe_ratio if metrics else None,
                        "roe": metrics.roe if metrics else None,
                    })
                return {
                    "success": True,
                    "industry": industry,
                    "top_stocks": top_stocks,
                }
            else:
                return {
                    "success": False,
                    "message": f"无法获取 {industry} 行业的排名"
                }
        except Exception as e:
            logger.error(f"排名异常: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def find_undervalued_stocks(self, industry: str, pe_threshold: float = 30):
        """
        查找被低估的股票
        Args:
            industry: 行业名称
            pe_threshold: PE百分位阈值（< threshold 为低估）
        Returns:
            低估股票列表
        """
        try:
            stock_codes = self.comparator.get_industry_stocks(industry)
            undervalued = []

            for code in stock_codes:
                comparison = self.comparator.compare_stock_with_industry(code, industry)

                if comparison and comparison.pe_percentile and comparison.pe_percentile < pe_threshold:
                    undervalued.append({
                        "stock_code": code,
                        "pe_percentile": comparison.pe_percentile,
                        "roe_percentile": comparison.roe_percentile,
                        "competitiveness": comparison.competitiveness_score,
                        "valuation": comparison.valuation_score,
                    })

            # 按PE百分位排序
            undervalued.sort(key=lambda x: x["pe_percentile"])

            return {
                "success": True,
                "industry": industry,
                "threshold": pe_threshold,
                "undervalued_stocks": undervalued,
                "count": len(undervalued),
            }
        except Exception as e:
            logger.error(f"查找低估股票异常: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def compare_industries(self, industries: list):
        """
        对比多个行业
        Args:
            industries: 行业列表
        Returns:
            行业对比数据
        """
        try:
            results = self.comparator.compare_multiple_industries(industries)

            if results:
                industry_data = []
                for industry, metrics in results.items():
                    industry_data.append({
                        "industry": industry,
                        "stock_count": len(metrics.stock_codes),
                        "avg_pe": metrics.avg_pe_ratio,
                        "avg_pb": metrics.avg_pb_ratio,
                        "avg_roe": metrics.avg_roe,
                        "avg_gross_margin": metrics.avg_gross_margin,
                        "avg_debt_ratio": metrics.avg_debt_ratio,
                    })

                return {
                    "success": True,
                    "industries": industry_data,
                    "count": len(industry_data),
                }
            else:
                return {
                    "success": False,
                    "message": "无法获取行业对比数据"
                }
        except Exception as e:
            logger.error(f"行业对比异常: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def get_industry_summary(self, industry: str):
        """
        获取行业总结
        Args:
            industry: 行业名称
        Returns:
            行业总结数据
        """
        try:
            metrics = self.comparator.analyze_industry(industry)

            if metrics:
                return {
                    "success": True,
                    "industry": industry,
                    "stock_count": len(metrics.stock_codes),
                    "stocks": metrics.stock_codes,
                    "metrics": {
                        "avg_pe_ratio": metrics.avg_pe_ratio,
                        "avg_pb_ratio": metrics.avg_pb_ratio,
                        "avg_roe": metrics.avg_roe,
                        "avg_gross_margin": metrics.avg_gross_margin,
                        "avg_debt_ratio": metrics.avg_debt_ratio,
                        "median_pe_ratio": metrics.median_pe_ratio,
                        "median_pb_ratio": metrics.median_pb_ratio,
                        "median_roe": metrics.median_roe,
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"无法获取 {industry} 行业数据"
                }
        except Exception as e:
            logger.error(f"行业总结异常: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("行业对比分析集成示例")
    print("=" * 80)

    # 初始化（可选：使用多源数据提供者）
    # provider = MultiSourceDataProvider(tushare_token="your_token")
    # helper = IndustryAnalysisHelper(data_provider=provider)

    # 初始化（默认使用 AkShare）
    helper = IndustryAnalysisHelper()

    # 示例 1：获取股票与行业的对比
    print("\n1. 股票与行业对比")
    print("-" * 80)
    result = helper.get_stock_peer_comparison("600519", "白酒")
    if result["success"]:
        print(f"股票: {result['stock_code']}")
        print(f"行业: {result['industry']}")
        print(f"PE 百分位: {result['pe_percentile']:.1f}%")
        print(f"ROE 百分位: {result['roe_percentile']:.1f}%")
        print(f"竞争力评分: {result['competitiveness_score']:.1f}/10")
    else:
        print(f"错误: {result.get('message')}")

    # 示例 2：获取行业顶级股票
    print("\n2. 行业顶级股票")
    print("-" * 80)
    result = helper.get_industry_top_stocks("白酒", top_n=3)
    if result["success"]:
        for stock in result["top_stocks"]:
            print(f"第 {stock['rank']} 名: {stock['stock_code']} (评分: {stock['score']:.2f})")
    else:
        print(f"错误: {result.get('message')}")

    # 示例 3：查找被低估的股票
    print("\n3. 被低估的股票（PE 百分位 < 30）")
    print("-" * 80)
    result = helper.find_undervalued_stocks("白酒", pe_threshold=30)
    if result["success"]:
        print(f"找到 {result['count']} 只被低估的股票:")
        for stock in result["undervalued_stocks"]:
            print(f"  {stock['stock_code']}: PE百分位 {stock['pe_percentile']:.1f}%, 竞争力 {stock['competitiveness']:.1f}/10")
    else:
        print(f"错误: {result.get('message')}")

    # 示例 4：行业总结
    print("\n4. 行业总结")
    print("-" * 80)
    result = helper.get_industry_summary("白酒")
    if result["success"]:
        print(f"行业: {result['industry']}")
        print(f"股票数: {result['stock_count']}")
        metrics = result["metrics"]
        print(f"平均 PE: {metrics['avg_pe_ratio']:.2f}")
        print(f"平均 ROE: {metrics['avg_roe']:.2%}")
        print(f"平均毛利率: {metrics['avg_gross_margin']:.2%}")
    else:
        print(f"错误: {result.get('message')}")

    # 示例 5：多行业对比
    print("\n5. 多行业对比")
    print("-" * 80)
    result = helper.compare_industries(["白酒", "家电", "银行"])
    if result["success"]:
        for industry in result["industries"]:
            print(f"{industry['industry']:8} - PE: {industry['avg_pe']:.2f}, ROE: {industry['avg_roe']:.2%}")
    else:
        print(f"错误: {result.get('message')}")

    print("\n" + "=" * 80)
    print("示例完成！")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

