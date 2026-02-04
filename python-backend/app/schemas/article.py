"""文章相关请求/响应模型"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class ArticleCreateRequest(BaseModel):
    """创建文章请求（第 5 期：新增风格和配图方式选择）"""
    
    topic: str = Field(..., min_length=1, description="选题")
    style: Optional[str] = Field(None, description="文章风格：tech/emotional/educational/humorous")
    enabled_image_methods: Optional[List[str]] = Field(
        None,
        alias="enabledImageMethods",
        description="允许的配图方式列表（为空表示支持所有方式）"
    )


class ArticleQueryRequest(PageRequest):
    """文章查询请求"""
    
    id: Optional[int] = Field(None, description="文章 ID")
    task_id: Optional[str] = Field(None, alias="taskId", description="任务 ID")
    user_id: Optional[int] = Field(None, alias="userId", description="用户 ID")
    topic: Optional[str] = Field(None, description="选题")
    status: Optional[str] = Field(None, description="状态")


class ArticleVO(BaseModel):
    """文章视图对象"""
    
    id: int
    task_id: str = Field(..., alias="taskId")
    user_id: int = Field(..., alias="userId")
    topic: str
    style: Optional[str] = None
    main_title: Optional[str] = Field(None, alias="mainTitle")
    sub_title: Optional[str] = Field(None, alias="subTitle")
    outline: Optional[List[Any]] = None
    content: Optional[str] = None
    full_content: Optional[str] = Field(None, alias="fullContent")
    cover_image: Optional[str] = Field(None, alias="coverImage")
    images: Optional[List[Any]] = None
    status: str
    error_message: Optional[str] = Field(None, alias="errorMessage")
    create_time: str = Field(..., alias="createTime")
    completed_time: Optional[str] = Field(None, alias="completedTime")
    update_time: str = Field(..., alias="updateTime")
    
    class Config:
        populate_by_name = True


# ArticleState 内部类定义
class TitleResult(BaseModel):
    """标题结果"""
    
    main_title: str = Field(..., alias="mainTitle")
    sub_title: str = Field(..., alias="subTitle")
    
    class Config:
        populate_by_name = True


class OutlineSection(BaseModel):
    """大纲章节"""
    
    section: int
    title: str
    points: List[str]


class OutlineResult(BaseModel):
    """大纲结果"""
    
    sections: List[OutlineSection]


class ImageRequirement(BaseModel):
    """配图需求（第 5 期：新增 imageSource、prompt、placeholderId）"""
    
    position: int
    type: str
    section_title: str = Field(..., alias="sectionTitle")
    keywords: str
    image_source: str = Field(..., alias="imageSource", description="图片来源")
    prompt: str = Field(default="", description="AI 生图提示词")
    placeholder_id: str = Field(..., alias="placeholderId", description="占位符ID")
    
    class Config:
        populate_by_name = True


class ImageResult(BaseModel):
    """配图结果（第 5 期：新增 placeholderId）"""
    
    position: int
    url: str
    method: str
    keywords: str
    section_title: str = Field(..., alias="sectionTitle")
    description: str
    placeholder_id: str = Field(..., alias="placeholderId", description="占位符ID")
    
    class Config:
        populate_by_name = True


class Agent4Result(BaseModel):
    """智能体4返回结果（第 5 期：占位符方案）"""
    
    content_with_placeholders: str = Field(..., alias="contentWithPlaceholders")
    image_requirements: List[ImageRequirement] = Field(..., alias="imageRequirements")
    
    class Config:
        populate_by_name = True


class ArticleState:
    """文章生成状态（智能体间共享的状态对象）"""
    
    def __init__(self):
        self.task_id: Optional[str] = None
        self.topic: Optional[str] = None
        self.style: Optional[str] = None  # 第 5 期新增
        self.enabled_image_methods: Optional[List[str]] = None  # 第 5 期新增
        self.title: Optional[TitleResult] = None
        self.outline: Optional[OutlineResult] = None
        self.content: Optional[str] = None
        self.image_requirements: Optional[List[ImageRequirement]] = None
        self.images: Optional[List[ImageResult]] = None
        self.cover_image: Optional[str] = None
        self.full_content: Optional[str] = None
