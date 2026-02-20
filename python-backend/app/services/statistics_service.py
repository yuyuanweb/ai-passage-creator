"""系统统计服务"""

import json
import logging
from datetime import datetime, time, timedelta
from typing import Optional

from databases import Database

from app.constants.user import UserConstant
from app.schemas.statistics import StatisticsVO
from app.utils.session import redis_client

logger = logging.getLogger(__name__)

STATISTICS_CACHE_KEY = "statistics:overview"
STATISTICS_CACHE_TTL_SECONDS = 3600


class StatisticsService:
    """系统统计服务"""

    def __init__(self, db: Database):
        self.db = db

    async def get_statistics(self) -> StatisticsVO:
        """获取系统统计（带 Redis 缓存）"""
        cached = await self._get_cached_statistics()
        if cached is not None:
            logger.info("从缓存获取统计数据")
            return cached

        now = datetime.now()
        today_start = self._get_today_start(now)
        week_start = self._get_week_start(now)
        month_start = self._get_month_start(now)

        today_count = await self._count_articles_by_range(today_start, now)
        week_count = await self._count_articles_by_range(week_start, now)
        month_count = await self._count_articles_by_range(month_start, now)
        total_count = await self._count_total_articles()
        success_rate = await self._calculate_success_rate(total_count)
        avg_duration_ms = await self._calculate_avg_duration()
        active_user_count = await self._count_active_users(week_start, now)
        total_user_count = await self._count_total_users()
        vip_user_count = await self._count_vip_users()
        quota_used = await self._calculate_quota_used()

        stats = StatisticsVO(
            todayCount=today_count,
            weekCount=week_count,
            monthCount=month_count,
            totalCount=total_count,
            successRate=success_rate,
            avgDurationMs=avg_duration_ms,
            activeUserCount=active_user_count,
            totalUserCount=total_user_count,
            vipUserCount=vip_user_count,
            quotaUsed=quota_used,
        )

        await self._set_cached_statistics(stats)
        return stats

    async def _count_articles_by_range(self, start: datetime, end: datetime) -> int:
        value = await self.db.fetch_val(
            query="""
                SELECT COUNT(1)
                FROM article
                WHERE isDelete = 0
                  AND createTime >= :startTime
                  AND createTime <= :endTime
            """,
            values={"startTime": start, "endTime": end},
        )
        return int(value or 0)

    async def _count_total_articles(self) -> int:
        value = await self.db.fetch_val(
            query="SELECT COUNT(1) FROM article WHERE isDelete = 0",
        )
        return int(value or 0)

    async def _calculate_success_rate(self, total_count: int) -> float:
        if total_count <= 0:
            return 0.0
        success_count = await self.db.fetch_val(
            query="""
                SELECT COUNT(1)
                FROM article
                WHERE isDelete = 0
                  AND status = :status
            """,
            values={"status": "COMPLETED"},
        )
        return (float(success_count or 0) / float(total_count)) * 100

    async def _calculate_avg_duration(self) -> int:
        value = await self.db.fetch_val(
            query="""
                SELECT AVG(TIMESTAMPDIFF(MICROSECOND, createTime, completedTime) / 1000)
                FROM article
                WHERE isDelete = 0
                  AND status = :status
                  AND completedTime IS NOT NULL
            """,
            values={"status": "COMPLETED"},
        )
        if value is None:
            return 0
        return int(float(value))

    async def _count_active_users(self, start: datetime, end: datetime) -> int:
        value = await self.db.fetch_val(
            query="""
                SELECT COUNT(DISTINCT userId)
                FROM article
                WHERE isDelete = 0
                  AND createTime >= :startTime
                  AND createTime <= :endTime
            """,
            values={"startTime": start, "endTime": end},
        )
        return int(value or 0)

    async def _count_total_users(self) -> int:
        value = await self.db.fetch_val("SELECT COUNT(1) FROM user WHERE isDelete = 0")
        return int(value or 0)

    async def _count_vip_users(self) -> int:
        value = await self.db.fetch_val(
            query="""
                SELECT COUNT(1)
                FROM user
                WHERE isDelete = 0
                  AND userRole = :vipRole
            """,
            values={"vipRole": UserConstant.VIP_ROLE},
        )
        return int(value or 0)

    async def _calculate_quota_used(self) -> int:
        row = await self.db.fetch_one(
            query="""
                SELECT
                    COUNT(1) AS normalUserCount,
                    COALESCE(SUM(quota), 0) AS remainingQuota
                FROM user
                WHERE isDelete = 0
                  AND userRole = :defaultRole
            """,
            values={"defaultRole": UserConstant.DEFAULT_ROLE},
        )
        if not row:
            return 0
        normal_user_count = int(row["normalUserCount"] or 0)
        remaining_quota = int(row["remainingQuota"] or 0)
        total_default_quota = normal_user_count * UserConstant.DEFAULT_QUOTA
        return total_default_quota - remaining_quota

    async def _get_cached_statistics(self) -> Optional[StatisticsVO]:
        if redis_client is None:
            return None
        try:
            cached = await redis_client.get(STATISTICS_CACHE_KEY)
            if not cached:
                return None
            return StatisticsVO(**json.loads(cached))
        except Exception:
            logger.exception("读取统计缓存失败")
            return None

    async def _set_cached_statistics(self, stats: StatisticsVO):
        if redis_client is None:
            return
        try:
            await redis_client.setex(
                STATISTICS_CACHE_KEY,
                STATISTICS_CACHE_TTL_SECONDS,
                json.dumps(stats.model_dump(by_alias=True), ensure_ascii=False),
            )
            logger.info("统计数据已缓存, ttlSeconds=%s", STATISTICS_CACHE_TTL_SECONDS)
        except Exception:
            logger.exception("写入统计缓存失败")

    @staticmethod
    def _get_today_start(now: datetime) -> datetime:
        return datetime.combine(now.date(), time.min)

    @staticmethod
    def _get_week_start(now: datetime) -> datetime:
        monday = now.date() - timedelta(days=now.weekday())
        return datetime.combine(monday, time.min)

    @staticmethod
    def _get_month_start(now: datetime) -> datetime:
        return datetime(now.year, now.month, 1)
