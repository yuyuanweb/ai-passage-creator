package com.yupi.template.service;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.RuntimeUtil;
import cn.hutool.system.SystemUtil;
import com.yupi.template.config.MermaidConfig;
import com.yupi.template.model.dto.image.ImageData;
import com.yupi.template.model.dto.image.ImageRequest;
import com.yupi.template.model.enums.ImageMethodEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;
import java.io.File;

import static com.yupi.template.constant.ArticleConstant.PICSUM_URL_TEMPLATE;

/**
 * Mermaid 流程图生成服务
 * 使用 mermaid-cli 将 Mermaid 代码转换为图片
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class MermaidService implements ImageSearchService {

    @Resource
    private MermaidConfig mermaidConfig;

    @Override
    public String searchImage(String keywords) {
        // 对于 Mermaid，keywords 就是 Mermaid 代码
        // 此方法已废弃，请使用 getImageData()
        ImageData imageData = generateDiagramData(keywords);
        // 返回 null，因为不再直接返回 URL
        return null;
    }

    @Override
    public String getImage(ImageRequest request) {
        // 此方法已废弃，请使用 getImageData()
        // 返回 null，上传逻辑由 ImageServiceStrategy 统一处理
        return null;
    }

    @Override
    public ImageData getImageData(ImageRequest request) {
        // 优先使用 prompt（Mermaid 代码），否则使用 keywords
        String mermaidCode = request.getEffectiveParam(true);
        return generateDiagramData(mermaidCode);
    }

    /**
     * 生成 Mermaid 图表数据
     *
     * @param mermaidCode Mermaid 代码
     * @return 图片字节数据，生成失败返回 null
     */
    public ImageData generateDiagramData(String mermaidCode) {
        if (mermaidCode == null || mermaidCode.trim().isEmpty()) {
            log.warn("Mermaid 代码为空");
            return null;
        }

        File tempInputFile = null;
        File tempOutputFile = null;

        try {
            // 创建临时输入文件
            tempInputFile = FileUtil.createTempFile("mermaid_input_", ".mmd", true);
            FileUtil.writeUtf8String(mermaidCode, tempInputFile);

            // 创建临时输出文件
            String outputExtension = "." + mermaidConfig.getOutputFormat();
            tempOutputFile = FileUtil.createTempFile("mermaid_output_", outputExtension, true);

            // 转换为图片
            convertMermaidToImage(tempInputFile, tempOutputFile);

            // 检查输出文件
            if (!tempOutputFile.exists() || tempOutputFile.length() == 0) {
                log.error("Mermaid CLI 执行失败，输出文件不存在或为空");
                return null;
            }

            // 读取图片字节数据
            byte[] imageBytes = FileUtil.readBytes(tempOutputFile);
            String mimeType = getMimeType(mermaidConfig.getOutputFormat());
            
            log.info("Mermaid 图表生成成功, size={} bytes", imageBytes.length);
            return ImageData.fromBytes(imageBytes, mimeType);

        } catch (Exception e) {
            log.error("Mermaid 图表生成异常", e);
            return null;
        } finally {
            // 清理临时文件
            if (tempInputFile != null) {
                FileUtil.del(tempInputFile);
            }
            if (tempOutputFile != null) {
                FileUtil.del(tempOutputFile);
            }
        }
    }

    /**
     * 根据输出格式获取 MIME 类型
     */
    private String getMimeType(String format) {
        return switch (format.toLowerCase()) {
            case "png" -> "image/png";
            case "svg" -> "image/svg+xml";
            case "pdf" -> "application/pdf";
            default -> "image/png";
        };
    }

    /**
     * 调用 Mermaid CLI 转换为图片
     */
    private void convertMermaidToImage(File inputFile, File outputFile) {
        try {
            // 根据操作系统选择命令
            String command = SystemUtil.getOsInfo().isWindows() ? "mmdc.cmd" : mermaidConfig.getCliCommand();

            // 构建命令行参数
            String cmdLine = String.format("%s -i %s -o %s -b %s",
                    command,
                    inputFile.getAbsolutePath(),
                    outputFile.getAbsolutePath(),
                    mermaidConfig.getBackgroundColor()
            );

            // 如果配置了宽度，添加宽度参数
            if (mermaidConfig.getWidth() != null && mermaidConfig.getWidth() > 0) {
                cmdLine += " -w " + mermaidConfig.getWidth();
            }

            log.info("执行 Mermaid CLI 命令: {}", cmdLine);

            // 执行命令（带超时）
            String result = RuntimeUtil.execForStr(cmdLine);
            
            log.debug("Mermaid CLI 执行结果: {}", result);

        } catch (Exception e) {
            log.error("执行 Mermaid CLI 失败", e);
            throw new RuntimeException("Mermaid CLI 执行失败: " + e.getMessage(), e);
        }
    }

    @Override
    public ImageMethodEnum getMethod() {
        return ImageMethodEnum.MERMAID;
    }

    @Override
    public String getFallbackImage(int position) {
        return String.format(PICSUM_URL_TEMPLATE, position);
    }

    @Override
    public boolean isAvailable() {
        try {
            // 检查 mermaid-cli 是否已安装
            String command = SystemUtil.getOsInfo().isWindows() ? "mmdc.cmd" : mermaidConfig.getCliCommand();
            String checkCmd = command + " --version";
            String version = RuntimeUtil.execForStr(checkCmd);
            log.info("Mermaid CLI 版本: {}", version);
            return version != null && !version.isEmpty();
        } catch (Exception e) {
            log.warn("Mermaid CLI 不可用: {}", e.getMessage());
            return false;
        }
    }
}
