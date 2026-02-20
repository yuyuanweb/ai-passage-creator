"""智能体执行日志 ORM 模型"""

from sqlalchemy import BigInteger, Column, DateTime, Integer, SmallInteger, String, Text
from sqlalchemy.sql import func

from app.database import Base


class AgentLog(Base):
    """智能体执行日志表"""

    __tablename__ = "agent_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    task_id = Column("taskId", String(64), nullable=False, comment="任务ID")
    agent_name = Column("agentName", String(64), nullable=False, comment="智能体名称")
    start_time = Column("startTime", DateTime, nullable=False, comment="开始时间")
    end_time = Column("endTime", DateTime, nullable=True, comment="结束时间")
    duration_ms = Column("durationMs", Integer, nullable=True, comment="耗时（毫秒）")
    status = Column("status", String(20), nullable=False, comment="状态：RUNNING/SUCCESS/FAILED")
    error_message = Column("errorMessage", Text, nullable=True, comment="错误信息")
    prompt = Column("prompt", Text, nullable=True, comment="使用的 Prompt")
    input_data = Column("inputData", Text, nullable=True, comment="输入数据（JSON）")
    output_data = Column("outputData", Text, nullable=True, comment="输出数据（JSON）")
    create_time = Column("createTime", DateTime, nullable=False, default=func.now(), comment="创建时间")
    update_time = Column(
        "updateTime",
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_delete = Column("isDelete", SmallInteger, nullable=False, default=0, comment="是否删除")
