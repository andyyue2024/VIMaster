"""
LLM 配置模块 - 支持多种大模型选型
"""
import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM 提供商枚举"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"  # 阿里通义千问
    ZHIPU = "zhipu"  # 智谱 GLM
    BAIDU = "baidu"  # 百度文心一言
    OLLAMA = "ollama"  # 本地部署
    CUSTOM = "custom"  # 自定义 API


@dataclass
class LLMProviderConfig:
    """单个 LLM 提供商配置"""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"

    # 模型参数
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # 请求参数
    timeout: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0

    # 其他
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result["provider"] = self.provider.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMProviderConfig":
        """从字典创建配置"""
        if "provider" in data:
            data["provider"] = LLMProvider(data["provider"])
        return cls(**data)


# 预设的模型配置
PRESET_CONFIGS: Dict[str, LLMProviderConfig] = {
    # OpenAI 系列
    "gpt-4o": LLMProviderConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o",
        temperature=0.7,
        max_tokens=4096,
    ),
    "gpt-4o-mini": LLMProviderConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.7,
        max_tokens=4096,
    ),
    "gpt-4-turbo": LLMProviderConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4-turbo",
        temperature=0.7,
        max_tokens=4096,
    ),
    "gpt-3.5-turbo": LLMProviderConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=2048,
    ),

    # Anthropic Claude 系列
    "claude-3-5-sonnet": LLMProviderConfig(
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=4096,
    ),
    "claude-3-opus": LLMProviderConfig(
        provider=LLMProvider.ANTHROPIC,
        model_name="claude-3-opus-20240229",
        temperature=0.7,
        max_tokens=4096,
    ),

    # DeepSeek 系列
    "deepseek-chat": LLMProviderConfig(
        provider=LLMProvider.DEEPSEEK,
        api_base="https://api.deepseek.com/v1",
        model_name="deepseek-chat",
        temperature=0.7,
        max_tokens=4096,
    ),
    "deepseek-coder": LLMProviderConfig(
        provider=LLMProvider.DEEPSEEK,
        api_base="https://api.deepseek.com/v1",
        model_name="deepseek-coder",
        temperature=0.7,
        max_tokens=4096,
    ),

    # 阿里通义千问系列
    "qwen-turbo": LLMProviderConfig(
        provider=LLMProvider.QWEN,
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-turbo",
        temperature=0.7,
        max_tokens=2048,
    ),
    "qwen-plus": LLMProviderConfig(
        provider=LLMProvider.QWEN,
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-plus",
        temperature=0.7,
        max_tokens=4096,
    ),
    "qwen-max": LLMProviderConfig(
        provider=LLMProvider.QWEN,
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-max",
        temperature=0.7,
        max_tokens=8192,
    ),

    # 智谱 GLM 系列
    "glm-4": LLMProviderConfig(
        provider=LLMProvider.ZHIPU,
        api_base="https://open.bigmodel.cn/api/paas/v4",
        model_name="glm-4",
        temperature=0.7,
        max_tokens=4096,
    ),
    "glm-4-flash": LLMProviderConfig(
        provider=LLMProvider.ZHIPU,
        api_base="https://open.bigmodel.cn/api/paas/v4",
        model_name="glm-4-flash",
        temperature=0.7,
        max_tokens=4096,
    ),

    # 本地 Ollama
    "ollama-llama3": LLMProviderConfig(
        provider=LLMProvider.OLLAMA,
        api_base="http://localhost:11434/v1",
        model_name="llama3",
        temperature=0.7,
        max_tokens=4096,
    ),
    "ollama-qwen2": LLMProviderConfig(
        provider=LLMProvider.OLLAMA,
        api_base="http://localhost:11434/v1",
        model_name="qwen2",
        temperature=0.7,
        max_tokens=4096,
    ),
}


@dataclass
class LLMConfig:
    """LLM 全局配置"""
    # 默认提供商配置
    default_provider: str = "gpt-3.5-turbo"

    # 各 Agent 的专属配置（可选覆盖默认配置）
    agent_configs: Dict[str, str] = field(default_factory=dict)

    # 自定义提供商配置
    custom_providers: Dict[str, LLMProviderConfig] = field(default_factory=dict)

    # API 密钥（按提供商分类）
    api_keys: Dict[str, str] = field(default_factory=dict)

    # 全局设置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    log_requests: bool = True

    def get_provider_config(self, agent_name: Optional[str] = None) -> LLMProviderConfig:
        """获取指定 Agent 的提供商配置"""
        # 查找 Agent 专属配置
        provider_name = self.default_provider
        if agent_name and agent_name in self.agent_configs:
            provider_name = self.agent_configs[agent_name]

        # 尝试从自定义配置获取
        if provider_name in self.custom_providers:
            config = self.custom_providers[provider_name]
        # 尝试从预设配置获取
        elif provider_name in PRESET_CONFIGS:
            config = PRESET_CONFIGS[provider_name]
        else:
            logger.warning(f"未找到配置 '{provider_name}'，使用默认 gpt-3.5-turbo")
            config = PRESET_CONFIGS["gpt-3.5-turbo"]

        # 填充 API 密钥
        if config.api_key is None:
            provider_key = config.provider.value
            if provider_key in self.api_keys:
                config.api_key = self.api_keys[provider_key]
            else:
                # 尝试从环境变量获取
                env_key_mapping = {
                    LLMProvider.OPENAI: "OPENAI_API_KEY",
                    LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
                    LLMProvider.DEEPSEEK: "DEEPSEEK_API_KEY",
                    LLMProvider.QWEN: "DASHSCOPE_API_KEY",
                    LLMProvider.ZHIPU: "ZHIPU_API_KEY",
                }
                env_key = env_key_mapping.get(config.provider)
                if env_key:
                    config.api_key = os.environ.get(env_key)

        return config

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "default_provider": self.default_provider,
            "agent_configs": self.agent_configs,
            "custom_providers": {
                k: v.to_dict() for k, v in self.custom_providers.items()
            },
            "api_keys": self.api_keys,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl,
            "log_requests": self.log_requests,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMConfig":
        """从字典创建配置"""
        config = cls()
        config.default_provider = data.get("default_provider", "gpt-3.5-turbo")
        config.agent_configs = data.get("agent_configs", {})
        config.api_keys = data.get("api_keys", {})
        config.enable_cache = data.get("enable_cache", True)
        config.cache_ttl = data.get("cache_ttl", 3600)
        config.log_requests = data.get("log_requests", True)

        # 解析自定义提供商配置
        if "custom_providers" in data:
            for name, provider_data in data["custom_providers"].items():
                config.custom_providers[name] = LLMProviderConfig.from_dict(provider_data)

        return config

    def save(self, path: str) -> None:
        """保存配置到 JSON 文件"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"LLM 配置已保存到 {path}")

    @classmethod
    def load(cls, path: str) -> "LLMConfig":
        """从 JSON 文件加载配置"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class LLMConfigManager:
    """LLM 配置管理器 - 单例模式"""

    _instance: Optional["LLMConfigManager"] = None
    _config: LLMConfig = LLMConfig()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls) -> LLMConfig:
        """获取当前配置"""
        return cls._config

    @classmethod
    def set_config(cls, config: LLMConfig) -> None:
        """设置配置"""
        cls._config = config
        logger.info("LLM 配置已更新")

    @classmethod
    def load_from_file(cls, path: str) -> LLMConfig:
        """从文件加载配置"""
        config = LLMConfig.load(path)
        cls._config = config
        logger.info(f"LLM 配置已从 {path} 加载")
        return config

    @classmethod
    def save_to_file(cls, path: str) -> None:
        """保存当前配置到文件"""
        cls._config.save(path)

    @classmethod
    def get_provider_config(cls, agent_name: Optional[str] = None) -> LLMProviderConfig:
        """获取指定 Agent 的提供商配置"""
        return cls._config.get_provider_config(agent_name)

    @classmethod
    def set_agent_provider(cls, agent_name: str, provider_name: str) -> None:
        """设置指定 Agent 使用的提供商"""
        cls._config.agent_configs[agent_name] = provider_name
        logger.info(f"Agent '{agent_name}' 已设置使用 '{provider_name}'")

    @classmethod
    def set_api_key(cls, provider: str, api_key: str) -> None:
        """设置提供商 API 密钥"""
        cls._config.api_keys[provider] = api_key
        logger.info(f"已设置 '{provider}' 的 API 密钥")


# ============================================================================
# 便捷函数
# ============================================================================


def get_llm_config() -> LLMConfig:
    """获取全局 LLM 配置"""
    return LLMConfigManager.get_config()


def set_llm_config(config: LLMConfig) -> None:
    """设置全局 LLM 配置"""
    LLMConfigManager.set_config(config)


def load_llm_config(path: str) -> LLMConfig:
    """从文件加载 LLM 配置"""
    return LLMConfigManager.load_from_file(path)


def get_provider_config(agent_name: Optional[str] = None) -> LLMProviderConfig:
    """获取提供商配置"""
    return LLMConfigManager.get_provider_config(agent_name)
