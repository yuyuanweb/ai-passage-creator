"""文章智能体编排服务"""

import json
import logging
from typing import Callable, List, Optional
from openai import AsyncOpenAI

from app.config import settings
from app.constants.prompt import PromptConstant
from app.schemas.article import (
    ArticleState,
    TitleResult,
    OutlineResult,
    OutlineSection,
    ImageRequirement,
    ImageResult,
    Agent4Result
)
from app.schemas.image import ImageRequest
from app.models.enums import SseMessageTypeEnum, ImageMethodEnum, ArticleStyleEnum
from app.services.image_service_strategy import ImageServiceStrategy

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
        
        # 初始化策略模式（第 5 期改动）
        self.image_service_strategy = ImageServiceStrategy()
    
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
        prompt += self._get_style_prompt(state.style)  # 第 5 期新增：风格 Prompt

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
        prompt += self._get_style_prompt(state.style)  # 第 5 期新增：风格 Prompt

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
        prompt += self._get_style_prompt(state.style)  # 第 5 期新增：风格 Prompt

        content = await self._call_llm_with_streaming(
            prompt, stream_handler, SseMessageTypeEnum.AGENT3_STREAMING
        )
        state.content = content
        logger.info(f"智能体3：正文生成成功, length={len(content)}")
    
    async def agent4_analyze_image_requirements(self, state: ArticleState):
        """智能体4：分析配图需求（第 5 期：占位符方案）"""
        # 构建可用配图方式说明
        available_methods = self._build_available_methods_description(
            state.enabled_image_methods
        )
        # 构建各配图方式的详细使用指南
        method_usage_guide = self._build_method_usage_guide(
            state.enabled_image_methods
        )

        prompt = (
            PromptConstant.AGENT4_IMAGE_REQUIREMENTS_PROMPT
            .replace("{mainTitle}", state.title.main_title)
            .replace("{content}", state.content)
            .replace("{availableMethods}", available_methods)
            .replace("{methodUsageGuide}", method_usage_guide)
        )
        
        content = await self._call_llm(prompt)
        agent4_data = self._parse_json_response(content, "配图需求")
        agent4_result = Agent4Result(**agent4_data)

        # 更新正文为包含占位符的版本
        state.content = agent4_result.content_with_placeholders

        # 验证并过滤配图需求
        validated_requirements = self._validate_and_filter_image_requirements(
            agent4_result.image_requirements,
            state.enabled_image_methods
        )

        state.image_requirements = validated_requirements
        logger.info(
            f"智能体4：配图需求分析成功, count={len(agent4_result.image_requirements)}, "
            f"validated={len(validated_requirements)}, 已在正文中插入占位符"
        )
    
    async def agent5_generate_images(
        self,
        state: ArticleState,
        stream_handler: Callable[[str], None]
    ):
        """智能体5：生成配图（第 5 期：策略模式 + 统一上传 COS）"""
        image_results = []
        
        for requirement in state.image_requirements:
            image_source = requirement.image_source
            logger.info(
                f"智能体5：开始获取配图, position={requirement.position}, "
                f"imageSource={image_source}, keywords={requirement.keywords}"
            )
            
            # 构建图片请求对象
            image_request = ImageRequest(
                keywords=requirement.keywords,
                prompt=requirement.prompt,
                position=requirement.position,
                type=requirement.type
            )
            
            # 使用策略模式获取图片并统一上传到 COS
            result = await self.image_service_strategy.get_image_and_upload(
                image_source,
                image_request
            )
            
            cos_url = result.url
            method = result.method
            
            # 创建配图结果（URL 已经是 COS 地址）
            image_result = self._build_image_result(requirement, cos_url, method)
            image_results.append(image_result)
            
            # 推送单张配图完成
            image_complete_message = (
                SseMessageTypeEnum.IMAGE_COMPLETE.get_streaming_prefix() +
                image_result.model_dump_json(by_alias=True)
            )
            stream_handler(image_complete_message)
            
            logger.info(
                f"智能体5：配图获取并上传成功, position={requirement.position}, "
                f"method={method.value}, cosUrl={cos_url}"
            )
        
        state.images = image_results
        logger.info(f"智能体5：所有配图生成并上传完成, count={len(image_results)}")
    
    def merge_images_into_content(self, state: ArticleState):
        """图文合成：根据占位符将配图插入正文（第 5 期：占位符方案）"""
        content = state.content
        images = state.images
        
        if not images:
            state.full_content = content
            return
        
        full_content = content

        # 遍历所有配图，根据占位符替换为实际图片
        for image in images:
            placeholder = image.placeholder_id
            if placeholder:
                image_markdown = f"![{image.description}]({image.url})"
                full_content = full_content.replace(placeholder, image_markdown)
        
        state.full_content = full_content
        logger.info(f"图文合成完成, fullContentLength={len(full_content)}")
    
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
            description=requirement.type,
            placeholderId=requirement.placeholder_id  # 第 5 期新增
        )
    
    def _get_style_prompt(self, style: Optional[str]) -> str:
        """根据风格获取对应的 Prompt 附加内容（第 5 期新增）"""
        if not style:
            return ""

        try:
            style_enum = ArticleStyleEnum(style)
            style_map = {
                ArticleStyleEnum.TECH: PromptConstant.STYLE_TECH_PROMPT,
                ArticleStyleEnum.EMOTIONAL: PromptConstant.STYLE_EMOTIONAL_PROMPT,
                ArticleStyleEnum.EDUCATIONAL: PromptConstant.STYLE_EDUCATIONAL_PROMPT,
                ArticleStyleEnum.HUMOROUS: PromptConstant.STYLE_HUMOROUS_PROMPT,
            }
            return style_map.get(style_enum, "")
        except ValueError:
            return ""

    def _build_available_methods_description(
        self,
        enabled_methods: Optional[List[str]]
    ) -> str:
        """构建可用配图方式说明"""
        # 如果为空或 None，表示支持所有方式
        if not enabled_methods:
            return self._get_all_methods_description()

        # 只描述允许的方式
        descriptions = []
        for method_str in enabled_methods:
            try:
                method = ImageMethodEnum(method_str)
                if not method.is_fallback():
                    desc = self._get_method_usage_description(method)
                    descriptions.append(f"   - {method.value}: {desc}")
            except ValueError:
                continue

        return "\n".join(descriptions)

    def _get_all_methods_description(self) -> str:
        """获取所有配图方式的完整描述"""
        return """   - PEXELS: 适合真实场景、产品照片、人物照片、自然风景等写实图片
   - NANO_BANANA: 适合创意插画、信息图表、需要文字渲染、抽象概念、艺术风格等 AI 生成图片
   - MERMAID: 适合流程图、架构图、时序图、关系图、甘特图等结构化图表
   - ICONIFY: 适合图标、符号、小型装饰性图标（如：箭头、勾选、星星、心形等）
   - EMOJI_PACK: 适合表情包、搞笑图片、轻松幽默的配图
   - SVG_DIAGRAM: 适合概念示意图、思维导图样式、逻辑关系展示（不涉及精确数据）"""

    def _get_method_usage_description(self, method: ImageMethodEnum) -> str:
        """获取配图方式的使用说明"""
        descriptions = {
            ImageMethodEnum.PEXELS: "适合真实场景、产品照片、人物照片、自然风景等写实图片",
            ImageMethodEnum.NANO_BANANA: "适合创意插画、信息图表、需要文字渲染、抽象概念、艺术风格等 AI 生成图片",
            ImageMethodEnum.MERMAID: "适合流程图、架构图、时序图、关系图、甘特图等结构化图表",
            ImageMethodEnum.ICONIFY: "适合图标、符号、小型装饰性图标（如：箭头、勾选、星星、心形等）",
            ImageMethodEnum.EMOJI_PACK: "适合表情包、搞笑图片、轻松幽默的配图",
            ImageMethodEnum.SVG_DIAGRAM: "适合概念示意图、思维导图样式、逻辑关系展示（不涉及精确数据）",
        }
        return descriptions.get(method, method.value)

    def _build_method_usage_guide(
        self,
        enabled_methods: Optional[List[str]]
    ) -> str:
        """构建配图方式的详细使用指南"""
        # 如果没有限制，返回所有方式的使用指南
        methods_to_include = enabled_methods if enabled_methods else [
            "PEXELS", "NANO_BANANA", "MERMAID", "ICONIFY", "EMOJI_PACK", "SVG_DIAGRAM"
        ]

        guides = []
        for method_str in methods_to_include:
            guide = self._get_method_detailed_guide(method_str)
            if guide:
                guides.append(guide)

        return "\n".join(guides)

    def _get_method_detailed_guide(self, method_str: str) -> str:
        """获取单个配图方式的详细使用指南"""
        guides = {
            "PEXELS": "- PEXELS: 提供英文搜索关键词(keywords)，要准确、具体。prompt 留空。",
            "NANO_BANANA": "- NANO_BANANA: 提供详细的英文生图提示词(prompt)，描述场景、风格、细节。keywords 留空。",
            "MERMAID": "- MERMAID: 在 prompt 字段生成完整的 Mermaid 代码（如流程图、架构图）。keywords 留空。",
            "ICONIFY": "- ICONIFY: 提供英文图标关键词(keywords)，如：check、arrow、star、heart。prompt 留空。",
            "EMOJI_PACK": "- EMOJI_PACK: 提供中文或英文关键词(keywords)描述表情内容。prompt 留空。系统会自动添加'表情包'搜索。",
            "SVG_DIAGRAM": "- SVG_DIAGRAM: 在 prompt 字段描述示意图需求（中文），说明要表达的概念和关系。keywords 留空。\n  示例：绘制思维导图样式的图，中心是'自律'，周围4个分支：习惯、环境、反馈、系统",
        }
        return guides.get(method_str, "")

    def _validate_and_filter_image_requirements(
        self,
        requirements: List[ImageRequirement],
        enabled_methods: Optional[List[str]]
    ) -> List[ImageRequirement]:
        """验证并过滤配图需求"""
        # 如果没有限制，返回所有需求
        if not enabled_methods:
            return requirements

        validated_requirements = []

        for req in requirements:
            image_source = req.image_source

            # 验证 imageSource 是否在允许列表中
            if image_source in enabled_methods:
                validated_requirements.append(req)
                logger.debug(f"配图需求验证通过, position={req.position}, imageSource={image_source}")
            else:
                logger.warning(
                    f"配图需求不符合限制被过滤, position={req.position}, "
                    f"imageSource={image_source}, enabledMethods={enabled_methods}"
                )

                # 尝试替换为允许的方式（优先使用第一个允许的方式）
                if enabled_methods:
                    fallback_source = enabled_methods[0]
                    req.image_source = fallback_source
                    validated_requirements.append(req)
                    logger.info(
                        f"配图需求已替换为允许的方式, position={req.position}, "
                        f"fallback={fallback_source}"
                    )

        return validated_requirements
    
    # endregion
