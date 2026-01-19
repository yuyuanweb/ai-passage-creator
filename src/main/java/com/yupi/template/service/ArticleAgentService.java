package com.yupi.template.service;

import com.alibaba.cloud.ai.dashscope.chat.DashScopeChatModel;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import com.yupi.template.constant.PromptConstant;
import com.yupi.template.model.dto.article.ArticleState;
import com.yupi.template.model.enums.ImageMethodEnum;
import com.yupi.template.model.enums.SseMessageTypeEnum;
import com.yupi.template.utils.GsonUtils;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * 文章智能体编排服务
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class ArticleAgentService {

    @Resource
    private DashScopeChatModel chatModel;

    @Resource
    private ImageServiceStrategy imageServiceStrategy;

    @Resource
    private CosService cosService;

    /**
     * 执行完整的文章生成流程
     *
     * @param state         文章状态
     * @param streamHandler 流式输出处理器
     */
    public void executeArticleGeneration(ArticleState state, Consumer<String> streamHandler) {
        try {
            // 智能体1：生成标题
            log.info("智能体1：开始生成标题, taskId={}", state.getTaskId());
            agent1GenerateTitle(state);
            streamHandler.accept(SseMessageTypeEnum.AGENT1_COMPLETE.getValue());

            // 智能体2：生成大纲（流式输出）
            log.info("智能体2：开始生成大纲, taskId={}", state.getTaskId());
            agent2GenerateOutline(state, streamHandler);
            streamHandler.accept(SseMessageTypeEnum.AGENT2_COMPLETE.getValue());

            // 智能体3：生成正文（流式输出）
            log.info("智能体3：开始生成正文, taskId={}", state.getTaskId());
            agent3GenerateContent(state, streamHandler);
            streamHandler.accept(SseMessageTypeEnum.AGENT3_COMPLETE.getValue());

            // 智能体4：分析配图需求
            log.info("智能体4：开始分析配图需求, taskId={}", state.getTaskId());
            agent4AnalyzeImageRequirements(state);
            streamHandler.accept(SseMessageTypeEnum.AGENT4_COMPLETE.getValue());

            // 智能体5：生成配图
            log.info("智能体5：开始生成配图, taskId={}", state.getTaskId());
            agent5GenerateImages(state, streamHandler);
            streamHandler.accept(SseMessageTypeEnum.AGENT5_COMPLETE.getValue());

            // 图文合成：将配图插入正文
            log.info("开始图文合成, taskId={}", state.getTaskId());
            mergeImagesIntoContent(state);
            streamHandler.accept(SseMessageTypeEnum.MERGE_COMPLETE.getValue());

            log.info("文章生成完成, taskId={}", state.getTaskId());
        } catch (Exception e) {
            log.error("文章生成失败, taskId={}", state.getTaskId(), e);
            throw new RuntimeException("文章生成失败: " + e.getMessage(), e);
        }
    }

    /**
     * 智能体1：生成标题
     */
    private void agent1GenerateTitle(ArticleState state) {
        String prompt = PromptConstant.AGENT1_TITLE_PROMPT
                .replace("{topic}", state.getTopic());

        String content = callLlm(prompt);
        ArticleState.TitleResult titleResult = parseJsonResponse(content, ArticleState.TitleResult.class, "标题");
        state.setTitle(titleResult);
        log.info("智能体1：标题生成成功, mainTitle={}", titleResult.getMainTitle());
    }

    /**
     * 智能体2：生成大纲（流式输出）
     */
    private void agent2GenerateOutline(ArticleState state, Consumer<String> streamHandler) {
        String prompt = PromptConstant.AGENT2_OUTLINE_PROMPT
                .replace("{mainTitle}", state.getTitle().getMainTitle())
                .replace("{subTitle}", state.getTitle().getSubTitle());

        String content = callLlmWithStreaming(prompt, streamHandler, SseMessageTypeEnum.AGENT2_STREAMING);
        ArticleState.OutlineResult outlineResult = parseJsonResponse(content, ArticleState.OutlineResult.class, "大纲");
        state.setOutline(outlineResult);
        log.info("智能体2：大纲生成成功, sections={}", outlineResult.getSections().size());
    }

    /**
     * 智能体3：生成正文（流式输出）
     */
    private void agent3GenerateContent(ArticleState state, Consumer<String> streamHandler) {
        String outlineText = GsonUtils.toJson(state.getOutline().getSections());
        String prompt = PromptConstant.AGENT3_CONTENT_PROMPT
                .replace("{mainTitle}", state.getTitle().getMainTitle())
                .replace("{subTitle}", state.getTitle().getSubTitle())
                .replace("{outline}", outlineText);

        String content = callLlmWithStreaming(prompt, streamHandler, SseMessageTypeEnum.AGENT3_STREAMING);
        state.setContent(content);
        log.info("智能体3：正文生成成功, length={}", content.length());
    }

    /**
     * 智能体4：分析配图需求
     */
    private void agent4AnalyzeImageRequirements(ArticleState state) {
        String prompt = PromptConstant.AGENT4_IMAGE_REQUIREMENTS_PROMPT
                .replace("{mainTitle}", state.getTitle().getMainTitle())
                .replace("{content}", state.getContent());

        String content = callLlm(prompt);
        List<ArticleState.ImageRequirement> imageRequirements = parseJsonListResponse(
                content, 
                new TypeToken<List<ArticleState.ImageRequirement>>(){}, 
                "配图需求"
        );
        state.setImageRequirements(imageRequirements);
        log.info("智能体4：配图需求分析成功, count={}", imageRequirements.size());
    }

    /**
     * 智能体5：生成配图（串行执行，支持混用多种配图方式）
     */
    private void agent5GenerateImages(ArticleState state, Consumer<String> streamHandler) {
        List<ArticleState.ImageResult> imageResults = new ArrayList<>();
        
        for (ArticleState.ImageRequirement requirement : state.getImageRequirements()) {
            String imageSource = requirement.getImageSource();
            log.info("智能体5：开始获取配图, position={}, imageSource={}, keywords={}", 
                    requirement.getPosition(), imageSource, requirement.getKeywords());
            
            // 使用策略模式根据 imageSource 选择对应的图片服务
            ImageServiceStrategy.ImageResult result = imageServiceStrategy.getImage(
                    imageSource,
                    requirement.getKeywords(),
                    requirement.getPrompt()
            );
            
            String imageUrl = result.getUrl();
            ImageMethodEnum method = result.getMethod();
            
            // 降级策略
            if (!result.isSuccess()) {
                imageUrl = imageServiceStrategy.getFallbackImage(requirement.getPosition());
                method = ImageMethodEnum.PICSUM;
                log.warn("智能体5：图片获取失败, 使用降级方案, position={}, originalSource={}", 
                        requirement.getPosition(), imageSource);
            }
            
            // 使用图片直接 URL（MVP 阶段不上传到 COS，简化流程）
            String finalImageUrl = cosService.useDirectUrl(imageUrl);
            
            // 创建配图结果
            ArticleState.ImageResult imageResult = buildImageResult(requirement, finalImageUrl, method);
            imageResults.add(imageResult);
            
            // 推送单张配图完成
            String imageCompleteMessage = SseMessageTypeEnum.IMAGE_COMPLETE.getStreamingPrefix() + GsonUtils.toJson(imageResult);
            streamHandler.accept(imageCompleteMessage);
            
            log.info("智能体5：配图获取成功, position={}, method={}", 
                    requirement.getPosition(), method.getValue());
        }
        
        state.setImages(imageResults);
        log.info("智能体5：所有配图生成完成, count={}", imageResults.size());
    }

    /**
     * 图文合成：将配图插入正文对应位置
     */
    private void mergeImagesIntoContent(ArticleState state) {
        String content = state.getContent();
        List<ArticleState.ImageResult> images = state.getImages();
        
        if (images == null || images.isEmpty()) {
            state.setFullContent(content);
            return;
        }

        StringBuilder fullContent = new StringBuilder();
        
        // 按行处理正文，在章节标题后插入对应图片
        String[] lines = content.split("\n");
        for (String line : lines) {
            fullContent.append(line).append("\n");
            
            // 检查是否是章节标题（以 ## 开头）
            if (line.startsWith("## ")) {
                String sectionTitle = line.substring(3).trim();
                insertImageAfterSection(fullContent, images, sectionTitle);
            }
        }
        
        state.setFullContent(fullContent.toString());
        log.info("图文合成完成, fullContentLength={}", fullContent.length());
    }

    // region 辅助方法

    /**
     * 调用 LLM（非流式）
     */
    private String callLlm(String prompt) {
        ChatResponse response = chatModel.call(new Prompt(new UserMessage(prompt)));
        return response.getResult().getOutput().getText();
    }

    /**
     * 调用 LLM（流式输出）
     */
    private String callLlmWithStreaming(String prompt, Consumer<String> streamHandler, SseMessageTypeEnum messageType) {
        StringBuilder contentBuilder = new StringBuilder();
        
        Flux<ChatResponse> streamResponse = chatModel.stream(new Prompt(new UserMessage(prompt)));
        
        streamResponse
                .doOnNext(response -> {
                    String chunk = response.getResult().getOutput().getText();
                    if (chunk != null && !chunk.isEmpty()) {
                        contentBuilder.append(chunk);
                        streamHandler.accept(messageType.getStreamingPrefix() + chunk);
                    }
                })
                .doOnError(error -> log.error("LLM 流式调用失败, messageType={}", messageType, error))
                .blockLast();
        
        return contentBuilder.toString();
    }

    /**
     * 解析 JSON 响应
     */
    private <T> T parseJsonResponse(String content, Class<T> clazz, String name) {
        try {
            return GsonUtils.fromJson(content, clazz);
        } catch (JsonSyntaxException e) {
            log.error("{}解析失败, content={}", name, content, e);
            throw new RuntimeException(name + "解析失败");
        }
    }

    /**
     * 解析 JSON 列表响应
     */
    private <T> T parseJsonListResponse(String content, TypeToken<T> typeToken, String name) {
        try {
            return GsonUtils.fromJson(content, typeToken);
        } catch (JsonSyntaxException e) {
            log.error("{}解析失败, content={}", name, content, e);
            throw new RuntimeException(name + "解析失败");
        }
    }

    /**
     * 构建配图结果
     */
    private ArticleState.ImageResult buildImageResult(ArticleState.ImageRequirement requirement, 
                                                       String imageUrl, 
                                                       ImageMethodEnum method) {
        ArticleState.ImageResult imageResult = new ArticleState.ImageResult();
        imageResult.setPosition(requirement.getPosition());
        imageResult.setUrl(imageUrl);
        imageResult.setMethod(method.getValue());
        imageResult.setKeywords(requirement.getKeywords());
        imageResult.setSectionTitle(requirement.getSectionTitle());
        imageResult.setDescription(requirement.getType());
        return imageResult;
    }

    /**
     * 在章节标题后插入对应图片
     */
    private void insertImageAfterSection(StringBuilder fullContent, 
                                          List<ArticleState.ImageResult> images, 
                                          String sectionTitle) {
        for (ArticleState.ImageResult image : images) {
            if (image.getPosition() > 1 && 
                image.getSectionTitle() != null && 
                sectionTitle.contains(image.getSectionTitle().trim())) {
                fullContent.append("\n![").append(image.getDescription())
                        .append("](").append(image.getUrl()).append(")\n");
                break;
            }
        }
    }

    // endregion
}
