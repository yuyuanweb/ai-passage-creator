"""依赖注入"""

import uuid
from typing import Optional
from fastapi import Cookie, Depends, HTTPException, status

from app.exceptions import ErrorCode, BusinessException
from app.schemas.user import LoginUserVO
from app.utils.session import get_session


async def get_session_id(session_id: Optional[str] = Cookie(None, alias="SESSION")) -> Optional[str]:
    """从 Cookie 中获取 Session ID"""
    return session_id


async def get_current_user(
    session_id: Optional[str] = Depends(get_session_id)
) -> Optional[LoginUserVO]:
    """获取当前登录用户（可选）"""
    if not session_id:
        return None
    
    session_data = await get_session(session_id)
    if not session_data or "user" not in session_data:
        return None
    
    user_data = session_data["user"]
    return LoginUserVO(**user_data)


async def require_login(
    current_user: Optional[LoginUserVO] = Depends(get_current_user)
) -> LoginUserVO:
    """要求必须登录"""
    if not current_user:
        raise BusinessException(ErrorCode.NOT_LOGIN_ERROR)
    return current_user


async def require_admin(
    current_user: LoginUserVO = Depends(require_login)
) -> LoginUserVO:
    """要求必须是管理员"""
    if current_user.user_role != "admin":
        raise BusinessException(ErrorCode.NO_AUTH_ERROR)
    return current_user


def generate_session_id() -> str:
    """生成 Session ID"""
    return str(uuid.uuid4())
