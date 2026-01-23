package com.yupi.template.service;

import com.yupi.template.model.dto.image.ImageData;
import com.yupi.template.model.dto.image.ImageRequest;
import com.yupi.template.model.enums.ImageMethodEnum;

/**
 * 图片服务接口
 * 抽象图片获取逻辑，便于扩展多种图片来源（如 Pexels、Unsplash、AI 生图等）
 * 
 * 扩展新的图片服务时：
 * 1. 实现此接口
 * 2. 在 ImageMethodEnum 中添加对应的枚举值
 * 3. 添加对应的配置类（如需要）
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
public interface ImageSearchService {

    /**
     * 根据请求获取图片（推荐使用此方法）
     * 
     * @param request 图片请求对象，包含 keywords、prompt 等参数
     * @return 图片 URL，获取失败返回 null
     */
    default String getImage(ImageRequest request) {
        // 默认实现：根据服务类型选择合适的参数
        String param = request.getEffectiveParam(getMethod().isAiGenerated());
        return searchImage(param);
    }

    /**
     * 获取图片数据（用于统一上传到 COS）
     * 子类可重写此方法返回更高效的数据格式（如字节数据）
     *
     * @param request 图片请求对象
     * @return ImageData 对象，包含图片字节或 URL
     */
    default ImageData getImageData(ImageRequest request) {
        // 默认实现：通过 getImage 获取 URL，然后转换为 ImageData
        String url = getImage(request);
        return ImageData.fromUrl(url);
    }

    /**
     * 根据关键词/提示词获取图片
     * 
     * @param keywords 搜索关键词（图库检索）或生图提示词（AI 生图）
     * @return 图片 URL，获取失败返回 null
     */
    String searchImage(String keywords);

    /**
     * 获取图片服务类型
     *
     * @return 图片服务类型枚举
     */
    ImageMethodEnum getMethod();

    /**
     * 获取降级图片 URL
     *
     * @param position 位置序号（用于生成唯一的随机图片）
     * @return 降级图片 URL
     */
    String getFallbackImage(int position);

    /**
     * 判断服务是否可用
     * 子类可重写此方法进行健康检查
     *
     * @return 服务是否可用
     */
    default boolean isAvailable() {
        return true;
    }
}
