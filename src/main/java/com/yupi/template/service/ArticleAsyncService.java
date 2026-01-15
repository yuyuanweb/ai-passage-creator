package com.yupi.template.service;

import com.google.gson.Gson;
import com.mybatisflex.core.query.QueryWrapper;
import com.yupi.template.manager.SseEmitterManager;
import com.yupi.template.mapper.ArticleMapper;
import com.yupi.template.model.dto.article.ArticleState;
import com.yupi.template.model.entity.Article;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import jakarta.annotation.Resource;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 文章异步任务服务
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Service
@Slf4j
public class ArticleAsyncService {

    @Resource
    private ArticleAgentService articleAgentService;

    @Resource
    private SseEmitterManager sseEmitterManager;

    @Resource
    private ArticleMapper articleMapper;

    private static final Gson GSON = new Gson();

    /**
     * 异步执行文章生成
     *
     * @param taskId 任务ID
     * @param topic  选题
     */
    @Async("articleExecutor")
    public void executeArticleGeneration(String taskId, String topic) {
        log.info("异步任务开始, taskId={}, topic={}", taskId, topic);
        
        try {
            // 更新状态为处理中
            updateArticleStatus(taskId, "PROCESSING", null);
            
            // 创建状态对象
            ArticleState state = new ArticleState();
            state.setTaskId(taskId);
            state.setTopic(topic);
            
            // 执行智能体编排,并通过 SSE 推送进度
            articleAgentService.executeArticleGeneration(state, message -> {
                handleAgentMessage(taskId, message, state);
            });
            
            // 保存完整文章到数据库
            saveArticleToDatabase(taskId, state);
            
            // 更新状态为已完成
            updateArticleStatus(taskId, "COMPLETED", null);
            
            // 推送完成消息
            Map<String, Object> completeData = new HashMap<>();
            completeData.put("type", "ALL_COMPLETE");
            completeData.put("taskId", taskId);
            sseEmitterManager.send(taskId, GSON.toJson(completeData));
            
            // 完成 SSE 连接
            sseEmitterManager.complete(taskId);
            
            log.info("异步任务完成, taskId={}", taskId);
        } catch (Exception e) {
            log.error("异步任务失败, taskId={}", taskId, e);
            
            // 更新状态为失败
            updateArticleStatus(taskId, "FAILED", e.getMessage());
            
            // 推送错误消息
            Map<String, Object> errorData = new HashMap<>();
            errorData.put("type", "ERROR");
            errorData.put("message", e.getMessage());
            sseEmitterManager.send(taskId, GSON.toJson(errorData));
            
            // 完成 SSE 连接
            sseEmitterManager.complete(taskId);
        }
    }

    /**
     * 处理智能体消息并推送
     */
    private void handleAgentMessage(String taskId, String message, ArticleState state) {
        Map<String, Object> data = new HashMap<>();
        
        if (message.equals("AGENT1_COMPLETE")) {
            // 智能体1完成
            data.put("type", "AGENT1_COMPLETE");
            data.put("title", state.getTitle());
        } else if (message.equals("AGENT2_COMPLETE")) {
            // 智能体2完成
            data.put("type", "AGENT2_COMPLETE");
            data.put("outline", state.getOutline().getSections());
        } else if (message.startsWith("AGENT3_STREAMING:")) {
            // 智能体3流式输出
            String chunk = message.substring("AGENT3_STREAMING:".length());
            data.put("type", "AGENT3_STREAMING");
            data.put("content", chunk);
        } else if (message.equals("AGENT3_COMPLETE")) {
            // 智能体3完成
            data.put("type", "AGENT3_COMPLETE");
        } else if (message.equals("AGENT4_COMPLETE")) {
            // 智能体4完成
            data.put("type", "AGENT4_COMPLETE");
            data.put("imageRequirements", state.getImageRequirements());
        } else if (message.startsWith("IMAGE_COMPLETE:")) {
            // 单张配图完成
            String imageJson = message.substring("IMAGE_COMPLETE:".length());
            data.put("type", "IMAGE_COMPLETE");
            data.put("image", GSON.fromJson(imageJson, ArticleState.ImageResult.class));
        } else if (message.equals("AGENT5_COMPLETE")) {
            // 智能体5完成
            data.put("type", "AGENT5_COMPLETE");
            data.put("images", state.getImages());
        } else {
            return;
        }
        
        sseEmitterManager.send(taskId, GSON.toJson(data));
    }

    /**
     * 保存文章到数据库
     */
    private void saveArticleToDatabase(String taskId, ArticleState state) {
        Article article = articleMapper.selectOneByQuery(
                QueryWrapper.create().eq("task_id", taskId)
        );
        
        if (article == null) {
            log.error("文章记录不存在, taskId={}", taskId);
            return;
        }
        
        article.setMainTitle(state.getTitle().getMainTitle());
        article.setSubTitle(state.getTitle().getSubTitle());
        article.setOutline(GSON.toJson(state.getOutline().getSections()));
        article.setContent(state.getContent());
        article.setImages(GSON.toJson(state.getImages()));
        article.setCompletedTime(LocalDateTime.now());
        
        articleMapper.update(article);
        log.info("文章保存成功, taskId={}", taskId);
    }

    /**
     * 更新文章状态
     */
    private void updateArticleStatus(String taskId, String status, String errorMessage) {
        Article article = articleMapper.selectOneByQuery(
                QueryWrapper.create().eq("task_id", taskId)
        );
        
        if (article == null) {
            log.error("文章记录不存在, taskId={}", taskId);
            return;
        }
        
        article.setStatus(status);
        article.setErrorMessage(errorMessage);
        articleMapper.update(article);
        
        log.info("文章状态已更新, taskId={}, status={}", taskId, status);
    }
}
