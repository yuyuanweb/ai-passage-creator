"""Mermaid 流程图生成服务（第 5 期新增）"""

import logging
import tempfile
import subprocess
from typing import Optional
from pathlib import Path

from app.config import settings
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService
from app.schemas.image import ImageData, ImageRequest

logger = logging.getLogger(__name__)


class MermaidService(ImageSearchService):
    """Mermaid 流程图生成服务"""
    
    def __init__(self):
        self.cli_command = settings.mermaid_cli_command
        self.background_color = settings.mermaid_background_color
        self.output_format = settings.mermaid_output_format
        self.width = settings.mermaid_width
        self.timeout = settings.mermaid_timeout / 1000  # 转为秒
    
    async def search_image(self, keywords: str) -> Optional[str]:
        """此方法已废弃，请使用 get_image_data()"""
        return None
    
    async def get_image(self, request: ImageRequest) -> Optional[str]:
        """此方法已废弃，请使用 get_image_data()"""
        return None
    
    async def get_image_data(self, request: ImageRequest) -> Optional[ImageData]:
        """获取图片数据"""
        # 优先使用 prompt（Mermaid 代码），否则使用 keywords
        mermaid_code = request.get_effective_param(True)
        return await self.generate_diagram_data(mermaid_code)
    
    async def generate_diagram_data(self, mermaid_code: str) -> Optional[ImageData]:
        """
        生成 Mermaid 图表数据
        
        Args:
            mermaid_code: Mermaid 代码
            
        Returns:
            图片字节数据，生成失败返回 None
        """
        if not mermaid_code or not mermaid_code.strip():
            logger.warning("Mermaid 代码为空")
            return None
        
        temp_input_file = None
        temp_output_file = None
        
        try:
            # 创建临时输入文件
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.mmd',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(mermaid_code)
                temp_input_file = f.name
            
            # 创建临时输出文件
            output_extension = f".{self.output_format}"
            with tempfile.NamedTemporaryFile(
                suffix=output_extension,
                delete=False
            ) as f:
                temp_output_file = f.name
            
            # 转换为图片
            await self._convert_mermaid_to_image(temp_input_file, temp_output_file)
            
            # 读取生成的图片
            with open(temp_output_file, 'rb') as f:
                image_bytes = f.read()
            
            # 确定 MIME 类型
            mime_type = self._get_mime_type()
            
            logger.info(
                f"Mermaid 图表生成成功, size={len(image_bytes)} bytes, "
                f"format={self.output_format}"
            )
            
            return ImageData.from_bytes(image_bytes, mime_type)
        except Exception as e:
            logger.error(f"Mermaid 图表生成异常: {e}")
            return None
        finally:
            # 清理临时文件
            if temp_input_file:
                Path(temp_input_file).unlink(missing_ok=True)
            if temp_output_file:
                Path(temp_output_file).unlink(missing_ok=True)
    
    async def _convert_mermaid_to_image(self, input_file: str, output_file: str):
        """转换 Mermaid 代码为图片"""
        cmd = [
            self.cli_command,
            '-i', input_file,
            '-o', output_file,
            '-b', self.background_color,
            '-w', str(self.width)
        ]
        
        logger.info(f"执行 Mermaid 转换命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            timeout=self.timeout,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Mermaid 转换失败: {result.stderr}")
    
    def _get_mime_type(self) -> str:
        """根据输出格式获取 MIME 类型"""
        format_lower = self.output_format.lower()
        if format_lower == "png":
            return "image/png"
        elif format_lower == "svg":
            return "image/svg+xml"
        elif format_lower == "pdf":
            return "application/pdf"
        else:
            return "image/png"
    
    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        return ImageMethodEnum.MERMAID
    
    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
    
    def is_available(self) -> bool:
        """检查 mmdc 命令是否可用"""
        try:
            result = subprocess.run(
                [self.cli_command, '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
