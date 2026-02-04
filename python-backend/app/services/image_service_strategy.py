"""图片服务策略选择器（第 5 期新增）"""

import logging
from typing import Dict, List, Optional

from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService
from app.services.pexels_service import PexelsService
from app.services.nano_banana_service import NanoBananaService
from app.services.mermaid_service import MermaidService
from app.services.iconify_service import IconifyService
from app.services.emoji_pack_service import EmojiPackService
from app.services.svg_diagram_service import SvgDiagramService
from app.services.cos_service import CosService
from app.schemas.image import ImageRequest, ImageData
from app.constants.article import ArticleConstant

logger = logging.getLogger(__name__)


class ImageResult:
    """图片获取结果"""
    
    def __init__(self, url: str, method: ImageMethodEnum):
        self.url = url
        self.method = method
    
    def is_success(self) -> bool:
        """判断是否成功"""
        return self.url is not None and len(self.url) > 0


class ImageServiceStrategy:
    """
    图片服务策略选择器
    根据图片来源类型选择对应的图片服务实现
    """
    
    def __init__(self):
        # 初始化所有图片服务
        self.service_map: Dict[ImageMethodEnum, ImageSearchService] = {}
        self.cos_service = CosService()
        
        # 注册所有服务
        self._register_services()
    
    def _register_services(self):
        """注册所有图片服务"""
        services = [
            PexelsService(),
            NanoBananaService(),
            MermaidService(),
            IconifyService(),
            EmojiPackService(),
            SvgDiagramService(),
        ]
        
        for service in services:
            method = service.get_method()
            self.service_map[method] = service
            logger.info(
                f"注册图片服务: {method.value} -> {service.__class__.__name__} "
                f"(AI生图: {method.is_ai_generated()}, 降级: {method.is_fallback()})"
            )
    
    async def get_image_and_upload(
        self,
        image_source: str,
        request: ImageRequest
    ) -> ImageResult:
        """
        获取图片并上传到 COS（推荐方法）
        统一处理所有图片来源的上传逻辑
        
        Args:
            image_source: 图片来源
            request: 图片请求对象
            
        Returns:
            图片获取结果（包含 COS URL）
        """
        method = self._resolve_method(image_source)
        service = self.service_map.get(method)
        
        if service is None or not service.is_available():
            logger.warning(f"图片服务不可用: {method}, 尝试降级")
            return await self._handle_fallback_with_upload(request.position)
        
        try:
            # 1. 获取图片数据
            image_data = await service.get_image_data(request)
            
            if image_data is None or not image_data.is_valid():
                logger.warning(f"图片数据获取失败, 使用降级方案, method={method}")
                return await self._handle_fallback_with_upload(request.position)
            
            # 2. 上传到 COS
            folder = self._get_folder_for_method(method)
            cos_url = await self.cos_service.upload_image_data(image_data, folder)
            
            if cos_url:
                logger.info(f"图片获取并上传成功, method={method}, cosUrl={cos_url}")
                return ImageResult(cos_url, method)
            else:
                logger.warning(f"图片上传 COS 失败, 使用降级方案, method={method}")
                return await self._handle_fallback_with_upload(request.position)
        except Exception as e:
            logger.error(f"获取图片并上传异常, method={method}, error={e}")
            return await self._handle_fallback_with_upload(request.position)
    
    def _resolve_method(self, image_source: str) -> ImageMethodEnum:
        """解析图片来源，处理未知值"""
        try:
            return ImageMethodEnum(image_source)
        except ValueError:
            logger.warning(
                f"未知的图片来源: {image_source}, "
                f"默认使用 {ImageMethodEnum.get_default_search_method().value}"
            )
            return ImageMethodEnum.get_default_search_method()
    
    async def _handle_fallback_with_upload(self, position: Optional[int]) -> ImageResult:
        """处理降级逻辑"""
        pos = position if position else 1
        fallback_url = self._get_fallback_image(pos)
        
        # 将降级图片也上传到 COS
        fallback_data = ImageData.from_url(fallback_url)
        cos_url = await self.cos_service.upload_image_data(fallback_data, "fallback")
        
        # 如果上传失败，直接使用原始 URL
        final_url = cos_url if cos_url else fallback_url
        return ImageResult(final_url, ImageMethodEnum.get_fallback_method())
    
    def _get_folder_for_method(self, method: ImageMethodEnum) -> str:
        """根据图片方法获取 COS 文件夹"""
        folder_map = {
            ImageMethodEnum.PEXELS: "pexels",
            ImageMethodEnum.NANO_BANANA: "nano-banana",
            ImageMethodEnum.MERMAID: "mermaid",
            ImageMethodEnum.ICONIFY: "iconify",
            ImageMethodEnum.EMOJI_PACK: "emoji-pack",
            ImageMethodEnum.SVG_DIAGRAM: "svg-diagram",
            ImageMethodEnum.PICSUM: "picsum",
        }
        return folder_map.get(method, "unknown")
    
    def _get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        # 优先使用已注册服务的降级方案
        default_service = self.service_map.get(ImageMethodEnum.get_default_search_method())
        if default_service:
            return default_service.get_fallback_image(position)
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
    
    def get_registered_methods(self) -> List[ImageMethodEnum]:
        """获取所有已注册的图片服务类型"""
        return list(self.service_map.keys())
