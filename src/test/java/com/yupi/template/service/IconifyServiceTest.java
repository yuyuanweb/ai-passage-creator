package com.yupi.template.service;

import com.yupi.template.config.IconifyConfig;
import com.yupi.template.model.dto.image.ImageRequest;
import com.yupi.template.model.enums.ImageMethodEnum;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Iconify 图标库检索服务测试
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@SpringBootTest
@ActiveProfiles("local")
class IconifyServiceTest {

    @Autowired
    private IconifyService iconifyService;

    @Autowired
    private IconifyConfig iconifyConfig;

    @Autowired
    private ImageServiceStrategy imageServiceStrategy;

    @BeforeEach
    void setUp() {
        assertNotNull(iconifyService, "IconifyService 未注入");
        assertNotNull(iconifyConfig, "IconifyConfig 未注入");
        assertNotNull(imageServiceStrategy, "ImageServiceStrategy 未注入");
    }

    @Test
    void testGetMethod() {
        // 验证服务类型
        assertEquals(ImageMethodEnum.ICONIFY, iconifyService.getMethod());
        // 验证枚举元数据
        assertFalse(ImageMethodEnum.ICONIFY.isAiGenerated(), 
                "ICONIFY 是图标检索，不是 AI 生成");
    }

    @Test
    void testServiceRegistration() {
        // 验证服务已正确注册到策略选择器
        ImageSearchService service = imageServiceStrategy.getService(ImageMethodEnum.ICONIFY);
        assertNotNull(service, "IconifyService 应该已注册到策略选择器");
        assertEquals(IconifyService.class, service.getClass());
    }

    /**
     * 测试搜索图标
     */
    @Test
    void testSearchIcon() {
        String keywords = "home";

        System.out.println("开始搜索图标, keywords: " + keywords);

        String iconUrl = iconifyService.searchImage(keywords);

        System.out.println("搜索结果: " + (iconUrl != null ? "成功" : "失败"));
        if (iconUrl != null) {
            System.out.println("图标 URL: " + iconUrl);
        }

        assertNotNull(iconUrl, "图标搜索失败");
        assertTrue(iconUrl.contains("api.iconify.design"), "图标 URL 应该包含 Iconify 域名");
        assertTrue(iconUrl.endsWith(".svg") || iconUrl.contains(".svg?"), "图标应该是 SVG 格式");
    }

    /**
     * 测试搜索常见图标
     */
    @Test
    void testSearchCommonIcons() {
        String[] keywords = {"check", "arrow", "star", "heart", "menu"};

        for (String keyword : keywords) {
            System.out.println("搜索图标: " + keyword);
            String iconUrl = iconifyService.searchImage(keyword);

            assertNotNull(iconUrl, "图标搜索失败: " + keyword);
            System.out.println("  -> " + iconUrl);
        }
    }

    /**
     * 测试通过 ImageRequest 搜索图标
     */
    @Test
    void testSearchWithRequest() {
        ImageRequest request = ImageRequest.builder()
                .keywords("check circle")
                .position(1)
                .type("icon")
                .build();

        System.out.println("通过 ImageRequest 搜索图标");

        String iconUrl = iconifyService.getImage(request);

        System.out.println("搜索结果: " + (iconUrl != null ? "成功" : "失败"));
        assertNotNull(iconUrl, "图标搜索失败");
    }

    /**
     * 测试通过策略模式获取图标
     */
    @Test
    void testGetIconViaStrategy() {
        ImageRequest request = ImageRequest.builder()
                .keywords("arrow forward")
                .position(2)
                .type("icon")
                .build();

        System.out.println("通过策略模式获取图标");

        ImageServiceStrategy.ImageResult result = imageServiceStrategy.getImage(
                ImageMethodEnum.ICONIFY.getValue(),
                request
        );

        System.out.println("获取结果: " + (result.isSuccess() ? "成功" : "失败"));
        System.out.println("使用方法: " + result.getMethod().getDescription());

        assertTrue(result.isSuccess(), "图标获取失败");
        assertEquals(ImageMethodEnum.ICONIFY, result.getMethod());
    }

    /**
     * 测试空关键词处理
     */
    @Test
    void testEmptyKeywords() {
        String iconUrl = iconifyService.searchImage("");
        assertNull(iconUrl, "空关键词应该返回 null");

        iconUrl = iconifyService.searchImage(null);
        assertNull(iconUrl, "null 关键词应该返回 null");
    }

    /**
     * 测试降级图片
     */
    @Test
    void testGetFallbackImage() {
        String fallback = iconifyService.getFallbackImage(1);
        assertNotNull(fallback);
        assertTrue(fallback.contains("picsum.photos"));
    }

    /**
     * 测试不存在的图标
     */
    @Test
    void testNonExistentIcon() {
        String keywords = "zzz-nonexistent-icon-xyz-123";

        System.out.println("搜索不存在的图标: " + keywords);

        String iconUrl = iconifyService.searchImage(keywords);

        System.out.println("搜索结果: " + (iconUrl != null ? "成功" : "失败"));
        
        // 应该返回 null，因为搜索不到
        assertNull(iconUrl, "不存在的图标应该返回 null");
    }
}
