package com.yupi.template.service;

import com.google.genai.Client;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.GenerateContentResponse;
import com.google.genai.types.ImageConfig;
import com.google.genai.types.Part;
import com.yupi.template.config.NanoBananaConfig;
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

    @Resource
    private CosService cosService;

    @Override
    public String searchImage(String keywords) {
        // 对于 Nano Banana，keywords 就是生图 prompt
        return generateImage(keywords);
    }

    /**
     * 根据提示词生成图片
     *
     * @param prompt 生图提示词
     * @return 图片 URL，生成失败返回 null
     */
    public String generateImage(String prompt) {
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
                                
                                // 上传图片到 COS 并返回 URL
                                return uploadImageToCos(imageBytes, mimeType);
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

    /**
     * 上传图片字节数据到 COS
     *
     * @param imageBytes 图片字节数据
     * @param mimeType   图片 MIME 类型
     * @return COS 图片 URL
     */
    private String uploadImageToCos(byte[] imageBytes, String mimeType) {
        try {
            // 生成临时文件名
            String extension = mimeType.contains("jpeg") || mimeType.contains("jpg") ? ".jpg" : ".png";
            String fileName = "nano-banana/" + System.currentTimeMillis() + "_" + 
                    java.util.UUID.randomUUID().toString().substring(0, 8) + extension;

            // 使用 CosService 上传（需要先转换为 URL 或直接上传字节）
            // 由于 CosService 目前只支持 URL 下载上传，这里直接使用 base64 data URL
            // 或者扩展 CosService 支持字节上传
            
            // 临时方案：将图片转为 base64 data URL（前端可直接使用）
            String base64 = java.util.Base64.getEncoder().encodeToString(imageBytes);
            String dataUrl = "data:" + mimeType + ";base64," + base64;
            
            log.info("Nano Banana 图片已生成 Data URL, length={}", dataUrl.length());
            return dataUrl;
            
        } catch (Exception e) {
            log.error("上传 Nano Banana 图片失败", e);
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
