"""Iconify 图标库检索服务（第 5 期新增）"""

import logging
import httpx
from typing import Optional
from urllib.parse import quote

from app.config import settings
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService

logger = logging.getLogger(__name__)


class IconifyService(ImageSearchService):
    """Iconify 图标库检索服务（提供 275k+ 开源图标）"""
    
    def __init__(self):
        self.api_url = settings.iconify_api_url
        self.search_limit = settings.iconify_search_limit
        self.default_height = settings.iconify_default_height
        self.default_color = settings.iconify_default_color
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """搜索图标并返回 SVG URL"""
        if not keywords or not keywords.strip():
            logger.warning("Iconify 搜索关键词为空")
            return None
        
        try:
            # 1. 搜索图标
            search_url = self._build_search_url(keywords)
            search_result = await self._call_api(search_url)
            
            if not search_result:
                return None
            
            # 2. 解析结果，获取第一个图标
            icon_name = self._extract_first_icon(search_result)
            if not icon_name:
                logger.warning(f"Iconify 未检索到图标: {keywords}")
                return None
            
            # 3. 构建 SVG URL
            svg_url = self._build_svg_url(icon_name)
            logger.info(f"Iconify 图标检索成功: {keywords} -> {icon_name}")
            
            return svg_url
        except Exception as e:
            logger.error(f"Iconify 图标检索异常, keywords={keywords}, error={e}")
            return None
    
    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        return ImageMethodEnum.ICONIFY
    
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
    
    def _build_search_url(self, keywords: str) -> str:
        """构建搜索 URL"""
        encoded_keywords = quote(keywords)
        return f"{self.api_url}/search?query={encoded_keywords}&limit={self.search_limit}"
    
    async def _call_api(self, url: str) -> Optional[dict]:
        """调用 Iconify API"""
        try:
            response = await self.client.get(url)
            if response.status_code != 200:
                logger.error(f"Iconify API 调用失败: {response.status_code}")
                return None
            return response.json()
        except Exception as e:
            logger.error(f"Iconify API 调用异常: {e}")
            return None
    
    def _extract_first_icon(self, search_result: dict) -> Optional[str]:
        """从搜索结果中提取第一个图标名称"""
        try:
            icons = search_result.get("icons", [])
            if not icons:
                return None
            return icons[0]
        except Exception as e:
            logger.error(f"解析 Iconify 搜索结果失败: {e}")
            return None
    
    def _build_svg_url(self, icon_name: str) -> str:
        """
        构建 SVG URL
        
        Args:
            icon_name: 图标名称（格式：prefix:name，如 mdi:home）
            
        Returns:
            SVG URL
        """
        # 将 "mdi:home" 转换为 "mdi/home"
        path = icon_name.replace(":", "/")
        
        url = f"{self.api_url}/{path}.svg"
        
        # 添加参数
        params = []
        if self.default_height and self.default_height > 0:
            params.append(f"height={self.default_height}")
        
        if self.default_color and self.default_color.strip():
            color = self.default_color
            if color.startswith("#"):
                color = "%23" + color[1:]
            params.append(f"color={color}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
