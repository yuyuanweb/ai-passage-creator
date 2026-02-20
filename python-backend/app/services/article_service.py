"""文章服务"""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from databases import Database
from sqlalchemy import and_, func, select

from app.exceptions import BusinessException, ErrorCode, throw_if, throw_if_not
from app.constants.user import UserConstant
from app.models.article import Article
from app.models.enums import ArticlePhaseEnum, ArticleStatusEnum, ImageMethodEnum
from app.schemas.article import (
    ArticleQueryRequest,
    ArticleState,
    ArticleVO,
    OutlineSection,
    TitleOption,
)
from app.schemas.user import LoginUserVO
from app.services.article_agent_service import ArticleAgentService

logger = logging.getLogger(__name__)


class ArticleService:
    """文章服务"""

    def __init__(self, db: Database):
        self.db = db
        self._default_non_vip_image_methods = [
            ImageMethodEnum.PEXELS.value,
            ImageMethodEnum.MERMAID.value,
            ImageMethodEnum.ICONIFY.value,
            ImageMethodEnum.EMOJI_PACK.value,
        ]
        self._vip_only_image_methods = {
            ImageMethodEnum.NANO_BANANA.value,
            ImageMethodEnum.SVG_DIAGRAM.value,
        }

    async def create_article_task(
        self,
        topic: str,
        login_user: LoginUserVO,
        style: Optional[str] = None,
        enabled_image_methods: Optional[List[str]] = None,
    ) -> str:
        """创建文章任务"""
        final_image_methods = self._process_image_methods(enabled_image_methods, login_user)
        self._validate_image_methods(final_image_methods, login_user)

        task_id = str(uuid.uuid4())
        now = datetime.now()
        query = """
            INSERT INTO article (
                taskId, userId, topic, style, enabledImageMethods, status, phase, createTime
            )
            VALUES (
                :taskId, :userId, :topic, :style, :enabledImageMethods, :status, :phase, :createTime
            )
        """
        await self.db.execute(
            query=query,
            values={
                "taskId": task_id,
                "userId": login_user.id,
                "topic": topic,
                "style": style,
                "enabledImageMethods": json.dumps(final_image_methods, ensure_ascii=False)
                if final_image_methods
                else None,
                "status": ArticleStatusEnum.PENDING.value,
                "phase": ArticlePhaseEnum.PENDING.value,
                "createTime": now,
            },
        )
        logger.info("文章任务创建成功, taskId=%s, userId=%s", task_id, login_user.id)
        return task_id

    async def create_article_task_with_quota_check(
        self,
        topic: str,
        login_user: LoginUserVO,
        style: Optional[str] = None,
        enabled_image_methods: Optional[List[str]] = None,
    ) -> str:
        """在同一事务中完成配额扣减和任务创建"""
        if self._is_vip_or_admin(login_user):
            return await self.create_article_task(
                topic=topic,
                login_user=login_user,
                style=style,
                enabled_image_methods=enabled_image_methods,
            )

        async with self.db.transaction():
            quota_row = await self.db.fetch_one(
                query="""
                    SELECT quota
                    FROM user
                    WHERE id = :userId AND isDelete = 0
                    FOR UPDATE
                """,
                values={"userId": login_user.id},
            )
            throw_if_not(quota_row, ErrorCode.NOT_FOUND_ERROR, "用户不存在")
            throw_if(quota_row["quota"] <= 0, ErrorCode.OPERATION_ERROR, "配额不足")

            await self.db.execute(
                query="""
                    UPDATE user
                    SET quota = quota - 1
                    WHERE id = :userId
                """,
                values={"userId": login_user.id},
            )

            return await self.create_article_task(
                topic=topic,
                login_user=login_user,
                style=style,
                enabled_image_methods=enabled_image_methods,
            )

    async def get_by_task_id(self, task_id: str):
        """根据任务 ID 查询文章记录"""
        query = select(Article).where(and_(Article.task_id == task_id, Article.is_delete == 0))
        return await self.db.fetch_one(query)

    async def get_article_detail(self, task_id: str, login_user: LoginUserVO) -> ArticleVO:
        """获取文章详情"""
        article = await self.get_by_task_id(task_id)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        self._check_article_permission(article, login_user)
        return self._to_article_vo(article)

    async def list_article_by_page(
        self,
        request: ArticleQueryRequest,
        login_user: LoginUserVO,
    ) -> Tuple[List[ArticleVO], int]:
        """分页查询文章列表"""
        conditions = [Article.is_delete == 0]
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

        count_query = select(func.count(Article.id)).where(and_(*conditions))
        total = await self.db.fetch_val(count_query)

        query = (
            select(Article)
            .where(and_(*conditions))
            .order_by(Article.create_time.desc())
            .limit(request.page_size)
            .offset((request.current - 1) * request.page_size)
        )
        articles = await self.db.fetch_all(query)
        return [self._to_article_vo(article) for article in articles], total

    async def delete_article(self, article_id: int, login_user: LoginUserVO) -> bool:
        """删除文章"""
        query = select(Article).where(and_(Article.id == article_id, Article.is_delete == 0))
        article = await self.db.fetch_one(query)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        self._check_article_permission(article, login_user)
        await self.db.execute(query="UPDATE article SET isDelete = 1 WHERE id = :id", values={"id": article_id})
        return True

    async def update_article_status(
        self,
        task_id: str,
        status: ArticleStatusEnum,
        error_message: Optional[str] = None,
    ):
        """更新文章状态"""
        if status == ArticleStatusEnum.COMPLETED:
            await self.db.execute(
                query="""
                    UPDATE article
                    SET status = :status, completedTime = :completedTime
                    WHERE taskId = :taskId
                """,
                values={
                    "status": status.value,
                    "completedTime": datetime.now(),
                    "taskId": task_id,
                },
            )
            return

        if status == ArticleStatusEnum.FAILED:
            await self.db.execute(
                query="""
                    UPDATE article
                    SET status = :status, errorMessage = :errorMessage
                    WHERE taskId = :taskId
                """,
                values={
                    "status": status.value,
                    "errorMessage": error_message,
                    "taskId": task_id,
                },
            )
            return

        await self.db.execute(
            query="UPDATE article SET status = :status WHERE taskId = :taskId",
            values={"status": status.value, "taskId": task_id},
        )

    async def update_phase(self, task_id: str, phase: ArticlePhaseEnum):
        """更新文章阶段"""
        article = await self.get_by_task_id(task_id)
        if not article:
            logger.error("文章记录不存在, taskId=%s", task_id)
            return

        current_phase_value = article["phase"] or ArticlePhaseEnum.PENDING.value
        try:
            current_phase = ArticlePhaseEnum(current_phase_value)
        except ValueError as exc:
            raise BusinessException(ErrorCode.OPERATION_ERROR, "当前阶段非法") from exc
        if current_phase != phase and not current_phase.can_transition_to(phase):
            raise BusinessException(ErrorCode.OPERATION_ERROR, "非法阶段流转")

        await self.db.execute(
            query="UPDATE article SET phase = :phase WHERE taskId = :taskId",
            values={"phase": phase.value, "taskId": task_id},
        )

    async def save_title_options(self, task_id: str, title_options: List[TitleOption]):
        """保存标题方案列表"""
        await self.db.execute(
            query="UPDATE article SET titleOptions = :titleOptions WHERE taskId = :taskId",
            values={
                "taskId": task_id,
                "titleOptions": json.dumps(
                    [item.model_dump(by_alias=True) for item in title_options],
                    ensure_ascii=False,
                ),
            },
        )

    async def confirm_title(
        self,
        task_id: str,
        selected_main_title: str,
        selected_sub_title: str,
        user_description: Optional[str],
        login_user: LoginUserVO,
    ):
        """确认标题并进入大纲阶段"""
        article = await self.get_by_task_id(task_id)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        self._check_article_permission(article, login_user)
        throw_if(
            article["phase"] != ArticlePhaseEnum.TITLE_SELECTING.value,
            ErrorCode.OPERATION_ERROR,
            "当前阶段不允许确认标题",
        )

        await self.db.execute(
            query="""
                UPDATE article
                SET mainTitle = :mainTitle,
                    subTitle = :subTitle,
                    userDescription = :userDescription,
                    phase = :phase
                WHERE taskId = :taskId
            """,
            values={
                "taskId": task_id,
                "mainTitle": selected_main_title,
                "subTitle": selected_sub_title,
                "userDescription": user_description,
                "phase": ArticlePhaseEnum.OUTLINE_GENERATING.value,
            },
        )

    async def confirm_outline(
        self,
        task_id: str,
        outline: List[OutlineSection],
        login_user: LoginUserVO,
    ):
        """确认大纲并进入正文阶段"""
        article = await self.get_by_task_id(task_id)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        self._check_article_permission(article, login_user)
        throw_if(
            article["phase"] != ArticlePhaseEnum.OUTLINE_EDITING.value,
            ErrorCode.OPERATION_ERROR,
            "当前阶段不允许确认大纲",
        )

        await self.db.execute(
            query="""
                UPDATE article
                SET outline = :outline,
                    phase = :phase
                WHERE taskId = :taskId
            """,
            values={
                "taskId": task_id,
                "outline": json.dumps([item.model_dump() for item in outline], ensure_ascii=False),
                "phase": ArticlePhaseEnum.CONTENT_GENERATING.value,
            },
        )

    async def save_outline(self, task_id: str, outline: List[OutlineSection]):
        """保存大纲内容（不推进阶段）"""
        await self.db.execute(
            query="UPDATE article SET outline = :outline WHERE taskId = :taskId",
            values={
                "taskId": task_id,
                "outline": json.dumps([item.model_dump() for item in outline], ensure_ascii=False),
            },
        )

    async def ai_modify_outline(
        self,
        task_id: str,
        modify_suggestion: str,
        login_user: LoginUserVO,
    ) -> List[OutlineSection]:
        """AI 修改大纲"""
        article = await self.get_by_task_id(task_id)
        throw_if_not(article, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        self._check_article_permission(article, login_user)
        throw_if(
            not self._is_vip_or_admin(login_user),
            ErrorCode.NO_AUTH_ERROR,
            "AI 修改大纲功能仅限 VIP 会员使用",
        )
        throw_if(
            article["phase"] != ArticlePhaseEnum.OUTLINE_EDITING.value,
            ErrorCode.OPERATION_ERROR,
            "当前阶段不允许 AI 修改大纲",
        )
        throw_if(not article["outline"], ErrorCode.OPERATION_ERROR, "当前文章尚未生成大纲")

        current_outline = [OutlineSection(**item) for item in json.loads(article["outline"])]
        agent_service = ArticleAgentService()
        modified_outline = await agent_service.ai_modify_outline(
            task_id=task_id,
            main_title=article["mainTitle"],
            sub_title=article["subTitle"],
            current_outline=current_outline,
            modify_suggestion=modify_suggestion,
        )
        await self.db.execute(
            query="UPDATE article SET outline = :outline WHERE taskId = :taskId",
            values={
                "taskId": task_id,
                "outline": json.dumps(
                    [item.model_dump() for item in modified_outline],
                    ensure_ascii=False,
                ),
            },
        )
        return modified_outline

    async def save_article_content(self, task_id: str, state: ArticleState):
        """保存文章内容"""
        cover_image = None
        if state.images:
            cover = next((img for img in state.images if img.position == 1), None)
            if cover and cover.url:
                cover_image = cover.url

        await self.db.execute(
            query="""
                UPDATE article
                SET mainTitle = :mainTitle,
                    subTitle = :subTitle,
                    outline = :outline,
                    content = :content,
                    fullContent = :fullContent,
                    coverImage = :coverImage,
                    images = :images
                WHERE taskId = :taskId
            """,
            values={
                "taskId": task_id,
                "mainTitle": state.title.main_title if state.title else None,
                "subTitle": state.title.sub_title if state.title else None,
                "outline": json.dumps([s.model_dump() for s in state.outline.sections], ensure_ascii=False)
                if state.outline
                else None,
                "content": state.content,
                "fullContent": state.full_content,
                "coverImage": cover_image,
                "images": json.dumps([img.model_dump(by_alias=True) for img in state.images], ensure_ascii=False)
                if state.images
                else None,
            },
        )

    def _check_article_permission(self, article, login_user: LoginUserVO):
        """检查文章访问权限"""
        if article["userId"] != login_user.id and login_user.user_role != UserConstant.ADMIN_ROLE:
            raise BusinessException(ErrorCode.NO_AUTH_ERROR, "无权限访问")

    def _is_vip_or_admin(self, login_user: LoginUserVO) -> bool:
        """是否为 VIP 或管理员"""
        return login_user.user_role in {UserConstant.ADMIN_ROLE, UserConstant.VIP_ROLE}

    def _process_image_methods(
        self,
        enabled_image_methods: Optional[List[str]],
        login_user: LoginUserVO,
    ) -> Optional[List[str]]:
        """处理配图方式默认值"""
        if enabled_image_methods:
            return enabled_image_methods

        if self._is_vip_or_admin(login_user):
            return None

        return list(self._default_non_vip_image_methods)

    def _validate_image_methods(
        self,
        enabled_image_methods: Optional[List[str]],
        login_user: LoginUserVO,
    ):
        """校验普通用户高级配图权限"""
        if not enabled_image_methods or self._is_vip_or_admin(login_user):
            return

        for method in enabled_image_methods:
            if method in self._vip_only_image_methods:
                raise BusinessException(
                    ErrorCode.NO_AUTH_ERROR,
                    "高级配图功能（AI 生图、SVG 图表）仅限 VIP 会员使用",
                )

    def _to_article_vo(self, article) -> ArticleVO:
        """转换为 ArticleVO"""
        article_dict = dict(article)
        title_options = json.loads(article_dict["titleOptions"]) if article_dict.get("titleOptions") else None
        outline = json.loads(article_dict["outline"]) if article_dict.get("outline") else None
        images = json.loads(article_dict["images"]) if article_dict.get("images") else None
        return ArticleVO(
            id=article_dict["id"],
            taskId=article_dict["taskId"],
            userId=article_dict["userId"],
            topic=article_dict["topic"],
            userDescription=article_dict.get("userDescription"),
            style=article_dict.get("style"),
            mainTitle=article_dict.get("mainTitle"),
            subTitle=article_dict.get("subTitle"),
            titleOptions=title_options,
            outline=outline,
            content=article_dict.get("content"),
            fullContent=article_dict.get("fullContent"),
            coverImage=article_dict.get("coverImage"),
            images=images,
            status=article_dict["status"],
            phase=article_dict.get("phase"),
            errorMessage=article_dict.get("errorMessage"),
            createTime=article_dict["createTime"].isoformat(),
            completedTime=article_dict["completedTime"].isoformat() if article_dict.get("completedTime") else None,
            updateTime=article_dict["updateTime"].isoformat(),
        )
