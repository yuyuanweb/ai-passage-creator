package com.yupi.template.service;

import com.alibaba.cloud.ai.dashscope.chat.DashScopeChatModel;
import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import com.yupi.template.constant.PromptConstant;
import com.yupi.template.model.dto.article.ArticleState;
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
    private PexelsService pexelsService;

    @Resource
    private CosService cosService;

    private static final Gson GSON = new Gson();

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
            streamHandler.accept("AGENT1_COMPLETE");

            // 智能体2：生成大纲
            log.info("智能体2：开始生成大纲, taskId={}", state.getTaskId());
            agent2GenerateOutline(state);
            streamHandler.accept("AGENT2_COMPLETE");

            // 智能体3：生成正文（流式输出）
            log.info("智能体3：开始生成正文, taskId={}", state.getTaskId());
            agent3GenerateContent(state, streamHandler);
            streamHandler.accept("AGENT3_COMPLETE");

            // 智能体4：分析配图需求
            log.info("智能体4：开始分析配图需求, taskId={}", state.getTaskId());
            agent4AnalyzeImageRequirements(state);
            streamHandler.accept("AGENT4_COMPLETE");

            // 智能体5：生成配图
            log.info("智能体5：开始生成配图, taskId={}", state.getTaskId());
            agent5GenerateImages(state, streamHandler);
            streamHandler.accept("AGENT5_COMPLETE");

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

        ChatResponse response = chatModel.call(new Prompt(new UserMessage(prompt)));
        String content = response.getResult().getOutput().getText();
        
        try {
            ArticleState.TitleResult titleResult = GSON.fromJson(content, ArticleState.TitleResult.class);
            state.setTitle(titleResult);
            log.info("智能体1：标题生成成功, mainTitle={}", titleResult.getMainTitle());
        } catch (JsonSyntaxException e) {
            log.error("智能体1：标题解析失败, content={}", content, e);
            throw new RuntimeException("标题解析失败");
        }
    }

    /**
     * 智能体2：生成大纲
     */
    private void agent2GenerateOutline(ArticleState state) {
        String prompt = PromptConstant.AGENT2_OUTLINE_PROMPT
                .replace("{mainTitle}", state.getTitle().getMainTitle())
                .replace("{subTitle}", state.getTitle().getSubTitle());

        ChatResponse response = chatModel.call(new Prompt(new UserMessage(prompt)));
        String content = response.getResult().getOutput().getText();
        
        try {
            ArticleState.OutlineResult outlineResult = GSON.fromJson(content, ArticleState.OutlineResult.class);
            state.setOutline(outlineResult);
            log.info("智能体2：大纲生成成功, sections={}", outlineResult.getSections().size());
        } catch (JsonSyntaxException e) {
            log.error("智能体2：大纲解析失败, content={}", content, e);
            throw new RuntimeException("大纲解析失败");
        }
    }

    /**
     * 智能体3：生成正文（流式输出）
     */
    private void agent3GenerateContent(ArticleState state, Consumer<String> streamHandler) {
        String outlineText = GSON.toJson(state.getOutline().getSections());
        String prompt = PromptConstant.AGENT3_CONTENT_PROMPT
                .replace("{mainTitle}", state.getTitle().getMainTitle())
                .replace("{subTitle}", state.getTitle().getSubTitle())
                .replace("{outline}", outlineText);

        StringBuilder contentBuilder = new StringBuilder();
        
        Flux<ChatResponse> streamResponse = chatModel.stream(new Prompt(new UserMessage(prompt)));
        streamResponse.subscribe(
                response -> {
                    String chunk = response.getResult().getOutput().getText();
                    contentBuilder.append(chunk);
                    // 推送流式内容
                    streamHandler.accept("AGENT3_STREAMING:" + chunk);
                },
                error -> {
                    log.error("智能体3：正文生成失败", error);
                    throw new RuntimeException("正文生成失败: " + error.getMessage());
                },
                () -> {
                    state.setContent(contentBuilder.toString());
                    log.info("智能体3：正文生成成功, length={}", contentBuilder.length());
                }
        );
        
        // 等待流式输出完成
        streamResponse.blockLast();
    }

    /**
     * 智能体4：分析配图需求
     */
    private void agent4AnalyzeImageRequirements(ArticleState state) {
        String prompt = PromptConstant.AGENT4_IMAGE_REQUIREMENTS_PROMPT
                .replace("{mainTitle}", state.getTitle().getMainTitle())
                .replace("{content}", state.getContent());

        ChatResponse response = chatModel.call(new Prompt(new UserMessage(prompt)));
        String content = response.getResult().getOutput().getText();
        
        try {
            List<ArticleState.ImageRequirement> imageRequirements = GSON.fromJson(
                    content, 
                    new TypeToken<List<ArticleState.ImageRequirement>>(){}.getType()
            );
            state.setImageRequirements(imageRequirements);
            log.info("智能体4：配图需求分析成功, count={}", imageRequirements.size());
        } catch (JsonSyntaxException e) {
            log.error("智能体4：配图需求解析失败, content={}", content, e);
            throw new RuntimeException("配图需求解析失败");
        }
    }

    /**
     * 智能体5：生成配图（串行执行）
     */
    private void agent5GenerateImages(ArticleState state, Consumer<String> streamHandler) {
        List<ArticleState.ImageResult> imageResults = new ArrayList<>();
        
        for (ArticleState.ImageRequirement requirement : state.getImageRequirements()) {
            log.info("智能体5：开始检索配图, position={}, keywords={}", 
                    requirement.getPosition(), requirement.getKeywords());
            
            // 调用 Pexels API 检索图片
            String imageUrl = pexelsService.searchImage(requirement.getKeywords());
            
            // 降级策略
            String method = "PEXELS";
            if (imageUrl == null) {
                imageUrl = pexelsService.getFallbackImage(requirement.getPosition());
                method = "PICSUM";
                log.warn("智能体5：Pexels 检索失败,使用降级方案, position={}", requirement.getPosition());
            }
            
            // 使用图片直接 URL（MVP 阶段不上传到 COS，简化流程）
            String finalImageUrl = cosService.useDirectUrl(imageUrl);
            
            // 创建配图结果
            ArticleState.ImageResult imageResult = new ArticleState.ImageResult();
            imageResult.setPosition(requirement.getPosition());
            imageResult.setUrl(finalImageUrl);
            imageResult.setMethod(method);
            imageResult.setKeywords(requirement.getKeywords());
            imageResult.setDescription(requirement.getType());
            
            imageResults.add(imageResult);
            
            // 推送单张配图完成
            streamHandler.accept("IMAGE_COMPLETE:" + GSON.toJson(imageResult));
            
            log.info("智能体5：配图检索成功, position={}, method={}", 
                    requirement.getPosition(), method);
        }
        
        state.setImages(imageResults);
        log.info("智能体5：所有配图生成完成, count={}", imageResults.size());
    }
}
