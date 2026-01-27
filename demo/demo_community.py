"""
社区分享演示脚本
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.community import (
    create_community_service,
    CommunityService,
    User,
    SharedContent,
    ShareVisibility,
    ContentType,
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def demo_user_registration():
    """演示 1: 用户注册和登录"""
    print("\n" + "=" * 80)
    print("演示 1: 用户注册和登录")
    print("=" * 80)

    service = create_community_service()

    # 注册用户
    user1 = service.register_user("investor1", "password123", "价值投资者")
    print(f"✓ 用户注册成功: {user1.username} (ID: {user1.user_id})")

    user2 = service.register_user("trader2", "password456", "趋势交易者")
    print(f"✓ 用户注册成功: {user2.username} (ID: {user2.user_id})")

    # 登录
    logged_in = service.login("investor1", "password123")
    if logged_in:
        print(f"✓ 登录成功: {logged_in.nickname}")

    return service


def demo_share_analysis(service: CommunityService):
    """演示 2: 分享分析结果"""
    print("\n" + "=" * 80)
    print("演示 2: 分享分析结果")
    print("=" * 80)

    # 分享分析
    analysis_data = {
        "overall_score": 78.5,
        "signal": "买入",
        "financial_metrics": {
            "pe_ratio": 35.5,
            "pb_ratio": 12.3,
            "roe": 0.32,
        },
        "valuation": {
            "intrinsic_value": 2200,
            "fair_price": 2000,
            "margin_of_safety": 11.11,
        },
        "recommendation": "当前价格具有一定安全边际，建议分批买入",
    }

    share = service.share_analysis(
        title="贵州茅台(600519)深度分析",
        stock_codes=["600519"],
        analysis_data=analysis_data,
        description="基于价值投资理论的全面分析，包含财务指标、估值和护城河评估",
        tags=["白酒", "消费", "价值投资", "长期持有"],
    )

    if share:
        print(f"✓ 分享成功!")
        print(f"  分享ID: {share.share_id}")
        print(f"  标题: {share.title}")
        print(f"  评分: {share.overall_score}")
        print(f"  信号: {share.signal}")
        print(f"  标签: {', '.join(share.tags)}")

    return share


def demo_share_portfolio(service: CommunityService):
    """演示 3: 分享投资组合"""
    print("\n" + "=" * 80)
    print("演示 3: 分享投资组合")
    print("=" * 80)

    portfolio_data = {
        "strategy": "价值成长平衡",
        "total_value": 1000000,
        "positions": [
            {"stock_code": "600519", "name": "贵州茅台", "weight": 0.30, "signal": "买入"},
            {"stock_code": "000858", "name": "五粮液", "weight": 0.20, "signal": "持有"},
            {"stock_code": "000651", "name": "格力电器", "weight": 0.25, "signal": "买入"},
            {"stock_code": "600036", "name": "招商银行", "weight": 0.25, "signal": "买入"},
        ],
        "expected_return": 0.15,
        "risk_level": "中等",
    }

    share = service.share_portfolio(
        title="2026年价值投资组合",
        stock_codes=["600519", "000858", "000651", "600036"],
        portfolio_data=portfolio_data,
        description="精选4只价值股，追求稳健收益",
        tags=["投资组合", "价值投资", "蓝筹股"],
    )

    if share:
        print(f"✓ 组合分享成功!")
        print(f"  分享ID: {share.share_id}")
        print(f"  标题: {share.title}")
        print(f"  股票: {', '.join(share.stock_codes)}")

    return share


def demo_comments_and_likes(service: CommunityService, share: SharedContent):
    """演示 4: 评论和点赞"""
    print("\n" + "=" * 80)
    print("演示 4: 评论和点赞")
    print("=" * 80)

    if not share:
        print("没有分享可以评论")
        return

    # 添加评论
    comment1 = service.add_comment(
        share.share_id,
        "分析很专业，学习了！请问对白酒行业未来怎么看？"
    )
    if comment1:
        print(f"✓ 评论已添加: {comment1.content[:30]}...")

    # 回复评论
    if comment1:
        reply = service.add_comment(
            share.share_id,
            "白酒行业长期看好，消费升级趋势明确",
            parent_id=comment1.comment_id
        )
        if reply:
            print(f"✓ 回复已添加: {reply.content[:30]}...")

    # 点赞
    liked = service.like(share.share_id, "share")
    if liked:
        print(f"✓ 点赞成功")

    # 查看更新后的分享
    updated_share = service.get_share(share.share_id)
    if updated_share:
        print(f"\n分享互动数据:")
        print(f"  浏览量: {updated_share.views_count}")
        print(f"  点赞数: {updated_share.likes_count}")
        print(f"  评论数: {updated_share.comments_count}")


def demo_browse_shares(service: CommunityService):
    """演示 5: 浏览和搜索分享"""
    print("\n" + "=" * 80)
    print("演示 5: 浏览和搜索分享")
    print("=" * 80)

    # 获取公开分享
    shares = service.get_public_shares(limit=10)
    print(f"\n公开分享列表 ({len(shares)} 条):")
    for share in shares:
        print(f"  [{share.content_type.value}] {share.title}")
        print(f"    👍 {share.likes_count}  💬 {share.comments_count}  👁 {share.views_count}")

    # 搜索
    results = service.search_shares("茅台")
    print(f"\n搜索 '茅台' 结果 ({len(results)} 条):")
    for share in results:
        print(f"  {share.title}")

    # 热门分享
    trending = service.get_trending_shares(limit=5)
    print(f"\n热门分享 ({len(trending)} 条):")
    for share in trending:
        print(f"  {share.title} (热度分: {share.likes_count*3 + share.comments_count*2 + share.views_count})")


def demo_community_stats(service: CommunityService):
    """演示 6: 社区统计"""
    print("\n" + "=" * 80)
    print("演示 6: 社区统计")
    print("=" * 80)

    stats = service.get_stats()

    print("\n社区统计:")
    print(f"  用户总数: {stats['total_users']}")
    print(f"  分享总数: {stats['total_shares']}")
    print(f"  评论总数: {stats['total_comments']}")
    print(f"  点赞总数: {stats['total_likes']}")


def main():
    """主演示函数"""
    print("\n" + "=" * 80)
    print("VIMaster - 社区分享功能演示")
    print("=" * 80)

    try:
        # 初始化服务并注册用户
        service = demo_user_registration()

        # 分享分析
        analysis_share = demo_share_analysis(service)

        # 分享组合
        portfolio_share = demo_share_portfolio(service)

        # 评论和点赞
        demo_comments_and_likes(service, analysis_share)

        # 浏览和搜索
        demo_browse_shares(service)

        # 统计
        demo_community_stats(service)

        print("\n" + "=" * 80)
        print("演示完成！社区数据保存在 data/community 目录")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"演示失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
