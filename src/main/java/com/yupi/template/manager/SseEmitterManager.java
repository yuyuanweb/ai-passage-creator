package com.yupi.template.manager;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * SSE Emitter 管理器
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Component
@Slf4j
public class SseEmitterManager {

    /**
     * 存储所有的 SseEmitter
     */
    private final Map<String, SseEmitter> emitterMap = new ConcurrentHashMap<>();

    /**
     * 超时时间：30分钟
     */
    private static final long TIMEOUT = 30 * 60 * 1000;

    /**
     * 创建 SseEmitter
     *
     * @param taskId 任务ID
     * @return SseEmitter
     */
    public SseEmitter createEmitter(String taskId) {
        SseEmitter emitter = new SseEmitter(TIMEOUT);
        
        // 设置超时回调
        emitter.onTimeout(() -> {
            log.warn("SSE 连接超时, taskId={}", taskId);
            emitterMap.remove(taskId);
        });
        
        // 设置完成回调
        emitter.onCompletion(() -> {
            log.info("SSE 连接完成, taskId={}", taskId);
            emitterMap.remove(taskId);
        });
        
        // 设置错误回调
        emitter.onError((e) -> {
            log.error("SSE 连接错误, taskId={}", taskId, e);
            emitterMap.remove(taskId);
        });
        
        emitterMap.put(taskId, emitter);
        log.info("SSE 连接已创建, taskId={}", taskId);
        
        return emitter;
    }

    /**
     * 发送消息
     *
     * @param taskId  任务ID
     * @param message 消息内容
     */
    public void send(String taskId, String message) {
        SseEmitter emitter = emitterMap.get(taskId);
        if (emitter == null) {
            log.warn("SSE Emitter 不存在, taskId={}", taskId);
            return;
        }
        
        try {
            emitter.send(SseEmitter.event()
                    .data(message)
                    .reconnectTime(3000));
            log.debug("SSE 消息发送成功, taskId={}, message={}", taskId, message);
        } catch (IOException e) {
            log.error("SSE 消息发送失败, taskId={}", taskId, e);
            emitterMap.remove(taskId);
        }
    }

    /**
     * 完成连接
     *
     * @param taskId 任务ID
     */
    public void complete(String taskId) {
        SseEmitter emitter = emitterMap.get(taskId);
        if (emitter == null) {
            log.warn("SSE Emitter 不存在, taskId={}", taskId);
            return;
        }
        
        try {
            emitter.complete();
            log.info("SSE 连接已完成, taskId={}", taskId);
        } catch (Exception e) {
            log.error("SSE 连接完成失败, taskId={}", taskId, e);
        } finally {
            emitterMap.remove(taskId);
        }
    }

    /**
     * 检查 Emitter 是否存在
     *
     * @param taskId 任务ID
     * @return 是否存在
     */
    public boolean exists(String taskId) {
        return emitterMap.containsKey(taskId);
    }
}
