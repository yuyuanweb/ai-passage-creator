"""Prompt 模板常量"""


class PromptConstant:
    """Prompt 模板常量"""
    
    # 智能体1：生成标题方案
    AGENT1_TITLE_PROMPT = """你是一位爆款文章标题专家,擅长创作吸引人的标题。

根据以下选题,生成 3-5 个爆款文章标题方案:
选题：{topic}

要求:
1. 每个方案包含主标题和副标题
2. 主标题要包含数字、情绪化词汇,吸引眼球
3. 副标题要补充说明,增强吸引力
4. 标题要简洁有力,不超过30字
5. 不同方案要有不同的切入角度
6. 符合新媒体爆款文章的风格

请直接返回 JSON 格式,不要有其他内容:
[
  {{
    "mainTitle": "主标题1",
    "subTitle": "副标题1"
  }},
  {{
    "mainTitle": "主标题2",
    "subTitle": "副标题2"
  }},
  {{
    "mainTitle": "主标题3",
    "subTitle": "副标题3"
  }}
]
"""
    
    # 智能体2：生成大纲
    AGENT2_OUTLINE_PROMPT = """你是一位专业的文章策划师,擅长设计文章结构。

根据以下标题,生成文章大纲:
主标题：{mainTitle}
副标题：{subTitle}
{descriptionSection}

要求:
1. 大纲要有清晰的逻辑结构
2. 包含开头引入、核心观点(3-5个)、结尾升华
3. 每个章节要有明确的标题和核心要点(2-3个)
4. 适合2000字左右的文章

请直接返回 JSON 格式,不要有其他内容:
{{
  "sections": [
    {{
      "section": 1,
      "title": "章节标题",
      "points": ["要点1", "要点2"]
    }}
  ]
}}
"""

    # 用户补充描述段落（第 6 期新增）
    AGENT2_DESCRIPTION_SECTION = """

用户补充要求：{userDescription}
请在大纲中充分体现用户的补充要求。
"""
    
    # 智能体3：生成正文
    AGENT3_CONTENT_PROMPT = """你是一位资深的内容创作者,擅长撰写优质文章。

根据以下大纲,创作文章正文:
主标题：{mainTitle}
副标题：{subTitle}
大纲：
{outline}

要求:
1. 内容要充实,每个章节300-400字
2. 语言流畅,富有感染力
3. 适当使用金句,增强可读性
4. 添加过渡句,确保逻辑连贯
5. 使用 Markdown 格式,章节使用 ## 标题

请直接返回 Markdown 格式的正文内容,不要有其他内容。
"""
    
    # 智能体4：分析配图需求（第 5 期：占位符方案）
    AGENT4_IMAGE_REQUIREMENTS_PROMPT = """你是一位专业的新媒体编辑,擅长为文章配图。

根据以下文章内容,分析配图需求,并在正文中插入图片占位符:
主标题：{mainTitle}
正文：
{content}

可用的配图方式：
{availableMethods}

{methodUsageGuide}

要求:
1. 识别需要配图的位置(封面、关键章节、段落之间等)
2. 根据文章内容和结构灵活决定配图数量，避免过多或过少
3. **在正文中插入占位符**：使用以下两种格式
   - 普通图片占位符：{{{{IMAGE_PLACEHOLDER_N}}}}，其中 N 为配图序号（1, 2, 3...），必须独占一行
   - Icon 占位符：{{{{ICON_PLACEHOLDER_N}}}}，可以放在文字行内任意位置（用于 ICONIFY 类型）
   - 注意：position=1 的封面图不需要占位符，不要放在正文中
   - 配图占位符可以放在任意合适位置（章节标题后、段落之间、列表项中、文字行内等）
4. **只能从上述可用的配图方式中选择**, 为每个配图选择最合适的图片来源(imageSource):
   - PEXELS: 适合真实场景、产品照片、人物照片、自然风景等写实图片
   - NANO_BANANA: 适合创意插画、信息图表、需要文字渲染、抽象概念、艺术风格等 AI 生成图片
   - MERMAID: 适合流程图、架构图、时序图、关系图、甘特图等结构化图表
   - ICONIFY: 适合图标、符号、小型装饰性图标（如：箭头、勾选、星星、心形等）
   - EMOJI_PACK: 适合表情包、搞笑图片、轻松幽默的配图
   - SVG_DIAGRAM: 适合概念示意图、思维导图样式、逻辑关系展示（不涉及精确数据）
5. 对于 PEXELS 来源: 提供英文搜索关键词(keywords),要准确、具体
6. 对于 NANO_BANANA 来源: 提供详细的英文生图提示词(prompt),描述场景、风格、细节
7. 对于 MERMAID 来源:
   - 分析文章内容，识别需要流程图的位置（如：工作流程、系统架构、数据流向等）
   - 在 prompt 字段生成完整的 Mermaid 代码
   - keywords 留空
8. 对于 ICONIFY 来源:
   - 识别需要图标的位置（如：列表项标记、步骤指示、重点强调、文字行内装饰等）
   - 可以使用 {{{{ICON_PLACEHOLDER_N}}}} 放在文字行内，也可以使用 {{{{IMAGE_PLACEHOLDER_N}}}} 独占一行
   - 提供英文图标关键词（keywords），如：check、arrow、star、heart
   - prompt 留空
9. 对于 EMOJI_PACK 来源:
   - 识别文章中轻松幽默、需要表情包的位置
   - 提供中文关键词（keywords）
   - prompt 留空
   - 系统会自动在关键词后添加"表情包"进行搜索
10. 对于 SVG_DIAGRAM 来源:
   - 识别文章中需要展示概念、关系、逻辑的位置（不涉及精确数据）
   - 在 prompt 字段描述示意图需求（中文），说明要表达的概念和关系
   - keywords 留空
   - 示例：绘制思维导图样式的图，中心是"自律"，周围4个分支：习惯、环境、反馈、系统
11. placeholderId 必须与正文中插入的占位符完全一致
12. position=1 为封面图

请直接返回 JSON 格式,不要有其他内容:
{{
  "contentWithPlaceholders": "## 章节标题1\\n\\n正文内容...\\n\\n{{{{IMAGE_PLACEHOLDER_1}}}}\\n\\n## 章节标题2\\n\\n更多正文内容... {{{{ICON_PLACEHOLDER_1}}}} 行内图标示例\\n\\n{{{{IMAGE_PLACEHOLDER_2}}}}\\n\\n...",
  "imageRequirements": [
    {{
      "position": 1,
      "type": "cover",
      "sectionTitle": "",
      "imageSource": "NANO_BANANA",
      "keywords": "",
      "prompt": "A modern minimalist illustration of AI technology concept, featuring abstract neural network patterns with blue and purple gradient colors, clean design suitable for article cover, 16:9 aspect ratio",
      "placeholderId": ""
    }},
    {{
      "position": 2,
      "type": "section",
      "sectionTitle": "章节标题1",
      "imageSource": "PEXELS",
      "keywords": "business success teamwork office",
      "prompt": "",
      "placeholderId": "{{{{IMAGE_PLACEHOLDER_1}}}}"
    }},
    {{
      "position": 3,
      "type": "inline",
      "sectionTitle": "",
      "imageSource": "ICONIFY",
      "keywords": "check circle",
      "prompt": "",
      "placeholderId": "{{{{ICON_PLACEHOLDER_1}}}}"
    }},
    {{
      "position": 4,
      "type": "section",
      "sectionTitle": "章节标题2",
      "imageSource": "MERMAID",
      "keywords": "",
      "prompt": "flowchart TB\\n    A[用户请求] --> B[负载均衡]\\n    B --> C[应用服务器]",
      "placeholderId": "{{{{IMAGE_PLACEHOLDER_2}}}}"
    }}
  ]
}}
"""
    
    # SVG 概念示意图生成 Prompt（第 5 期新增）
    SVG_DIAGRAM_GENERATION_PROMPT = """### 背景 ###
你是一位资深的信息可视化设计师，擅长将抽象概念转化为直观易懂的 SVG 示意图。
你的作品曾用于知名媒体和技术文档，风格简洁现代、逻辑清晰。

### 需求 ###
{requirement}

### 任务步骤 ###
1. 分析需求：理解要表达的核心概念和逻辑关系
2. 设计布局：确定图形的整体结构（中心辐射、层级、流程等）
3. 选择元素：使用圆形、矩形、箭头、连线等基础图形
4. 配色美化：应用现代配色方案，确保视觉协调
5. 生成代码：输出完整规范的 SVG 代码

### 技术规范 ###
- 必须包含 <?xml version="1.0" encoding="UTF-8"?> 声明
- 必须设置 viewBox="0 0 800 600"，便于自适应缩放
- 字体使用 font-family="Arial, sans-serif"，确保跨平台兼容
- 使用语义化的 id 和 class 命名

### 输出要求 ###
请直接输出完整的 SVG 代码，不要有其他任何内容（不要markdown代码块标记）。
从 <?xml 开始，到 </svg> 结束。
"""
    
    # 科技风格 Prompt 附加（第 5 期新增）
    STYLE_TECH_PROMPT = """

**重要：请使用科技风格进行创作**
- 语言专业、严谨，多使用专业术语和行业词汇
- 逻辑清晰，重视数据和事实支撑
- 叙述客观理性，避免主观情感表达
- 突出技术创新、发展趋势、解决方案
- 可适当引用权威资料或专家观点
"""
    
    # 情感风格 Prompt 附加（第 5 期新增）
    STYLE_EMOTIONAL_PROMPT = """

**重要：请使用情感风格进行创作**
- 语言温暖细腻，富有感染力和共鸣
- 善用比喻、排比等修辞手法增强表现力
- 注重情感表达，讲述真实故事和感悟
- 引发读者情感共鸣，传递正能量
- 适当使用抒情语句，增加文章温度
"""
    
    # 教育风格 Prompt 附加（第 5 期新增）
    STYLE_EDUCATIONAL_PROMPT = """

**重要：请使用教育风格进行创作**
- 语言通俗易懂，深入浅出地讲解概念
- 结构清晰，循序渐进，便于学习理解
- 多用案例、类比帮助读者理解复杂内容
- 总结重点知识点，提供实用的学习建议
- 鼓励思考，启发读者自主学习和探索
"""
    
    # 轻松幽默风格 Prompt 附加（第 5 期新增）
    STYLE_HUMOROUS_PROMPT = """

**重要：请使用轻松幽默风格进行创作**
- 语言轻松活泼，幽默风趣
- 善用网络流行语、俏皮话和有趣的比喻
- 适当自嘲或调侃，增加趣味性
- 内容轻松易读，让读者在愉快中获取信息
- 可加入一些有趣的段子或梗，但不失专业性
"""

    # AI 修改大纲 Prompt（第 6 期新增）
    AI_MODIFY_OUTLINE_PROMPT = """你是一位专业的文章策划师,擅长根据用户反馈优化文章结构。

当前文章信息：
主标题：{mainTitle}
副标题：{subTitle}

当前大纲：
{currentOutline}

用户修改建议：
{modifySuggestion}

要求：
1. 根据用户的修改建议，调整大纲结构
2. 保持大纲的逻辑性和完整性
3. 如果用户建议删除某章节，则删除；建议增加则增加；建议修改则修改
4. 保持 JSON 格式不变
5. 章节序号自动重新排序

请直接返回修改后的 JSON 格式大纲，不要有其他内容：
{{
  "sections": [
    {{
      "section": 1,
      "title": "章节标题",
      "points": ["要点1", "要点2"]
    }}
  ]
}}
"""
