"""文章异步任务服务"""

import json
import logging
import asyncio
from typing import Dict, Any

from app.schemas.article import ArticleState
from app.models.enums import ArticleStatusEnum, SseMessageTypeEnum
from app.services.article_agent_service import ArticleAgentService
from app.services.article_service import ArticleService
from app.managers.sse_manager import sse_emitter_manager
from app.database import database

logger = logging.getLogger(__name__)


class ArticleAsyncService:
    """文章异步任务服务"""
    
    async def execute_article_generation(self, task_id: str, topic: str):
        """
        异步执行文章生成
        
        Args:
            task_id: 任务 ID
            topic: 选题
        """
        logger.info(f"异步任务开始, taskId={task_id}, topic={topic}")
        
        # 初始化服务
        article_agent_service = ArticleAgentService()
        article_service = ArticleService(database)
        
        try:
            # 更新状态为处理中
            await article_service.update_article_status(task_id, ArticleStatusEnum.PROCESSING)
            
            # 创建状态对象
            state = ArticleState()
            state.task_id = task_id
            state.topic = topic
            
            # 执行智能体编排,并通过 SSE 推送进度
            await article_agent_service.execute_article_generation(
                state,
                lambda message: self._handle_agent_message(task_id, message, state)
            )
            
            # 保存完整文章到数据库
            await article_service.save_article_content(task_id, state)
            
            # 更新状态为已完成
            await article_service.update_article_status(task_id, ArticleStatusEnum.COMPLETED)
            
            # 推送完成消息
            self._send_sse_message(
                task_id,
                SseMessageTypeEnum.ALL_COMPLETE,
                {"taskId": task_id}
            )
            
            # 完成 SSE 连接
            sse_emitter_manager.complete(task_id)
            
            logger.info(f"异步任务完成, taskId={task_id}")
        except Exception as e:
            logger.error(f"异步任务失败, taskId={task_id}, error={e}")
            
            # 更新状态为失败
            await article_service.update_article_status(
                task_id,
                ArticleStatusEnum.FAILED,
                str(e)
            )
            
            # 推送错误消息
            self._send_sse_message(
                task_id,
                SseMessageTypeEnum.ERROR,
                {"message": str(e)}
            )
            
            # 完成 SSE 连接
            sse_emitter_manager.complete(task_id)
    
    def _handle_agent_message(self, task_id: str, message: str, state: ArticleState):
        """处理智能体消息并推送"""
        data = self._build_message_data(message, state)
        if data is not None:
            sse_emitter_manager.send(task_id, json.dumps(data, ensure_ascii=False))
    
    def _build_message_data(self, message: str, state: ArticleState) -> Dict[str, Any]:
        """构建消息数据"""
        # 处理流式消息（带冒号分隔符）
        streaming_prefix2 = SseMessageTypeEnum.AGENT2_STREAMING.get_streaming_prefix()
        streaming_prefix3 = SseMessageTypeEnum.AGENT3_STREAMING.get_streaming_prefix()
        image_complete_prefix = SseMessageTypeEnum.IMAGE_COMPLETE.get_streaming_prefix()
        
        if message.startswith(streaming_prefix2):
            return self._build_streaming_data(
                SseMessageTypeEnum.AGENT2_STREAMING,
                message[len(streaming_prefix2):]
            )
        
        if message.startswith(streaming_prefix3):
            return self._build_streaming_data(
                SseMessageTypeEnum.AGENT3_STREAMING,
                message[len(streaming_prefix3):]
            )
        
        if message.startswith(image_complete_prefix):
            image_json = message[len(image_complete_prefix):]
            return self._build_image_complete_data(image_json)
        
        # 处理完成消息（枚举值）
        return self._build_complete_message_data(message, state)
    
    def _build_streaming_data(self, type_enum: SseMessageTypeEnum, content: str) -> Dict[str, Any]:
        """构建流式输出数据"""
        return {
            "type": type_enum.value,
            "content": content
        }
    
    def _build_image_complete_data(self, image_json: str) -> Dict[str, Any]:
        """构建图片完成数据"""
        return {
            "type": SseMessageTypeEnum.IMAGE_COMPLETE.value,
            "image": json.loads(image_json)
        }
    
    def _build_complete_message_data(self, message: str, state: ArticleState) -> Dict[str, Any]:
        """构建完成消息数据"""
        data = {}
        
        if message == SseMessageTypeEnum.AGENT1_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.AGENT1_COMPLETE.value
            data["title"] = state.title.model_dump(by_alias=True) if state.title else None
        elif message == SseMessageTypeEnum.AGENT2_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.AGENT2_COMPLETE.value
            data["outline"] = [s.model_dump() for s in state.outline.sections] if state.outline else []
        elif message == SseMessageTypeEnum.AGENT3_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.AGENT3_COMPLETE.value
        elif message == SseMessageTypeEnum.AGENT4_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.AGENT4_COMPLETE.value
            data["imageRequirements"] = [
                req.model_dump(by_alias=True) for req in state.image_requirements
            ] if state.image_requirements else []
        elif message == SseMessageTypeEnum.AGENT5_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.AGENT5_COMPLETE.value
            data["images"] = [
                img.model_dump(by_alias=True) for img in state.images
            ] if state.images else []
        elif message == SseMessageTypeEnum.MERGE_COMPLETE.value:
            data["type"] = SseMessageTypeEnum.MERGE_COMPLETE.value
            data["fullContent"] = state.full_content
        else:
            return None
        
        return data
    
    def _send_sse_message(
        self,
        task_id: str,
        type_enum: SseMessageTypeEnum,
        additional_data: Dict[str, Any]
    ):
        """发送 SSE 消息"""
        data = {"type": type_enum.value}
        data.update(additional_data)
        sse_emitter_manager.send(task_id, json.dumps(data, ensure_ascii=False))


# 全局单例
article_async_service = ArticleAsyncService()
