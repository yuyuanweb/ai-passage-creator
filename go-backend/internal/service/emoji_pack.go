package service

import (
	"fmt"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/model"
)

// EmojiPackService 表情包检索服务（基于 Bing 图片搜索）
// 程序自动在关键词后拼接"表情包"进行搜索
type EmojiPackService struct {
	config config.EmojiPackConfig
}

// NewEmojiPackService 创建表情包服务
func NewEmojiPackService(cfg config.EmojiPackConfig) *EmojiPackService {
	return &EmojiPackService{
		config: cfg,
	}
}

// GetMethod 返回方法名
func (s *EmojiPackService) GetMethod() string {
	return common.ImageMethodEmojiPack
}

// IsAvailable 是否可用
func (s *EmojiPackService) IsAvailable() bool {
	return s.config.Suffix != ""
}

// SearchImage 搜索表情包并返回图片 URL
func (s *EmojiPackService) SearchImage(keywords string) (string, error) {
	if strings.TrimSpace(keywords) == "" {
		log.Println("表情包搜索关键词为空")
		return "", fmt.Errorf("关键词为空")
	}

	// 1. 构建搜索词（程序固定拼接"表情包"）
	searchText := keywords + s.config.Suffix
	log.Printf("表情包搜索: %s -> %s", keywords, searchText)

	// 2. 构建搜索 URL
	fetchURL := s.buildSearchURL(searchText)

	// 3. 使用 goquery 获取页面
	timeout := time.Duration(s.config.Timeout) * time.Millisecond
	client := &http.Client{Timeout: timeout}

	req, err := http.NewRequest("GET", fetchURL, nil)
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Bing 页面获取失败, keywords=%s, err=%v", keywords, err)
		return "", fmt.Errorf("页面获取失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("Bing 返回错误状态码, keywords=%s, status=%d", keywords, resp.StatusCode)
		return "", fmt.Errorf("HTTP状态码错误: %d", resp.StatusCode)
	}

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		log.Printf("解析HTML失败, keywords=%s, err=%v", keywords, err)
		return "", fmt.Errorf("解析HTML失败: %w", err)
	}

	// 4. 定位图片容器
	div := doc.Find(".dgControl").First()
	if div.Length() == 0 {
		log.Printf("Bing 未找到图片容器, keywords=%s", keywords)
		return "", fmt.Errorf("未找到图片容器")
	}

	// 5. 使用 CSS 选择器提取图片
	imgElements := div.Find("img.mimg")
	if imgElements.Length() == 0 {
		log.Printf("Bing 未检索到表情包, keywords=%s, searchText=%s", keywords, searchText)
		return "", fmt.Errorf("未检索到表情包")
	}

	// 6. 获取第一张图片 URL
	imageURL, exists := imgElements.First().Attr("src")
	if !exists || strings.TrimSpace(imageURL) == "" {
		log.Printf("图片 URL 为空, keywords=%s", keywords)
		return "", fmt.Errorf("图片URL为空")
	}

	// 7. 清理 URL 参数（移除 ?w=xxx&h=xxx）
	imageURL = s.cleanImageURL(imageURL)

	log.Printf("表情包检索成功: %s -> %s", keywords, imageURL)
	return imageURL, nil
}

// GetImageData 获取图片数据（EmojiPack 是检索类服务，使用 SearchImage）
func (s *EmojiPackService) GetImageData(req *model.ImageRequest) (*model.ImageData, error) {
	url, err := s.SearchImage(req.Keywords)
	if err != nil {
		return nil, err
	}
	return model.FromURL(url), nil
}

// buildSearchURL 构建 Bing 图片搜索 URL
func (s *EmojiPackService) buildSearchURL(searchText string) string {
	encodedText := url.QueryEscape(searchText)
	// 必须添加 mmasync=1 参数
	return fmt.Sprintf("%s?q=%s&mmasync=1",
		common.BingImageSearchURL,
		encodedText)
}

// cleanImageURL 清理图片 URL 参数
// 移除 ?w=xxx&h=xxx 等参数，避免图片质量下降和访问问题
func (s *EmojiPackService) cleanImageURL(imageURL string) string {
	if imageURL == "" {
		return imageURL
	}

	// 查找问号位置
	idx := strings.Index(imageURL, "?")
	if idx > 0 {
		return imageURL[:idx]
	}

	return imageURL
}
