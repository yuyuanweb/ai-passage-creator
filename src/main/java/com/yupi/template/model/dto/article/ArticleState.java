package com.yupi.template.model.dto.article;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 文章生成状态（智能体间共享的状态对象）
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
public class ArticleState implements Serializable {

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 选题
     */
    private String topic;

    /**
     * 标题结果（智能体1输出）
     */
    private TitleResult title;

    /**
     * 大纲结果（智能体2输出）
     */
    private OutlineResult outline;

    /**
     * 正文内容（智能体3输出）
     */
    private String content;

    /**
     * 配图需求列表（智能体4输出）
     */
    private List<ImageRequirement> imageRequirements;

    /**
     * 封面图 URL（单独存储，同时 images 列表中的 position=1 也是封面图）
     */
    private String coverImage;

    /**
     * 配图结果列表（智能体5输出）
     */
    private List<ImageResult> images;

    /**
     * 标题结果
     */
    @Data
    public static class TitleResult implements Serializable {
        private String mainTitle;
        private String subTitle;
    }

    /**
     * 大纲结果
     */
    @Data
    public static class OutlineResult implements Serializable {
        private List<OutlineSection> sections;
    }

    /**
     * 大纲章节
     */
    @Data
    public static class OutlineSection implements Serializable {
        private Integer section;
        private String title;
        private List<String> points;
    }

    /**
     * 配图需求
     */
    @Data
    public static class ImageRequirement implements Serializable {
        private Integer position;
        private String type;
        private String sectionTitle;
        private String keywords;
        /**
         * 图片来源：PEXELS（图库检索）或 NANO_BANANA（AI 生图）
         */
        private String imageSource;
        /**
         * AI 生图提示词（当 imageSource 为 NANO_BANANA 时使用）
         */
        private String prompt;
    }

    /**
     * 配图结果
     */
    @Data
    public static class ImageResult implements Serializable {
        private Integer position;
        private String url;
        private String method;
        private String keywords;
        private String sectionTitle;
        private String description;
    }

    /**
     * 完整图文内容（合成后）
     */
    private String fullContent;

    private static final long serialVersionUID = 1L;
}
