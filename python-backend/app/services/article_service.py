"""文章服务"""

import json
import uuid
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func, and_
from databases import Database

from app.models.article import Article
from app.models.enums import ArticleStatusEnum
from app.schemas.article import ArticleQueryRequest, ArticleVO, ArticleState
from app.schemas.user import LoginUserVO
from app.exceptions import ErrorCode, throw_if_not, BusinessException
import logging

logger = logging.getLogger(__name__)


class ArticleService:
    """文章服务"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_article_task_with_quota_check(
        self,
        topic: str,
        login_user: LoginUserVO
    ) -> str:
        """
        创建文章任务（暂不检查配额，第 7 期实现）
        
        Args:
            topic: 选题
            login_user: 登录用户
            
        Returns:
            任务 ID
        """
        # 生成任务 ID
        task_id = str(uuid.uuid4())
        
        # 插入文章记录
        query = """
            INSERT INTO article (taskId, userId, topic, status, createTime)
            VALUES (:taskId, :userId, :topic, :status, :createTime)
        """
        await self.db.execute(
            query=query,
            values={
                "taskId": task_id,
                "userId": login_user.id,
                "topic": topic,
                "status": ArticleStatusEnum.PENDING.value,
                "createTime": datetime.now()
            }
        )
        
        logger.info(f"文章任务创建成功, taskId={task_id}, userId={login_user.id}")
        return task_id
    
    async def get_article_detail(self, task_id: str, login_user: LoginUserVO) -> ArticleVO:
        """
        获取文章详情
        
        Args:
            task_id: 任务 ID
            login_user: 登录用户
            
        Returns:
            文章视图对象
        """
        query = select(Article).where(
            and_(Article.task_id == task_id, Article.is_delete == 0)
        )
        article = await self.db.fetch_one(query)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        
        # 权限校验：只能查看自己的文章
        if article["userId"] != login_user.id and login_user.user_role != "admin":
            raise BusinessException(ErrorCode.NO_AUTH_ERROR, "无权限访问")
        
        return self._to_article_vo(article)
    
    async def list_article_by_page(
        self,
        request: ArticleQueryRequest,
        login_user: LoginUserVO
    ) -> Tuple[List[ArticleVO], int]:
        """
        分页查询文章列表
        
        Args:
            request: 查询请求
            login_user: 登录用户
            
        Returns:
            文章列表和总数
        """
        # 构建查询条件
        conditions = [Article.is_delete == 0]
        
        # 非管理员只能查看自己的文章
        if login_user.user_role != "admin":
            conditions.append(Article.user_id == login_user.id)
        
        if request.id:
            conditions.append(Article.id == request.id)
        if request.task_id:
            conditions.append(Article.task_id == request.task_id)
        if request.user_id:
            conditions.append(Article.user_id == request.user_id)
        if request.topic:
            conditions.append(Article.topic.like(f"%{request.topic}%"))
        if request.status:
            conditions.append(Article.status == request.status)
        
        # 查询总数
        count_query = select(func.count(Article.id)).where(and_(*conditions))
        total = await self.db.fetch_val(count_query)
        
        # 分页查询
        query = select(Article).where(and_(*conditions))
        
        # 排序
        query = query.order_by(Article.create_time.desc())
        
        # 分页
        offset = (request.current - 1) * request.page_size
        query = query.limit(request.page_size).offset(offset)
        
        articles = await self.db.fetch_all(query)
        article_list = [self._to_article_vo(article) for article in articles]
        
        return article_list, total
    
    async def delete_article(self, article_id: int, login_user: LoginUserVO) -> bool:
        """
        删除文章
        
        Args:
            article_id: 文章 ID
            login_user: 登录用户
            
        Returns:
            是否成功
        """
        # 查询文章
        query = select(Article).where(and_(Article.id == article_id, Article.is_delete == 0))
        article = await self.db.fetch_one(query)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        
        # 权限校验
        if article["userId"] != login_user.id and login_user.user_role != "admin":
            raise BusinessException(ErrorCode.NO_AUTH_ERROR, "无权限删除")
        
        # 逻辑删除
        query = "UPDATE article SET isDelete = 1 WHERE id = :id"
        await self.db.execute(query=query, values={"id": article_id})
        
        return True
    
    async def update_article_status(
        self,
        task_id: str,
        status: ArticleStatusEnum,
        error_message: Optional[str] = None
    ):
        """
        更新文章状态
        
        Args:
            task_id: 任务 ID
            status: 状态
            error_message: 错误信息
        """
        if status == ArticleStatusEnum.COMPLETED:
            query = """
                UPDATE article 
                SET status = :status, completedTime = :completedTime 
                WHERE taskId = :taskId
            """
            await self.db.execute(
                query=query,
                values={
                    "status": status.value,
                    "completedTime": datetime.now(),
                    "taskId": task_id
                }
            )
        elif status == ArticleStatusEnum.FAILED:
            query = """
                UPDATE article 
                SET status = :status, errorMessage = :errorMessage 
                WHERE taskId = :taskId
            """
            await self.db.execute(
                query=query,
                values={
                    "status": status.value,
                    "errorMessage": error_message,
                    "taskId": task_id
                }
            )
        else:
            query = "UPDATE article SET status = :status WHERE taskId = :taskId"
            await self.db.execute(
                query=query,
                values={"status": status.value, "taskId": task_id}
            )
    
    async def save_article_content(self, task_id: str, state: ArticleState):
        """
        保存文章内容
        
        Args:
            task_id: 任务 ID
            state: 文章状态
        """
        # 从 images 列表中提取 position=1 的封面图 URL
        cover_image = None
        if state.images:
            cover = next((img for img in state.images if img.position == 1), None)
            if cover and cover.url:
                cover_image = cover.url
        
        query = """
            UPDATE article 
            SET mainTitle = :mainTitle,
                subTitle = :subTitle,
                outline = :outline,
                content = :content,
                fullContent = :fullContent,
                coverImage = :coverImage,
                images = :images
            WHERE taskId = :taskId
        """
        await self.db.execute(
            query=query,
            values={
                "mainTitle": state.title.main_title,
                "subTitle": state.title.sub_title,
                "outline": json.dumps(
                    [s.model_dump() for s in state.outline.sections],
                    ensure_ascii=False
                ),
                "content": state.content,
                "fullContent": state.full_content,
                "coverImage": cover_image,
                "images": json.dumps(
                    [img.model_dump(by_alias=True) for img in state.images],
                    ensure_ascii=False
                ),
                "taskId": task_id
            }
        )
    
    def _to_article_vo(self, article) -> ArticleVO:
        """转换为 ArticleVO"""
        article_dict = dict(article)
        return ArticleVO(
            id=article_dict["id"],
            taskId=article_dict["taskId"],
            userId=article_dict["userId"],
            topic=article_dict["topic"],
            mainTitle=article_dict["mainTitle"],
            subTitle=article_dict["subTitle"],
            outline=article_dict["outline"],
            content=article_dict["content"],
            fullContent=article_dict["fullContent"],
            coverImage=article_dict.get("coverImage"),
            images=article_dict["images"],
            status=article_dict["status"],
            errorMessage=article_dict["errorMessage"],
            createTime=article_dict["createTime"].isoformat(),
            completedTime=article_dict["completedTime"].isoformat() if article_dict["completedTime"] else None,
            updateTime=article_dict["updateTime"].isoformat()
        )
