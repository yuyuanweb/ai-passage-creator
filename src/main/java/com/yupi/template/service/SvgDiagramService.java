package com.yupi.template.service;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.StrUtil;
import com.alibaba.cloud.ai.dashscope.chat.DashScopeChatModel;
import com.yupi.template.config.SvgDiagramConfig;
import com.yupi.template.constant.PromptConstant;
import com.yupi.template.model.enums.ImageMethodEnum;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;
import java.io.File;

import static com.yupi.template.constant.ArticleConstant.PICSUM_URL_TEMPLATE;

/**
 * SVG 概念示意图生成服务
 * 使用 AI 生成 SVG 代码，适合概念示意、思维导图样式、关系展示等场景
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class SvgDiagramService implements ImageSearchService {

    @Resource
    private SvgDiagramConfig svgDiagramConfig;

    @Resource
    private DashScopeChatModel chatModel;

    @Resource
    private CosService cosService;

    @Override
    public String searchImage(String keywords) {
        // keywords 是图表需求描述
        return generateSvgDiagram(keywords);
    }

    /**
     * 生成 SVG 概念示意图
     *
     * @param requirement 示意图需求描述
     * @return 图片 URL，生成失败返回 null
     */
    public String generateSvgDiagram(String requirement) {
        if (StrUtil.isBlank(requirement)) {
            log.warn("SVG 图表需求为空");
            return null;
        }

        File tempFile = null;

        try {
            // 1. 调用 LLM 生成 SVG 代码
            String svgCode = callLlmToGenerateSvg(requirement);

            if (StrUtil.isBlank(svgCode)) {
                log.error("LLM 未生成 SVG 代码");
                return null;
            }

            // 2. 验证 SVG 格式
            if (!isValidSvg(svgCode)) {
                log.error("生成的 SVG 代码格式无效");
                return null;
            }

            // 3. 保存为临时文件
            tempFile = FileUtil.createTempFile("svg_chart_", ".svg", true);
            FileUtil.writeUtf8String(svgCode, tempFile);

            log.info("SVG 代码已保存到临时文件, size={}", tempFile.length());

            // 4. 上传到 COS
            String cosUrl = cosService.uploadFile(tempFile, svgDiagramConfig.getFolder());

            if (cosUrl != null && !cosUrl.isEmpty()) {
                log.info("SVG 概念示意图生成成功, url={}", cosUrl);
                return cosUrl;
            } else {
                log.error("上传 SVG 概念示意图到 COS 失败");
                return null;
            }

        } catch (Exception e) {
            log.error("SVG 概念示意图生成异常, requirement={}", requirement, e);
            return null;
        } finally {
            // 清理临时文件
            if (tempFile != null) {
                FileUtil.del(tempFile);
            }
        }
    }

    /**
     * 调用 LLM 生成 SVG 代码
     */
    private String callLlmToGenerateSvg(String requirement) {
        String prompt = PromptConstant.SVG_DIAGRAM_GENERATION_PROMPT
                .replace("{requirement}", requirement);

        log.info("开始调用 LLM 生成 SVG 概念示意图");

        ChatResponse response = chatModel.call(new Prompt(new UserMessage(prompt)));
        String svgCode = response.getResult().getOutput().getText().trim();

        // 提取 SVG 代码（移除可能的 markdown 代码块标记）
        svgCode = extractSvgCode(svgCode);

        return svgCode;
    }

    /**
     * 提取 SVG 代码（去除 markdown 代码块）
     */
    private String extractSvgCode(String text) {
        if (text == null) {
            return null;
        }

        // 去除 markdown 代码块标记
        text = text.replace("```xml", "").replace("```svg", "").replace("```", "").trim();

        // 确保包含 XML 声明
        if (!text.startsWith("<?xml")) {
            // 如果没有 XML 声明但有 <svg 标签，添加声明
            if (text.contains("<svg")) {
                text = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + text;
            }
        }

        return text;
    }

    /**
     * 验证 SVG 格式
     */
    private boolean isValidSvg(String svgCode) {
        if (StrUtil.isBlank(svgCode)) {
            return false;
        }

        // 基本验证：包含 svg 标签
        return svgCode.contains("<svg") && svgCode.contains("</svg>");
    }

    @Override
    public ImageMethodEnum getMethod() {
        return ImageMethodEnum.SVG_DIAGRAM;
    }

    @Override
    public String getFallbackImage(int position) {
        return String.format(PICSUM_URL_TEMPLATE, position);
    }
}
