package service

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/model"
)

// MermaidService Mermaid 流程图生成服务
// 使用 mermaid-cli 将 Mermaid 代码转换为图片
type MermaidService struct {
	config config.MermaidConfig
}

// NewMermaidService 创建 Mermaid 服务
func NewMermaidService(cfg config.MermaidConfig) *MermaidService {
	return &MermaidService{
		config: cfg,
	}
}

// GetMethod 返回方法名
func (s *MermaidService) GetMethod() string {
	return common.ImageMethodMermaid
}

// IsAvailable 是否可用（检查 mmdc 命令是否存在）
func (s *MermaidService) IsAvailable() bool {
	if s.config.CLI == "" {
		return false
	}
	// 检查 mmdc 命令是否可用
	_, err := exec.LookPath(s.config.CLI)
	return err == nil
}

// SearchImage Mermaid 是生成类服务，不实现此方法
func (s *MermaidService) SearchImage(keywords string) (string, error) {
	return "", fmt.Errorf("Mermaid 是生成类服务，请使用 GetImageData")
}

// GetImageData 生成 Mermaid 图表数据
func (s *MermaidService) GetImageData(req *model.ImageRequest) (*model.ImageData, error) {
	// 优先使用 Prompt（Mermaid 代码），否则使用 Keywords
	mermaidCode := req.GetEffectiveParam(true)
	return s.GenerateDiagramData(mermaidCode)
}

// GenerateDiagramData 生成 Mermaid 图表数据
func (s *MermaidService) GenerateDiagramData(mermaidCode string) (*model.ImageData, error) {
	if strings.TrimSpace(mermaidCode) == "" {
		log.Println("Mermaid 代码为空")
		return nil, fmt.Errorf("Mermaid代码为空")
	}

	// 创建临时输入文件
	tmpInput, err := os.CreateTemp("", "mermaid_input_*.mmd")
	if err != nil {
		return nil, fmt.Errorf("创建临时输入文件失败: %w", err)
	}
	defer os.Remove(tmpInput.Name())

	// 写入 Mermaid 代码
	if _, err := tmpInput.WriteString(mermaidCode); err != nil {
		return nil, fmt.Errorf("写入Mermaid代码失败: %w", err)
	}
	tmpInput.Close()

	// 创建临时输出文件
	outputExtension := "." + s.config.OutputFormat
	tmpOutput, err := os.CreateTemp("", "mermaid_output_*"+outputExtension)
	if err != nil {
		return nil, fmt.Errorf("创建临时输出文件失败: %w", err)
	}
	tmpOutput.Close()
	defer os.Remove(tmpOutput.Name())

	// 转换为图片
	if err := s.convertMermaidToImage(tmpInput.Name(), tmpOutput.Name()); err != nil {
		return nil, err
	}

	// 检查输出文件
	fileInfo, err := os.Stat(tmpOutput.Name())
	if err != nil || fileInfo.Size() == 0 {
		return nil, fmt.Errorf("Mermaid CLI 执行失败，输出文件不存在或为空")
	}

	// 读取图片字节数据
	imageBytes, err := os.ReadFile(tmpOutput.Name())
	if err != nil {
		return nil, fmt.Errorf("读取输出文件失败: %w", err)
	}

	mimeType := s.getMimeType(s.config.OutputFormat)
	log.Printf("Mermaid 图表生成成功, size=%d bytes", len(imageBytes))

	return model.FromBytes(imageBytes, mimeType), nil
}

// convertMermaidToImage 使用 mmdc 转换 Mermaid 代码为图片
func (s *MermaidService) convertMermaidToImage(inputFile, outputFile string) error {
	args := []string{
		"-i", inputFile,
		"-o", outputFile,
		"-t", s.config.Theme,
		"-w", fmt.Sprintf("%d", s.config.Width),
		"-H", fmt.Sprintf("%d", s.config.Height),
	}

	ctx := context.Background()
	// 设置超时
	if s.config.Timeout > 0 {
		timeout := time.Duration(s.config.Timeout) * time.Millisecond
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, timeout)
		defer cancel()
	}

	cmd := exec.CommandContext(ctx, s.config.CLI, args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("Mermaid CLI 执行失败: %w, output: %s", err, string(output))
	}

	return nil
}

// getMimeType 根据输出格式获取 MIME 类型
func (s *MermaidService) getMimeType(format string) string {
	switch strings.ToLower(format) {
	case "png":
		return "image/png"
	case "svg":
		return "image/svg+xml"
	case "pdf":
		return "application/pdf"
	default:
		return "image/png"
	}
}
