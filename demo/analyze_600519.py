"""
分析脚本：用于生成股票 600519 的完整分析报告
"""
import sys
import os
import logging
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import ValueInvestingApp

# 配置日志以捕获 agent 的详细输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_analysis():
    """运行股票 600519 的分析"""
    print("="*100)
    print("VIMaster - 价值投资分析系统")
    print("="*100)
    print("\n开始分析股票 600519 (贵州茅台)...\n")

    app = ValueInvestingApp()
    app.analyze_single_stock("600519")

    print("\n分析完成！")

if __name__ == "__main__":
    run_analysis()
