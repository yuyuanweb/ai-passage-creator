"""Pexels 图片检索服务"""

import httpx
import logging
from typing import Optional

from app.config import settings
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService

logger = logging.getLogger(__name__)


class PexelsService(ImageSearchService):
    """Pexels 图片检索服务"""
    
    def __init__(self):
        self.api_key = settings.pexels_api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """
        搜索图片
        
        Args:
            keywords: 搜索关键词
            
        Returns:
            图片 URL，未找到返回 None
        """
        try:
            url = self._build_search_url(keywords)
            
            headers = {"Authorization": self.api_key}
            response = await self.client.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Pexels API 调用失败: {response.status_code}")
                return None
            
            return self._extract_image_url(response.json(), keywords)
        except Exception as e:
            logger.error(f"Pexels API 调用异常: {e}")
            return None
    
    def get_method(self) -> ImageMethodEnum:
        """获取配图方式"""
        return ImageMethodEnum.PEXELS
    
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
    
    def _build_search_url(self, keywords: str) -> str:
        """构建搜索 URL"""
        return (
            f"{ArticleConstant.PEXELS_API_URL}"
            f"?query={keywords}"
            f"&per_page={ArticleConstant.PEXELS_PER_PAGE}"
            f"&orientation={ArticleConstant.PEXELS_ORIENTATION_LANDSCAPE}"
        )
    
    def _extract_image_url(self, response_data: dict, keywords: str) -> Optional[str]:
        """从响应中提取图片 URL"""
        photos = response_data.get("photos", [])
        
        if not photos:
            logger.warning(f"Pexels 未检索到图片: {keywords}")
            return None
        
        photo = photos[0]
        src = photo.get("src", {})
        return src.get("large")
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
