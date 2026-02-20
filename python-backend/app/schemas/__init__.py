"""Pydantic 请求/响应模型"""

from app.schemas.common import BaseResponse, PageRequest, DeleteRequest
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserAddRequest,
    UserUpdateRequest,
    UserQueryRequest,
    UserVO,
    LoginUserVO
)
from app.schemas.article import (
    ArticleCreateRequest,
    ArticleQueryRequest,
    ArticleVO,
    ArticleState,
    TitleResult,
    OutlineSection,
    OutlineResult,
    ImageRequirement,
    ImageResult,
    Agent4Result
)
from app.schemas.statistics import AgentLogVO, AgentExecutionStatsVO, StatisticsVO

__all__ = [
    "BaseResponse",
    "PageRequest",
    "DeleteRequest",
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserAddRequest",
    "UserUpdateRequest",
    "UserQueryRequest",
    "UserVO",
    "LoginUserVO",
    "ArticleCreateRequest",
    "ArticleQueryRequest",
    "ArticleVO",
    "ArticleState",
    "TitleResult",
    "OutlineSection",
    "OutlineResult",
    "ImageRequirement",
    "ImageResult",
    "Agent4Result",
    "AgentLogVO",
    "AgentExecutionStatsVO",
    "StatisticsVO",
]
