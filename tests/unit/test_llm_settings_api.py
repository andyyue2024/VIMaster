"""
LLM 配置 API 单元测试
"""
import pytest
import json
import sys
import os

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestLLMConfigImports:
    """测试 LLM 配置模块导入"""

    def test_import_preset_configs(self):
        """测试导入 PRESET_CONFIGS"""
        from src.agents.llm.llm_config import PRESET_CONFIGS
        assert PRESET_CONFIGS is not None
        assert isinstance(PRESET_CONFIGS, dict)

    def test_import_llm_config_manager(self):
        """测试导入 LLMConfigManager"""
        from src.agents.llm.llm_config import LLMConfigManager
        assert LLMConfigManager is not None

    def test_import_llm_config(self):
        """测试导入 LLMConfig"""
        from src.agents.llm.llm_config import LLMConfig
        assert LLMConfig is not None


class TestPresetConfigs:
    """测试预设模型配置"""

    def test_preset_configs_not_empty(self):
        """测试预设配置不为空"""
        from src.agents.llm.llm_config import PRESET_CONFIGS
        assert len(PRESET_CONFIGS) > 0

    def test_preset_configs_has_gpt35(self):
        """测试预设配置包含 gpt-3.5-turbo"""
        from src.agents.llm.llm_config import PRESET_CONFIGS
        assert "gpt-3.5-turbo" in PRESET_CONFIGS

    def test_preset_configs_has_gpt4o(self):
        """测试预设配置包含 gpt-4o"""
        from src.agents.llm.llm_config import PRESET_CONFIGS
        assert "gpt-4o" in PRESET_CONFIGS

    def test_preset_configs_has_claude(self):
        """测试预设配置包含 Claude 模型"""
        from src.agents.llm.llm_config import PRESET_CONFIGS
        claude_models = [k for k in PRESET_CONFIGS.keys() if "claude" in k.lower()]
        assert len(claude_models) > 0

    def test_preset_configs_has_deepseek(self):
        """测试预设配置包含 DeepSeek 模型"""
        from src.agents.llm.llm_config import PRESET_CONFIGS
        deepseek_models = [k for k in PRESET_CONFIGS.keys() if "deepseek" in k.lower()]
        assert len(deepseek_models) > 0


class TestLLMConfigManager:
    """测试 LLM 配置管理器"""

    def test_get_config(self):
        """测试获取配置"""
        from src.agents.llm.llm_config import LLMConfigManager
        config = LLMConfigManager.get_config()
        assert config is not None

    def test_config_has_default_provider(self):
        """测试配置有默认提供商"""
        from src.agents.llm.llm_config import LLMConfigManager
        config = LLMConfigManager.get_config()
        assert hasattr(config, 'default_provider')
        assert config.default_provider is not None

    def test_config_has_enable_cache(self):
        """测试配置有缓存开关"""
        from src.agents.llm.llm_config import LLMConfigManager
        config = LLMConfigManager.get_config()
        assert hasattr(config, 'enable_cache')
        assert isinstance(config.enable_cache, bool)

    def test_config_has_cache_ttl(self):
        """测试配置有缓存 TTL"""
        from src.agents.llm.llm_config import LLMConfigManager
        config = LLMConfigManager.get_config()
        assert hasattr(config, 'cache_ttl')
        assert isinstance(config.cache_ttl, int)

    def test_config_has_api_keys(self):
        """测试配置有 API 密钥字典"""
        from src.agents.llm.llm_config import LLMConfigManager
        config = LLMConfigManager.get_config()
        assert hasattr(config, 'api_keys')
        assert isinstance(config.api_keys, dict)


class TestLLMSettingsAPI:
    """测试 LLM 设置 Web API"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from src.web.app import create_web_app
        app = create_web_app()
        app.config['TESTING'] = True
        return app.test_client()

    def test_get_llm_models_status_code(self, client):
        """测试获取模型列表状态码"""
        response = client.get('/api/settings/llm/models')
        assert response.status_code == 200

    def test_get_llm_models_success(self, client):
        """测试获取模型列表成功"""
        response = client.get('/api/settings/llm/models')
        data = json.loads(response.data)
        assert data.get('success') is True

    def test_get_llm_models_has_models(self, client):
        """测试获取模型列表包含 models 数据"""
        response = client.get('/api/settings/llm/models')
        data = json.loads(response.data)
        assert 'data' in data
        assert 'models' in data['data']
        assert len(data['data']['models']) > 0

    def test_get_llm_settings_status_code(self, client):
        """测试获取 LLM 设置状态码"""
        response = client.get('/api/settings/llm')
        assert response.status_code == 200

    def test_get_llm_settings_success(self, client):
        """测试获取 LLM 设置成功"""
        response = client.get('/api/settings/llm')
        data = json.loads(response.data)
        assert data.get('success') is True

    def test_get_llm_settings_has_default_provider(self, client):
        """测试获取 LLM 设置包含默认提供商"""
        response = client.get('/api/settings/llm')
        data = json.loads(response.data)
        assert 'data' in data
        assert 'default_provider' in data['data']

    def test_post_llm_settings_status_code(self, client):
        """测试保存 LLM 设置状态码"""
        response = client.post(
            '/api/settings/llm',
            json={'default_provider': 'gpt-4o', 'enable_cache': True},
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_post_llm_settings_success(self, client):
        """测试保存 LLM 设置成功"""
        response = client.post(
            '/api/settings/llm',
            json={'default_provider': 'gpt-4o', 'enable_cache': True},
            content_type='application/json'
        )
        data = json.loads(response.data)
        assert data.get('success') is True


class TestLLMConfigSerialization:
    """测试 LLM 配置序列化"""

    def test_config_to_dict(self):
        """测试配置转换为字典"""
        from src.agents.llm.llm_config import LLMConfigManager
        config = LLMConfigManager.get_config()
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'default_provider' in config_dict

    def test_config_from_dict(self):
        """测试从字典创建配置"""
        from src.agents.llm.llm_config import LLMConfig
        test_dict = {
            'default_provider': 'gpt-4o',
            'enable_cache': True,
            'cache_ttl': 3600,
        }
        config = LLMConfig.from_dict(test_dict)
        assert config.default_provider == 'gpt-4o'
        assert config.enable_cache is True
        assert config.cache_ttl == 3600
