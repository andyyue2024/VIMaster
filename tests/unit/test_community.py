"""
社区功能单元测试
"""
import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.community import (
    User,
    SharedContent,
    Comment,
    ShareVisibility,
    ContentType,
    CommunityStorage,
    CommunityService,
    create_community_service,
)


class TestUser:
    """用户测试"""

    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            user_id="test123",
            username="testuser",
            nickname="测试用户",
        )

        assert user.user_id == "test123"
        assert user.username == "testuser"
        assert user.nickname == "测试用户"

    def test_user_to_dict(self):
        """测试转换为字典"""
        user = User(user_id="test123", username="testuser")
        data = user.to_dict()

        assert data["user_id"] == "test123"
        assert data["username"] == "testuser"

    def test_user_from_dict(self):
        """测试从字典创建"""
        data = {"user_id": "abc", "username": "john", "nickname": "约翰"}
        user = User.from_dict(data)

        assert user.user_id == "abc"
        assert user.nickname == "约翰"


class TestSharedContent:
    """分享内容测试"""

    def test_shared_content_creation(self):
        """测试分享内容创建"""
        share = SharedContent(
            share_id="share123",
            user_id="user1",
            content_type=ContentType.ANALYSIS,
            title="测试分享",
            stock_codes=["600519"],
        )

        assert share.share_id == "share123"
        assert share.content_type == ContentType.ANALYSIS
        assert "600519" in share.stock_codes

    def test_shared_content_to_dict(self):
        """测试转换为字典"""
        share = SharedContent(
            share_id="share123",
            user_id="user1",
            content_type=ContentType.PORTFOLIO,
            title="组合分享",
            visibility=ShareVisibility.PUBLIC,
        )

        data = share.to_dict()

        assert data["content_type"] == "portfolio"
        assert data["visibility"] == "public"

    def test_shared_content_from_dict(self):
        """测试从字典创建"""
        data = {
            "share_id": "abc",
            "user_id": "user1",
            "content_type": "analysis",
            "title": "测试",
            "visibility": "friends",
        }

        share = SharedContent.from_dict(data)

        assert share.share_id == "abc"
        assert share.content_type == ContentType.ANALYSIS
        assert share.visibility == ShareVisibility.FRIENDS


class TestComment:
    """评论测试"""

    def test_comment_creation(self):
        """测试评论创建"""
        comment = Comment(
            comment_id="c123",
            share_id="s123",
            user_id="u123",
            content="很好的分析！",
        )

        assert comment.comment_id == "c123"
        assert comment.content == "很好的分析！"

    def test_reply_comment(self):
        """测试回复评论"""
        reply = Comment(
            comment_id="c456",
            share_id="s123",
            user_id="u456",
            content="同意！",
            parent_id="c123",
        )

        assert reply.parent_id == "c123"


class TestCommunityStorage:
    """社区存储测试"""

    def test_save_and_get_user(self):
        """测试保存和获取用户"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = CommunityStorage(tmpdir)

            user = User(user_id="u1", username="test", nickname="测试")
            storage.save_user(user)

            loaded = storage.get_user("u1")

            assert loaded is not None
            assert loaded.username == "test"

    def test_save_and_get_share(self):
        """测试保存和获取分享"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = CommunityStorage(tmpdir)

            share = SharedContent(
                share_id="s1",
                user_id="u1",
                content_type=ContentType.ANALYSIS,
                title="测试分享",
            )
            storage.save_share(share)

            loaded = storage.get_share("s1")

            assert loaded is not None
            assert loaded.title == "测试分享"

    def test_delete_share(self):
        """测试删除分享"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = CommunityStorage(tmpdir)

            share = SharedContent(
                share_id="s1",
                user_id="u1",
                content_type=ContentType.ANALYSIS,
                title="测试",
            )
            storage.save_share(share)

            result = storage.delete_share("s1")

            assert result is True
            assert storage.get_share("s1") is None


class TestCommunityService:
    """社区服务测试"""

    def test_register_user(self):
        """测试注册用户"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            user = service.register_user("testuser", "password", "测试用户")

            assert user is not None
            assert user.username == "testuser"

    def test_login(self):
        """测试登录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            service.register_user("testuser", "password")
            logged_in = service.login("testuser", "password")

            assert logged_in is not None
            assert service.get_current_user() is not None

    def test_share_analysis(self):
        """测试分享分析"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            user = service.register_user("testuser", "password")
            service.set_current_user(user)

            share = service.share_analysis(
                title="测试分析",
                stock_codes=["600519"],
                analysis_data={"score": 80},
            )

            assert share is not None
            assert share.title == "测试分析"

    def test_add_comment(self):
        """测试添加评论"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            user = service.register_user("testuser", "password")
            service.set_current_user(user)

            share = service.share_analysis("测试", ["600519"], {})
            comment = service.add_comment(share.share_id, "好评论！")

            assert comment is not None
            assert comment.content == "好评论！"

    def test_like_and_unlike(self):
        """测试点赞和取消点赞"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            user = service.register_user("testuser", "password")
            service.set_current_user(user)

            share = service.share_analysis("测试", ["600519"], {})

            # 点赞
            result = service.like(share.share_id)
            assert result is True
            assert service.is_liked(share.share_id) is True

            # 取消点赞
            result = service.unlike(share.share_id)
            assert result is True
            assert service.is_liked(share.share_id) is False

    def test_search_shares(self):
        """测试搜索分享"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            user = service.register_user("testuser", "password")
            service.set_current_user(user)

            service.share_analysis("贵州茅台分析", ["600519"], {})
            service.share_analysis("五粮液分析", ["000858"], {})

            results = service.search_shares("茅台")

            assert len(results) == 1
            assert "茅台" in results[0].title

    def test_get_stats(self):
        """测试获取统计"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = CommunityService(CommunityStorage(tmpdir))

            user = service.register_user("testuser", "password")
            service.set_current_user(user)
            service.share_analysis("测试", ["600519"], {})

            stats = service.get_stats()

            assert stats["total_users"] == 1
            assert stats["total_shares"] == 1
