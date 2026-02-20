"""统计与执行日志相关模型"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AgentLogVO(BaseModel):
    """智能体执行日志视图对象"""

    id: int
    task_id: str = Field(..., alias="taskId")
    agent_name: str = Field(..., alias="agentName")
    start_time: str = Field(..., alias="startTime")
    end_time: Optional[str] = Field(None, alias="endTime")
    duration_ms: Optional[int] = Field(None, alias="durationMs")
    status: str
    error_message: Optional[str] = Field(None, alias="errorMessage")
    prompt: Optional[str] = None
    input_data: Optional[str] = Field(None, alias="inputData")
    output_data: Optional[str] = Field(None, alias="outputData")
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True


class AgentExecutionStatsVO(BaseModel):
    """任务执行统计"""

    task_id: str = Field(..., alias="taskId")
    total_duration_ms: int = Field(..., alias="totalDurationMs")
    agent_count: int = Field(..., alias="agentCount")
    agent_durations: Dict[str, int] = Field(default_factory=dict, alias="agentDurations")
    overall_status: str = Field(..., alias="overallStatus")
    logs: List[AgentLogVO] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class StatisticsVO(BaseModel):
    """系统统计数据"""

    today_count: int = Field(..., alias="todayCount")
    week_count: int = Field(..., alias="weekCount")
    month_count: int = Field(..., alias="monthCount")
    total_count: int = Field(..., alias="totalCount")
    success_rate: float = Field(..., alias="successRate")
    avg_duration_ms: int = Field(..., alias="avgDurationMs")
    active_user_count: int = Field(..., alias="activeUserCount")
    total_user_count: int = Field(..., alias="totalUserCount")
    vip_user_count: int = Field(..., alias="vipUserCount")
    quota_used: int = Field(..., alias="quotaUsed")

    class Config:
        populate_by_name = True
"""统计与执行日志相关模型"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AgentLogVO(BaseModel):
    """智能体执行日志视图对象"""

    id: int
    task_id: str = Field(..., alias="taskId")
    agent_name: str = Field(..., alias="agentName")
    start_time: str = Field(..., alias="startTime")
    end_time: Optional[str] = Field(None, alias="endTime")
    duration_ms: Optional[int] = Field(None, alias="durationMs")
    status: str
    error_message: Optional[str] = Field(None, alias="errorMessage")
    prompt: Optional[str] = None
    input_data: Optional[str] = Field(None, alias="inputData")
    output_data: Optional[str] = Field(None, alias="outputData")
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True


class AgentExecutionStatsVO(BaseModel):
    """任务执行统计"""

    task_id: str = Field(..., alias="taskId")
    total_duration_ms: int = Field(..., alias="totalDurationMs")
    agent_count: int = Field(..., alias="agentCount")
    agent_durations: Dict[str, int] = Field(default_factory=dict, alias="agentDurations")
    overall_status: str = Field(..., alias="overallStatus")
    logs: List[AgentLogVO] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class StatisticsVO(BaseModel):
    """系统统计数据"""

    today_count: int = Field(..., alias="todayCount")
    week_count: int = Field(..., alias="weekCount")
    month_count: int = Field(..., alias="monthCount")
    total_count: int = Field(..., alias="totalCount")
    success_rate: float = Field(..., alias="successRate")
    avg_duration_ms: int = Field(..., alias="avgDurationMs")
    active_user_count: int = Field(..., alias="activeUserCount")
    total_user_count: int = Field(..., alias="totalUserCount")
    vip_user_count: int = Field(..., alias="vipUserCount")
    quota_used: int = Field(..., alias="quotaUsed")

    class Config:
        populate_by_name = True
