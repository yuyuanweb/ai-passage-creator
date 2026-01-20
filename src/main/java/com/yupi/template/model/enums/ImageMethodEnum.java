package com.yupi.template.model.enums;

import lombok.Getter;

/**
 * 配图方式枚举
 * 
 * 扩展新的图片来源时，只需添加新的枚举值并设置正确的属性：
 * - isAiGenerated: 是否为 AI 生图方式（决定使用 prompt 还是 keywords）
 * - isFallback: 是否为降级方案
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Getter
public enum ImageMethodEnum {

    /**
     * Pexels 图库检索
     */
    PEXELS("PEXELS", "Pexels 图库", false, false),

    /**
     * Nano Banana AI 生图（Gemini 原生图片生成）
     */
    NANO_BANANA("NANO_BANANA", "Nano Banana AI 生图", true, false),

    /**
     * Mermaid 流程图生成
     */
    MERMAID("MERMAID", "Mermaid 流程图生成", true, false),

    /**
     * Iconify 图标库检索
     */
    ICONIFY("ICONIFY", "Iconify 图标库", false, false),

    /**
     * 表情包检索（Bing 图片搜索）
     */
    EMOJI_PACK("EMOJI_PACK", "表情包检索", false, false),

    /**
     * SVG 概念示意图生成（AI 生成 SVG 代码）
     */
    SVG_DIAGRAM("SVG_DIAGRAM", "SVG 概念示意图", true, false),

    /**
     * Picsum 随机图片（降级方案）
     */
    PICSUM("PICSUM", "Picsum 随机图片", false, true);

    // ============ 扩展示例 ============
    // DALL_E("DALL_E", "DALL-E AI 生图", true, false),
    // MIDJOURNEY("MIDJOURNEY", "Midjourney AI 生图", true, false),
    // UNSPLASH("UNSPLASH", "Unsplash 图库", false, false),
    // STABLE_DIFFUSION("STABLE_DIFFUSION", "Stable Diffusion AI 生图", true, false),

    /**
     * 方法值
     */
    private final String value;

    /**
     * 方法描述
     */
    private final String description;

    /**
     * 是否为 AI 生图方式
     * true: 使用 prompt 生成图片（如 DALL-E、Midjourney、Nano Banana）
     * false: 使用 keywords 检索图片（如 Pexels、Unsplash）
     */
    private final boolean aiGenerated;

    /**
     * 是否为降级方案
     */
    private final boolean fallback;

    ImageMethodEnum(String value, String description, boolean aiGenerated, boolean fallback) {
        this.value = value;
        this.description = description;
        this.aiGenerated = aiGenerated;
        this.fallback = fallback;
    }

    /**
     * 根据值获取枚举
     *
     * @param value 方法值
     * @return 枚举实例
     */
    public static ImageMethodEnum getByValue(String value) {
        if (value == null) {
            return null;
        }
        for (ImageMethodEnum methodEnum : values()) {
            if (methodEnum.getValue().equals(value)) {
                return methodEnum;
            }
        }
        return null;
    }

    /**
     * 获取默认的图库检索方式
     */
    public static ImageMethodEnum getDefaultSearchMethod() {
        return PEXELS;
    }

    /**
     * 获取默认的 AI 生图方式
     */
    public static ImageMethodEnum getDefaultAiMethod() {
        return NANO_BANANA;
    }

    /**
     * 获取降级方案
     */
    public static ImageMethodEnum getFallbackMethod() {
        return PICSUM;
    }
}
