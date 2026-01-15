package com.yupi.template.service;

import com.qcloud.cos.COSClient;
import com.qcloud.cos.ClientConfig;
import com.qcloud.cos.auth.BasicCOSCredentials;
import com.qcloud.cos.auth.COSCredentials;
import com.qcloud.cos.http.HttpProtocol;
import com.qcloud.cos.model.ObjectMetadata;
import com.qcloud.cos.model.PutObjectRequest;
import com.qcloud.cos.region.Region;
import com.yupi.template.config.CosConfig;
import lombok.extern.slf4j.Slf4j;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

/**
 * 腾讯云 COS 服务
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class CosService {

    @Resource
    private CosConfig cosConfig;

    private COSClient cosClient;

    private final OkHttpClient httpClient = new OkHttpClient();

    @PostConstruct
    public void init() {
        COSCredentials cred = new BasicCOSCredentials(cosConfig.getSecretId(), cosConfig.getSecretKey());
        Region region = new Region(cosConfig.getRegion());
        ClientConfig clientConfig = new ClientConfig(region);
        clientConfig.setHttpProtocol(HttpProtocol.https);
        cosClient = new COSClient(cred, clientConfig);
    }

    /**
     * 上传图片到 COS
     *
     * @param imageUrl 图片 URL
     * @param folder   文件夹
     * @return COS 图片 URL
     */
    public String uploadImage(String imageUrl, String folder) {
        try {
            // 下载图片
            Request request = new Request.Builder().url(imageUrl).build();
            try (Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    log.error("下载图片失败: {}", imageUrl);
                    return imageUrl; // 降级：直接返回原始 URL
                }

                byte[] imageBytes = response.body().bytes();
                
                // 生成文件名
                String fileName = folder + "/" + UUID.randomUUID() + ".jpg";
                
                // 上传到 COS
                try (InputStream inputStream = new ByteArrayInputStream(imageBytes)) {
                    ObjectMetadata metadata = new ObjectMetadata();
                    metadata.setContentLength(imageBytes.length);
                    metadata.setContentType("image/jpeg");
                    
                    PutObjectRequest putObjectRequest = new PutObjectRequest(
                            cosConfig.getBucket(), fileName, inputStream, metadata);
                    
                    cosClient.putObject(putObjectRequest);
                    
                    // 返回访问 URL
                    return String.format("https://%s.cos.%s.myqcloud.com/%s", 
                            cosConfig.getBucket(), cosConfig.getRegion(), fileName);
                }
            }
        } catch (IOException e) {
            log.error("上传图片到 COS 失败", e);
            return imageUrl; // 降级：直接返回原始 URL
        }
    }

    /**
     * 直接使用图片 URL（不上传到 COS）
     *
     * @param imageUrl 图片 URL
     * @return 图片 URL
     */
    public String useDirectUrl(String imageUrl) {
        return imageUrl;
    }
}
