"""
单元测试 - 测试性能优化改进
"""
import pytest
import sys
import time
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, 'E:\\Workplace-Pycharm\\VIMaster')

from src.data.akshare_provider import (
    AkshareDataProvider, clear_cache,
    _get_cached_stock_spot, _get_cached_stock_info_df,
    CACHE_EXPIRY_SECONDS
)
from src.schedulers.workflow_scheduler import (
    WorkflowScheduler, AnalysisManager, ExecutionMode, DEFAULT_MAX_WORKERS
)
from src.models.data_models import (
    FinancialMetrics, StockAnalysisContext, AnalysisReport, InvestmentSignal
)


class TestCaching:
    """测试缓存功能"""

    def setup_method(self):
        """每个测试前清除缓存"""
        clear_cache()

    @patch('src.data.akshare_provider.ak.stock_zh_a_spot')
    def test_stock_spot_caching(self, mock_stock_spot):
        """测试股票实时行情缓存"""
        # 创建测试数据
        mock_df = pd.DataFrame({
            '代码': ['600519', '000858'],
            '名称': ['贵州茅台', '五粮液'],
            '最新价': [1000.0, 200.0],
            '市盈率': [25.0, 20.0],
            '市净率': [10.0, 8.0],
        })
        mock_stock_spot.return_value = mock_df

        # 第一次调用 - 应该调用API
        result1 = _get_cached_stock_spot()
        assert mock_stock_spot.call_count == 1
        assert result1 is not None

        # 第二次调用 - 应该使用缓存，不再调用API
        result2 = _get_cached_stock_spot()
        assert mock_stock_spot.call_count == 1  # 仍然是1次
        assert result2 is not None

    @patch('src.data.akshare_provider.ak.stock_info_a_code_name')
    def test_stock_info_caching(self, mock_stock_info):
        """测试股票基本信息缓存"""
        # 创建测试数据
        mock_df = pd.DataFrame({
            '代码': ['600519'],
            '行业': ['食品饮料'],
            '市场': ['沪深A股'],
        })
        mock_stock_info.return_value = mock_df

        # 第一次调用 - 应该调用API
        result1 = _get_cached_stock_info_df()
        assert mock_stock_info.call_count == 1

        # 第二次调用 - 应该使用缓存
        result2 = _get_cached_stock_info_df()
        assert mock_stock_info.call_count == 1  # 仍然是1次

    @patch('src.data.akshare_provider.ak.stock_main_ind', create=True)
    def test_main_indicators_caching(self, mock_main_ind):
        """测试主要财务指标缓存（lru_cache）"""
        # 创建测试数据
        mock_df = pd.DataFrame({
            'roe': [0.20],
            '毛利率': [0.60],
            'eps': [40.0],
        })
        mock_main_ind.return_value = mock_df

        # 第一次调用 - 应该调用API
        result1 = AkshareDataProvider._get_main_indicators("sh600519")
        assert mock_main_ind.call_count == 1
        assert result1 == (0.20, 0.60, 40.0)

        # 第二次调用相同参数 - 应该使用缓存
        result2 = AkshareDataProvider._get_main_indicators("sh600519")
        assert mock_main_ind.call_count == 1  # 仍然是1次
        assert result2 == (0.20, 0.60, 40.0)

        # 不同参数 - 应该调用API
        result3 = AkshareDataProvider._get_main_indicators("sz000858")
        assert mock_main_ind.call_count == 2

    def test_clear_cache(self):
        """测试清除缓存功能"""
        # 清除缓存应该不抛出异常
        clear_cache()

    @patch('src.data.akshare_provider.ak.stock_main_ind', create=True)
    @patch('src.data.akshare_provider.ak.stock_zh_a_spot')
    def test_get_stock_info_uses_cache(self, mock_stock_spot, mock_main_ind):
        """测试 get_stock_info 使用缓存"""
        # 创建测试数据
        mock_df = pd.DataFrame({
            '代码': ['600519'],
            '名称': ['贵州茅台'],
            '最新价': [1000.0],
            '市盈率': [25.0],
            '市净率': [10.0],
        })
        mock_stock_spot.return_value = mock_df

        # 获取多次相同股票的信息
        result1 = AkshareDataProvider.get_stock_info("600519")
        result2 = AkshareDataProvider.get_stock_info("600519")

        # 应该只调用一次API
        assert mock_stock_spot.call_count == 1
        assert result1 == result2

    @patch('src.data.akshare_provider.ak.stock_info_a_code_name')
    def test_get_industry_info_uses_cache(self, mock_stock_info):
        """测试 get_industry_info 使用缓存"""
        # 创建测试数据
        mock_df = pd.DataFrame({
            '代码': ['600519'],
            '行业': ['食品饮料'],
            '市场': ['沪深A股'],
        })
        mock_stock_info.return_value = mock_df

        # 获取多次相同股票的行业信息
        result1 = AkshareDataProvider.get_industry_info("600519")
        result2 = AkshareDataProvider.get_industry_info("600519")

        # 应该只调用一次API
        assert mock_stock_info.call_count == 1
        assert result1 is not None


class TestParallelExecution:
    """测试并行执行功能"""

    def test_execution_mode_enum(self):
        """测试执行模式枚举"""
        assert ExecutionMode.SEQUENTIAL.value == "sequential"
        assert ExecutionMode.PARALLEL.value == "parallel"

    def test_default_max_workers(self):
        """测试默认最大线程数"""
        assert DEFAULT_MAX_WORKERS == 4

    def test_workflow_scheduler_parallel_mode(self):
        """测试工作流调度器并行模式初始化"""
        scheduler = WorkflowScheduler(ExecutionMode.PARALLEL)
        assert scheduler.execution_mode == ExecutionMode.PARALLEL

    def test_analysis_manager_default_parallel(self):
        """测试分析管理器默认使用并行模式"""
        manager = AnalysisManager()
        assert manager.scheduler.execution_mode == ExecutionMode.PARALLEL

    def test_analysis_manager_sequential_mode(self):
        """测试分析管理器可以设置顺序模式"""
        manager = AnalysisManager(execution_mode=ExecutionMode.SEQUENTIAL)
        assert manager.scheduler.execution_mode == ExecutionMode.SEQUENTIAL

    @patch('src.schedulers.workflow_scheduler.WorkflowScheduler.analyze_stock')
    def test_analyze_stocks_parallel(self, mock_analyze):
        """测试并行分析多只股票"""
        # Mock 单个股票分析结果
        def create_mock_context(code):
            context = StockAnalysisContext(stock_code=code)
            context.final_signal = InvestmentSignal.BUY
            context.overall_score = 75.0
            return context

        mock_analyze.side_effect = lambda code, name="": create_mock_context(code)

        scheduler = WorkflowScheduler(ExecutionMode.PARALLEL)
        scheduler.register_agents()

        stock_codes = ["600519", "000858", "000001"]
        report = scheduler.analyze_stocks(stock_codes)

        # 验证结果
        assert report.total_stocks_analyzed == 3
        assert len(report.stocks) == 3

    @patch('src.schedulers.workflow_scheduler.WorkflowScheduler.analyze_stock')
    def test_analyze_stocks_sequential(self, mock_analyze):
        """测试顺序分析多只股票"""
        def create_mock_context(code):
            context = StockAnalysisContext(stock_code=code)
            context.final_signal = InvestmentSignal.HOLD
            context.overall_score = 60.0
            return context

        mock_analyze.side_effect = lambda code, name="": create_mock_context(code)

        scheduler = WorkflowScheduler(ExecutionMode.SEQUENTIAL)
        scheduler.register_agents()

        stock_codes = ["600519", "000858"]
        report = scheduler.analyze_stocks(stock_codes)

        assert report.total_stocks_analyzed == 2

    @patch('src.schedulers.workflow_scheduler.WorkflowScheduler.analyze_stock')
    def test_parallel_preserves_order(self, mock_analyze):
        """测试并行执行保持结果顺序"""
        call_order = []

        def create_mock_context(code):
            call_order.append(code)
            context = StockAnalysisContext(stock_code=code)
            context.final_signal = InvestmentSignal.HOLD
            return context

        mock_analyze.side_effect = lambda code, name="": create_mock_context(code)

        scheduler = WorkflowScheduler(ExecutionMode.PARALLEL)
        scheduler.register_agents()

        stock_codes = ["600519", "000858", "000001"]
        report = scheduler.analyze_stocks(stock_codes)

        # 结果顺序应该与输入顺序一致
        result_codes = [stock.stock_code for stock in report.stocks]
        assert result_codes == stock_codes

    @patch('src.schedulers.workflow_scheduler.WorkflowScheduler.analyze_stock')
    def test_parallel_handles_failure(self, mock_analyze):
        """测试并行执行处理失败情况"""
        def create_mock_context(code):
            if code == "999999":
                return None  # 模拟失败
            context = StockAnalysisContext(stock_code=code)
            context.final_signal = InvestmentSignal.HOLD
            return context

        mock_analyze.side_effect = lambda code, name="": create_mock_context(code)

        scheduler = WorkflowScheduler(ExecutionMode.PARALLEL)
        scheduler.register_agents()

        stock_codes = ["600519", "999999", "000858"]
        report = scheduler.analyze_stocks(stock_codes)

        # 只有2只成功
        assert report.total_stocks_analyzed == 2


class TestAnalysisManagerIntegration:
    """测试分析管理器集成"""

    @patch('src.data.akshare_provider.AkshareDataProvider.get_financial_metrics')
    @patch('src.data.akshare_provider.AkshareDataProvider.get_industry_info')
    def test_analyze_portfolio_parallel(self, mock_industry, mock_metrics):
        """测试并行分析组合"""
        mock_metrics.return_value = FinancialMetrics(
            stock_code="600519",
            pe_ratio=25.0,
            pb_ratio=10.0,
            roe=0.20,
            gross_margin=0.60,
            current_price=1000.0,
            earnings_per_share=40.0,
            debt_ratio=0.25
        )

        mock_industry.return_value = {
            "industry": "食品饮料",
            "market": "沪深京A"
        }

        manager = AnalysisManager(execution_mode=ExecutionMode.PARALLEL)
        report = manager.analyze_portfolio(["600519", "600519"])

        assert report.total_stocks_analyzed == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
