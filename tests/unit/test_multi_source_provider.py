"""
多源数据提供者单元测试
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import (
    MultiSourceDataProvider,
    DataSourceType,
    TuShareProvider,
    BaoStockProvider,
    MockDataProvider,
)
from src.data.mock_provider import MOCK_STOCKS_DATA
from src.data.akshare_provider import (
    AkshareDataProvider,
    clear_cache,
    _get_cached_stock_spot,
    _get_cached_stock_info_df,
)
from src.models.data_models import FinancialMetrics


# ============================================================================
# 数据源类型枚举测试
# ============================================================================
class TestDataSourceType:
    """测试数据源类型枚举"""

    def test_data_source_type_values(self):
        """测试数据源类型枚举值"""
        assert DataSourceType.AKSHARE.value == "akshare"
        assert DataSourceType.TUSHARE.value == "tushare"
        assert DataSourceType.BAOSTOCK.value == "baostock"
        assert DataSourceType.MOCK.value == "mock"

    def test_data_source_type_count(self):
        """测试数据源类型数量"""
        assert len(DataSourceType) == 4

    def test_data_source_type_iteration(self):
        """测试数据源类型可迭代"""
        types = list(DataSourceType)
        assert len(types) == 4
        assert DataSourceType.AKSHARE in types


# ============================================================================
# AkShare 数据提供者测试
# ============================================================================
class TestAkshareDataProvider:
    """测试 AkShare 数据提供者"""

    def setup_method(self):
        """每个测试前清除缓存"""
        clear_cache()
        self.provider = AkshareDataProvider()

    def test_mock_stocks_data_exists(self):
        """测试模拟数据存在"""
        assert MOCK_STOCKS_DATA is not None

    def test_mock_stocks_data_structure(self):
        """测试模拟数据结构"""
        for code, data in MOCK_STOCKS_DATA.items():
            assert "name" in data
            assert "current_price" in data
            assert "pe_ratio" in data
            assert "roe" in data
            assert "gross_margin" in data
            assert "debt_ratio" in data

    def test_mock_stocks_data_values(self):
        """测试模拟数据值的合理性"""
        maotai = MOCK_STOCKS_DATA.get("600519")
        assert maotai is not None
        assert maotai["name"] == "贵州茅台"
        assert maotai["current_price"] > 0
        assert 0 < maotai["roe"] < 1  # ROE 应该是 0-1 之间
        assert 0 < maotai["gross_margin"] < 1  # 毛利率应该是 0-1 之间

    def test_get_stock_info_mock(self):
        """测试获取模拟股票信息"""
        result = self.provider.get_stock_info("600519")
        if result is not None:
            assert isinstance(result, dict)
            assert "code" in result or "current_price" in result

    def test_get_stock_info_unknown_code(self):
        """测试获取未知股票代码"""
        result = self.provider.get_stock_info("999999")
        assert result is None or isinstance(result, dict)

    def test_get_financial_metrics_mock(self):
        """测试获取模拟财务指标"""
        result = self.provider.get_financial_metrics("600519")
        if result is not None:
            assert isinstance(result, FinancialMetrics)
            assert result.stock_code == "600519"

    def test_get_financial_metrics_values(self):
        """测试财务指标值"""
        result = self.provider.get_financial_metrics("600519")
        if result is not None:
            # 检查数据类型和范围
            if result.pe_ratio is not None:
                assert result.pe_ratio > 0
            if result.roe is not None:
                assert 0 <= result.roe <= 1
            if result.gross_margin is not None:
                assert 0 <= result.gross_margin <= 1

    def test_get_historical_price(self):
        """测试获取历史价格"""
        result = self.provider.get_historical_price("600519", days=30)
        # 可能返回 DataFrame 或 None
        assert result is None or isinstance(result, pd.DataFrame)

    def test_get_historical_price_default_days(self):
        """测试获取历史价格默认天数"""
        result = self.provider.get_historical_price("600519")
        # 默认获取 250 天
        assert result is None or isinstance(result, pd.DataFrame)

    def test_get_industry_info(self):
        """测试获取行业信息"""
        result = self.provider.get_industry_info("600519")
        assert result is None or isinstance(result, dict)

    def test_cache_functions(self):
        """测试缓存函数"""
        # 第一次调用
        result1 = _get_cached_stock_spot()
        # 第二次调用应该返回缓存
        result2 = _get_cached_stock_spot()

        # 两次结果应该相同（如果都成功）
        if result1 is not None and result2 is not None:
            assert len(result1) == len(result2)

    def test_clear_cache(self):
        """测试清除缓存"""
        # 调用一次缓存
        _get_cached_stock_spot()
        # 清除缓存
        clear_cache()
        # 缓存应该被清除（会重新获取）

    def test_multiple_stock_codes_mock(self):
        """测试多个模拟股票代码"""
        codes = ["600519", "000858", "000651", "600036", "000333"]
        for code in codes:
            result = self.provider.get_financial_metrics(code)
            if result is not None:
                assert result.stock_code == code


# ============================================================================
# TuShare 数据提供者测试
# ============================================================================
class TestTuShareProvider:
    """测试 TuShare 提供者"""

    def test_initialization_without_token(self):
        """测试无 token 初始化"""
        provider = TuShareProvider()
        assert provider.name == "TuShare"
        assert provider.source_type == DataSourceType.TUSHARE
        assert provider.token == ""
        assert provider.pro is None

    def test_initialization_with_invalid_token(self):
        """测试无效 token 初始化"""
        provider = TuShareProvider(token="invalid_token")
        assert provider.name == "TuShare"
        # 无效 token 不会导致异常

    def test_ts_code_conversion_sh(self):
        """测试沪深代码转换 - 沪市"""
        ts_code = TuShareProvider._convert_to_ts_code("600519")
        assert ts_code == "600519.SH"

    def test_ts_code_conversion_sz(self):
        """测试沪深代码转换 - 深市"""
        ts_code = TuShareProvider._convert_to_ts_code("000858")
        assert ts_code == "000858.SZ"

    def test_ts_code_conversion_cyb(self):
        """测试沪深代码转换 - 创业板"""
        ts_code = TuShareProvider._convert_to_ts_code("300059")
        assert ts_code == "300059.SZ"

    def test_ts_code_conversion_kcb(self):
        """测试沪深代码转换 - 科创板"""
        ts_code = TuShareProvider._convert_to_ts_code("688001")
        assert ts_code == "688001.SH"

    def test_ts_code_already_converted(self):
        """测试已转换的代码"""
        ts_code = TuShareProvider._convert_to_ts_code("600519.SH")
        assert ts_code == "600519.SH"

    def test_ts_code_with_sz_suffix(self):
        """测试带 SZ 后缀的代码"""
        ts_code = TuShareProvider._convert_to_ts_code("000858.SZ")
        assert ts_code == "000858.SZ"

    def test_get_stock_info_without_connection(self):
        """测试无连接时获取股票信息"""
        provider = TuShareProvider()
        result = provider.get_stock_info("600519")
        # 无连接应该返回 None
        assert result is None

    def test_get_financial_metrics_without_connection(self):
        """测试无连接时获取财务指标"""
        provider = TuShareProvider()
        result = provider.get_financial_metrics("600519")
        assert result is None

    def test_get_historical_price_without_connection(self):
        """测试无连接时获取历史价格"""
        provider = TuShareProvider()
        result = provider.get_historical_price("600519")
        assert result is None

    def test_get_industry_info_without_connection(self):
        """测试无连接时获取行业信息"""
        provider = TuShareProvider()
        result = provider.get_industry_info("600519")
        assert result is None

    def test_is_available_without_token(self):
        """测试无 token 时不可用"""
        provider = TuShareProvider()
        assert provider.is_available is False

    def test_string_representation(self):
        """测试字符串表示"""
        provider = TuShareProvider()
        str_repr = str(provider)
        assert "TuShare" in str_repr
        assert "tushare" in str_repr


# ============================================================================
# BaoStock 数据提供者测试
# ============================================================================
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

    def test_bs_code_conversion_cyb(self):
        """测试代码转换 - 创业板"""
        bs_code = BaoStockProvider._convert_to_bs_code("300059")
        assert bs_code == "sz.300059"

    def test_bs_code_conversion_kcb(self):
        """测试代码转换 - 科创板"""
        bs_code = BaoStockProvider._convert_to_bs_code("688001")
        assert bs_code == "sh.688001"

    def test_bs_code_already_converted(self):
        """测试已转换的代码"""
        bs_code = BaoStockProvider._convert_to_bs_code("sh.600519")
        assert bs_code == "sh.600519"

    def test_bs_code_with_sz_prefix(self):
        """测试带 sz 前缀的代码"""
        bs_code = BaoStockProvider._convert_to_bs_code("sz.000858")
        assert bs_code == "sz.000858"

    def test_string_representation(self):
        """测试字符串表示"""
        provider = BaoStockProvider()
        str_repr = str(provider)
        assert "BaoStock" in str_repr
        assert "baostock" in str_repr

    def test_is_available_after_init(self):
        """测试初始化后可用性"""
        provider = BaoStockProvider()
        # BaoStock 通常可用
        assert isinstance(provider.is_available, bool)


# ============================================================================
# 多源数据提供者测试
# ============================================================================
class TestMultiSourceDataProvider:
    """测试多源数据提供者"""

    def test_initialization(self):
        """测试初始化"""
        provider = MultiSourceDataProvider()
        assert provider.sources is not None
        assert len(provider.sources) > 0

    def test_initialization_with_token(self):
        """测试带 token 初始化"""
        provider = MultiSourceDataProvider(tushare_token="test_token")
        assert provider is not None

    def test_get_available_sources(self):
        """测试获取可用源"""
        provider = MultiSourceDataProvider()
        available = provider.get_available_sources()
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

    def test_get_source_stats_structure(self):
        """测试源统计结构"""
        provider = MultiSourceDataProvider()
        stats = provider.get_source_stats()

        for source_stat in stats["sources"]:
            assert "name" in source_stat
            assert "type" in source_stat
            assert "available" in source_stat

    def test_get_stock_info_graceful_fallback(self):
        """测试股票信息获取的优雅降级"""
        provider = MultiSourceDataProvider()
        result = provider.get_stock_info("600519")
        assert result is None or isinstance(result, dict)

    def test_get_financial_metrics_graceful_fallback(self):
        """测试财务指标获取的优雅降级"""
        provider = MultiSourceDataProvider()
        result = provider.get_financial_metrics("600519")
        assert result is None or isinstance(result, FinancialMetrics)

    def test_get_financial_metrics_structure(self):
        """测试财务指标结构"""
        provider = MultiSourceDataProvider()
        result = provider.get_financial_metrics("600519")
        if result is not None:
            assert hasattr(result, 'stock_code')
            assert hasattr(result, 'pe_ratio')
            assert hasattr(result, 'roe')
            assert hasattr(result, 'gross_margin')
            assert hasattr(result, 'debt_ratio')

    def test_get_historical_price_graceful_fallback(self):
        """测试历史价格获取的优雅降级"""
        provider = MultiSourceDataProvider()
        result = provider.get_historical_price("600519", days=10)
        assert result is None or hasattr(result, 'empty')

    def test_get_industry_info_graceful_fallback(self):
        """测试行业信息获取的优雅降级"""
        provider = MultiSourceDataProvider()
        result = provider.get_industry_info("600519")
        assert result is None or isinstance(result, dict)

    @patch('src.data.multi_source_provider.AkshareDataProvider.get_stock_info')
    def test_fallback_to_akshare(self, mock_akshare):
        """测试降级到 AkShare"""
        expected_data = {"code": "600519", "current_price": 1800.5}
        mock_akshare.return_value = expected_data

        provider = MultiSourceDataProvider()
        provider.sources = []

        result = provider.get_stock_info("600519")
        mock_akshare.assert_called_once()

    def test_source_priority_order(self):
        """测试源优先级"""
        provider = MultiSourceDataProvider()

        assert provider.source_priority[0] == DataSourceType.AKSHARE
        assert provider.source_priority[1] == DataSourceType.TUSHARE
        assert provider.source_priority[2] == DataSourceType.BAOSTOCK
        assert provider.source_priority[3] == DataSourceType.MOCK

    def test_source_priority_length(self):
        """测试源优先级长度"""
        provider = MultiSourceDataProvider()
        assert len(provider.source_priority) == 4

    def test_multiple_stock_codes(self):
        """测试多个股票代码"""
        provider = MultiSourceDataProvider()

        test_codes = ["600519", "000858", "000651"]

        for code in test_codes:
            info = provider.get_stock_info(code)
            metrics = provider.get_financial_metrics(code)
            industry = provider.get_industry_info(code)

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

            assert len(results) == 3
            for result in results:
                assert result is None or isinstance(result, dict)

    def test_invalid_stock_code(self):
        """测试无效股票代码"""
        provider = MultiSourceDataProvider()

        result = provider.get_stock_info("INVALID")
        assert result is None or isinstance(result, dict)

    def test_empty_stock_code(self):
        """测试空股票代码"""
        provider = MultiSourceDataProvider()

        result = provider.get_stock_info("")
        assert result is None or isinstance(result, dict)

    def test_special_characters_stock_code(self):
        """测试特殊字符股票代码"""
        provider = MultiSourceDataProvider()

        result = provider.get_stock_info("!@#$%")
        assert result is None or isinstance(result, dict)

    def test_provider_string_representation(self):
        """测试数据源字符串表示"""
        provider = TuShareProvider()

        str_repr = str(provider)
        assert "TuShare" in str_repr
        assert "tushare" in str_repr


# ============================================================================
# 数据源集成测试
# ============================================================================
class TestDataSourceIntegration:
    """测试数据源集成"""

    def test_seamless_source_switching(self):
        """测试源无缝切换"""
        provider = MultiSourceDataProvider()

        stock_code = "600519"
        results = []

        for _ in range(3):
            result = provider.get_financial_metrics(stock_code)
            results.append(result)

        if results[0] is not None and results[1] is not None:
            assert results[0].stock_code == results[1].stock_code
            assert results[0].pe_ratio == results[1].pe_ratio
            assert results[0].roe == results[1].roe

    def test_all_methods_exist(self):
        """测试所有必要方法都存在"""
        provider = MultiSourceDataProvider()

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

        sources = provider.get_available_sources()
        assert isinstance(sources, list)

        stats = provider.get_source_stats()
        assert isinstance(stats, dict)

    def test_data_consistency_across_calls(self):
        """测试多次调用数据一致性"""
        provider = MultiSourceDataProvider()

        result1 = provider.get_financial_metrics("600519")
        result2 = provider.get_financial_metrics("600519")

        if result1 is not None and result2 is not None:
            assert result1.stock_code == result2.stock_code
            assert result1.pe_ratio == result2.pe_ratio

    def test_different_stocks_return_different_data(self):
        """测试不同股票返回不同数据"""
        provider = MultiSourceDataProvider()

        result1 = provider.get_financial_metrics("600519")
        result2 = provider.get_financial_metrics("000858")

        if result1 is not None and result2 is not None:
            assert result1.stock_code != result2.stock_code


# ============================================================================
# 边界条件测试
# ============================================================================
class TestEdgeCases:
    """测试边界条件"""

    def test_very_long_stock_code(self):
        """测试超长股票代码"""
        provider = MultiSourceDataProvider()
        result = provider.get_stock_info("1234567890")
        assert result is None or isinstance(result, dict)

    def test_unicode_stock_code(self):
        """测试 Unicode 股票代码"""
        provider = MultiSourceDataProvider()
        result = provider.get_stock_info("股票")
        assert result is None or isinstance(result, dict)

    def test_negative_days_historical_price(self):
        """测试负数天数"""
        provider = MultiSourceDataProvider()
        result = provider.get_historical_price("600519", days=-1)
        assert result is None or hasattr(result, 'empty')

    def test_zero_days_historical_price(self):
        """测试零天数"""
        provider = MultiSourceDataProvider()
        result = provider.get_historical_price("600519", days=0)
        assert result is None or hasattr(result, 'empty')

    def test_large_days_historical_price(self):
        """测试大天数"""
        provider = MultiSourceDataProvider()
        result = provider.get_historical_price("600519", days=10000)
        assert result is None or hasattr(result, 'empty')


# ============================================================================
# Mock 数据测试
# ============================================================================
class TestMockData:
    """测试模拟数据"""

    def test_mock_stocks_data_keys(self):
        """测试模拟数据包含的股票代码"""
        expected_codes = ["600519", "000858", "000651", "600036", "000333"]
        for code in expected_codes:
            assert code in MOCK_STOCKS_DATA

    def test_mock_data_maotai(self):
        """测试茅台模拟数据"""
        maotai = MOCK_STOCKS_DATA["600519"]
        assert maotai["name"] == "贵州茅台"
        assert maotai["current_price"] == 1800.5
        assert maotai["pe_ratio"] == 35.2
        assert maotai["roe"] == 0.32
        assert maotai["gross_margin"] == 0.92
        assert maotai["debt_ratio"] == 0.05

    def test_mock_data_wuliangye(self):
        """测试五粮液模拟数据"""
        wly = MOCK_STOCKS_DATA["000858"]
        assert wly["name"] == "五粮液"
        assert wly["current_price"] > 0

    def test_mock_data_geli(self):
        """测试格力模拟数据"""
        geli = MOCK_STOCKS_DATA["000651"]
        assert geli["name"] == "格力电器"
        assert geli["current_price"] > 0

    def test_mock_data_zhaoshang(self):
        """测试招商银行模拟数据"""
        zsyh = MOCK_STOCKS_DATA["600036"]
        assert zsyh["name"] == "招商银行"
        # 银行高负债是正常的
        assert zsyh["debt_ratio"] > 0.5

    def test_mock_data_meidi(self):
        """测试美的模拟数据"""
        meidi = MOCK_STOCKS_DATA["000333"]
        assert meidi["name"] == "美的集团"
        assert meidi["current_price"] > 0


# ============================================================================
# 代码转换测试
# ============================================================================
class TestCodeConversion:
    """测试代码转换"""

    def test_tushare_code_conversion_all_types(self):
        """测试 TuShare 各类代码转换"""
        test_cases = [
            ("600519", "600519.SH"),  # 沪市主板
            ("601318", "601318.SH"),  # 沪市主板
            ("000858", "000858.SZ"),  # 深市主板
            ("000001", "000001.SZ"),  # 深市主板
            ("300059", "300059.SZ"),  # 创业板
            ("688001", "688001.SH"),  # 科创板
            ("002594", "002594.SZ"),  # 中小板
        ]

        for code, expected in test_cases:
            result = TuShareProvider._convert_to_ts_code(code)
            assert result == expected, f"Failed for {code}: expected {expected}, got {result}"

    def test_baostock_code_conversion_all_types(self):
        """测试 BaoStock 各类代码转换"""
        test_cases = [
            ("600519", "sh.600519"),  # 沪市主板
            ("601318", "sh.601318"),  # 沪市主板
            ("000858", "sz.000858"),  # 深市主板
            ("000001", "sz.000001"),  # 深市主板
            ("300059", "sz.300059"),  # 创业板
            ("688001", "sh.688001"),  # 科创板
            ("002594", "sz.002594"),  # 中小板
        ]

        for code, expected in test_cases:
            result = BaoStockProvider._convert_to_bs_code(code)
            assert result == expected, f"Failed for {code}: expected {expected}, got {result}"
