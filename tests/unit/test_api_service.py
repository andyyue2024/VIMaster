"""
API 服务单元测试
"""
import sys
from pathlib import Path
import tempfile
import os
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.api import (
    ApiKey,
    ApiKeyManager,
    PlanType,
    PlanConfig,
    PLAN_CONFIGS,
    RateLimiter,
    UsageTracker,
    UsageRecord,
    FLASK_AVAILABLE,
)


class TestApiKey:
    """API 密钥测试"""

    def test_api_key_creation(self):
        """测试密钥创建"""
        key = ApiKey(
            key_id="test123",
            api_key="vk_test",
            secret_key="secret",
            user_id="user1",
            plan=PlanType.BASIC,
        )

        assert key.key_id == "test123"
        assert key.plan == PlanType.BASIC

    def test_api_key_to_dict(self):
        """测试转换为字典"""
        key = ApiKey(
            key_id="test",
            api_key="vk_test",
            secret_key="secret",
            user_id="user1",
        )

        data = key.to_dict()

        assert data["key_id"] == "test"
        assert data["plan"] == "free"

    def test_api_key_from_dict(self):
        """测试从字典创建"""
        data = {
            "key_id": "test",
            "api_key": "vk_test",
            "secret_key": "secret",
            "user_id": "user1",
            "plan": "pro",
        }

        key = ApiKey.from_dict(data)

        assert key.key_id == "test"
        assert key.plan == PlanType.PRO


class TestPlanConfig:
    """计划配置测试"""

    def test_plan_configs(self):
        """测试计划配置"""
        assert PlanType.FREE in PLAN_CONFIGS
        assert PlanType.BASIC in PLAN_CONFIGS
        assert PlanType.PRO in PLAN_CONFIGS
        assert PlanType.ENTERPRISE in PLAN_CONFIGS

    def test_plan_quota(self):
        """测试配额递增"""
        free_quota = PLAN_CONFIGS[PlanType.FREE].daily_quota
        basic_quota = PLAN_CONFIGS[PlanType.BASIC].daily_quota
        pro_quota = PLAN_CONFIGS[PlanType.PRO].daily_quota

        assert free_quota < basic_quota < pro_quota


class TestApiKeyManager:
    """密钥管理器测试"""

    def test_create_key(self):
        """测试创建密钥"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApiKeyManager(data_dir=tmpdir)

            key = manager.create_key("user1", PlanType.BASIC)

            assert key is not None
            assert key.api_key.startswith("vk_")
            assert key.plan == PlanType.BASIC

    def test_get_key(self):
        """测试获取密钥"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApiKeyManager(data_dir=tmpdir)

            created = manager.create_key("user1")
            retrieved = manager.get_key(created.api_key)

            assert retrieved is not None
            assert retrieved.key_id == created.key_id

    def test_validate_key(self):
        """测试验证密钥"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApiKeyManager(data_dir=tmpdir)

            key = manager.create_key("user1")

            valid, message = manager.validate_key(key.api_key)
            assert valid is True

            valid, message = manager.validate_key("invalid_key")
            assert valid is False

    def test_revoke_key(self):
        """测试撤销密钥"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApiKeyManager(data_dir=tmpdir)

            key = manager.create_key("user1")
            manager.revoke_key(key.api_key)

            valid, message = manager.validate_key(key.api_key)
            assert valid is False

    def test_upgrade_plan(self):
        """测试升级计划"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ApiKeyManager(data_dir=tmpdir)

            key = manager.create_key("user1", PlanType.FREE)
            manager.upgrade_plan(key.api_key, PlanType.PRO)

            updated = manager.get_key(key.api_key)
            assert updated.plan == PlanType.PRO


class TestRateLimiter:
    """限流器测试"""

    def test_rate_limit(self):
        """测试限流"""
        limiter = RateLimiter()

        # 前 5 次应该允许
        for i in range(5):
            allowed, remaining = limiter.check_rate_limit("test_key", 5)
            assert allowed is True

        # 第 6 次应该被限制
        allowed, remaining = limiter.check_rate_limit("test_key", 5)
        assert allowed is False


class TestUsageRecord:
    """使用记录测试"""

    def test_usage_record_creation(self):
        """测试使用记录创建"""
        record = UsageRecord(
            record_id="r123",
            key_id="k123",
            endpoint="/api/v1/analyze",
            method="GET",
            timestamp="2026-01-27T10:00:00",
            response_time_ms=100.5,
            status_code=200,
        )

        assert record.record_id == "r123"
        assert record.response_time_ms == 100.5

    def test_usage_record_to_dict(self):
        """测试转换为字典"""
        record = UsageRecord(
            record_id="r123",
            key_id="k123",
            endpoint="/test",
            method="GET",
            timestamp="2026-01-27",
            response_time_ms=50,
            status_code=200,
        )

        data = record.to_dict()

        assert data["record_id"] == "r123"
        assert data["status_code"] == 200


class TestUsageTracker:
    """使用追踪器测试"""

    def test_record_usage(self):
        """测试记录使用"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = UsageTracker(data_dir=tmpdir)

            record = UsageRecord(
                record_id="r1",
                key_id="k1",
                endpoint="/test",
                method="GET",
                timestamp="2026-01-27T10:00:00",
                response_time_ms=100,
                status_code=200,
            )

            tracker.record(record)

            assert len(tracker.records) == 1

    def test_get_usage_stats(self):
        """测试获取统计"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = UsageTracker(data_dir=tmpdir)

            for i in range(5):
                record = UsageRecord(
                    record_id=f"r{i}",
                    key_id="k1",
                    endpoint="/test",
                    method="GET",
                    timestamp="2026-01-27T10:00:00",
                    response_time_ms=100,
                    status_code=200,
                )
                tracker.record(record)

            stats = tracker.get_usage_stats("k1")

            assert stats["total_requests"] == 5
