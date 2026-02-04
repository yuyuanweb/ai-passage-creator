"""SSE Emitter 管理器"""

import logging
import asyncio
from typing import Dict
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class SseEmitterManager:
    """SSE Emitter 管理器"""
    
    def __init__(self):
        # 存储所有的队列
        self._queues: Dict[str, asyncio.Queue] = {}
    
    def create_emitter(self, task_id: str) -> StreamingResponse:
        """
        创建 SSE Emitter
        
        Args:
            task_id: 任务ID
            
        Returns:
            StreamingResponse
        """
        # 创建队列
        queue = asyncio.Queue()
        self._queues[task_id] = queue
        
        logger.info(f"SSE 连接已创建, taskId={task_id}")
        
        # 创建事件流生成器
        async def event_generator():
            try:
                while True:
                    # 从队列获取消息
                    message = await queue.get()
                    
                    # 如果是完成信号，结束流
                    if message == "__COMPLETE__":
                        break
                    
                    # 格式化为 SSE 格式
                    yield f"data: {message}\n\n"
            except asyncio.CancelledError:
                logger.info(f"SSE 连接被取消, taskId={task_id}")
            except Exception as e:
                logger.error(f"SSE 连接错误, taskId={task_id}, error={e}")
            finally:
                # 清理队列
                if task_id in self._queues:
                    del self._queues[task_id]
                logger.info(f"SSE 连接已关闭, taskId={task_id}")
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    def send(self, task_id: str, message: str):
        """
        发送消息
        
        Args:
            task_id: 任务ID
            message: 消息内容
        """
        queue = self._queues.get(task_id)
        if queue is None:
            logger.warning(f"SSE Emitter 不存在, taskId={task_id}")
            return
        
        try:
            queue.put_nowait(message)
            logger.debug(f"SSE 消息发送成功, taskId={task_id}")
        except Exception as e:
            logger.error(f"SSE 消息发送失败, taskId={task_id}, error={e}")
    
    def complete(self, task_id: str):
        """
        完成连接
        
        Args:
            task_id: 任务ID
        """
        queue = self._queues.get(task_id)
        if queue is None:
            logger.warning(f"SSE Emitter 不存在, taskId={task_id}")
            return
        
        try:
            queue.put_nowait("__COMPLETE__")
            logger.info(f"SSE 连接已完成, taskId={task_id}")
        except Exception as e:
            logger.error(f"SSE 连接完成失败, taskId={task_id}, error={e}")
    
    def exists(self, task_id: str) -> bool:
        """
        检查 Emitter 是否存在
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否存在
        """
        return task_id in self._queues


# 全局单例
sse_emitter_manager = SseEmitterManager()
