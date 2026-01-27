"""
多源数据提供者单元测试
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import (
    MultiSourceDataProvider,
    BaseDataSource,
    DataSourceType,
    TuShareProvider,
    BaoStockProvider,
)
from src.models.data_models import FinancialMetrics


class TestBaseDataSource:
    """测试基类"""

    def test_data_source_type_enum(self):
        """测试数据源类型枚举"""
        assert DataSourceType.AKSHARE.value == "akshare"
        assert DataSourceType.TUSHARE.value == "tushare"
        assert DataSourceType.BAOSTOCK.value == "baostock"
        assert DataSourceType.MOCK.value == "mock"


class TestTuShareProvider:
    """测试 TuShare 提供者"""

    def test_initialization(self):
        """测试初始化"""
        # 不提供 token，应该初始化但不连接
        provider = TuShareProvider()
        assert provider.name == "TuShare"
        assert provider.source_type == DataSourceType.TUSHARE

    def test_ts_code_conversion_sh(self):
        """测试沪深代码转换 - 沪市"""
        ts_code = TuShareProvider._convert_to_ts_code("600519")
        assert ts_code == "600519.SH"

    def test_ts_code_conversion_sz(self):
        """测试沪深代码转换 - 深市"""
        ts_code = TuShareProvider._convert_to_ts_code("000858")
        assert ts_code == "000858.SZ"

    def test_ts_code_already_converted(self):
        """测试已转换的代码"""
        ts_code = TuShareProvider._convert_to_ts_code("600519.SH")
        assert ts_code == "600519.SH"


class TestBaoStockProvider:
    """测试 BaoStock 提供者"""

    def test_initialization(self):
        """测试初始化"""
        provider = BaoStockProvider()
        assert provider.name == "BaoStock"
        assert provider.source_type == DataSourceType.BAOSTOCK

    def test_bs_code_conversion_sh(self):
        """测试代码转换 - 沪市"""
        bs_code = BaoStockProvider._convert_to_bs_code("600519")
        assert bs_code == "sh.600519"

    def test_bs_code_conversion_sz(self):
        """测试代码转换 - 深市"""
        bs_code = BaoStockProvider._convert_to_bs_code("000858")
        assert bs_code == "sz.000858"

    def test_bs_code_already_converted(self):
        """测试已转换的代码"""
        bs_code = BaoStockProvider._convert_to_bs_code("sh.600519")
        assert bs_code == "sh.600519"


class TestMultiSourceDataProvider:
    """测试多源数据提供者"""

    def test_initialization(self):
        """测试初始化"""
        provider = MultiSourceDataProvider()
        assert provider.sources is not None
        assert len(provider.sources) > 0

    def test_get_available_sources(self):
        """测试获取可用源"""
        provider = MultiSourceDataProvider()
        available = provider.get_available_sources()
        # 至少应该有一些源可用
        assert available is not None
        assert isinstance(available, list)

    def test_get_source_stats(self):
        """测试获取源统计"""
        provider = MultiSourceDataProvider()
        stats = provider.get_source_stats()

        assert "total_sources" in stats
        assert "available_sources" in stats
        assert "unavailable_sources" in stats
        assert "sources" in stats

        assert stats["total_sources"] > 0
        assert stats["available_sources"] >= 0
        assert stats["unavailable_sources"] >= 0
        assert len(stats["sources"]) == stats["total_sources"]

    def test_get_stock_info_graceful_fallback(self):
        """测试股票信息获取的优雅降级"""
        provider = MultiSourceDataProvider()

        # 应该返回 None 或数据，不应该抛出异常
        result = provider.get_stock_info("600519")
        assert result is None or isinstance(result, dict)

    def test_get_financial_metrics_graceful_fallback(self):
        """测试财务指标获取的优雅降级"""
        provider = MultiSourceDataProvider()

        # 应该返回 None 或 FinancialMetrics，不应该抛出异常
        result = provider.get_financial_metrics("600519")
        assert result is None or isinstance(result, FinancialMetrics)

    def test_get_historical_price_graceful_fallback(self):
        """测试历史价格获取的优雅降级"""
        provider = MultiSourceDataProvider()

        # 应该返回 None 或 DataFrame，不应该抛出异常
        result = provider.get_historical_price("600519", days=10)
        assert result is None or hasattr(result, 'empty')

    def test_get_industry_info_graceful_fallback(self):
        """测试行业信息获取的优雅降级"""
        provider = MultiSourceDataProvider()

        # 应该返回 None 或 dict，不应该抛出异常
        result = provider.get_industry_info("600519")
        assert result is None or isinstance(result, dict)

    @patch('src.data.multi_source_provider.AkshareDataProvider.get_stock_info')
    def test_fallback_to_akshare(self, mock_akshare):
        """测试降级到 AkShare"""
        # 设置 mock 返回值
        expected_data = {"code": "600519", "current_price": 1800.5}
        mock_akshare.return_value = expected_data

        provider = MultiSourceDataProvider()

        # 使主要源不可用
        provider.sources = []

        # 调用方法应该降级到 AkShare
        result = provider.get_stock_info("600519")

        # 应该从 AkShare 获取数据
        mock_akshare.assert_called_once()

    def test_source_priority_order(self):
        """测试源优先级"""
        provider = MultiSourceDataProvider()

        # 检查优先级顺序
        assert provider.source_priority[0] == DataSourceType.TUSHARE
        assert provider.source_priority[1] == DataSourceType.BAOSTOCK
        assert provider.source_priority[2] == DataSourceType.AKSHARE
        assert provider.source_priority[3] == DataSourceType.MOCK

    def test_multiple_stock_codes(self):
        """测试多个股票代码"""
        provider = MultiSourceDataProvider()

        test_codes = ["600519", "000858", "000651"]

        for code in test_codes:
            # 应该都能处理而不抛出异常
            info = provider.get_stock_info(code)
            metrics = provider.get_financial_metrics(code)
            industry = provider.get_industry_info(code)

            # 结果应该是 None 或有效对象
            assert info is None or isinstance(info, dict)
            assert metrics is None or isinstance(metrics, FinancialMetrics)
            assert industry is None or isinstance(industry, dict)

    def test_concurrent_requests(self):
        """测试并发请求"""
        from concurrent.futures import ThreadPoolExecutor

        provider = MultiSourceDataProvider()
        stocks = ["600519", "000858", "000651"]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(provider.get_stock_info, stock)
                for stock in stocks
            ]

            results = [f.result() for f in futures]

            # 应该获得 3 个结果
            assert len(results) == 3
            # 每个结果应该是 None 或 dict
            for result in results:
                assert result is None or isinstance(result, dict)

    def test_invalid_stock_code(self):
        """测试无效股票代码"""
        provider = MultiSourceDataProvider()

        # 获取结果，可能返回 None 或者模拟数据
        result = provider.get_stock_info("INVALID")
        # 允许返回 None 或 dict（备选源可能返回模拟数据）
        assert result is None or isinstance(result, dict)

    def test_provider_string_representation(self):
        """测试数据源字符串表示"""
        provider = TuShareProvider()

        # 应该包含名称和状态
        str_repr = str(provider)
        assert "TuShare" in str_repr
        assert "tushare" in str_repr


class TestDataSourceIntegration:
    """测试数据源集成"""

    def test_seamless_source_switching(self):
        """测试源无缝切换"""
        provider = MultiSourceDataProvider()

        # 获取同一只股票多次
        stock_code = "600519"
        results = []

        for _ in range(3):
            result = provider.get_financial_metrics(stock_code)
            results.append(result)

        # 如果任何请求成功，后续相同请求的核心数据应该相同（忽略时间戳）
        if results[0] is not None and results[1] is not None:
            # 比较核心字段而不是整个对象（update_time 可能不同）
            assert results[0].stock_code == results[1].stock_code
            assert results[0].pe_ratio == results[1].pe_ratio
            assert results[0].roe == results[1].roe

    def test_all_methods_exist(self):
        """测试所有必要方法都存在"""
        provider = MultiSourceDataProvider()

        # 检查所有必要方法
        assert hasattr(provider, 'get_stock_info')
        assert hasattr(provider, 'get_financial_metrics')
        assert hasattr(provider, 'get_historical_price')
        assert hasattr(provider, 'get_industry_info')
        assert hasattr(provider, 'get_available_sources')
        assert hasattr(provider, 'get_source_stats')
        assert hasattr(provider, 'print_source_stats')

    def test_method_return_types(self):
        """测试方法返回类型"""
        provider = MultiSourceDataProvider()

        # 检查返回类型
        sources = provider.get_available_sources()
        assert isinstance(sources, list)

        stats = provider.get_source_stats()
        assert isinstance(stats, dict)

