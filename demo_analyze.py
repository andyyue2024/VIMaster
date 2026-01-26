#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交互演示脚本 - 演示analyze 600519命令
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import ValueInvestingApp

def main():
    """演示程序功能"""
    app = ValueInvestingApp()

    # 演示analyze 600519
    print("\n" + "="*80)
    print("演示: analyze 600519")
    print("="*80 + "\n")
    app.analyze_single_stock("600519")

if __name__ == "__main__":
    main()
