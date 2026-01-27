"""
Agent 配置单元测试
"""
import sys
from pathlib import Path
import json
import tempfile
import os

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.agents.agent_config import (
    AgentConfig,
    AgentConfigManager,
    FinancialAnalysisConfig,
    ValuationConfig,
    RiskManagementConfig,
    get_agent_config,
    set_agent_config,
    reset_agent_config,
)


class TestAgentConfig:
    """Agent 配置测试"""

    def test_default_config_creation(self):
        """测试默认配置创建"""
        config = AgentConfig()
        
        assert config.financial.roe_excellent == 0.20
        assert config.valuation.discount_rate == 0.10
        assert config.risk_management.max_single_position == 0.20

    def test_config_to_dict(self):
        """测试转换为字典"""
        config = AgentConfig()
        data = config.to_dict()
        
        assert "financial" in data
        assert "valuation" in data
        assert "risk_management" in data
        assert data["financial"]["roe_excellent"] == 0.20

    def test_config_from_dict(self):
        """测试从字典创建"""
        data = {
            "financial": {"roe_excellent": 0.25},
            "valuation": {"discount_rate": 0.12},
        }
        
        config = AgentConfig.from_dict(data)
        
        assert config.financial.roe_excellent == 0.25
        assert config.valuation.discount_rate == 0.12

    def test_config_save_and_load(self):
        """测试保存和加载"""
        config = AgentConfig()
        config.financial.roe_excellent = 0.30
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_config.json")
            config.save(path)
            
            loaded = AgentConfig.load(path)
            
            assert loaded.financial.roe_excellent == 0.30


class TestAgentConfigManager:
    """配置管理器测试"""

    def setup_method(self):
        reset_agent_config()

    def test_singleton(self):
        """测试单例模式"""
        m1 = AgentConfigManager()
        m2 = AgentConfigManager()
        
        assert m1 is m2

    def test_get_set_config(self):
        """测试获取和设置配置"""
        config = AgentConfig()
        config.debug_mode = True
        
        set_agent_config(config)
        loaded = get_agent_config()
        
        assert loaded.debug_mode is True

    def test_update_config(self):
        """测试部分更新"""
        AgentConfigManager.update_config(debug_mode=True)
        
        config = get_agent_config()
        
        assert config.debug_mode is True

    def test_get_sub_configs(self):
        """测试获取子配置"""
        fin_cfg = AgentConfigManager.get_financial_config()
        val_cfg = AgentConfigManager.get_valuation_config()
        risk_cfg = AgentConfigManager.get_risk_management_config()
        
        assert isinstance(fin_cfg, FinancialAnalysisConfig)
        assert isinstance(val_cfg, ValuationConfig)
        assert isinstance(risk_cfg, RiskManagementConfig)


class TestFinancialAnalysisConfig:
    """财务分析配置测试"""

    def test_default_thresholds(self):
        """测试默认阈值"""
        cfg = FinancialAnalysisConfig()
        
        assert cfg.roe_excellent == 0.20
        assert cfg.roe_good == 0.15
        assert cfg.roe_minimum == 0.10
        assert cfg.debt_ratio_safe == 0.40

    def test_custom_thresholds(self):
        """测试自定义阈值"""
        cfg = FinancialAnalysisConfig(
            roe_excellent=0.25,
            debt_ratio_safe=0.30
        )
        
        assert cfg.roe_excellent == 0.25
        assert cfg.debt_ratio_safe == 0.30


class TestValuationConfig:
    """估值配置测试"""

    def test_default_params(self):
        """测试默认参数"""
        cfg = ValuationConfig()
        
        assert cfg.discount_rate == 0.10
        assert cfg.terminal_growth_rate == 0.03
        assert cfg.projection_years == 10

    def test_weight_sum(self):
        """测试权重之和"""
        cfg = ValuationConfig()
        
        total = cfg.weight_dcf + cfg.weight_pe + cfg.weight_pb
        assert total == 1.0


class TestRiskManagementConfig:
    """风险管理配置测试"""

    def test_default_limits(self):
        """测试默认限制"""
        cfg = RiskManagementConfig()
        
        assert cfg.max_single_position == 0.20
        assert cfg.max_industry_exposure == 0.40
        assert cfg.min_cash_reserve == 0.10

    def test_stop_loss_take_profit(self):
        """测试止损止盈"""
        cfg = RiskManagementConfig()
        
        assert cfg.default_stop_loss == 0.15
        assert cfg.default_take_profit == 0.50
        assert cfg.trailing_stop_enabled is True
