# 添加阶段相关字段
# @author <a href="https://codefather.cn">编程导航学习圈</a>

-- 为 article 表添加阶段相关字段
ALTER TABLE article
    ADD COLUMN phase VARCHAR(50) DEFAULT 'PENDING' COMMENT '当前阶段：PENDING/TITLE_GENERATING/TITLE_SELECTING/OUTLINE_GENERATING/OUTLINE_EDITING/CONTENT_GENERATING' AFTER status,
    ADD COLUMN titleOptions JSON NULL COMMENT '标题方案列表（3-5个方案）' AFTER subTitle,
    ADD COLUMN userDescription TEXT NULL COMMENT '用户补充描述' AFTER topic,
    ADD COLUMN enabledImageMethods JSON NULL COMMENT '允许的配图方式列表' AFTER userDescription;
