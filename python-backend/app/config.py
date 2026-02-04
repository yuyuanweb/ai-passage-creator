"""配置管理 - 第 3 期：添加 AI 相关配置"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录（python-backend 目录）
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """应用配置（第 3 期：AI 核心创作流程）"""
    
    # 服务器配置
    server_port: int = 8567
    server_host: str = "0.0.0.0"
    
    # 数据库配置
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str
    
    # Redis 配置
    redis_host: str
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Session 配置
    session_secret_key: str
    session_max_age: int = 2592000  # 30 天
    
    # 密码加密盐值
    password_salt: str
    
    # AI 配置（第 3 期新增）
    dashscope_api_key: str
    dashscope_model: str = "qwen-plus"
    
    # Pexels 图片搜索（第 3 期新增）
    pexels_api_key: str
    
    # 腾讯云 COS（第 3 期新增）
    tencent_cos_secret_id: str
    tencent_cos_secret_key: str
    tencent_cos_region: str
    tencent_cos_bucket: str
    tencent_cos_domain: str = ""
    
    # Nano Banana / Gemini AI 生图（第 5 期新增）
    nano_banana_api_key: str
    nano_banana_model: str = "gemini-2.5-flash-image"
    nano_banana_aspect_ratio: str = "16:9"
    nano_banana_image_size: str = "1K"
    nano_banana_output_mime_type: str = "image/png"
    
    # Mermaid 配置（第 5 期新增）
    mermaid_cli_command: str = "mmdc"
    mermaid_background_color: str = "transparent"
    mermaid_output_format: str = "svg"
    mermaid_width: int = 1200
    mermaid_timeout: int = 30000
    
    # Iconify 配置（第 5 期新增）
    iconify_api_url: str = "https://api.iconify.design"
    iconify_search_limit: int = 10
    iconify_default_height: int = 64
    iconify_default_color: str = ""
    
    # 表情包配置（第 5 期新增）
    emoji_pack_search_url: str = "https://cn.bing.com/images/async"
    emoji_pack_suffix: str = "表情包"
    emoji_pack_timeout: int = 10000
    
    # SVG 示意图配置（第 5 期新增）
    svg_diagram_default_width: int = 800
    svg_diagram_default_height: int = 600
    svg_diagram_folder: str = "svg-diagrams"
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
    
    @property
    def redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
