package com.yupi.template.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Nano Banana (Gemini 原生图片生成) 配置
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Configuration
@ConfigurationProperties(prefix = "nano-banana")
@Data
public class NanoBananaConfig {

    /**
     * Gemini API Key
     */
    private String apiKey;

    /**
     * 模型名称
     * gemini-2.5-flash-image: 速度快，适合高吞吐低延迟
     * gemini-3-pro-image-preview: 专业级，支持高级推理和高分辨率
     */
    private String model = "gemini-2.5-flash-image";

    /**
     * 图片宽高比
     * 支持: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
     */
    private String aspectRatio = "16:9";

    /**
     * 图片分辨率（仅 gemini-3-pro-image-preview 支持）
     * 支持: 1K, 2K, 4K
     */
    private String imageSize = "1K";

    /**
     * 输出图片格式
     * 支持: image/jpeg, image/png
     */
    private String outputMimeType = "image/png";
}
