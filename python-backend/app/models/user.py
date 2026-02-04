"""用户 ORM 模型"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """用户表"""
    
    __tablename__ = "user"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    user_account = Column("userAccount", String(256), nullable=False, unique=True, comment="账号")
    user_password = Column("userPassword", String(512), nullable=False, comment="密码")
    user_name = Column("userName", String(256), nullable=True, comment="用户昵称")
    user_avatar = Column("userAvatar", String(1024), nullable=True, comment="用户头像")
    user_profile = Column("userProfile", String(512), nullable=True, comment="用户简介")
    user_role = Column("userRole", String(256), nullable=False, default="user", comment="用户角色：user/admin")
    
    edit_time = Column("editTime", DateTime, nullable=False, default=func.now(), comment="编辑时间")
    create_time = Column("createTime", DateTime, nullable=False, default=func.now(), comment="创建时间")
    update_time = Column("updateTime", DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_delete = Column("isDelete", SmallInteger, nullable=False, default=0, comment="是否删除")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "userAccount": self.user_account,
            "userName": self.user_name,
            "userAvatar": self.user_avatar,
            "userProfile": self.user_profile,
            "userRole": self.user_role,
            "createTime": self.create_time.isoformat() if self.create_time else None,
            "updateTime": self.update_time.isoformat() if self.update_time else None,
        }
