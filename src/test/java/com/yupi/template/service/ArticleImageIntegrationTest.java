package com.yupi.template.service;

import com.yupi.template.model.dto.article.ArticleState;
import com.yupi.template.model.dto.image.ImageRequest;
import com.yupi.template.model.entity.Article;
import com.yupi.template.model.entity.User;
import com.yupi.template.model.enums.ArticleStatusEnum;
import com.yupi.template.utils.GsonUtils;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 文章配图集成测试
 * 测试所有配图方式（PEXELS、NANO_BANANA、MERMAID、ICONIFY、EMOJI_PACK）
 *
 * @author <a href="https://codefather.cn">编程导航学习圈</a>
 */
@SpringBootTest
@ActiveProfiles("local")
class ArticleImageIntegrationTest {

    @Autowired
    private ImageServiceStrategy imageServiceStrategy;

    @Autowired
    private ArticleService articleService;

    @Autowired
    private UserService userService;

    /**
     * 集成测试：使用测试文章测试所有配图方式
     */
    @Test
    void testAllImageMethodsWithArticle() {
        System.out.println("========== 开始测试所有配图方式 ==========\n");

        // 构建测试文章状态
        ArticleState state = buildTestArticleState();

        System.out.println("【测试文章】");
        System.out.println("标题: " + state.getTitle().getMainTitle());
        System.out.println("副标题: " + state.getTitle().getSubTitle());
        System.out.println("\n正文:\n" + state.getContent());
        System.out.println("\n========================================\n");

        // 手动构建配图需求（模拟智能体4输出）
        List<ArticleState.ImageRequirement> imageRequirements = buildImageRequirements();
        state.setImageRequirements(imageRequirements);

        // 测试智能体5：生成配图
        List<ArticleState.ImageResult> imageResults = new ArrayList<>();

        System.out.println("【开始生成配图】\n");

        for (ArticleState.ImageRequirement requirement : imageRequirements) {
            System.out.printf("Position %d - %s (%s)%n",
                    requirement.getPosition(),
                    requirement.getSectionTitle().isEmpty() ? "封面图" : requirement.getSectionTitle(),
                    requirement.getImageSource());

            // 构建请求
            ImageRequest request = ImageRequest.builder()
                    .keywords(requirement.getKeywords())
                    .prompt(requirement.getPrompt())
                    .position(requirement.getPosition())
                    .type(requirement.getType())
                    .build();

            // 使用策略模式获取图片
            ImageServiceStrategy.ImageResult result = imageServiceStrategy.getImage(
                    requirement.getImageSource(),
                    request
            );

            if (result.isSuccess()) {
                System.out.println("  ✓ 成功: " + result.getMethod().getDescription());
                System.out.println("  URL: " + 
                        (result.getUrl().length() > 100 
                                ? result.getUrl().substring(0, 100) + "..." 
                                : result.getUrl()));

                // 构建结果
                ArticleState.ImageResult imageResult = new ArticleState.ImageResult();
                imageResult.setPosition(requirement.getPosition());
                imageResult.setUrl(result.getUrl());
                imageResult.setMethod(result.getMethod().getValue());
                imageResult.setKeywords(requirement.getKeywords());
                imageResult.setSectionTitle(requirement.getSectionTitle());
                imageResult.setDescription(requirement.getType());
                imageResults.add(imageResult);
            } else {
                System.out.println("  ✗ 失败: 降级到 " + result.getMethod().getDescription());
            }

            System.out.println();
        }

        state.setImages(imageResults);

        // 图文合成
        String fullContent = mergeImagesIntoContent(state);
        state.setFullContent(fullContent);

        // 输出最终结果
        System.out.println("\n========================================");
        System.out.println("【配图完成统计】");
        System.out.println("总配图数: " + imageResults.size());
        for (ArticleState.ImageResult result : imageResults) {
            System.out.printf("- Position %d: %s%n", result.getPosition(), result.getMethod());
        }

        System.out.println("\n========================================");
        System.out.println("【最终图文内容】\n");
        System.out.println(fullContent);
        System.out.println("\n========================================");

        // 保存到数据库
        saveToDatabase(state);

        System.out.println("\n✓ 测试完成，数据已保存到数据库");
        System.out.println("任务ID: " + state.getTaskId());
    }

    /**
     * 保存文章到数据库
     */
    private void saveToDatabase(ArticleState state) {
        try {
            // 获取测试用户
            User testUser = userService.getById(1L);
            if (testUser == null) {
                System.out.println("警告：未找到测试用户，跳过数据库保存");
                return;
            }

            // 创建文章实体
            Article article = Article.builder()
                    .taskId(state.getTaskId())
                    .userId(testUser.getId())
                    .topic(state.getTopic())
                    .mainTitle(state.getTitle().getMainTitle())
                    .subTitle(state.getTitle().getSubTitle())
                    .outline(null)  // 测试跳过大纲
                    .content(state.getContent())
                    .fullContent(state.getFullContent())
                    .images(GsonUtils.toJson(state.getImages()))
                    .status(ArticleStatusEnum.COMPLETED.getValue())
                    .completedTime(LocalDateTime.now())
                    .build();

            // 保存到数据库
            boolean saved = articleService.save(article);
            
            if (saved) {
                System.out.println("✓ 文章已保存到数据库, ID: " + article.getId());
            } else {
                System.out.println("✗ 文章保存失败");
            }

        } catch (Exception e) {
            System.out.println("警告：保存到数据库失败: " + e.getMessage());
        }
    }

    /**
     * 构建测试文章状态
     */
    private ArticleState buildTestArticleState() {
        ArticleState state = new ArticleState();
        state.setTaskId("test-001");
        state.setTopic("多种配图方式测试");

        // 标题
        ArticleState.TitleResult title = new ArticleState.TitleResult();
        title.setMainTitle("5种配图方式完整演示");
        title.setSubTitle("PEXELS、AI生图、流程图、图标、表情包全覆盖");
        state.setTitle(title);

        // 正文（包含5个章节，对应5种配图方式）
        String content = """
## 真实场景展示

这一章节展示真实的办公场景照片，使用 PEXELS 图库检索。

团队协作是现代企业成功的关键因素。

## AI 创意插画

这一章节展示 AI 生成的创意插画，使用 NANO_BANANA 技术。

人工智能技术正在改变我们的工作方式。

## 系统架构图

这一章节展示系统架构流程图，使用 MERMAID 生成。

完整的系统架构包含多个组件的协同工作。

## 核心功能列表

这一章节使用图标标记核心功能，使用 ICONIFY 图标库。

我们的系统提供了完善的功能支持。

## 常见问题解答

这一章节使用表情包增加趣味性，使用 EMOJI_PACK 检索。

用户经常会遇到一些疑问，我们来一一解答。
""";
        state.setContent(content);

        return state;
    }

    /**
     * 构建配图需求（模拟智能体4输出）
     */
    private List<ArticleState.ImageRequirement> buildImageRequirements() {
        List<ArticleState.ImageRequirement> requirements = new ArrayList<>();

        // 1. PEXELS - 真实场景
        ArticleState.ImageRequirement req1 = new ArticleState.ImageRequirement();
        req1.setPosition(1);
        req1.setType("section");
        req1.setSectionTitle("真实场景展示");
        req1.setImageSource("PEXELS");
        req1.setKeywords("business teamwork office meeting");
        req1.setPrompt("");
        requirements.add(req1);

        // 2. NANO_BANANA - AI 生图
        ArticleState.ImageRequirement req2 = new ArticleState.ImageRequirement();
        req2.setPosition(2);
        req2.setType("section");
        req2.setSectionTitle("AI 创意插画");
        req2.setImageSource("NANO_BANANA");
        req2.setKeywords("");
        req2.setPrompt("A minimalist illustration of artificial intelligence concept, featuring a glowing neural network with blue and purple gradient, modern digital art style, clean composition");
        requirements.add(req2);

        // 3. MERMAID - 流程图
        ArticleState.ImageRequirement req3 = new ArticleState.ImageRequirement();
        req3.setPosition(3);
        req3.setType("section");
        req3.setSectionTitle("系统架构图");
        req3.setImageSource("MERMAID");
        req3.setKeywords("");
        req3.setPrompt("flowchart TB\n    User[用户] --> LB[负载均衡]\n    LB --> App1[应用服务器1]\n    LB --> App2[应用服务器2]\n    App1 --> DB[(数据库)]\n    App2 --> DB\n    App1 --> Cache[(Redis缓存)]\n    App2 --> Cache");
        requirements.add(req3);

        // 4. ICONIFY - 图标
        ArticleState.ImageRequirement req4 = new ArticleState.ImageRequirement();
        req4.setPosition(4);
        req4.setType("section");
        req4.setSectionTitle("核心功能列表");
        req4.setImageSource("ICONIFY");
        req4.setKeywords("check circle");
        req4.setPrompt("");
        requirements.add(req4);

        // 5. EMOJI_PACK - 表情包
        ArticleState.ImageRequirement req5 = new ArticleState.ImageRequirement();
        req5.setPosition(5);
        req5.setType("section");
        req5.setSectionTitle("常见问题解答");
        req5.setImageSource("EMOJI_PACK");
        req5.setKeywords("疑问");
        req5.setPrompt("");
        requirements.add(req5);

        return requirements;
    }

    /**
     * 图文合成：将配图插入正文对应位置
     */
    private String mergeImagesIntoContent(ArticleState state) {
        String content = state.getContent();
        List<ArticleState.ImageResult> images = state.getImages();

        if (images == null || images.isEmpty()) {
            return content;
        }

        StringBuilder fullContent = new StringBuilder();

        // 按行处理正文，在章节标题后插入对应图片
        String[] lines = content.split("\n");
        for (String line : lines) {
            fullContent.append(line).append("\n");

            // 检查是否是章节标题（以 ## 开头）
            if (line.startsWith("## ")) {
                String sectionTitle = line.substring(3).trim();

                // 查找对应的配图
                for (ArticleState.ImageResult image : images) {
                    if (image.getSectionTitle() != null 
                            && sectionTitle.contains(image.getSectionTitle().trim())) {
                        fullContent.append("\n![")
                                .append(image.getDescription())
                                .append("](")
                                .append(image.getUrl())
                                .append(")\n");
                        break;
                    }
                }
            }
        }

        return fullContent.toString();
    }
}
