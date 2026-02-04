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
]
