package com.yupi.template.config;

import com.yupi.template.constant.PromptConstant;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import jakarta.annotation.PostConstruct;
import java.util.HashMap;
import java.util.Map;

/**
 * Prompt 配置类
 * 支持通过配置文件覆盖默认 Prompt
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Configuration
@ConfigurationProperties(prefix = "prompt")
@Data
public class PromptConfig {

    /**
     * Prompt 版本号
     */
    private String version = "1.0";

    /**
     * Prompt 模板映射
     */
    private Map<String, String> templates = new HashMap<>();

    @PostConstruct
    public void init() {
        // 从 PromptConstant 初始化默认值
        templates.putIfAbsent("agent1_title", PromptConstant.AGENT1_TITLE_PROMPT);
        templates.putIfAbsent("agent2_outline", PromptConstant.AGENT2_OUTLINE_PROMPT);
        templates.putIfAbsent("agent3_content", PromptConstant.AGENT3_CONTENT_PROMPT);
        templates.putIfAbsent("agent4_image", PromptConstant.AGENT4_IMAGE_REQUIREMENTS_PROMPT);
        templates.putIfAbsent("ai_modify_outline", PromptConstant.AI_MODIFY_OUTLINE_PROMPT);
    }

    /**
     * 获取 Prompt 模板
     *
     * @param key Prompt 键名
     * @return Prompt 内容
     */
    public String getPrompt(String key) {
        return templates.getOrDefault(key, "");
    }
}
