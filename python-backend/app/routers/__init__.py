"""API 路由"""

from app.routers.user import router as user_router
from app.routers.health import router as health_router
from app.routers.article import router as article_router

__all__ = ["user_router", "health_router", "article_router"]
