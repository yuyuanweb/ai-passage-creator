package com.yupi.template.service;

import com.google.genai.Client;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.GenerateContentResponse;
import com.google.genai.types.ImageConfig;
import com.google.genai.types.Part;
import com.yupi.template.config.NanoBananaConfig;
import com.yupi.template.model.dto.image.ImageData;
import com.yupi.template.model.dto.image.ImageRequest;
import com.yupi.template.model.enums.ImageMethodEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;

import static com.yupi.template.constant.ArticleConstant.PICSUM_URL_TEMPLATE;

/**
 * Nano Banana (Gemini 原生图片生成) 服务
 * 使用 Gemini 2.5 Flash Image 或 Gemini 3 Pro Image 模型生成图片
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class NanoBananaService implements ImageSearchService {

    @Resource
    private NanoBananaConfig nanoBananaConfig;

    @Override
    public String searchImage(String keywords) {
        // 此方法已废弃，请使用 getImageData()
        // 返回 null，上传逻辑由 ImageServiceStrategy 统一处理
        return null;
    }

    @Override
    public ImageData getImageData(ImageRequest request) {
        String prompt = request.getEffectiveParam(true);
        return generateImageData(prompt);
    }

    /**
     * 根据提示词生成图片数据
     *
     * @param prompt 生图提示词
     * @return ImageData 包含图片字节数据，生成失败返回 null
     */
    public ImageData generateImageData(String prompt) {
        try {
            // 使用 Builder 显式设置 API Key
            Client genaiClient = Client.builder()
                    .apiKey(nanoBananaConfig.getApiKey())
                    .build();
            
            try {
                // 构建图片配置
                ImageConfig.Builder imageConfigBuilder = ImageConfig.builder()
                        .aspectRatio(nanoBananaConfig.getAspectRatio());

                // Gemini 3 Pro Image 支持更高分辨率
                String model = nanoBananaConfig.getModel();
                if (model != null && model.contains("gemini-3-pro")) {
                    imageConfigBuilder.imageSize(nanoBananaConfig.getImageSize());
                }

                // 构建生成配置
                GenerateContentConfig config = GenerateContentConfig.builder()
                        .responseModalities("TEXT", "IMAGE")
                        .imageConfig(imageConfigBuilder.build())
                        .build();

                log.info("Nano Banana 开始生成图片, model={}, prompt={}", model, prompt);

                // 调用 Gemini API 生成图片
                GenerateContentResponse response = genaiClient.models.generateContent(
                        model != null ? model : "gemini-2.5-flash-image",
                        prompt,
                        config);

                // 从响应中提取图片数据
                if (response.parts() != null) {
                    for (Part part : response.parts()) {
                        if (part.inlineData().isPresent()) {
                            var blob = part.inlineData().get();
                            if (blob.data().isPresent()) {
                                byte[] imageBytes = blob.data().get();
                                String mimeType = blob.mimeType().orElse("image/png");
                                
                                log.info("Nano Banana 图片生成成功, size={} bytes, mimeType={}", 
                                        imageBytes.length, mimeType);
                                
                                return ImageData.fromBytes(imageBytes, mimeType);
                            }
                        }
                    }
                }

                log.warn("Nano Banana 未生成图片, prompt={}", prompt);
                return null;

            } finally {
                genaiClient.close();
            }
        } catch (Exception e) {
            log.error("Nano Banana 生成图片异常, prompt={}", prompt, e);
            return null;
        }
    }

    @Override
    public ImageMethodEnum getMethod() {
        return ImageMethodEnum.NANO_BANANA;
    }

    @Override
    public String getFallbackImage(int position) {
        return String.format(PICSUM_URL_TEMPLATE, position);
    }
}
