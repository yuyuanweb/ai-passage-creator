"""SVG 概念示意图生成服务（第 5 期新增）"""

import logging
from typing import Optional
from openai import AsyncOpenAI

from app.config import settings
from app.constants.prompt import PromptConstant
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService
from app.schemas.image import ImageData, ImageRequest

logger = logging.getLogger(__name__)


class SvgDiagramService(ImageSearchService):
    """SVG 概念示意图生成服务"""
    
    def __init__(self):
        # 使用 DashScope
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = settings.dashscope_model
        self.default_width = settings.svg_diagram_default_width
        self.default_height = settings.svg_diagram_default_height
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """此方法已废弃，请使用 get_image_data()"""
        return None
    
    async def get_image_data(self, request: ImageRequest) -> Optional[ImageData]:
        """获取图片数据"""
        requirement = request.get_effective_param(True)
        return await self.generate_svg_diagram_data(requirement)
    
    async def generate_svg_diagram_data(self, requirement: str) -> Optional[ImageData]:
        """
        生成 SVG 概念示意图数据
        
        Args:
            requirement: 示意图需求描述
            
        Returns:
            ImageData 包含 SVG 字节数据，生成失败返回 None
        """
        if not requirement or not requirement.strip():
            logger.warning("SVG 图表需求为空")
            return None
        
        try:
            # 1. 调用 LLM 生成 SVG 代码
            svg_code = await self._call_llm_to_generate_svg(requirement)
            
            if not svg_code or not svg_code.strip():
                logger.error("LLM 未生成 SVG 代码")
                return None
            
            # 2. 验证 SVG 格式
            if not self._is_valid_svg(svg_code):
                logger.error("生成的 SVG 代码格式无效")
                return None
            
            # 3. 转换为字节数据
            svg_bytes = svg_code.encode('utf-8')
            
            logger.info(f"SVG 概念示意图生成成功, size={len(svg_bytes)} bytes")
            return ImageData.from_bytes(svg_bytes, "image/svg+xml")
        except Exception as e:
            logger.error(f"SVG 概念示意图生成异常, requirement={requirement}, error={e}")
            return None
    
    async def _call_llm_to_generate_svg(self, requirement: str) -> Optional[str]:
        """调用 LLM 生成 SVG 代码"""
        prompt = PromptConstant.SVG_DIAGRAM_GENERATION_PROMPT.replace(
            "{requirement}", requirement
        )
        
        logger.info("开始调用 LLM 生成 SVG 概念示意图")
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        svg_code = response.choices[0].message.content.strip()
        
        # 提取 SVG 代码（移除可能的 markdown 代码块标记）
        svg_code = self._extract_svg_code(svg_code)
        
        return svg_code
    
    def _extract_svg_code(self, content: str) -> str:
        """提取 SVG 代码（移除 markdown 代码块标记）"""
        content = content.strip()
        
        # 移除 markdown 代码块标记
        if content.startswith("```"):
            lines = content.split("\n")
            # 跳过第一行（```svg 或 ```）
            lines = lines[1:]
            # 移除最后的 ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)
        
        return content.strip()
    
    def _is_valid_svg(self, svg_code: str) -> bool:
        """验证 SVG 格式是否有效"""
        if not svg_code:
            return False
        
        svg_lower = svg_code.lower()
        
        # 检查是否包含 <svg 和 </svg> 标签
        has_svg_tag = "<svg" in svg_lower and "</svg>" in svg_lower
        
        # 检查是否包含 XML 声明（可选）
        has_xml_declaration = svg_code.strip().startswith("<?xml")
        
        # 至少要有 SVG 标签
        return has_svg_tag
    
    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        return ImageMethodEnum.SVG_DIAGRAM
    
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
