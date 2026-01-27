# 社区分享功能指南

**版本**: v5.0  
**日期**: 2026年1月27日  
**状态**: ✅ 已完成

---

## 📋 概述

VIMaster 现已支持 **社区分享功能**，包括：

- 👥 **用户系统** - 注册、登录、个人资料
- 📝 **分享功能** - 分享分析结果、投资组合
- 💬 **评论系统** - 评论、回复
- 👍 **点赞功能** - 点赞分享和评论
- 🔍 **搜索发现** - 搜索、热门、推荐

---

## 🚀 快速开始

### 基本使用

```python
from src.community import create_community_service

# 创建社区服务
service = create_community_service()

# 注册用户
user = service.register_user("investor1", "password", "价值投资者")

# 登录
service.login("investor1", "password")

# 分享分析结果
share = service.share_analysis(
    title="贵州茅台深度分析",
    stock_codes=["600519"],
    analysis_data={"score": 85, "signal": "买入"},
    tags=["白酒", "价值投资"],
)

print(f"分享成功: {share.share_id}")
```

---

## 🎯 核心功能

### 1️⃣ 用户管理

```python
# 注册
user = service.register_user("username", "password", "昵称")

# 登录
user = service.login("username", "password")

# 获取当前用户
current = service.get_current_user()
```

### 2️⃣ 分享分析

```python
from src.community import ShareVisibility

# 分享分析结果
share = service.share_analysis(
    title="股票分析标题",
    stock_codes=["600519"],
    analysis_data={
        "overall_score": 78.5,
        "signal": "买入",
        "valuation": {"fair_price": 2000},
    },
    description="详细描述...",
    tags=["标签1", "标签2"],
    visibility=ShareVisibility.PUBLIC,  # 公开
)
```

### 3️⃣ 分享投资组合

```python
share = service.share_portfolio(
    title="2026年投资组合",
    stock_codes=["600519", "000858", "000651"],
    portfolio_data={
        "strategy": "价值成长平衡",
        "positions": [
            {"stock_code": "600519", "weight": 0.4},
            {"stock_code": "000858", "weight": 0.3},
        ],
    },
    tags=["投资组合", "蓝筹"],
)
```

### 4️⃣ 评论功能

```python
# 添加评论
comment = service.add_comment(share.share_id, "分析很专业！")

# 回复评论
reply = service.add_comment(
    share.share_id,
    "谢谢支持！",
    parent_id=comment.comment_id
)

# 获取评论列表
comments = service.get_comments(share.share_id)
```

### 5️⃣ 点赞功能

```python
# 点赞分享
service.like(share.share_id, "share")

# 点赞评论
service.like(comment.comment_id, "comment")

# 取消点赞
service.unlike(share.share_id)

# 检查是否已点赞
is_liked = service.is_liked(share.share_id)
```

### 6️⃣ 浏览和搜索

```python
# 获取公开分享
shares = service.get_public_shares(limit=20)

# 获取用户分享
user_shares = service.get_user_shares(user_id)

# 搜索分享
results = service.search_shares("茅台")

# 获取热门分享
trending = service.get_trending_shares(limit=10)
```

---

## 📊 数据结构

### User (用户)

| 字段 | 类型 | 说明 |
|------|------|------|
| `user_id` | str | 用户 ID |
| `username` | str | 用户名 |
| `nickname` | str | 昵称 |
| `avatar_url` | str | 头像 URL |
| `bio` | str | 个人简介 |
| `followers_count` | int | 粉丝数 |
| `shares_count` | int | 分享数 |

### SharedContent (分享内容)

| 字段 | 类型 | 说明 |
|------|------|------|
| `share_id` | str | 分享 ID |
| `user_id` | str | 用户 ID |
| `content_type` | ContentType | 内容类型 |
| `title` | str | 标题 |
| `description` | str | 描述 |
| `content` | dict | 内容数据 |
| `stock_codes` | list | 股票代码 |
| `tags` | list | 标签 |
| `visibility` | ShareVisibility | 可见性 |
| `likes_count` | int | 点赞数 |
| `comments_count` | int | 评论数 |
| `views_count` | int | 浏览数 |

### Comment (评论)

| 字段 | 类型 | 说明 |
|------|------|------|
| `comment_id` | str | 评论 ID |
| `share_id` | str | 分享 ID |
| `user_id` | str | 用户 ID |
| `content` | str | 评论内容 |
| `parent_id` | str | 父评论 ID |
| `likes_count` | int | 点赞数 |

---

## 🔧 API 参考

### CommunityService

```python
class CommunityService:
    # 用户管理
    def register_user(username, password, nickname="") -> User
    def login(username, password) -> Optional[User]
    def get_current_user() -> Optional[User]
    
    # 分享
    def share_analysis(title, stock_codes, analysis_data, ...) -> SharedContent
    def share_portfolio(title, stock_codes, portfolio_data, ...) -> SharedContent
    def get_share(share_id) -> Optional[SharedContent]
    def delete_share(share_id) -> bool
    
    # 浏览
    def get_public_shares(limit=50) -> List[SharedContent]
    def get_user_shares(user_id) -> List[SharedContent]
    def search_shares(keyword) -> List[SharedContent]
    def get_trending_shares(limit=10) -> List[SharedContent]
    
    # 评论
    def add_comment(share_id, content, parent_id=None) -> Comment
    def get_comments(share_id) -> List[Comment]
    
    # 点赞
    def like(target_id, target_type="share") -> bool
    def unlike(target_id) -> bool
    def is_liked(target_id) -> bool
    
    # 统计
    def get_stats() -> Dict
```

---

## 🎯 使用场景

### 场景 1: 分享分析报告

```python
# 分析股票
context = app.manager.analyze_single_stock("600519")

# 分享到社区
share = community.share_analysis(
    title=f"{context.stock_code} 分析报告",
    stock_codes=[context.stock_code],
    analysis_data={
        "overall_score": context.overall_score,
        "signal": context.final_signal.value,
        "valuation": context.valuation.__dict__ if context.valuation else {},
    },
)
```

### 场景 2: 讨论股票

```python
# 搜索相关分享
shares = community.search_shares("600519")

# 参与讨论
for share in shares:
    community.add_comment(share.share_id, "我也看好这只股票！")
```

### 场景 3: 发现热门分析

```python
# 获取热门分享
trending = community.get_trending_shares(limit=10)

for share in trending:
    print(f"📊 {share.title}")
    print(f"   👍 {share.likes_count} 💬 {share.comments_count}")
```

---

## 📂 文件清单

| 文件 | 说明 |
|------|------|
| `src/community/community_service.py` | 核心实现 (500+ 行) |
| `src/community/__init__.py` | 包导出 |
| `demo/demo_community.py` | 演示脚本 |
| `tests/unit/test_community.py` | 单元测试 |

---

## 📁 数据存储

社区数据存储在 `data/community` 目录：

```
data/community/
├── users/          # 用户数据
├── shares/         # 分享数据
├── comments/       # 评论数据
├── likes/          # 点赞数据
└── follows/        # 关注数据
```

---

## 🔒 可见性说明

| 可见性 | 说明 |
|--------|------|
| `PUBLIC` | 所有人可见 |
| `PRIVATE` | 仅自己可见 |
| `FRIENDS` | 仅好友可见 |

---

**项目状态**: 🟢 **已完成**  
**版本**: v5.0
