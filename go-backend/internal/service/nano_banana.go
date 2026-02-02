package service

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/model"
	"google.golang.org/genai"
)

// NanoBananaService Nano Banana AI 生图服务（基于 Gemini API）
type NanoBananaService struct {
	config config.NanoBananaConfig
}

// NewNanoBananaService 创建 Nano Banana 服务
func NewNanoBananaService(cfg config.NanoBananaConfig) *NanoBananaService {
	return &NanoBananaService{
		config: cfg,
	}
}

// GetMethod 返回方法名
func (s *NanoBananaService) GetMethod() string {
	return common.ImageMethodNanoBanana
}

// IsAvailable 是否可用
func (s *NanoBananaService) IsAvailable() bool {
	return s.config.APIKey != "" && s.config.Model != ""
}

// SearchImage NanoBanana 是生成类服务，不实现此方法
func (s *NanoBananaService) SearchImage(keywords string) (string, error) {
	return "", fmt.Errorf("NanoBanana 是生成类服务，请使用 GetImageData")
}

// GetImageData 生成图片数据
func (s *NanoBananaService) GetImageData(req *model.ImageRequest) (*model.ImageData, error) {
	prompt := req.GetEffectiveParam(true)
	return s.GenerateImageData(prompt)
}

// GenerateImageData 根据提示词生成图片数据
func (s *NanoBananaService) GenerateImageData(prompt string) (*model.ImageData, error) {
	if strings.TrimSpace(prompt) == "" {
		return nil, fmt.Errorf("生图提示词为空")
	}

	ctx := context.Background()

	// 创建客户端（使用官方 google.golang.org/genai 包）
	client, err := genai.NewClient(ctx, &genai.ClientConfig{
		APIKey: s.config.APIKey,
	})
	if err != nil {
		return nil, fmt.Errorf("创建Gemini客户端失败: %w", err)
	}

	log.Printf("Nano Banana 开始生成图片, model=%s, prompt=%s", s.config.Model, prompt)

	// 构建内容
	contents := []*genai.Content{
		{
			Role: genai.RoleUser,
			Parts: []*genai.Part{
				{Text: prompt},
			},
		},
	}

	// 生成内容（使用官方 API）
	result, err := client.Models.GenerateContent(ctx, s.config.Model, contents, nil)
	if err != nil {
		return nil, fmt.Errorf("生成图片失败: %w", err)
	}

	// 提取图片数据
	if result != nil && result.Candidates != nil && len(result.Candidates) > 0 {
		for _, part := range result.Candidates[0].Content.Parts {
			// 检查是否为 InlineData（图片）
			if part.InlineData != nil {
				imageBytes := part.InlineData.Data
				if len(imageBytes) > 0 {
					// 获取 MIME 类型
					mimeType := part.InlineData.MIMEType
					if mimeType == "" {
						mimeType = "image/png"
					}

					log.Printf("Nano Banana 图片生成成功, size=%d bytes, mimeType=%s",
						len(imageBytes), mimeType)

					return model.FromBytes(imageBytes, mimeType), nil
				}
			}

			// 如果是文本，记录日志
			if part.Text != "" {
				log.Printf("Nano Banana 响应文本: %s", part.Text)
			}
		}
	}

	return nil, fmt.Errorf("Nano Banana 未生成图片")
}
