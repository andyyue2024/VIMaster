"""
多源数据提供者演示脚本
展示如何使用多个数据源获取股票信息
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import MultiSourceDataProvider
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主程序"""
    print("\n" + "=" * 80)
    print("VIMaster - 多源数据提供者演示")
    print("=" * 80)

    # 初始化多源数据提供者 (不提供 TuShare token 以演示降级)
    provider = MultiSourceDataProvider()

    # 打印数据源状态
    provider.print_source_stats()

    # 测试股票代码
    test_stocks = ["600519", "000858", "000651"]

    for stock_code in test_stocks:
        print(f"\n" + "-" * 80)
        print(f"分析股票: {stock_code}")
        print("-" * 80)

        # 获取股票信息
        print("\n1. 获取股票信息:")
        stock_info = provider.get_stock_info(stock_code)
        if stock_info:
            for key, value in stock_info.items():
                print(f"  {key}: {value}")
        else:
            print(f"  无法获取股票 {stock_code} 的信息")

        # 获取财务指标
        print("\n2. 获取财务指标:")
        metrics = provider.get_financial_metrics(stock_code)
        if metrics:
            print(f"  当前价格: {metrics.current_price}")
            print(f"  PE比率: {metrics.pe_ratio}")
            print(f"  PB比率: {metrics.pb_ratio}")
            print(f"  ROE: {metrics.roe}")
            print(f"  毛利率: {metrics.gross_margin}")
            print(f"  负债率: {metrics.debt_ratio}")
        else:
            print(f"  无法获取股票 {stock_code} 的财务指标")

        # 获取行业信息
        print("\n3. 获取行业信息:")
        industry_info = provider.get_industry_info(stock_code)
        if industry_info:
            for key, value in industry_info.items():
                print(f"  {key}: {value}")
        else:
            print(f"  无法获取股票 {stock_code} 的行业信息")

    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

