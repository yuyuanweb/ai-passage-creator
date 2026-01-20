package com.yupi.template.constant;

/**
 * Prompt 模板常量
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
public interface PromptConstant {

    /**
     * 智能体1：生成标题
     */
    String AGENT1_TITLE_PROMPT = """
            你是一位爆款文章标题专家,擅长创作吸引人的标题。
            
            根据以下选题,生成一个爆款文章标题(主标题 + 副标题):
            选题：{topic}
            
            要求:
            1. 主标题要包含数字、情绪化词汇,吸引眼球
            2. 副标题要补充说明,增强吸引力
            3. 标题要简洁有力,不超过30字
            4. 符合新媒体爆款文章的风格
            
            请直接返回 JSON 格式,不要有其他内容:
            {
              "mainTitle": "主标题",
              "subTitle": "副标题"
            }
            """;

    /**
     * 智能体2：生成大纲
     */
    String AGENT2_OUTLINE_PROMPT = """
            你是一位专业的文章策划师,擅长设计文章结构。
            
            根据以下标题,生成文章大纲:
            主标题：{mainTitle}
            副标题：{subTitle}
            
            要求:
            1. 大纲要有清晰的逻辑结构
            2. 包含开头引入、核心观点(3-5个)、结尾升华
            3. 每个章节要有明确的标题和核心要点(2-3个)
            4. 适合2000字左右的文章
            
            请直接返回 JSON 格式,不要有其他内容:
            {
              "sections": [
                {
                  "section": 1,
                  "title": "章节标题",
                  "points": ["要点1", "要点2"]
                }
              ]
            }
            """;

    /**
     * SVG 概念示意图生成 Prompt
     */
    String SVG_DIAGRAM_GENERATION_PROMPT = """
            ### 背景 ###
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
            
            ### 设计风格 ###
            - 配色：蓝色系为主（#4A90D9、#6BB3F0、#E8F4FC），辅以渐变效果
            - 布局：留白充足，元素间距均匀，层次分明
            - 文字：标签简洁，字号适中（14-18px），颜色对比清晰
            - 连线：使用带箭头的线条表示方向和关系，线条粗细 2-3px
            
            ### 输出要求 ###
            直接返回完整的 SVG XML 代码，不要有任何解释或其他内容。
            """;

    /**
     * 智能体3：生成正文
     */
    String AGENT3_CONTENT_PROMPT = """
            你是一位资深的内容创作者,擅长撰写优质文章。
            
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
            """;

    /**
     * 智能体4：分析配图需求（支持多种图片来源）
     */
    String AGENT4_IMAGE_REQUIREMENTS_PROMPT = """
            你是一位专业的新媒体编辑,擅长为文章配图。
            
            根据以下文章内容,分析配图需求:
            主标题：{mainTitle}
            正文：
            {content}
            
            要求:
            1. 识别需要配图的位置(封面、关键章节等)
            2. 建议配图数量: 3-5张
            3. 为每个配图选择最合适的图片来源(imageSource):
               - PEXELS: 适合真实场景、产品照片、人物照片、自然风景等写实图片
               - NANO_BANANA: 适合创意插画、信息图表、需要文字渲染、抽象概念、艺术风格等 AI 生成图片
               - MERMAID: 适合流程图、架构图、时序图、关系图、甘特图等结构化图表
               - ICONIFY: 适合图标、符号、小型装饰性图标（如：箭头、勾选、星星、心形等）
               - EMOJI_PACK: 适合表情包、搞笑图片、轻松幽默的配图
               - SVG_DIAGRAM: 适合概念示意图、思维导图样式、逻辑关系展示（不涉及精确数据）
            4. 对于 PEXELS 来源: 提供英文搜索关键词(keywords),要准确、具体
            5. 对于 NANO_BANANA 来源: 提供详细的英文生图提示词(prompt),描述场景、风格、细节
            6. 对于 MERMAID 来源: 
               - 分析文章内容，识别需要流程图的位置（如：工作流程、系统架构、数据流向等）
               - 在 prompt 字段生成完整的 Mermaid 代码
               - keywords 留空
            7. 对于 ICONIFY 来源:
               - 识别需要图标的位置（如：列表项标记、步骤指示、重点强调等）
               - 提供英文图标关键词（keywords），如：check、arrow、star、heart
               - prompt 留空
            8. 对于 EMOJI_PACK 来源:
               - 识别文章中轻松幽默、需要表情包的位置
               - 提供中文或英文关键词（keywords），描述表情内容，如：开心、哭笑、无语、疑问
               - prompt 留空
               - 系统会自动在关键词后添加"表情包"进行搜索
            9. 对于 SVG_DIAGRAM 来源:
               - 识别文章中需要展示概念、关系、逻辑的位置（不涉及精确数据）
               - 在 prompt 字段描述示意图需求（中文），说明要表达的概念和关系
               - keywords 留空
               - 示例：绘制思维导图样式的图，中心是"自律"，周围4个分支：习惯、环境、反馈、系统
            10. sectionTitle 必须与正文中的章节标题完全一致(用于定位插入位置)
            11. position=1 为封面图,sectionTitle 留空
            
            请直接返回 JSON 格式,不要有其他内容:
            [
              {
                "position": 1,
                "type": "cover",
                "sectionTitle": "",
                "imageSource": "NANO_BANANA",
                "keywords": "",
                "prompt": "A modern minimalist illustration of AI technology concept, featuring abstract neural network patterns with blue and purple gradient colors, clean design suitable for article cover, 16:9 aspect ratio"
              },
              {
                "position": 2,
                "type": "section",
                "sectionTitle": "章节标题（与正文完全一致）",
                "imageSource": "PEXELS",
                "keywords": "business success teamwork office",
                "prompt": ""
              },
              {
                "position": 3,
                "type": "section",
                "sectionTitle": "系统架构（与正文完全一致）",
                "imageSource": "MERMAID",
                "keywords": "",
                "prompt": "flowchart TB\\n    A[用户请求] --> B[负载均衡]\\n    B --> C[应用服务器]\\n    C --> D[数据库]\\n    C --> E[缓存]"
              },
              {
                "position": 4,
                "type": "section",
                "sectionTitle": "核心优势（与正文完全一致）",
                "imageSource": "ICONIFY",
                "keywords": "check circle",
                "prompt": ""
              },
              {
                "position": 5,
                "type": "section",
                "sectionTitle": "常见问题（与正文完全一致）",
                "imageSource": "EMOJI_PACK",
                "keywords": "疑问",
                "prompt": ""
              },
              {
                "position": 6,
                "type": "section",
                "sectionTitle": "核心理念（与正文完全一致）",
                "imageSource": "SVG_DIAGRAM",
                "keywords": "",
                "prompt": "绘制概念示意图，中心圆形写'自律系统'，周围4个圆形分别是：习惯设计、环境优化、即时反馈、持续迭代，用箭头连接表示关系"
              }
            ]
            """;
}
