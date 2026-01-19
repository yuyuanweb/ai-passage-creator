package com.yupi.template.service;

import com.yupi.template.config.NanoBananaConfig;
import com.yupi.template.model.enums.ImageMethodEnum;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Nano Banana 图片生成服务测试
 * 
 * 注意：此测试会实际调用 Gemini API，请确保配置了有效的 API Key
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@SpringBootTest
@ActiveProfiles("local")
class NanoBananaServiceTest {

    @Autowired
    private NanoBananaService nanoBananaService;

    @Autowired
    private NanoBananaConfig nanoBananaConfig;

    @BeforeEach
    void setUp() {
        assertNotNull(nanoBananaService, "NanoBananaService 未注入");
        assertNotNull(nanoBananaConfig, "NanoBananaConfig 未注入");
    }

    @Test
    void testGetMethod() {
        assertEquals(ImageMethodEnum.NANO_BANANA, nanoBananaService.getMethod());
    }

    @Test
    void testGetFallbackImage() {
        String fallback = nanoBananaService.getFallbackImage(1);
        assertNotNull(fallback);
        assertTrue(fallback.contains("picsum.photos"));
    }

    /**
     * 测试图片生成功能
     * 注意：此测试会实际调用 Gemini API，会产生费用
     */
    @Test
    void testGenerateImage() {
        // 检查是否配置了 API Key
        if (nanoBananaConfig.getApiKey() == null || nanoBananaConfig.getApiKey().isEmpty()) {
            System.out.println("跳过测试：未配置 Gemini API Key");
            return;
        }

        String prompt = "A simple minimalist illustration of a cute robot reading a book, " +
                "blue and white color scheme, clean design, digital art style";
        
        System.out.println("开始生成图片, prompt: " + prompt);
        System.out.println("使用模型: " + nanoBananaConfig.getModel());
        
        String imageUrl = nanoBananaService.generateImage(prompt);
        
        System.out.println("生成结果: " + (imageUrl != null ? "成功" : "失败"));
        if (imageUrl != null) {
            // 如果是 data URL，只打印前100个字符
            if (imageUrl.startsWith("data:")) {
                System.out.println("图片类型: Data URL");
                System.out.println("图片预览: " + imageUrl.substring(0, Math.min(100, imageUrl.length())) + "...");
            } else {
                System.out.println("图片 URL: " + imageUrl);
            }
        }
        
        assertNotNull(imageUrl, "图片生成失败");
        assertTrue(imageUrl.startsWith("data:image/") || imageUrl.startsWith("http"), 
                "图片 URL 格式不正确");
    }

    /**
     * 测试 searchImage 方法（通过 ImageSearchService 接口调用）
     */
    @Test
    void testSearchImage() {
        // 检查是否配置了 API Key
        if (nanoBananaConfig.getApiKey() == null || nanoBananaConfig.getApiKey().isEmpty()) {
            System.out.println("跳过测试：未配置 Gemini API Key");
            return;
        }

        String keywords = "futuristic city skyline sunset";
        
        System.out.println("开始通过 searchImage 生成图片, keywords: " + keywords);
        
        String imageUrl = nanoBananaService.searchImage(keywords);
        
        System.out.println("生成结果: " + (imageUrl != null ? "成功" : "失败"));
        
        assertNotNull(imageUrl, "图片生成失败");
    }
}
