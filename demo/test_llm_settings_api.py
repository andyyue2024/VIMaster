"""测试 LLM 配置 API"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试预设模型
from src.agents.llm.llm_config import PRESET_CONFIGS, LLMConfigManager, LLMConfig
print(f"预设模型数量: {len(PRESET_CONFIGS)}")
for name in list(PRESET_CONFIGS.keys())[:5]:
    print(f"  - {name}")
print("  ...")

# 测试配置管理器
config = LLMConfigManager.get_config()
print(f"\n当前配置:")
print(f"  默认提供商: {config.default_provider}")
print(f"  启用缓存: {config.enable_cache}")
print(f"  缓存 TTL: {config.cache_ttl}")

# 测试 Web API
print("\n测试 Web API...")
from src.web.app import create_web_app
import json

app = create_web_app()
client = app.test_client()

# 测试获取模型列表
r = client.get('/api/settings/llm/models')
print(f"GET /api/settings/llm/models: {r.status_code}")
data = json.loads(r.data)
if data.get('success'):
    print(f"  模型数量: {len(data['data']['models'])}")

# 测试获取设置
r = client.get('/api/settings/llm')
print(f"GET /api/settings/llm: {r.status_code}")
data = json.loads(r.data)
if data.get('success'):
    print(f"  默认提供商: {data['data']['default_provider']}")

# 测试保存设置
r = client.post('/api/settings/llm',
    json={'default_provider': 'gpt-4o', 'enable_cache': True},
    content_type='application/json')
print(f"POST /api/settings/llm: {r.status_code}")
data = json.loads(r.data)
print(f"  结果: {data.get('success')}")

print("\n✅ LLM 配置 API 测试完成！")
