package com.yupi.template.model.dto.article;

import lombok.Data;

import java.io.Serializable;

/**
 * 创建文章请求
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
public class ArticleCreateRequest implements Serializable {

    /**
     * 选题
     */
    private String topic;

    private static final long serialVersionUID = 1L;
}
