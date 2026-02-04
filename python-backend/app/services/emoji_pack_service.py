"""表情包检索服务（第 5 期新增）"""

import logging
import httpx
from typing import Optional
from urllib.parse import quote
from bs4 import BeautifulSoup

from app.config import settings
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService

logger = logging.getLogger(__name__)


class EmojiPackService(ImageSearchService):
    """表情包检索服务（基于 Bing 图片搜索）"""
    
    def __init__(self):
        self.search_url = settings.emoji_pack_search_url
        self.suffix = settings.emoji_pack_suffix
        self.timeout = settings.emoji_pack_timeout / 1000  # 转为秒
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """搜索表情包"""
        if not keywords or not keywords.strip():
            logger.warning("表情包搜索关键词为空")
            return None
        
        try:
            # 1. 构建搜索词（程序固定拼接"表情包"）
            search_text = keywords + self.suffix
            logger.info(f"表情包搜索: {keywords} -> {search_text}")
            
            # 2. 构建搜索 URL
            fetch_url = self._build_search_url(search_text)
            
            # 3. 获取页面
            response = await self.client.get(fetch_url)
            if response.status_code != 200:
                logger.error(f"Bing 搜索失败: {response.status_code}")
                return None
            
            # 4. 解析 HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 5. 定位图片容器
            div = soup.find('div', class_='dgControl')
            if not div:
                logger.warning(f"Bing 未找到图片容器, keywords={keywords}")
                return None
            
            # 6. 使用 CSS 选择器提取图片
            img_elements = div.select('img.mimg')
            if not img_elements:
                logger.warning(f"Bing 未检索到表情包, keywords={keywords}, searchText={search_text}")
                return None
            
            # 7. 获取第一张图片 URL
            image_url = img_elements[0].get('src')
            if not image_url or not image_url.strip():
                logger.warning(f"图片 URL 为空, keywords={keywords}")
                return None
            
            # 8. 清理 URL 参数（移除 ?w=xxx&h=xxx）
            image_url = self._clean_image_url(image_url)
            
            logger.info(f"表情包检索成功: {keywords} -> {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"表情包检索异常, keywords={keywords}, error={e}")
            return None
    
    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        return ImageMethodEnum.EMOJI_PACK
    
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
    
    def _build_search_url(self, search_text: str) -> str:
        """构建 Bing 图片搜索 URL"""
        encoded_text = quote(search_text)
        # 必须添加 mmasync=1 参数
        return f"{self.search_url}?q={encoded_text}&mmasync=1"
    
    def _clean_image_url(self, url: str) -> str:
        """
        清理图片 URL 参数
        移除 ?w=xxx&h=xxx 等参数，避免图片质量下降
        """
        if not url or not url.strip():
            return url
        
        question_mark_index = url.find("?")
        if question_mark_index > 0:
            return url[:question_mark_index]
        
        return url
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
