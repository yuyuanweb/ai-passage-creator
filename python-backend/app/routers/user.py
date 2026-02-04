"""用户路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Response
from databases import Database

from app.database import get_db
from app.schemas.common import BaseResponse, DeleteRequest
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserAddRequest,
    UserUpdateRequest,
    UserQueryRequest,
    UserVO,
    LoginUserVO
)
from app.services.user_service import UserService
from app.deps import get_current_user, require_login, require_admin, generate_session_id
from app.utils.session import set_session, remove_session
from app.config import settings

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.post("/register", response_model=BaseResponse[int])
async def register(
    request: UserRegisterRequest,
    db: Database = Depends(get_db)
):
    """用户注册"""
    service = UserService(db)
    user_id = await service.register(request)
    return BaseResponse.success(data=user_id, message="注册成功")


@router.post("/login", response_model=BaseResponse[LoginUserVO])
async def login(
    request: UserLoginRequest,
    response: Response,
    db: Database = Depends(get_db)
):
    """用户登录"""
    service = UserService(db)
    user = await service.login(request)
    
    # 生成 Session ID
    session_id = generate_session_id()
    
    # 保存到 Redis
    await set_session(session_id, {"user": user.model_dump(by_alias=True)})
    
    # 设置 Cookie
    response.set_cookie(
        key="SESSION",
        value=session_id,
        max_age=settings.session_max_age,
        httponly=True,
        samesite="lax"
    )
    
    return BaseResponse.success(data=user, message="登录成功")


@router.post("/logout", response_model=BaseResponse[bool])
async def logout(
    response: Response,
    current_user: Optional[LoginUserVO] = Depends(get_current_user)
):
    """用户登出"""
    # 删除 Cookie
    response.delete_cookie(key="SESSION")
    
    return BaseResponse.success(data=True, message="登出成功")


@router.get("/get/login", response_model=BaseResponse[LoginUserVO])
async def get_login_user(
    current_user: LoginUserVO = Depends(require_login)
):
    """获取当前登录用户"""
    return BaseResponse.success(data=current_user)


@router.get("/get", response_model=BaseResponse[UserVO])
async def get_user_by_id(
    id: int,
    db: Database = Depends(get_db)
):
    """根据 ID 获取用户"""
    service = UserService(db)
    user = await service.get_by_id(id)
    return BaseResponse.success(data=user)


@router.post("/list/page", response_model=BaseResponse[dict])
async def list_users_by_page(
    request: UserQueryRequest,
    db: Database = Depends(get_db),
    _: LoginUserVO = Depends(require_admin)
):
    """分页查询用户列表（管理员）"""
    service = UserService(db)
    users, total = await service.list_by_page(request)
    
    return BaseResponse.success(data={
        "records": users,
        "total": total,
        "current": request.current,
        "size": request.page_size
    })


@router.post("/add", response_model=BaseResponse[int])
async def add_user(
    request: UserAddRequest,
    db: Database = Depends(get_db),
    _: LoginUserVO = Depends(require_admin)
):
    """添加用户（管理员）"""
    service = UserService(db)
    user_id = await service.add_user(request)
    return BaseResponse.success(data=user_id, message="添加成功")


@router.post("/update", response_model=BaseResponse[bool])
async def update_user(
    request: UserUpdateRequest,
    db: Database = Depends(get_db),
    _: LoginUserVO = Depends(require_admin)
):
    """更新用户（管理员）"""
    service = UserService(db)
    result = await service.update_user(request)
    return BaseResponse.success(data=result, message="更新成功")


@router.post("/delete", response_model=BaseResponse[bool])
async def delete_user(
    request: DeleteRequest,
    db: Database = Depends(get_db),
    _: LoginUserVO = Depends(require_admin)
):
    """删除用户（管理员）"""
    service = UserService(db)
    result = await service.delete_user(request.id)
    return BaseResponse.success(data=result, message="删除成功")
