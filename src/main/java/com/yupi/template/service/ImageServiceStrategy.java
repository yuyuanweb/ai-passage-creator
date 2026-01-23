package com.yupi.template.service;

import com.yupi.template.model.dto.image.ImageData;
import com.yupi.template.model.dto.image.ImageRequest;
import com.yupi.template.model.enums.ImageMethodEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * 图片服务策略选择器
 * 根据图片来源类型选择对应的图片服务实现
 * 
 * 设计说明：
 * - 自动注册所有 ImageSearchService 实现
 * - 根据 ImageMethodEnum 的元数据自动选择正确的参数
 * - 支持服务可用性检查和自动降级
 * - 统一处理图片上传到 COS
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class ImageServiceStrategy {

    @Resource
    private List<ImageSearchService> imageSearchServices;

    @Resource
    private CosService cosService;

    /**
     * 图片服务映射：ImageMethodEnum -> ImageSearchService
     */
    private final Map<ImageMethodEnum, ImageSearchService> serviceMap = new EnumMap<>(ImageMethodEnum.class);

    @PostConstruct
    public void init() {
        // 将所有 ImageSearchService 实现注册到映射表
        for (ImageSearchService service : imageSearchServices) {
            ImageMethodEnum method = service.getMethod();
            serviceMap.put(method, service);
            log.info("注册图片服务: {} -> {} (AI生图: {}, 降级: {})", 
                    method.getValue(), 
                    service.getClass().getSimpleName(),
                    method.isAiGenerated(),
                    method.isFallback());
        }
    }

    /**
     * 获取图片并上传到 COS（推荐方法）
     * 统一处理所有图片来源的上传逻辑
     *
     * @param imageSource 图片来源
     * @param request     图片请求对象
     * @return 图片获取结果（包含 COS URL）
     */
    public ImageResult getImageAndUpload(String imageSource, ImageRequest request) {
        ImageMethodEnum method = resolveMethod(imageSource);
        ImageSearchService service = serviceMap.get(method);
        
        if (service == null || !service.isAvailable()) {
            log.warn("图片服务不可用: {}, 尝试降级", method);
            return handleFallbackWithUpload(request.getPosition());
        }

        try {
            // 1. 获取图片数据
            ImageData imageData = service.getImageData(request);
            
            if (imageData == null || !imageData.isValid()) {
                log.warn("图片数据获取失败, 使用降级方案, method={}", method);
                return handleFallbackWithUpload(request.getPosition());
            }
            
            // 2. 上传到 COS
            String folder = getFolderForMethod(method);
            String cosUrl = cosService.uploadImageData(imageData, folder);
            
            if (cosUrl != null && !cosUrl.isEmpty()) {
                log.info("图片获取并上传成功, method={}, cosUrl={}", method, cosUrl);
                return new ImageResult(cosUrl, method);
            } else {
                log.warn("图片上传 COS 失败, 使用降级方案, method={}", method);
                return handleFallbackWithUpload(request.getPosition());
            }
        } catch (Exception e) {
            log.error("获取图片并上传异常, method={}", method, e);
            return handleFallbackWithUpload(request.getPosition());
        }
    }

    /**
     * 根据图片请求获取图片
     *
     * @param imageSource 图片来源
     * @param request     图片请求对象
     * @return 图片获取结果
     * @deprecated 使用 getImageAndUpload() 替代
     */
    @Deprecated
    public ImageResult getImage(String imageSource, ImageRequest request) {
        ImageMethodEnum method = resolveMethod(imageSource);
        ImageSearchService service = serviceMap.get(method);
        
        if (service == null || !service.isAvailable()) {
            log.warn("图片服务不可用: {}, 尝试降级", method);
            return handleFallback(request.getPosition());
        }

        String imageUrl = service.getImage(request);
        
        if (imageUrl != null && !imageUrl.isEmpty()) {
            return new ImageResult(imageUrl, method);
        } else {
            log.warn("图片获取失败, 使用降级方案, method={}", method);
            return handleFallback(request.getPosition());
        }
    }

    /**
     * 根据图片来源获取对应的图片（兼容旧接口，不上传到 COS）
     *
     * @param imageSource 图片来源（PEXELS / NANO_BANANA 等）
     * @param keywords    关键词（用于图库检索）
     * @param prompt      提示词（用于 AI 生图）
     * @return 图片获取结果
     * @deprecated 使用 getImageAndUpload() 替代
     */
    @Deprecated
    public ImageResult getImage(String imageSource, String keywords, String prompt) {
        ImageRequest request = ImageRequest.builder()
                .keywords(keywords)
                .prompt(prompt)
                .build();
        return getImage(imageSource, request);
    }

    /**
     * 根据图片方法获取 COS 文件夹
     */
    private String getFolderForMethod(ImageMethodEnum method) {
        return switch (method) {
            case PEXELS -> "pexels";
            case NANO_BANANA -> "nano-banana";
            case MERMAID -> "mermaid";
            case ICONIFY -> "iconify";
            case EMOJI_PACK -> "emoji-pack";
            case SVG_DIAGRAM -> "svg-diagram";
            case PICSUM -> "picsum";
        };
    }

    /**
     * 解析图片来源，处理未知值
     */
    private ImageMethodEnum resolveMethod(String imageSource) {
        ImageMethodEnum method = ImageMethodEnum.getByValue(imageSource);
        if (method == null) {
            log.warn("未知的图片来源: {}, 默认使用 {}", imageSource, ImageMethodEnum.getDefaultSearchMethod());
            return ImageMethodEnum.getDefaultSearchMethod();
        }
        return method;
    }

    /**
     * 处理降级逻辑
     */
    private ImageResult handleFallback(Integer position) {
        int pos = position != null ? position : 1;
        String fallbackUrl = getFallbackImage(pos);
        return new ImageResult(fallbackUrl, ImageMethodEnum.getFallbackMethod());
    }

    /**
     * 处理降级逻辑
     */
    private ImageResult handleFallbackWithUpload(Integer position) {
        int pos = position != null ? position : 1;
        String fallbackUrl = getFallbackImage(pos);
        
        // 将降级图片也上传到 COS
        ImageData fallbackData = ImageData.fromUrl(fallbackUrl);
        String cosUrl = cosService.uploadImageData(fallbackData, "fallback");
        
        // 如果上传失败，直接使用原始 URL
        String finalUrl = (cosUrl != null && !cosUrl.isEmpty()) ? cosUrl : fallbackUrl;
        return new ImageResult(finalUrl, ImageMethodEnum.getFallbackMethod());
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
        // 优先使用已注册服务的降级方案
        ImageSearchService defaultService = serviceMap.get(ImageMethodEnum.getDefaultSearchMethod());
        if (defaultService != null) {
            return defaultService.getFallbackImage(position);
        }
        return String.format("https://picsum.photos/800/600?random=%d", position);
    }

    /**
     * 获取所有已注册的图片服务类型
     */
    public List<ImageMethodEnum> getRegisteredMethods() {
        return List.copyOf(serviceMap.keySet());
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
