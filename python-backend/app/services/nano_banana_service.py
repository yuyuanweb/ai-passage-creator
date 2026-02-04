"""Nano Banana (Gemini 原生图片生成) 服务（第 5 期新增）"""

import logging
from typing import Optional
from google import genai
from google.genai import types

from app.config import settings
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService
from app.schemas.image import ImageData, ImageRequest

logger = logging.getLogger(__name__)


class NanoBananaService(ImageSearchService):
    """Nano Banana (Gemini 原生图片生成) 服务"""
    
    def __init__(self):
        self.api_key = settings.nano_banana_api_key
        self.model = settings.nano_banana_model
        self.aspect_ratio = settings.nano_banana_aspect_ratio
        self.image_size = settings.nano_banana_image_size
        # 初始化 Gemini 客户端
        self.client = genai.Client(api_key=self.api_key)
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """此方法已废弃，请使用 get_image_data()"""
        return None
    
    async def get_image_data(self, request: ImageRequest) -> Optional[ImageData]:
        """获取图片数据"""
        prompt = request.get_effective_param(True)
        return await self.generate_image_data(prompt)
    
    async def generate_image_data(self, prompt: str) -> Optional[ImageData]:
        """
        根据提示词生成图片数据
        
        Args:
            prompt: 生图提示词
            
        Returns:
            ImageData 包含图片字节数据，生成失败返回 None
        """
        try:
            # 构建图片配置
            image_config_params = {"aspect_ratio": self.aspect_ratio}
            
            # Gemini 3 Pro Image 支持更高分辨率
            if self.model and "gemini-3-pro" in self.model:
                image_config_params["image_size"] = self.image_size
            
            # 使用 types.ImageConfig 构建配置对象
            image_config = types.ImageConfig(**image_config_params)
            
            # 构建生成配置
            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=image_config
            )
            
            logger.info(f"Nano Banana 开始生成图片, model={self.model}, prompt={prompt}")
            
            # 调用 Gemini API 生成图片
            response = self.client.models.generate_content(
                model=self.model or "gemini-2.5-flash-image",
                contents=prompt,
                config=config
            )
            
            # 从响应中提取图片数据
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        image_bytes = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "image/png"
                        
                        logger.info(
                            f"Nano Banana 图片生成成功, "
                            f"size={len(image_bytes)} bytes, mimeType={mime_type}"
                        )
                        
                        return ImageData.from_bytes(image_bytes, mime_type)
            
            logger.error("Nano Banana 响应中未找到图片数据")
            return None
        except Exception as e:
            logger.error(f"Nano Banana 生成图片异常: {e}")
            return None
    
    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        return ImageMethodEnum.NANO_BANANA
    
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
