"""
LLM Agent 模块单元测试
"""
import pytest
import sys
import os

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestLLMAgentImports:
    """测试 LLM Agent 模块导入"""

    def test_import_get_all_master_agents(self):
        """测试导入 get_all_master_agents 函数"""
        from src.agents import get_all_master_agents
        assert callable(get_all_master_agents)

    def test_import_get_all_expert_agents(self):
        """测试导入 get_all_expert_agents 函数"""
        from src.agents import get_all_expert_agents
        assert callable(get_all_expert_agents)

    def test_import_get_master_agent_by_name(self):
        """测试导入 get_master_agent_by_name 函数"""
        from src.agents import get_master_agent_by_name
        assert callable(get_master_agent_by_name)

    def test_import_get_expert_agent_by_name(self):
        """测试导入 get_expert_agent_by_name 函数"""
        from src.agents import get_expert_agent_by_name
        assert callable(get_expert_agent_by_name)


class TestMasterAgents:
    """测试投资大师 Agent"""

    def test_get_all_master_agents_returns_list(self):
        """测试 get_all_master_agents 返回列表"""
        from src.agents import get_all_master_agents
        masters = get_all_master_agents()
        assert isinstance(masters, list)

    def test_master_agents_count(self):
        """测试大师 Agent 数量为 7"""
        from src.agents import get_all_master_agents
        masters = get_all_master_agents()
        assert len(masters) == 7

    def test_master_agents_have_name(self):
        """测试每个大师 Agent 都有 name 属性"""
        from src.agents import get_all_master_agents
        masters = get_all_master_agents()
        for master in masters:
            assert hasattr(master, 'name')
            assert master.name is not None

    def test_master_agents_have_description(self):
        """测试每个大师 Agent 都有 description 属性"""
        from src.agents import get_all_master_agents
        masters = get_all_master_agents()
        for master in masters:
            assert hasattr(master, 'description')
            assert master.description is not None

    def test_get_master_agent_by_name_valid(self):
        """测试通过名称获取大师 Agent"""
        from src.agents import get_master_agent_by_name
        agent = get_master_agent_by_name("WarrenBuffettAgent")
        assert agent is not None
        assert agent.name == "WarrenBuffettAgent"

    def test_get_master_agent_by_name_invalid(self):
        """测试获取不存在的大师 Agent 返回 None"""
        from src.agents import get_master_agent_by_name
        agent = get_master_agent_by_name("NonExistentAgent")
        assert agent is None


class TestExpertAgents:
    """测试分析专家 Agent"""

    def test_get_all_expert_agents_returns_list(self):
        """测试 get_all_expert_agents 返回列表"""
        from src.agents import get_all_expert_agents
        experts = get_all_expert_agents()
        assert isinstance(experts, list)

    def test_expert_agents_count(self):
        """测试专家 Agent 数量为 6"""
        from src.agents import get_all_expert_agents
        experts = get_all_expert_agents()
        assert len(experts) == 6

    def test_expert_agents_have_name(self):
        """测试每个专家 Agent 都有 name 属性"""
        from src.agents import get_all_expert_agents
        experts = get_all_expert_agents()
        for expert in experts:
            assert hasattr(expert, 'name')
            assert expert.name is not None

    def test_expert_agents_have_description(self):
        """测试每个专家 Agent 都有 description 属性"""
        from src.agents import get_all_expert_agents
        experts = get_all_expert_agents()
        for expert in experts:
            assert hasattr(expert, 'description')
            assert expert.description is not None

    def test_get_expert_agent_by_name_valid(self):
        """测试通过名称获取专家 Agent"""
        from src.agents import get_expert_agent_by_name
        # 使用简化名称格式
        agent = get_expert_agent_by_name("fundamentals")
        assert agent is not None
        assert "Fundamentals" in agent.name

    def test_get_expert_agent_by_name_invalid(self):
        """测试获取不存在的专家 Agent 返回 None"""
        from src.agents import get_expert_agent_by_name
        agent = get_expert_agent_by_name("NonExistentAgent")
        assert agent is None


class TestLLMAgentNames:
    """测试 LLM Agent 名称"""

    def test_master_agent_names(self):
        """测试大师 Agent 名称列表"""
        from src.agents import get_all_master_agents
        masters = get_all_master_agents()
        names = [m.name for m in masters]

        expected_names = [
            "BenGrahamAgent",
            "PhilipFisherAgent",
            "CharlieMungerAgent",
            "WarrenBuffettAgent",
            "StanleyDruckenmillerAgent",
            "CathieWoodAgent",
            "BillAckmanAgent",
        ]

        for expected in expected_names:
            assert expected in names, f"缺少大师 Agent: {expected}"

    def test_expert_agent_names(self):
        """测试专家 Agent 名称列表"""
        from src.agents import get_all_expert_agents
        experts = get_all_expert_agents()
        names = [e.name for e in experts]

        expected_names = [
            "FundamentalsAgent",
            "SentimentAgent",
            "ValuationExpertAgent",
            "TechnicalAgent",
            "RiskManagerAgent",
            "PortfolioManagerAgent",
        ]

        for expected in expected_names:
            assert expected in names, f"缺少专家 Agent: {expected}"
