package com.yupi.template.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Iconify 图标库配置
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Configuration
@ConfigurationProperties(prefix = "iconify")
@Data
public class IconifyConfig {

    /**
     * Iconify API 地址
     */
    private String apiUrl = "https://api.iconify.design";

    /**
     * 搜索结果限制数量
     */
    private Integer searchLimit = 10;

    /**
     * 默认图标高度（像素）
     */
    private Integer defaultHeight = 64;

    /**
     * 默认图标颜色（留空使用 currentColor，或设置如 "#000000"）
     */
    private String defaultColor = "";
}
