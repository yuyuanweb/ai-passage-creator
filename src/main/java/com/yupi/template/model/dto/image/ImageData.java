package com.yupi.template.model.dto.image;

import lombok.Builder;
import lombok.Data;

import java.util.Base64;

/**
 * 图片数据封装类
 * 用于统一处理不同来源的图片数据（字节、URL、base64 等）
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
@Builder
public class ImageData {

    /**
     * 图片字节数据
     */
    private byte[] bytes;

    /**
     * 图片 URL（外部 URL 或 base64 data URL）
     */
    private String url;

    /**
     * MIME 类型（如 image/png, image/jpeg, image/svg+xml）
     */
    private String mimeType;

    /**
     * 数据类型
     */
    private DataType dataType;

    /**
     * 数据类型枚举
     */
    public enum DataType {
        /**
         * 字节数据
         */
        BYTES,
        /**
         * 外部 URL
         */
        URL,
        /**
         * base64 data URL
         */
        DATA_URL
    }

    /**
     * 从外部 URL 创建 ImageData
     *
     * @param url 外部 URL
     * @return ImageData 实例
     */
    public static ImageData fromUrl(String url) {
        if (url == null || url.isEmpty()) {
            return null;
        }
        
        // 判断是否为 base64 data URL
        if (url.startsWith("data:")) {
            return fromDataUrl(url);
        }
        
        return ImageData.builder()
                .url(url)
                .dataType(DataType.URL)
                .build();
    }

    /**
     * 从 base64 data URL 创建 ImageData
     *
     * @param dataUrl base64 data URL
     * @return ImageData 实例
     */
    public static ImageData fromDataUrl(String dataUrl) {
        if (dataUrl == null || !dataUrl.startsWith("data:")) {
            return null;
        }
        
        // 解析 data URL 格式: data:image/png;base64,xxxxx
        String mimeType = "image/png";
        int mimeEnd = dataUrl.indexOf(";");
        if (mimeEnd > 5) {
            mimeType = dataUrl.substring(5, mimeEnd);
        }
        
        return ImageData.builder()
                .url(dataUrl)
                .mimeType(mimeType)
                .dataType(DataType.DATA_URL)
                .build();
    }

    /**
     * 从字节数据创建 ImageData
     *
     * @param bytes    图片字节数据
     * @param mimeType MIME 类型
     * @return ImageData 实例
     */
    public static ImageData fromBytes(byte[] bytes, String mimeType) {
        if (bytes == null || bytes.length == 0) {
            return null;
        }
        
        return ImageData.builder()
                .bytes(bytes)
                .mimeType(mimeType != null ? mimeType : "image/png")
                .dataType(DataType.BYTES)
                .build();
    }

    /**
     * 获取图片字节数据
     * 如果是 data URL，会解码 base64
     *
     * @return 图片字节数据
     */
    public byte[] getImageBytes() {
        if (dataType == DataType.BYTES) {
            return bytes;
        }
        
        if (dataType == DataType.DATA_URL && url != null) {
            // 解析 base64 data URL
            int base64Start = url.indexOf(",");
            if (base64Start > 0) {
                String base64Data = url.substring(base64Start + 1);
                return Base64.getDecoder().decode(base64Data);
            }
        }
        
        return null;
    }

    /**
     * 判断是否有有效数据
     *
     * @return 是否有效
     */
    public boolean isValid() {
        return switch (dataType) {
            case BYTES -> bytes != null && bytes.length > 0;
            case URL, DATA_URL -> url != null && !url.isEmpty();
        };
    }

    /**
     * 根据 MIME 类型获取文件扩展名
     *
     * @return 文件扩展名（带点）
     */
    public String getFileExtension() {
        if (mimeType == null) {
            return ".png";
        }
        
        return switch (mimeType.toLowerCase()) {
            case "image/jpeg", "image/jpg" -> ".jpg";
            case "image/png" -> ".png";
            case "image/gif" -> ".gif";
            case "image/webp" -> ".webp";
            case "image/svg+xml" -> ".svg";
            default -> ".png";
        };
    }
}
