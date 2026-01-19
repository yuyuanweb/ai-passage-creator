package com.yupi.template.service;

import com.yupi.template.model.enums.ImageMethodEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 图片服务策略选择器
 * 根据图片来源类型选择对应的图片服务实现
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class ImageServiceStrategy {

    @Resource
    private List<ImageSearchService> imageSearchServices;

    /**
     * 图片服务映射：ImageMethodEnum -> ImageSearchService
     */
    private final Map<ImageMethodEnum, ImageSearchService> serviceMap = new HashMap<>();

    @PostConstruct
    public void init() {
        // 将所有 ImageSearchService 实现注册到映射表
        for (ImageSearchService service : imageSearchServices) {
            serviceMap.put(service.getMethod(), service);
            log.info("注册图片服务: {} -> {}", service.getMethod(), service.getClass().getSimpleName());
        }
    }

    /**
     * 根据图片来源获取对应的图片
     *
     * @param imageSource 图片来源（PEXELS / NANO_BANANA）
     * @param keywords    关键词（用于 Pexels 检索）
     * @param prompt      提示词（用于 Nano Banana 生图）
     * @return 图片获取结果
     */
    public ImageResult getImage(String imageSource, String keywords, String prompt) {
        ImageMethodEnum method = ImageMethodEnum.getByValue(imageSource);
        
        // 默认使用 Pexels
        if (method == null) {
            method = ImageMethodEnum.PEXELS;
            log.warn("未知的图片来源: {}, 默认使用 PEXELS", imageSource);
        }

        ImageSearchService service = serviceMap.get(method);
        if (service == null) {
            log.error("未找到图片服务实现: {}", method);
            return new ImageResult(null, ImageMethodEnum.PICSUM);
        }

        // 根据不同来源使用不同的参数
        String searchParam = method == ImageMethodEnum.NANO_BANANA ? prompt : keywords;
        if (searchParam == null || searchParam.isEmpty()) {
            searchParam = keywords; // 降级使用 keywords
        }

        String imageUrl = service.searchImage(searchParam);
        
        if (imageUrl != null) {
            return new ImageResult(imageUrl, method);
        } else {
            // 降级方案
            log.warn("图片获取失败, 使用降级方案, method={}", method);
            return new ImageResult(null, ImageMethodEnum.PICSUM);
        }
    }

    /**
     * 获取指定方法的图片服务
     *
     * @param method 图片方法
     * @return 图片服务，未找到返回 null
     */
    public ImageSearchService getService(ImageMethodEnum method) {
        return serviceMap.get(method);
    }

    /**
     * 获取降级图片
     *
     * @param position 位置序号
     * @return 降级图片 URL
     */
    public String getFallbackImage(int position) {
        // 使用 Pexels 服务的降级方案（Picsum）
        ImageSearchService pexelsService = serviceMap.get(ImageMethodEnum.PEXELS);
        if (pexelsService != null) {
            return pexelsService.getFallbackImage(position);
        }
        return String.format("https://picsum.photos/800/600?random=%d", position);
    }

    /**
     * 图片获取结果
     */
    public static class ImageResult {
        private final String url;
        private final ImageMethodEnum method;

        public ImageResult(String url, ImageMethodEnum method) {
            this.url = url;
            this.method = method;
        }

        public String getUrl() {
            return url;
        }

        public ImageMethodEnum getMethod() {
            return method;
        }

        public boolean isSuccess() {
            return url != null && !url.isEmpty();
        }
    }
}
