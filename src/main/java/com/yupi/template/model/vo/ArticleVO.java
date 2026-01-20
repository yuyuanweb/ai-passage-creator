package com.yupi.template.model.vo;

import com.google.gson.reflect.TypeToken;
import com.yupi.template.model.entity.Article;
import com.yupi.template.utils.GsonUtils;
import lombok.Data;
import org.springframework.beans.BeanUtils;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 文章视图
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
public class ArticleVO implements Serializable {

    /**
     * id
     */
    private Long id;

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 选题
     */
    private String topic;

    /**
     * 用户补充描述
     */
    private String userDescription;

    /**
     * 主标题
     */
    private String mainTitle;

    /**
     * 副标题
     */
    private String subTitle;

    /**
     * 标题方案列表
     */
    private List<TitleOption> titleOptions;

    /**
     * 大纲
     */
    private List<OutlineItem> outline;

    /**
     * 正文
     */
    private String content;

    /**
     * 完整图文（含配图）
     */
    private String fullContent;

    /**
     * 封面图 URL
     */
    private String coverImage;

    /**
     * 配图列表
     */
    private List<ImageItem> images;

    /**
     * 状态
     */
    private String status;

    /**
     * 当前阶段
     */
    private String phase;

    /**
     * 错误信息
     */
    private String errorMessage;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 完成时间
     */
    private LocalDateTime completedTime;

    /**
     * 标题方案
     */
    @Data
    public static class TitleOption implements Serializable {
        private String mainTitle;
        private String subTitle;
    }

    /**
     * 大纲项
     */
    @Data
    public static class OutlineItem implements Serializable {
        private Integer section;
        private String title;
        private List<String> points;
    }

    /**
     * 配图项
     */
    @Data
    public static class ImageItem implements Serializable {
        private Integer position;
        private String url;
        private String method;
        private String keywords;
        private String sectionTitle;
        private String description;
    }

    /**
     * 对象转包装类
     *
     * @param article 文章
     * @return 文章视图
     */
    public static ArticleVO objToVo(Article article) {
        if (article == null) {
            return null;
        }
        ArticleVO articleVO = new ArticleVO();
        BeanUtils.copyProperties(article, articleVO);
        
        // 转换 JSON 字段
        if (article.getTitleOptions() != null) {
            articleVO.setTitleOptions(GsonUtils.fromJson(article.getTitleOptions(), 
                new TypeToken<List<TitleOption>>(){}));
        }
        if (article.getOutline() != null) {
            articleVO.setOutline(GsonUtils.fromJson(article.getOutline(), 
                new TypeToken<List<OutlineItem>>(){}));
        }
        if (article.getImages() != null) {
            articleVO.setImages(GsonUtils.fromJson(article.getImages(), 
                new TypeToken<List<ImageItem>>(){}));
        }
        
        return articleVO;
    }

    private static final long serialVersionUID = 1L;
}
