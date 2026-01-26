"""
Pytest 配置和 fixtures
"""
import pytest
import sys
import os
import logging

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture
def mock_stock_code():
    """提供测试用的股票代码"""
    return "600519"


@pytest.fixture
def mock_stock_name():
    """提供测试用的股票名称"""
    return "贵州茅台"


@pytest.fixture
def sample_financial_metrics():
    """提供示例财务指标"""
    from src.models.data_models import FinancialMetrics

    return FinancialMetrics(
        stock_code="600519",
        pe_ratio=25.0,
        pb_ratio=10.0,
        roe=0.20,
        gross_margin=0.60,
        current_price=1000.0,
        earnings_per_share=40.0,
        debt_ratio=0.25,
        profit_growth=0.15,
        free_cash_flow=1000000000
    )


@pytest.fixture
def sample_context():
    """提供示例分析上下文"""
    from src.models.data_models import StockAnalysisContext, FinancialMetrics

    context = StockAnalysisContext(
        stock_code="600519",
        stock_name="贵州茅台"
    )

    context.financial_metrics = FinancialMetrics(
        stock_code="600519",
        pe_ratio=25.0,
        pb_ratio=10.0,
        roe=0.20,
        gross_margin=0.60,
        current_price=1000.0,
        earnings_per_share=40.0,
        debt_ratio=0.25,
        profit_growth=0.15
    )

    return context


@pytest.fixture
def scheduler():
    """提供工作流调度器"""
    from src.schedulers.workflow_scheduler import WorkflowScheduler

    scheduler = WorkflowScheduler()
    scheduler.register_agents()

    return scheduler


@pytest.fixture
def analysis_manager():
    """提供分析管理器"""
    from src.schedulers.workflow_scheduler import AnalysisManager

    return AnalysisManager()
