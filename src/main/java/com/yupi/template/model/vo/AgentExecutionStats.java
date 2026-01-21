package com.yupi.template.model.vo;

import com.yupi.template.model.entity.AgentLog;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * 智能体执行统计 VO
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentExecutionStats implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 总耗时（毫秒）
     */
    private Integer totalDurationMs;

    /**
     * 智能体数量
     */
    private Integer agentCount;

    /**
     * 各智能体耗时（key: agentName, value: durationMs）
     */
    private Map<String, Integer> agentDurations;

    /**
     * 总体状态：SUCCESS（全部成功）、FAILED（存在失败）、RUNNING（执行中）
     */
    private String overallStatus;

    /**
     * 详细日志列表
     */
    private List<AgentLog> logs;
}
