"""健康检查路由"""

from fastapi import APIRouter
from app.schemas.common import BaseResponse

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("", response_model=BaseResponse[str])
async def health_check():
    """健康检查"""
    return BaseResponse.success(data="ok", message="服务正常")
