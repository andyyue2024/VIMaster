"""
社区分享模块 - 支持分析结果分享、评论、点赞等社交功能
"""
import logging
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class ShareVisibility(Enum):
    """分享可见性"""
    PUBLIC = "public"       # 公开
    PRIVATE = "private"     # 私有
    FRIENDS = "friends"     # 仅好友可见


class ContentType(Enum):
    """内容类型"""
    ANALYSIS = "analysis"       # 分析报告
    PORTFOLIO = "portfolio"     # 投资组合
    STRATEGY = "strategy"       # 投资策略
    COMMENT = "comment"         # 评论
    ARTICLE = "article"         # 文章


@dataclass
class User:
    """用户"""
    user_id: str
    username: str
    nickname: str = ""
    avatar_url: str = ""
    bio: str = ""
    created_at: str = ""
    followers_count: int = 0
    following_count: int = 0
    shares_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":
        return User(**{k: v for k, v in data.items() if hasattr(User, k)})


@dataclass
class SharedContent:
    """分享内容"""
    share_id: str
    user_id: str
    content_type: ContentType
    title: str
    description: str = ""
    content: Dict[str, Any] = field(default_factory=dict)

    # 股票相关
    stock_codes: List[str] = field(default_factory=list)

    # 分析数据
    overall_score: Optional[float] = None
    signal: str = ""

    # 元数据
    visibility: ShareVisibility = ShareVisibility.PUBLIC
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    # 互动数据
    likes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    shares_count: int = 0

    # 附件
    attachments: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["content_type"] = self.content_type.value
        data["visibility"] = self.visibility.value
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SharedContent":
        data = data.copy()
        if "content_type" in data:
            data["content_type"] = ContentType(data["content_type"])
        if "visibility" in data:
            data["visibility"] = ShareVisibility(data["visibility"])
        return SharedContent(**{k: v for k, v in data.items() if hasattr(SharedContent, k)})


@dataclass
class Comment:
    """评论"""
    comment_id: str
    share_id: str
    user_id: str
    content: str
    parent_id: Optional[str] = None  # 回复的评论 ID
    created_at: str = ""
    likes_count: int = 0
    replies_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Comment":
        return Comment(**{k: v for k, v in data.items() if hasattr(Comment, k)})


@dataclass
class Like:
    """点赞"""
    like_id: str
    user_id: str
    target_id: str  # 分享或评论的 ID
    target_type: str  # "share" or "comment"
    created_at: str = ""


class CommunityStorage:
    """社区数据存储（基于文件系统）"""

    def __init__(self, data_dir: str = "data/community"):
        self.data_dir = data_dir
        self._lock = threading.Lock()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """确保目录存在"""
        dirs = ["users", "shares", "comments", "likes", "follows"]
        for d in dirs:
            os.makedirs(os.path.join(self.data_dir, d), exist_ok=True)

    def _get_path(self, category: str, item_id: str) -> str:
        return os.path.join(self.data_dir, category, f"{item_id}.json")

    def _save_json(self, path: str, data: Dict) -> None:
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json(self, path: str) -> Optional[Dict]:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _list_items(self, category: str) -> List[str]:
        dir_path = os.path.join(self.data_dir, category)
        if not os.path.exists(dir_path):
            return []
        return [f[:-5] for f in os.listdir(dir_path) if f.endswith(".json")]

    # 用户操作
    def save_user(self, user: User) -> None:
        self._save_json(self._get_path("users", user.user_id), user.to_dict())

    def get_user(self, user_id: str) -> Optional[User]:
        data = self._load_json(self._get_path("users", user_id))
        return User.from_dict(data) if data else None

    # 分享操作
    def save_share(self, share: SharedContent) -> None:
        self._save_json(self._get_path("shares", share.share_id), share.to_dict())

    def get_share(self, share_id: str) -> Optional[SharedContent]:
        data = self._load_json(self._get_path("shares", share_id))
        return SharedContent.from_dict(data) if data else None

    def delete_share(self, share_id: str) -> bool:
        path = self._get_path("shares", share_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def list_shares(self, limit: int = 50) -> List[SharedContent]:
        share_ids = self._list_items("shares")
        shares = []
        for sid in share_ids[:limit]:
            share = self.get_share(sid)
            if share:
                shares.append(share)
        return sorted(shares, key=lambda s: s.created_at, reverse=True)

    # 评论操作
    def save_comment(self, comment: Comment) -> None:
        self._save_json(self._get_path("comments", comment.comment_id), comment.to_dict())

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        data = self._load_json(self._get_path("comments", comment_id))
        return Comment.from_dict(data) if data else None

    def get_share_comments(self, share_id: str) -> List[Comment]:
        comment_ids = self._list_items("comments")
        comments = []
        for cid in comment_ids:
            comment = self.get_comment(cid)
            if comment and comment.share_id == share_id:
                comments.append(comment)
        return sorted(comments, key=lambda c: c.created_at)

    # 点赞操作
    def save_like(self, like: Like) -> None:
        self._save_json(self._get_path("likes", like.like_id), asdict(like))

    def get_like(self, user_id: str, target_id: str) -> Optional[Like]:
        like_id = f"{user_id}_{target_id}"
        data = self._load_json(self._get_path("likes", like_id))
        if data:
            return Like(**data)
        return None

    def delete_like(self, like_id: str) -> bool:
        path = self._get_path("likes", like_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False


class CommunityService:
    """社区服务"""

    def __init__(self, storage: Optional[CommunityStorage] = None):
        self.storage = storage or CommunityStorage()
        self._current_user: Optional[User] = None

    def register_user(self, username: str, password: str, nickname: str = "") -> User:
        """注册用户"""
        user_id = str(uuid.uuid4())[:8]
        user = User(
            user_id=user_id,
            username=username,
            nickname=nickname or username,
            created_at=datetime.now().isoformat(),
        )
        self.storage.save_user(user)
        logger.info(f"用户注册成功: {username}")
        return user

    def login(self, username: str, password: str) -> Optional[User]:
        """登录（简化版，实际应验证密码）"""
        # 简化：通过用户名查找
        for uid in self.storage._list_items("users"):
            user = self.storage.get_user(uid)
            if user and user.username == username:
                self._current_user = user
                logger.info(f"用户登录: {username}")
                return user
        return None

    def get_current_user(self) -> Optional[User]:
        """获取当前用户"""
        return self._current_user

    def set_current_user(self, user: User) -> None:
        """设置当前用户"""
        self._current_user = user

    def share_analysis(
        self,
        title: str,
        stock_codes: List[str],
        analysis_data: Dict[str, Any],
        description: str = "",
        tags: List[str] = None,
        visibility: ShareVisibility = ShareVisibility.PUBLIC,
    ) -> Optional[SharedContent]:
        """分享分析结果"""
        if not self._current_user:
            logger.warning("未登录，无法分享")
            return None

        share = SharedContent(
            share_id=str(uuid.uuid4())[:12],
            user_id=self._current_user.user_id,
            content_type=ContentType.ANALYSIS,
            title=title,
            description=description,
            content=analysis_data,
            stock_codes=stock_codes,
            overall_score=analysis_data.get("overall_score"),
            signal=analysis_data.get("signal", ""),
            visibility=visibility,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        self.storage.save_share(share)

        # 更新用户分享数
        self._current_user.shares_count += 1
        self.storage.save_user(self._current_user)

        logger.info(f"分析已分享: {title}")
        return share

    def share_portfolio(
        self,
        title: str,
        stock_codes: List[str],
        portfolio_data: Dict[str, Any],
        description: str = "",
        tags: List[str] = None,
    ) -> Optional[SharedContent]:
        """分享投资组合"""
        if not self._current_user:
            return None

        share = SharedContent(
            share_id=str(uuid.uuid4())[:12],
            user_id=self._current_user.user_id,
            content_type=ContentType.PORTFOLIO,
            title=title,
            description=description,
            content=portfolio_data,
            stock_codes=stock_codes,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        self.storage.save_share(share)
        logger.info(f"组合已分享: {title}")
        return share

    def get_share(self, share_id: str) -> Optional[SharedContent]:
        """获取分享详情"""
        share = self.storage.get_share(share_id)
        if share:
            # 增加浏览量
            share.views_count += 1
            self.storage.save_share(share)
        return share

    def get_public_shares(self, limit: int = 50, content_type: Optional[ContentType] = None) -> List[SharedContent]:
        """获取公开分享列表"""
        shares = self.storage.list_shares(limit * 2)  # 多取一些，过滤后可能不够
        public_shares = [s for s in shares if s.visibility == ShareVisibility.PUBLIC]

        if content_type:
            public_shares = [s for s in public_shares if s.content_type == content_type]

        return public_shares[:limit]

    def get_user_shares(self, user_id: str) -> List[SharedContent]:
        """获取用户的分享"""
        shares = self.storage.list_shares(100)
        return [s for s in shares if s.user_id == user_id]

    def delete_share(self, share_id: str) -> bool:
        """删除分享"""
        share = self.storage.get_share(share_id)
        if not share:
            return False

        if self._current_user and share.user_id != self._current_user.user_id:
            logger.warning("无权删除他人分享")
            return False

        return self.storage.delete_share(share_id)

    def add_comment(self, share_id: str, content: str, parent_id: Optional[str] = None) -> Optional[Comment]:
        """添加评论"""
        if not self._current_user:
            return None

        share = self.storage.get_share(share_id)
        if not share:
            return None

        comment = Comment(
            comment_id=str(uuid.uuid4())[:12],
            share_id=share_id,
            user_id=self._current_user.user_id,
            content=content,
            parent_id=parent_id,
            created_at=datetime.now().isoformat(),
        )

        self.storage.save_comment(comment)

        # 更新分享评论数
        share.comments_count += 1
        self.storage.save_share(share)

        # 如果是回复，更新父评论回复数
        if parent_id:
            parent = self.storage.get_comment(parent_id)
            if parent:
                parent.replies_count += 1
                self.storage.save_comment(parent)

        logger.info(f"评论已添加: {share_id}")
        return comment

    def get_comments(self, share_id: str) -> List[Comment]:
        """获取分享的评论"""
        return self.storage.get_share_comments(share_id)

    def like(self, target_id: str, target_type: str = "share") -> bool:
        """点赞"""
        if not self._current_user:
            return False

        # 检查是否已点赞
        existing = self.storage.get_like(self._current_user.user_id, target_id)
        if existing:
            return False

        like = Like(
            like_id=f"{self._current_user.user_id}_{target_id}",
            user_id=self._current_user.user_id,
            target_id=target_id,
            target_type=target_type,
            created_at=datetime.now().isoformat(),
        )

        self.storage.save_like(like)

        # 更新点赞数
        if target_type == "share":
            share = self.storage.get_share(target_id)
            if share:
                share.likes_count += 1
                self.storage.save_share(share)
        elif target_type == "comment":
            comment = self.storage.get_comment(target_id)
            if comment:
                comment.likes_count += 1
                self.storage.save_comment(comment)

        return True

    def unlike(self, target_id: str) -> bool:
        """取消点赞"""
        if not self._current_user:
            return False

        like_id = f"{self._current_user.user_id}_{target_id}"
        like_data = self.storage._load_json(self.storage._get_path("likes", like_id))

        if not like_data:
            return False

        target_type = like_data.get("target_type", "share")
        self.storage.delete_like(like_id)

        # 更新点赞数
        if target_type == "share":
            share = self.storage.get_share(target_id)
            if share and share.likes_count > 0:
                share.likes_count -= 1
                self.storage.save_share(share)

        return True

    def is_liked(self, target_id: str) -> bool:
        """检查是否已点赞"""
        if not self._current_user:
            return False
        return self.storage.get_like(self._current_user.user_id, target_id) is not None

    def search_shares(self, keyword: str, limit: int = 20) -> List[SharedContent]:
        """搜索分享"""
        shares = self.get_public_shares(limit=100)
        results = []

        keyword_lower = keyword.lower()
        for share in shares:
            if (keyword_lower in share.title.lower() or
                keyword_lower in share.description.lower() or
                any(keyword_lower in tag.lower() for tag in share.tags) or
                any(keyword_lower in code.lower() for code in share.stock_codes)):
                results.append(share)

        return results[:limit]

    def get_trending_shares(self, limit: int = 10) -> List[SharedContent]:
        """获取热门分享"""
        shares = self.get_public_shares(limit=100)

        # 按互动量排序
        def score(s):
            return s.likes_count * 3 + s.comments_count * 2 + s.views_count

        return sorted(shares, key=score, reverse=True)[:limit]

    def get_stats(self) -> Dict[str, int]:
        """获取社区统计"""
        return {
            "total_users": len(self.storage._list_items("users")),
            "total_shares": len(self.storage._list_items("shares")),
            "total_comments": len(self.storage._list_items("comments")),
            "total_likes": len(self.storage._list_items("likes")),
        }


# 便捷函数
def create_community_service(data_dir: str = "data/community") -> CommunityService:
    """创建社区服务"""
    storage = CommunityStorage(data_dir)
    return CommunityService(storage)
