"""用户相关请求/响应模型"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.common import PageRequest


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    
    user_account: str = Field(..., min_length=4, max_length=256, alias="userAccount", description="账号")
    user_password: str = Field(..., min_length=8, max_length=512, alias="userPassword", description="密码")
    check_password: str = Field(..., min_length=8, max_length=512, alias="checkPassword", description="确认密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    
    user_account: str = Field(..., min_length=4, max_length=256, alias="userAccount", description="账号")
    user_password: str = Field(..., min_length=8, max_length=512, alias="userPassword", description="密码")


class UserAddRequest(BaseModel):
    """添加用户请求（管理员）"""
    
    user_account: str = Field(..., alias="userAccount", description="账号")
    user_password: str = Field(..., alias="userPassword", description="密码")
    user_name: Optional[str] = Field(None, alias="userName", description="用户昵称")
    user_avatar: Optional[str] = Field(None, alias="userAvatar", description="用户头像")
    user_profile: Optional[str] = Field(None, alias="userProfile", description="用户简介")
    user_role: str = Field(default="user", alias="userRole", description="用户角色")


class UserUpdateRequest(BaseModel):
    """更新用户请求（管理员）"""
    
    id: int = Field(..., description="用户 ID")
    user_name: Optional[str] = Field(None, alias="userName", description="用户昵称")
    user_avatar: Optional[str] = Field(None, alias="userAvatar", description="用户头像")
    user_profile: Optional[str] = Field(None, alias="userProfile", description="用户简介")
    user_role: Optional[str] = Field(None, alias="userRole", description="用户角色")


class UserQueryRequest(PageRequest):
    """用户查询请求"""
    
    id: Optional[int] = Field(None, description="用户 ID")
    user_account: Optional[str] = Field(None, alias="userAccount", description="账号")
    user_name: Optional[str] = Field(None, alias="userName", description="用户昵称")
    user_profile: Optional[str] = Field(None, alias="userProfile", description="用户简介")
    user_role: Optional[str] = Field(None, alias="userRole", description="用户角色")


class UserVO(BaseModel):
    """用户视图对象"""
    
    id: int
    user_account: str = Field(..., alias="userAccount")
    user_name: Optional[str] = Field(None, alias="userName")
    user_avatar: Optional[str] = Field(None, alias="userAvatar")
    user_profile: Optional[str] = Field(None, alias="userProfile")
    user_role: str = Field(..., alias="userRole")
    create_time: str = Field(..., alias="createTime")
    
    class Config:
        populate_by_name = True


class LoginUserVO(BaseModel):
    """登录用户视图对象"""
    
    id: int
    user_account: str = Field(..., alias="userAccount")
    user_name: Optional[str] = Field(None, alias="userName")
    user_avatar: Optional[str] = Field(None, alias="userAvatar")
    user_profile: Optional[str] = Field(None, alias="userProfile")
    user_role: str = Field(..., alias="userRole")
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    
    class Config:
        populate_by_name = True
