#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本 - 自动化测试程序功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import ValueInvestingApp

def test_analyze():
    """测试analyze命令"""
    print("\n" + "="*80)
    print("测试: analyze 600519")
    print("="*80)

    app = ValueInvestingApp()
    app.analyze_single_stock("600519")

    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)

def test_portfolio():
    """测试portfolio命令"""
    print("\n" + "="*80)
    print("测试: portfolio 600519 000858 000651")
    print("="*80)

    app = ValueInvestingApp()
    app.analyze_multiple_stocks(["600519", "000858", "000651"])

    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)

if __name__ == "__main__":
    # 测试单只股票分析
    test_analyze()

    # 测试多只股票分析
    test_portfolio()
