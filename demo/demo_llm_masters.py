"""
LLM 大师 Agent 演示脚本

本脚本展示如何使用基于大语言模型的投资大师 Agent 分析股票。

使用前请确保：
1. 配置了 LLM API 密钥（在 config/llm_config.json 或环境变量中）
2. 安装了 openai 库：pip install openai

支持的 LLM 提供商：
- OpenAI (GPT-4o, GPT-4, GPT-3.5-turbo)
- Anthropic Claude (Claude 3.5 Sonnet, Claude 3 Opus)
- DeepSeek
- 阿里通义千问 (Qwen)
- 智谱 GLM
- Ollama (本地部署)
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.llm import (
    LLMConfig,
    LLMProvider,
    LLMConfigManager,
    BenGrahamAgent,
    PhilipFisherAgent,
    CharlieMungerAgent,
    WarrenBuffettAgent,
    StanleyDruckenmillerAgent,
    CathieWoodAgent,
    BillAckmanAgent,
    get_all_master_agents,
    get_master_agent_by_name,
)
from src.agents.llm.master_agents import run_all_masters_analysis, get_master_consensus
from src.schedulers.workflow_scheduler import AnalysisManager


def print_separator():
    print("\n" + "="*80 + "\n")


def demo_list_agents():
    """展示所有可用的大师 Agent"""
    print("📋 可用的 LLM 投资大师 Agent")
    print_separator()

    agents = get_all_master_agents()
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name}")
        print(f"   描述: {agent.description}")
        print(f"   提示词文件: {agent.master_file}")
        print()


def demo_configure_llm():
    """展示如何配置 LLM 提供商"""
    print("⚙️ 配置 LLM 提供商")
    print_separator()

    # 获取当前配置
    config = LLMConfigManager.get_config()
    print(f"默认提供商: {config.default_provider}")
    print(f"缓存启用: {config.enable_cache}")
    print()

    # 显示 Agent 专属配置
    print("Agent 专属配置:")
    for agent_name, provider in config.agent_configs.items():
        print(f"  {agent_name}: {provider}")
    print()

    # 展示如何切换模型
    print("💡 示例：为巴菲特 Agent 切换到不同模型")
    print("   agent = WarrenBuffettAgent()")
    print("   agent.set_provider('gpt-4o')      # 使用 OpenAI GPT-4o")
    print("   agent.set_provider('claude-3-5-sonnet')  # 使用 Claude")
    print("   agent.set_provider('deepseek-chat')      # 使用 DeepSeek")
    print("   agent.set_provider('qwen-plus')          # 使用通义千问")


def demo_single_master(stock_code: str = "600519"):
    """展示使用单个大师分析"""
    print(f"👤 使用单个大师 Agent 分析股票 {stock_code}")
    print_separator()

    # 获取基础分析数据
    manager = AnalysisManager()
    context = manager.analyze_single_stock(stock_code)

    if not context:
        print(f"⚠️ 无法获取股票 {stock_code} 的数据")
        return

    # 创建巴菲特 Agent
    buffett = WarrenBuffettAgent()
    print(f"使用 {buffett.name} 分析...")
    print(f"提供商配置: {buffett}")
    print()

    # 注意：实际运行需要配置 API 密钥
    print("💡 注意：要运行 LLM 分析，请确保配置了 API 密钥")
    print("   方式1：设置环境变量 OPENAI_API_KEY")
    print("   方式2：在 config/llm_config.json 中配置 api_keys")
    print()

    # 展示如何获取投资信号（模拟）
    print("示例输出格式：")
    print("""
{
    "signal": "bullish",
    "confidence": 75.0,
    "reasoning": "根据巴菲特的投资原则分析：
        1. 能力圈: 白酒行业业务模式清晰
        2. 护城河: 品牌护城河强大，茅台品牌价值极高
        3. ROE: 32%，远超15%的优质标准
        4. 负债率: 5%，财务非常稳健
        虽然当前估值偏高，但公司质地优秀，长期持有价值明显"
}
""")


def demo_all_masters(stock_code: str = "600519"):
    """展示使用所有大师分析并获取共识"""
    print(f"👥 使用所有投资大师分析股票 {stock_code}")
    print_separator()

    agents = get_all_master_agents()
    print(f"将使用 {len(agents)} 位投资大师进行分析：")
    for agent in agents:
        print(f"  • {agent.name}")
    print()

    print("💡 运行所有大师分析的命令：")
    print(f"   python run.py masters {stock_code}")
    print()

    print("分析完成后将生成：")
    print("  1. 每位大师的独立分析报告")
    print("  2. 大师共识（多数派观点）")
    print("  3. 平均信心度")
    print()

    print("共识结果示例：")
    print("""
【大师共识】
  共识信号: BULLISH
  看涨: 5 | 中性: 1 | 看跌: 1
  平均信心度: 72.3%
""")


def demo_api_keys():
    """展示如何配置 API 密钥"""
    print("🔑 API 密钥配置指南")
    print_separator()

    print("方式1：环境变量（推荐）")
    print("-" * 40)
    print("""
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-xxx"
$env:ANTHROPIC_API_KEY = "sk-ant-xxx"
$env:DEEPSEEK_API_KEY = "sk-xxx"
$env:DASHSCOPE_API_KEY = "sk-xxx"  # 阿里通义千问
$env:ZHIPU_API_KEY = "xxx"         # 智谱

# Linux/Mac
export OPENAI_API_KEY="sk-xxx"
""")

    print("\n方式2：配置文件 config/llm_config.json")
    print("-" * 40)
    print("""
{
  "api_keys": {
    "openai": "sk-xxx",
    "anthropic": "sk-ant-xxx",
    "deepseek": "sk-xxx",
    "qwen": "sk-xxx",
    "zhipu": "xxx"
  }
}
""")

    print("\n方式3：代码中动态设置")
    print("-" * 40)
    print("""
from src.agents.llm import LLMConfigManager

LLMConfigManager.set_api_key("openai", "sk-xxx")
LLMConfigManager.set_api_key("anthropic", "sk-ant-xxx")
""")


def main():
    print("🌟 VIMaster LLM 投资大师 Agent 演示")
    print("="*80)
    print()

    # 1. 列出所有大师 Agent
    demo_list_agents()

    # 2. 配置说明
    demo_configure_llm()
    print_separator()

    # 3. API 密钥配置
    demo_api_keys()
    print_separator()

    # 4. 单个大师分析示例
    demo_single_master("600519")
    print_separator()

    # 5. 所有大师分析示例
    demo_all_masters("600519")

    print("\n" + "="*80)
    print("✅ 演示完成！")
    print()
    print("下一步：")
    print("  1. 配置 LLM API 密钥")
    print("  2. 运行: python run.py masters 600519")
    print("  3. 或进入交互模式: python run.py")
    print("="*80)


if __name__ == "__main__":
    main()
