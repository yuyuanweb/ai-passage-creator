package com.yupi.template.model.enums;

import lombok.Getter;

/**
 * 文章阶段枚举
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@Getter
public enum ArticlePhaseEnum {

    PENDING("PENDING", "等待处理"),
    TITLE_GENERATING("TITLE_GENERATING", "生成标题中"),
    TITLE_SELECTING("TITLE_SELECTING", "等待选择标题"),
    OUTLINE_GENERATING("OUTLINE_GENERATING", "生成大纲中"),
    OUTLINE_EDITING("OUTLINE_EDITING", "等待编辑大纲"),
    CONTENT_GENERATING("CONTENT_GENERATING", "生成正文中");

    /**
     * 阶段值
     */
    private final String value;

    /**
     * 阶段描述
     */
    private final String description;

    ArticlePhaseEnum(String value, String description) {
        this.value = value;
        this.description = description;
    }

    /**
     * 根据值获取枚举
     *
     * @param value 阶段值
     * @return 枚举实例
     */
    public static ArticlePhaseEnum getByValue(String value) {
        if (value == null) {
            return null;
        }
        for (ArticlePhaseEnum phaseEnum : values()) {
            if (phaseEnum.getValue().equals(value)) {
                return phaseEnum;
            }
        }
        return null;
    }

    /**
     * 校验是否可以转换到目标阶段
     *
     * @param targetPhase 目标阶段
     * @return 是否可以转换
     */
    public boolean canTransitionTo(ArticlePhaseEnum targetPhase) {
        if (targetPhase == null) {
            return false;
        }
        
        // 定义合法的状态转换
        return switch (this) {
            case PENDING -> targetPhase == TITLE_GENERATING;
            case TITLE_GENERATING -> targetPhase == TITLE_SELECTING;
            case TITLE_SELECTING -> targetPhase == OUTLINE_GENERATING;
            case OUTLINE_GENERATING -> targetPhase == OUTLINE_EDITING;
            case OUTLINE_EDITING -> targetPhase == CONTENT_GENERATING;
            case CONTENT_GENERATING -> false; // 最终阶段，不再转换
        };
    }
}
