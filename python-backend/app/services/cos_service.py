"""腾讯云 COS 服务"""

import logging
import httpx
from typing import Optional
from qcloud_cos import CosConfig, CosS3Client
from io import BytesIO

from app.config import settings

logger = logging.getLogger(__name__)


class CosService:
    """腾讯云 COS 服务"""
    
    def __init__(self):
        # 初始化 COS 客户端
        config = CosConfig(
            Region=settings.tencent_cos_region,
            SecretId=settings.tencent_cos_secret_id,
            SecretKey=settings.tencent_cos_secret_key,
            Scheme='https'
        )
        self.client = CosS3Client(config)
        self.bucket = settings.tencent_cos_bucket
        self.region = settings.tencent_cos_region
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def upload_image(self, image_url: str, folder: str) -> str:
        """
        上传图片到 COS
        
        Args:
            image_url: 图片 URL
            folder: 文件夹
            
        Returns:
            COS 图片 URL
        """
        try:
            # 下载图片
            response = await self.http_client.get(image_url)
            if response.status_code != 200:
                logger.error(f"下载图片失败: {image_url}")
                return image_url  # 降级：直接返回原始 URL
            
            image_bytes = response.content
            
            # 生成文件名
            import uuid
            file_name = f"{folder}/{uuid.uuid4()}.jpg"
            
            # 上传到 COS
            self.client.put_object(
                Bucket=self.bucket,
                Body=BytesIO(image_bytes),
                Key=file_name,
                ContentType='image/jpeg'
            )
            
            # 返回访问 URL
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{file_name}"
        except Exception as e:
            logger.error(f"上传图片到 COS 失败: {e}")
            return image_url  # 降级：直接返回原始 URL
    
    def use_direct_url(self, image_url: str) -> str:
        """
        直接使用图片 URL（不上传到 COS）
        
        Args:
            image_url: 图片 URL
            
        Returns:
            图片 URL
        """
        return image_url
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.http_client.aclose()
