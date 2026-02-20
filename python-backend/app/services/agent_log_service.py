"""智能体执行日志服务"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from databases import Database

from app.schemas.statistics import AgentExecutionStatsVO, AgentLogVO

logger = logging.getLogger(__name__)


class AgentLogService:
    """智能体执行日志服务"""

    def __init__(self, db: Database):
        self.db = db

    def save_log_async(self, log_data: Dict[str, Any]):
        """异步保存日志，不阻塞主执行链路"""
        asyncio.create_task(self._save_log(log_data))

    async def _save_log(self, log_data: Dict[str, Any]):
        """写入日志记录"""
        try:
            await self.db.execute(
                query="""
                    INSERT INTO agent_log (
                        taskId, agentName, startTime, endTime, durationMs, status,
                        errorMessage, prompt, inputData, outputData
                    )
                    VALUES (
                        :taskId, :agentName, :startTime, :endTime, :durationMs, :status,
                        :errorMessage, :prompt, :inputData, :outputData
                    )
                """,
                values={
                    "taskId": log_data.get("taskId"),
                    "agentName": log_data.get("agentName"),
                    "startTime": log_data.get("startTime"),
                    "endTime": log_data.get("endTime"),
                    "durationMs": log_data.get("durationMs"),
                    "status": log_data.get("status"),
                    "errorMessage": log_data.get("errorMessage"),
                    "prompt": log_data.get("prompt"),
                    "inputData": log_data.get("inputData"),
                    "outputData": log_data.get("outputData"),
                },
            )
            logger.info(
                "智能体日志已保存, taskId=%s, agentName=%s, status=%s, durationMs=%s",
                log_data.get("taskId"),
                log_data.get("agentName"),
                log_data.get("status"),
                log_data.get("durationMs"),
            )
        except Exception:
            logger.exception(
                "保存智能体日志失败, taskId=%s, agentName=%s",
                log_data.get("taskId"),
                log_data.get("agentName"),
            )

    async def get_logs_by_task_id(self, task_id: str) -> List[AgentLogVO]:
        """查询任务下的执行日志"""
        rows = await self.db.fetch_all(
            query="""
                SELECT id, taskId, agentName, startTime, endTime, durationMs, status,
                       errorMessage, prompt, inputData, outputData, createTime, updateTime
                FROM agent_log
                WHERE taskId = :taskId AND isDelete = 0
                ORDER BY createTime ASC
            """,
            values={"taskId": task_id},
        )
        return [self._to_agent_log_vo(dict(row)) for row in rows]

    async def get_execution_stats(self, task_id: str) -> AgentExecutionStatsVO:
        """获取任务执行统计"""
        logs = await self.get_logs_by_task_id(task_id)
        if not logs:
            return AgentExecutionStatsVO(
                taskId=task_id,
                totalDurationMs=0,
                agentCount=0,
                agentDurations={},
                overallStatus="NOT_FOUND",
                logs=[],
            )

        total_duration_ms = 0
        agent_durations: Dict[str, int] = {}
        overall_status = "SUCCESS"

        for log_item in logs:
            if log_item.duration_ms is not None:
                total_duration_ms += log_item.duration_ms
                agent_durations[log_item.agent_name] = log_item.duration_ms
            if log_item.status == "FAILED":
                overall_status = "FAILED"
            elif log_item.status == "RUNNING" and overall_status != "FAILED":
                overall_status = "RUNNING"

        return AgentExecutionStatsVO(
            taskId=task_id,
            totalDurationMs=total_duration_ms,
            agentCount=len(logs),
            agentDurations=agent_durations,
            overallStatus=overall_status,
            logs=logs,
        )

    def _to_agent_log_vo(self, row: Dict[str, Any]) -> AgentLogVO:
        """数据库记录转日志 VO"""
        return AgentLogVO(
            id=row["id"],
            taskId=row["taskId"],
            agentName=row["agentName"],
            startTime=self._to_iso(row.get("startTime")),
            endTime=self._to_iso(row.get("endTime")),
            durationMs=row.get("durationMs"),
            status=row["status"],
            errorMessage=row.get("errorMessage"),
            prompt=row.get("prompt"),
            inputData=row.get("inputData"),
            outputData=row.get("outputData"),
            createTime=self._to_iso(row.get("createTime")),
            updateTime=self._to_iso(row.get("updateTime")),
        )

    @staticmethod
    def _to_iso(value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat()
