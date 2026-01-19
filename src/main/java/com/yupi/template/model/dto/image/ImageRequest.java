package com.yupi.template.model.dto.image;

import lombok.Builder;
import lombok.Data;

/**
 * 图片请求对象
 * 统一封装图片获取所需的各种参数，便于扩展
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
@Builder
public class ImageRequest {

    /**
     * 搜索关键词（用于图库检索）
     */
    private String keywords;

    /**
     * 生图提示词（用于 AI 生图）
     */
    private String prompt;

    /**
     * 图片位置序号
     */
    private Integer position;

    /**
     * 图片类型（cover/section）
     */
    private String type;

    /**
     * 宽高比（如 16:9, 1:1）
     */
    private String aspectRatio;

    /**
     * 图片风格描述
     */
    private String style;

    /**
     * 获取有效的搜索/生成参数
     * AI 生图优先使用 prompt，图库检索使用 keywords
     *
     * @param isAiGenerated 是否为 AI 生图方式
     * @return 有效的参数
     */
    public String getEffectiveParam(boolean isAiGenerated) {
        if (isAiGenerated) {
            return prompt != null && !prompt.isEmpty() ? prompt : keywords;
        }
        return keywords != null && !keywords.isEmpty() ? keywords : prompt;
    }
}
