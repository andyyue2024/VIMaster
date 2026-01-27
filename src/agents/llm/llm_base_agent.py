"""
LLM 基础 Agent - 基于大语言模型的 Agent 基类
"""
import json
import logging
import time
from abc import abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.models.data_models import StockAnalysisContext
from src.agents.llm.llm_config import (
    LLMConfigManager,
    LLMProviderConfig,
    LLMProvider,
)

logger = logging.getLogger(__name__)

# 尝试导入 OpenAI 客户端
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# 尝试导入 Anthropic 客户端
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None


class LLMBaseAgent(BaseAgent):
    """
    基于 LLM 的 Agent 基类

    所有大师投资 Agent 继承此类，使用 LLM 进行分析
    """

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        master_file: Optional[str] = None,
    ):
        """
        初始化 LLM Agent

        Args:
            name: Agent 名称
            description: Agent 描述
            system_prompt: 系统提示词（来自 master 文件）
            master_file: master 文件路径（可选）
        """
        super().__init__(name, description)
        self.system_prompt = system_prompt
        self.master_file = master_file
        self._client = None
        self._provider_config: Optional[LLMProviderConfig] = None

    def _get_provider_config(self) -> LLMProviderConfig:
        """获取此 Agent 的 LLM 提供商配置"""
        if self._provider_config is None:
            self._provider_config = LLMConfigManager.get_provider_config(self.name)
        return self._provider_config

    def _get_client(self):
        """获取或创建 LLM 客户端"""
        if self._client is not None:
            return self._client

        config = self._get_provider_config()

        if config.provider in [
            LLMProvider.OPENAI,
            LLMProvider.DEEPSEEK,
            LLMProvider.QWEN,
            LLMProvider.ZHIPU,
            LLMProvider.OLLAMA,
            LLMProvider.CUSTOM,
        ]:
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "openai 库未安装，请运行: pip install openai"
                )
            self._client = OpenAI(
                api_key=config.api_key or "dummy",
                base_url=config.api_base,
                timeout=config.timeout,
            )
        elif config.provider == LLMProvider.ANTHROPIC:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError(
                    "anthropic 库未安装，请运行: pip install anthropic"
                )
            self._client = Anthropic(
                api_key=config.api_key,
                timeout=config.timeout,
            )
        else:
            raise ValueError(f"不支持的 LLM 提供商: {config.provider}")

        return self._client

    def _call_llm(self, user_message: str) -> str:
        """
        调用 LLM 获取响应

        Args:
            user_message: 用户消息

        Returns:
            LLM 响应文本
        """
        config = self._get_provider_config()
        client = self._get_client()

        logger.debug(f"[{self.name}] 调用 LLM: {config.provider.value}/{config.model_name}")

        retry_count = config.retry_count
        last_error = None

        for attempt in range(retry_count):
            try:
                if config.provider == LLMProvider.ANTHROPIC:
                    # Anthropic API
                    response = client.messages.create(
                        model=config.model_name,
                        max_tokens=config.max_tokens,
                        temperature=config.temperature,
                        system=self.system_prompt,
                        messages=[
                            {"role": "user", "content": user_message}
                        ],
                    )
                    return response.content[0].text
                else:
                    # OpenAI 兼容 API
                    response = client.chat.completions.create(
                        model=config.model_name,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        temperature=config.temperature,
                        max_tokens=config.max_tokens,
                        top_p=config.top_p,
                        frequency_penalty=config.frequency_penalty,
                        presence_penalty=config.presence_penalty,
                    )
                    return response.choices[0].message.content

            except Exception as e:
                last_error = e
                logger.warning(
                    f"[{self.name}] LLM 调用失败 (尝试 {attempt + 1}/{retry_count}): {e}"
                )
                if attempt < retry_count - 1:
                    time.sleep(config.retry_delay * (attempt + 1))

        raise RuntimeError(f"LLM 调用失败，已重试 {retry_count} 次: {last_error}")

    def _parse_signal_response(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 返回的投资信号 JSON

        Args:
            response: LLM 响应文本

        Returns:
            解析后的信号字典
        """
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        import re
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 尝试提取代码块中的 JSON
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # 返回默认值
        logger.warning(f"[{self.name}] 无法解析 LLM 响应为 JSON: {response[:200]}...")
        return {
            "signal": "neutral",
            "confidence": 50.0,
            "reasoning": response,
        }

    def _prepare_analysis_data(self, context: StockAnalysisContext) -> Dict[str, Any]:
        """
        准备分析数据，供 LLM 分析使用

        Args:
            context: 股票分析上下文

        Returns:
            分析数据字典
        """
        data = {
            "stock_code": context.stock_code,
            "stock_name": context.stock_name,
            "analysis_date": context.analysis_date.isoformat() if context.analysis_date else None,
        }

        # 添加财务指标
        if context.financial_metrics:
            fm = context.financial_metrics
            data["financial_metrics"] = {
                "pe_ratio": fm.pe_ratio,
                "pb_ratio": fm.pb_ratio,
                "roe": fm.roe,
                "gross_margin": fm.gross_margin,
                "free_cash_flow": fm.free_cash_flow,
                "debt_ratio": fm.debt_ratio,
                "current_price": fm.current_price,
                "earnings_per_share": fm.earnings_per_share,
                "book_value_per_share": fm.book_value_per_share,
                "revenue_growth": fm.revenue_growth,
                "profit_growth": fm.profit_growth,
                "dividend_yield": fm.dividend_yield,
            }

        # 添加护城河分析
        if context.competitive_moat:
            cm = context.competitive_moat
            data["competitive_moat"] = {
                "brand_strength": cm.brand_strength,
                "cost_advantage": cm.cost_advantage,
                "network_effect": cm.network_effect,
                "switching_cost": cm.switching_cost,
                "overall_score": cm.overall_score,
                "description": cm.description,
            }

        # 添加估值分析
        if context.valuation:
            v = context.valuation
            data["valuation"] = {
                "intrinsic_value": v.intrinsic_value,
                "dcf_value": v.dcf_value,
                "pe_valuation": v.pe_valuation,
                "pb_valuation": v.pb_valuation,
                "margin_of_safety": v.margin_of_safety,
                "current_price": v.current_price,
                "fair_price": v.fair_price,
                "valuation_score": v.valuation_score,
            }

        return data

    @abstractmethod
    def _build_user_message(self, context: StockAnalysisContext) -> str:
        """
        构建用户消息（子类必须实现）

        Args:
            context: 股票分析上下文

        Returns:
            用户消息字符串
        """
        pass

    @abstractmethod
    def _process_signal(
        self,
        context: StockAnalysisContext,
        signal: Dict[str, Any]
    ) -> StockAnalysisContext:
        """
        处理 LLM 返回的信号，更新上下文（子类必须实现）

        Args:
            context: 股票分析上下文
            signal: LLM 返回的信号字典

        Returns:
            更新后的上下文
        """
        pass

    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        执行 LLM 分析

        Args:
            context: 股票分析上下文

        Returns:
            更新后的分析上下文
        """
        try:
            # 构建用户消息
            user_message = self._build_user_message(context)

            # 调用 LLM
            response = self._call_llm(user_message)

            # 解析响应
            signal = self._parse_signal_response(response)

            # 记录原始响应
            if not hasattr(context, 'llm_responses'):
                context.llm_responses = {}
            context.llm_responses[self.name] = {
                "raw_response": response,
                "parsed_signal": signal,
                "timestamp": datetime.now().isoformat(),
            }

            # 处理信号并更新上下文
            return self._process_signal(context, signal)

        except Exception as e:
            logger.error(f"[{self.name}] 分析失败: {e}", exc_info=True)
            # 返回原始上下文，不中断流程
            return context

    def get_investment_signal(self, context: StockAnalysisContext) -> Dict[str, Any]:
        """
        获取投资信号（便捷方法）

        Args:
            context: 股票分析上下文

        Returns:
            投资信号字典
        """
        user_message = self._build_user_message(context)
        response = self._call_llm(user_message)
        return self._parse_signal_response(response)

    def set_provider(self, provider_name: str) -> None:
        """
        设置此 Agent 使用的 LLM 提供商

        Args:
            provider_name: 提供商名称（如 "gpt-4o", "claude-3-5-sonnet" 等）
        """
        LLMConfigManager.set_agent_provider(self.name, provider_name)
        # 清除缓存的配置和客户端
        self._provider_config = None
        self._client = None
        logger.info(f"[{self.name}] 已切换到提供商: {provider_name}")

    def __repr__(self) -> str:
        config = self._get_provider_config()
        return f"<{self.__class__.__name__} name={self.name} provider={config.provider.value}/{config.model_name}>"
