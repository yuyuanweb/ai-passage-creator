package service

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"time"

	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/model"
)

// IconifyService Iconify 图标库检索服务
// 提供 275k+ 开源图标检索和 SVG 生成
type IconifyService struct {
	config config.IconifyConfig
	client *http.Client
}

// NewIconifyService 创建 Iconify 服务
func NewIconifyService(cfg config.IconifyConfig) *IconifyService {
	return &IconifyService{
		config: cfg,
		client: &http.Client{
			Timeout: time.Duration(cfg.Timeout) * time.Millisecond,
		},
	}
}

// GetMethod 返回方法名
func (s *IconifyService) GetMethod() string {
	return common.ImageMethodIconify
}

// IsAvailable 是否可用
func (s *IconifyService) IsAvailable() bool {
	return s.config.BaseURL != ""
}

// SearchImage 搜索图标并返回 SVG URL
func (s *IconifyService) SearchImage(keywords string) (string, error) {
	if keywords == "" {
		log.Println("Iconify 搜索关键词为空")
		return "", fmt.Errorf("关键词为空")
	}

	// 1. 搜索图标
	searchURL := s.buildSearchURL(keywords)
	searchResult, err := s.callAPI(searchURL)
	if err != nil {
		log.Printf("Iconify 搜索API调用失败, keywords=%s, err=%v", keywords, err)
		return "", err
	}

	// 2. 解析结果，获取第一个图标
	iconName, err := s.extractFirstIcon(searchResult)
	if err != nil || iconName == "" {
		log.Printf("Iconify 未检索到图标: %s", keywords)
		return "", fmt.Errorf("未找到图标")
	}

	// 3. 构建 SVG URL
	svgURL := s.buildSVGURL(iconName)
	log.Printf("Iconify 图标检索成功: %s -> %s", keywords, iconName)

	return svgURL, nil
}

// GetImageData 获取图片数据（Iconify 直接返回 URL，不需要下载）
func (s *IconifyService) GetImageData(req *model.ImageRequest) (*model.ImageData, error) {
	// Iconify 是检索类服务，使用 SearchImage
	url, err := s.SearchImage(req.Keywords)
	if err != nil {
		return nil, err
	}
	return model.FromURL(url), nil
}

// buildSearchURL 构建搜索 URL
func (s *IconifyService) buildSearchURL(keywords string) string {
	encodedKeywords := url.QueryEscape(keywords)
	return fmt.Sprintf("%s/search?query=%s&limit=5",
		s.config.BaseURL,
		encodedKeywords)
}

// buildSVGURL 构建 SVG URL
func (s *IconifyService) buildSVGURL(iconName string) string {
	return fmt.Sprintf("%s/%s.svg", s.config.BaseURL, iconName)
}

// callAPI 调用 Iconify API
func (s *IconifyService) callAPI(apiURL string) (string, error) {
	resp, err := s.client.Get(apiURL)
	if err != nil {
		return "", fmt.Errorf("HTTP请求失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("HTTP状态码错误: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("读取响应失败: %w", err)
	}

	return string(body), nil
}

// extractFirstIcon 从搜索结果中提取第一个图标名称
func (s *IconifyService) extractFirstIcon(searchResult string) (string, error) {
	var result struct {
		Icons []string `json:"icons"`
	}

	if err := json.Unmarshal([]byte(searchResult), &result); err != nil {
		return "", fmt.Errorf("解析JSON失败: %w", err)
	}

	if len(result.Icons) == 0 {
		return "", fmt.Errorf("未找到图标")
	}

	return result.Icons[0], nil
}
