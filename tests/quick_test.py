#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速功能测试
"""
import sys
sys.path.insert(0, '..')

from src.data.akshare_provider import AkshareDataProvider

print("快速功能测试")
print("="*50)

# Test 1: Mock data generation
print("\n[Test 1] 生成模拟财务指标")
metrics = AkshareDataProvider._get_mock_financial_metrics('600519')
if metrics:
    print(f"  OK: 股票={metrics.stock_code}")
    print(f"      价格={metrics.current_price}")
    print(f"      PE比率={metrics.pe_ratio}")
else:
    print("  FAIL")

# Test 2: Stock info
print("\n[Test 2] 获取股票基本信息")
info = AkshareDataProvider._get_mock_stock_info('000858')
if info:
    print(f"  OK: 股票={info.get('code')}")
    print(f"      名称={info.get('name')}")
    print(f"      价格={info.get('current_price')}")
else:
    print("  FAIL")

# Test 3: Full flow
print("\n[Test 3] 完整流程测试")
from src.app import ValueInvestingApp
app = ValueInvestingApp()
ctx = app.manager.analyze_single_stock('000651')
if ctx:
    print(f"  OK: 分析成功")
    print(f"      股票={ctx.stock_code}")
    print(f"      综合评分={ctx.overall_score:.2f}/100")
    print(f"      最终信号={ctx.final_signal.value}")
else:
    print("  FAIL")

print("\n" + "="*50)
print("所有测试完成!")
