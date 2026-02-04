"""通用请求/响应模型"""

from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """统一响应格式"""
    
    code: int = Field(default=0, description="状态码")
    data: Optional[T] = Field(default=None, description="响应数据")
    message: str = Field(default="ok", description="响应消息")
    
    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "ok") -> "BaseResponse[T]":
        """成功响应"""
        return cls(code=0, data=data, message=message)
    
    @classmethod
    def error(cls, code: int, message: str) -> "BaseResponse[T]":
        """错误响应"""
        return cls(code=code, data=None, message=message)


class PageRequest(BaseModel):
    """分页请求"""
    
    current: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=10, ge=1, le=100, alias="pageSize", description="每页大小")
    sort_field: Optional[str] = Field(default=None, alias="sortField", description="排序字段")
    sort_order: Optional[str] = Field(default="descend", alias="sortOrder", description="排序顺序")


class DeleteRequest(BaseModel):
    """删除请求"""
    
    id: int = Field(..., description="要删除的 ID")
