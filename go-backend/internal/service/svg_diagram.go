package service

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/model"

	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/openai"
)

// SVGDiagramService SVG 概念示意图生成服务
// 调用 LLM 生成 SVG 代码
type SVGDiagramService struct {
	config   config.SVGDiagramConfig
	aiConfig config.AIConfig
}

// NewSVGDiagramService 创建 SVG 示意图服务
func NewSVGDiagramService(cfg config.SVGDiagramConfig, aiCfg config.AIConfig) *SVGDiagramService {
	return &SVGDiagramService{
		config:   cfg,
		aiConfig: aiCfg,
	}
}

// GetMethod 返回方法名
func (s *SVGDiagramService) GetMethod() string {
	return common.ImageMethodSVGDiagram
}

// IsAvailable 是否可用
func (s *SVGDiagramService) IsAvailable() bool {
	return s.config.Enabled && s.aiConfig.DashScope.APIKey != ""
}

// SearchImage SVGDiagram 是生成类服务，不实现此方法
func (s *SVGDiagramService) SearchImage(keywords string) (string, error) {
	return "", fmt.Errorf("SVGDiagram 是生成类服务，请使用 GetImageData")
}

// GetImageData 生成 SVG 示意图数据
func (s *SVGDiagramService) GetImageData(req *model.ImageRequest) (*model.ImageData, error) {
	requirement := req.GetEffectiveParam(true)
	return s.GenerateSVGDiagramData(requirement)
}

// GenerateSVGDiagramData 生成 SVG 概念示意图数据
func (s *SVGDiagramService) GenerateSVGDiagramData(requirement string) (*model.ImageData, error) {
	if strings.TrimSpace(requirement) == "" {
		log.Println("SVG 图表需求为空")
		return nil, fmt.Errorf("需求为空")
	}

	// 1. 调用 LLM 生成 SVG 代码
	svgCode, err := s.callLLMToGenerateSVG(requirement)
	if err != nil || strings.TrimSpace(svgCode) == "" {
		return nil, fmt.Errorf("LLM 未生成 SVG 代码: %w", err)
	}

	// 2. 验证 SVG 格式
	if !s.isValidSVG(svgCode) {
		return nil, fmt.Errorf("生成的 SVG 代码格式无效")
	}

	// 3. 转换为字节数据
	svgBytes := []byte(svgCode)

	log.Printf("SVG 概念示意图生成成功, size=%d bytes", len(svgBytes))
	return model.FromBytes(svgBytes, "image/svg+xml"), nil
}

// callLLMToGenerateSVG 调用 LLM 生成 SVG 代码
func (s *SVGDiagramService) callLLMToGenerateSVG(requirement string) (string, error) {
	// 创建 LLM 客户端
	llm, err := openai.New(
		openai.WithBaseURL("https://dashscope.aliyuncs.com/compatible-mode/v1"),
		openai.WithToken(s.aiConfig.DashScope.APIKey),
		openai.WithModel(s.aiConfig.DashScope.Model),
	)
	if err != nil {
		return "", fmt.Errorf("创建LLM客户端失败: %w", err)
	}

	// 构建提示词
	prompt := strings.ReplaceAll(common.SVGDiagramGenerationPrompt, "{requirement}", requirement)

	// 调用 LLM
	ctx := context.Background()
	content, err := llms.GenerateFromSinglePrompt(ctx, llm, prompt)
	if err != nil {
		return "", fmt.Errorf("LLM调用失败: %w", err)
	}

	return strings.TrimSpace(content), nil
}

// isValidSVG 验证 SVG 格式
func (s *SVGDiagramService) isValidSVG(svgCode string) bool {
	trimmed := strings.TrimSpace(svgCode)
	// 简单验证：包含 <svg 和 </svg> 标签
	return strings.Contains(strings.ToLower(trimmed), "<svg") &&
		strings.Contains(strings.ToLower(trimmed), "</svg>")
}
