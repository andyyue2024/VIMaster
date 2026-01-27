"""测试脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("开始测试...")

# 测试导入
from src.agents import get_all_master_agents, get_all_expert_agents

masters = get_all_master_agents()
experts = get_all_expert_agents()

print(f"大师 Agent: {len(masters)} 个")
for m in masters:
    print(f"  - {m.name}")

print(f"\n专家 Agent: {len(experts)} 个")
for e in experts:
    print(f"  - {e.name}")

print("\n✅ 全部导入成功！")
