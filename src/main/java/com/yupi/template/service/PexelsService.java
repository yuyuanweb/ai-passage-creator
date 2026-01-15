package com.yupi.template.service;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.yupi.template.config.PexelsConfig;
import lombok.extern.slf4j.Slf4j;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;
import java.io.IOException;

/**
 * Pexels 图片检索服务
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class PexelsService {

    @Resource
    private PexelsConfig pexelsConfig;

    private final OkHttpClient httpClient = new OkHttpClient();

    private static final String PEXELS_API_URL = "https://api.pexels.com/v1/search";

    /**
     * 根据关键词检索图片
     *
     * @param keywords 搜索关键词
     * @return 图片 URL
     */
    public String searchImage(String keywords) {
        try {
            String url = PEXELS_API_URL + "?query=" + keywords + "&per_page=1&orientation=landscape";
            
            Request request = new Request.Builder()
                    .url(url)
                    .addHeader("Authorization", pexelsConfig.getApiKey())
                    .build();

            try (Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    log.error("Pexels API 调用失败: {}", response.code());
                    return null;
                }

                String responseBody = response.body().string();
                JsonObject jsonObject = JsonParser.parseString(responseBody).getAsJsonObject();
                JsonArray photos = jsonObject.getAsJsonArray("photos");
                
                if (photos.size() == 0) {
                    log.warn("Pexels 未检索到图片: {}", keywords);
                    return null;
                }

                JsonObject photo = photos.get(0).getAsJsonObject();
                JsonObject src = photo.getAsJsonObject("src");
                return src.get("large").getAsString();
            }
        } catch (IOException e) {
            log.error("Pexels API 调用异常", e);
            return null;
        }
    }

    /**
     * 降级方案：使用 picsum 随机图片
     *
     * @param position 位置序号
     * @return 图片 URL
     */
    public String getFallbackImage(int position) {
        return "https://picsum.photos/800/600?random=" + position;
    }
}
