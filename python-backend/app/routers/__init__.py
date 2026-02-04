"""API 路由"""

from app.routers.user import router as user_router
from app.routers.health import router as health_router

__all__ = ["user_router", "health_router"]
