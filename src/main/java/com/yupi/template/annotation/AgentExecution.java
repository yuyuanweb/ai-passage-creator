package com.yupi.template.annotation;

import java.lang.annotation.*;

/**
 * 智能体执行注解
 * 用于标记智能体方法，自动记录执行日志和性能数据
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface AgentExecution {
    
    /**
     * 智能体名称
     * 例如: "agent1_generate_titles", "agent2_generate_outline"
     */
    String value();
    
    /**
     * 智能体描述
     */
    String description() default "";
}
