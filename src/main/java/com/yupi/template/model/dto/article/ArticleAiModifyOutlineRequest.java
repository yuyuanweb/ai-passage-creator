package com.yupi.template.model.dto.article;

import lombok.Data;

import java.io.Serializable;

/**
 * AI 修改大纲请求
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
public class ArticleAiModifyOutlineRequest implements Serializable {

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 用户的修改建议
     */
    private String modifySuggestion;

    private static final long serialVersionUID = 1L;
}
