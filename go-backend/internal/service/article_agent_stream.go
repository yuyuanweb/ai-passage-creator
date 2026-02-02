package service

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"github.com/tmc/langchaingo/llms"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
)

// agent2GenerateOutlineStream 智能体2：生成大纲（流式输出）
func (s *ArticleAgentService) agent2GenerateOutlineStream(ctx context.Context, state *model.ArticleState) error {
	prompt := strings.ReplaceAll(common.Agent2OutlinePrompt, "{mainTitle}", state.Title.MainTitle)
	prompt = strings.ReplaceAll(prompt, "{subTitle}", state.Title.SubTitle)

	var contentBuilder strings.Builder

	// 流式生成
	_, err := s.llm.GenerateContent(ctx, []llms.MessageContent{
		llms.TextParts(llms.ChatMessageTypeHuman, prompt),
	}, llms.WithStreamingFunc(func(ctx context.Context, chunk []byte) error {
		text := string(chunk)
		contentBuilder.WriteString(text)

		// 推送流式内容
		s.sendMessage(state.TaskID, map[string]interface{}{
			"type":    "AGENT2_STREAMING",
			"content": text,
		})
		return nil
	}))

	if err != nil {
		return err
	}

	content := contentBuilder.String()

	var outline model.OutlineResult
	if err := json.Unmarshal([]byte(content), &outline); err != nil {
		log.Printf("智能体2：大纲解析失败, content=%s", content)
		return fmt.Errorf("parse outline failed: %w", err)
	}

	state.Outline = &outline
	log.Printf("智能体2：大纲生成成功, sections=%d", len(outline.Sections))
	return nil
}

// mergeImagesIntoContent 图文合成：根据占位符将配图插入正文
func (s *ArticleAgentService) mergeImagesIntoContent(state *model.ArticleState) {
	// 使用包含占位符的正文（Agent4 生成）
	content := state.ContentWithPlaceholders
	images := state.Images

	log.Printf("图文合成：ContentWithPlaceholders长度=%d, 图片数量=%d", len(content), len(images))

	if len(images) == 0 {
		state.FullContent = content
		return
	}

	fullContent := content

	// 遍历所有配图，根据占位符替换为实际图片
	replacedCount := 0
	for i, image := range images {
		placeholderID := image.PlaceholderID
		log.Printf("图文合成：处理图片[%d] placeholderID=%s, url=%s", i, placeholderID, image.URL)

		if placeholderID != "" {
			// 检查占位符是否存在
			if strings.Contains(fullContent, placeholderID) {
				imageMarkdown := fmt.Sprintf("![%s](%s)", image.Description, image.URL)
				fullContent = strings.ReplaceAll(fullContent, placeholderID, imageMarkdown)
				replacedCount++
				log.Printf("图文合成：成功替换占位符 %s", placeholderID)
			} else {
				log.Printf("图文合成：警告 - 占位符未找到: %s", placeholderID)
			}
		} else {
			log.Printf("图文合成：警告 - 图片[%d]的placeholderID为空", i)
		}
	}

	state.FullContent = fullContent
	log.Printf("图文合成完成, fullContentLength=%d, 成功替换=%d个占位符", len(fullContent), replacedCount)
}
