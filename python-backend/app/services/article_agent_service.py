"""文章智能体编排服务"""

import json
import logging
from typing import Callable, List
from openai import AsyncOpenAI

from app.config import settings
from app.constants.prompt import PromptConstant
from app.schemas.article import (
    ArticleState,
    TitleResult,
    OutlineResult,
    OutlineSection,
    ImageRequirement,
    ImageResult
)
from app.models.enums import SseMessageTypeEnum, ImageMethodEnum
from app.services.pexels_service import PexelsService
from app.services.cos_service import CosService

logger = logging.getLogger(__name__)


class ArticleAgentService:
    """文章智能体编排服务"""
    
    def __init__(self):
        # 初始化 OpenAI 客户端（DashScope 兼容）
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = settings.dashscope_model
        
        # 初始化服务
        self.pexels_service = PexelsService()
        self.cos_service = CosService()
    
    async def execute_article_generation(
        self,
        state: ArticleState,
        stream_handler: Callable[[str], None]
    ):
        """
        执行完整的文章生成流程
        
        Args:
            state: 文章状态
            stream_handler: 流式输出处理器
        """
        try:
            # 智能体1：生成标题
            logger.info(f"智能体1：开始生成标题, taskId={state.task_id}")
            await self.agent1_generate_title(state)
            stream_handler(SseMessageTypeEnum.AGENT1_COMPLETE.value)
            
            # 智能体2：生成大纲（流式输出）
            logger.info(f"智能体2：开始生成大纲, taskId={state.task_id}")
            await self.agent2_generate_outline(state, stream_handler)
            stream_handler(SseMessageTypeEnum.AGENT2_COMPLETE.value)
            
            # 智能体3：生成正文（流式输出）
            logger.info(f"智能体3：开始生成正文, taskId={state.task_id}")
            await self.agent3_generate_content(state, stream_handler)
            stream_handler(SseMessageTypeEnum.AGENT3_COMPLETE.value)
            
            # 智能体4：分析配图需求
            logger.info(f"智能体4：开始分析配图需求, taskId={state.task_id}")
            await self.agent4_analyze_image_requirements(state)
            stream_handler(SseMessageTypeEnum.AGENT4_COMPLETE.value)
            
            # 智能体5：生成配图
            logger.info(f"智能体5：开始生成配图, taskId={state.task_id}")
            await self.agent5_generate_images(state, stream_handler)
            stream_handler(SseMessageTypeEnum.AGENT5_COMPLETE.value)
            
            # 图文合成：将配图插入正文
            logger.info(f"开始图文合成, taskId={state.task_id}")
            self.merge_images_into_content(state)
            stream_handler(SseMessageTypeEnum.MERGE_COMPLETE.value)
            
            logger.info(f"文章生成完成, taskId={state.task_id}")
        except Exception as e:
            logger.error(f"文章生成失败, taskId={state.task_id}, error={e}")
            raise RuntimeError(f"文章生成失败: {str(e)}")
    
    async def agent1_generate_title(self, state: ArticleState):
        """智能体1：生成标题"""
        prompt = PromptConstant.AGENT1_TITLE_PROMPT.replace("{topic}", state.topic)
        
        content = await self._call_llm(prompt)
        title_data = self._parse_json_response(content, "标题")
        state.title = TitleResult(**title_data)
        logger.info(f"智能体1：标题生成成功, mainTitle={state.title.main_title}")
    
    async def agent2_generate_outline(
        self,
        state: ArticleState,
        stream_handler: Callable[[str], None]
    ):
        """智能体2：生成大纲（流式输出）"""
        prompt = (
            PromptConstant.AGENT2_OUTLINE_PROMPT
            .replace("{mainTitle}", state.title.main_title)
            .replace("{subTitle}", state.title.sub_title)
        )
        
        content = await self._call_llm_with_streaming(
            prompt, stream_handler, SseMessageTypeEnum.AGENT2_STREAMING
        )
        outline_data = self._parse_json_response(content, "大纲")
        sections = [OutlineSection(**section) for section in outline_data["sections"]]
        state.outline = OutlineResult(sections=sections)
        logger.info(f"智能体2：大纲生成成功, sections={len(state.outline.sections)}")
    
    async def agent3_generate_content(
        self,
        state: ArticleState,
        stream_handler: Callable[[str], None]
    ):
        """智能体3：生成正文（流式输出）"""
        outline_text = json.dumps(
            [section.model_dump() for section in state.outline.sections],
            ensure_ascii=False
        )
        prompt = (
            PromptConstant.AGENT3_CONTENT_PROMPT
            .replace("{mainTitle}", state.title.main_title)
            .replace("{subTitle}", state.title.sub_title)
            .replace("{outline}", outline_text)
        )
        
        content = await self._call_llm_with_streaming(
            prompt, stream_handler, SseMessageTypeEnum.AGENT3_STREAMING
        )
        state.content = content
        logger.info(f"智能体3：正文生成成功, length={len(content)}")
    
    async def agent4_analyze_image_requirements(self, state: ArticleState):
        """智能体4：分析配图需求"""
        prompt = (
            PromptConstant.AGENT4_IMAGE_REQUIREMENTS_PROMPT
            .replace("{mainTitle}", state.title.main_title)
            .replace("{content}", state.content)
        )
        
        content = await self._call_llm(prompt)
        requirements_data = self._parse_json_response(content, "配图需求", is_list=True)
        state.image_requirements = [ImageRequirement(**req) for req in requirements_data]
        logger.info(f"智能体4：配图需求分析成功, count={len(state.image_requirements)}")
    
    async def agent5_generate_images(
        self,
        state: ArticleState,
        stream_handler: Callable[[str], None]
    ):
        """智能体5：生成配图（串行执行）"""
        image_results = []
        
        for requirement in state.image_requirements:
            logger.info(
                f"智能体5：开始检索配图, position={requirement.position}, "
                f"keywords={requirement.keywords}"
            )
            
            # 调用图片检索服务
            image_url = await self.pexels_service.search_image(requirement.keywords)
            
            # 降级策略
            method = self.pexels_service.get_method()
            if image_url is None:
                image_url = self.pexels_service.get_fallback_image(requirement.position)
                method = ImageMethodEnum.PICSUM
                logger.warning(f"智能体5：图片检索失败, 使用降级方案, position={requirement.position}")
            
            # 使用图片直接 URL（MVP 阶段不上传到 COS，简化流程）
            final_image_url = self.cos_service.use_direct_url(image_url)
            
            # 创建配图结果
            image_result = self._build_image_result(requirement, final_image_url, method)
            image_results.append(image_result)
            
            # 推送单张配图完成
            image_complete_message = (
                SseMessageTypeEnum.IMAGE_COMPLETE.get_streaming_prefix() +
                image_result.model_dump_json(by_alias=True)
            )
            stream_handler(image_complete_message)
            
            logger.info(
                f"智能体5：配图检索成功, position={requirement.position}, "
                f"method={method.value}"
            )
        
        state.images = image_results
        logger.info(f"智能体5：所有配图生成完成, count={len(image_results)}")
    
    def merge_images_into_content(self, state: ArticleState):
        """图文合成：将配图插入正文对应位置"""
        content = state.content
        images = state.images
        
        if not images:
            state.full_content = content
            return
        
        full_content_lines = []
        
        # 按行处理正文，在章节标题后插入对应图片
        lines = content.split("\n")
        for line in lines:
            full_content_lines.append(line)
            
            if line.startswith("## "):
                section_title = line[3:].strip()
                self._insert_image_after_section(full_content_lines, images, section_title)
        
        state.full_content = "\n".join(full_content_lines)
        logger.info(f"图文合成完成, fullContentLength={len(state.full_content)}")
    
    # region 辅助方法
    
    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM（非流式）"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    async def _call_llm_with_streaming(
        self,
        prompt: str,
        stream_handler: Callable[[str], None],
        message_type: SseMessageTypeEnum
    ) -> str:
        """调用 LLM（流式输出）"""
        content_builder = []
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_builder.append(content)
                stream_handler(message_type.get_streaming_prefix() + content)
        
        return "".join(content_builder)
    
    def _parse_json_response(self, content: str, name: str, is_list: bool = False) -> dict or list:
        """解析 JSON 响应"""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"{name}解析失败, content={content}, error={e}")
            raise RuntimeError(f"{name}解析失败")
    
    def _build_image_result(
        self,
        requirement: ImageRequirement,
        image_url: str,
        method: ImageMethodEnum
    ) -> ImageResult:
        """构建配图结果"""
        return ImageResult(
            position=requirement.position,
            url=image_url,
            method=method.value,
            keywords=requirement.keywords,
            sectionTitle=requirement.section_title,
            description=requirement.type
        )
    
    def _insert_image_after_section(
        self,
        full_content_lines: List[str],
        images: List[ImageResult],
        section_title: str
    ):
        """在章节标题后插入对应图片"""
        for image in images:
            if (image.position > 1 and 
                image.section_title and 
                section_title in image.section_title.strip()):
                full_content_lines.append(f"\n![{image.description}]({image.url})")
                break
    
    # endregion
