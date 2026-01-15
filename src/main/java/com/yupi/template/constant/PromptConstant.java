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
     * 智能体4：分析配图需求
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
            3. 为每个配图位置生成英文搜索关键词(适合 Pexels 图库检索)
            4. 关键词要准确、具体,能检索到高质量图片
            
            请直接返回 JSON 格式,不要有其他内容:
            [
              {
                "position": 1,
                "type": "cover",
                "keywords": "AI technology office modern"
              }
            ]
            """;
}
