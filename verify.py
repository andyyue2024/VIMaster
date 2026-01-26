#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证脚本 - 验证程序是否正确运行
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import ValueInvestingApp

def verify():
    """验证程序功能"""
    app = ValueInvestingApp()

    print("\n" + "="*60)
    print("验证程序功能")
    print("="*60)

    # 测试1: 单只股票分析
    print("\n[测试1] 分析股票 600519")
    ctx = app.manager.analyze_single_stock('600519')
    if ctx:
        print("  [OK] 分析成功!")
        print(f"  - 综合评分: {ctx.overall_score:.2f}/100")
        print(f"  - 最终信号: {ctx.final_signal.value}")
        print(f"  - 财务指标: {ctx.financial_metrics.stock_code if ctx.financial_metrics else 'N/A'}")
        print(f"  - 当前价格: {ctx.financial_metrics.current_price if ctx.financial_metrics else 'N/A'}")
    else:
        print("  [FAIL] 分析失败")
        return False

    # 测试2: 多只股票分析
    print("\n[测试2] 分析3只股票组合")
    report = app.manager.analyze_portfolio(['600519', '000858', '000651'])
    if report:
        print("  [OK] 组合分析成功!")
        print(f"  - 分析股票数: {report.total_stocks_analyzed}")
        print(f"  - 强烈买入: {report.strong_buy_count}")
        print(f"  - 买入: {report.buy_count}")
        print(f"  - 卖出: {report.sell_count}")
    else:
        print("  [FAIL] 组合分析失败")
        return False

    print("\n" + "="*60)
    print("所有测试通过! 程序运行正常.")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    verify()
