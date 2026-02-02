package service

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"

	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/model"

	"github.com/google/uuid"
	"github.com/tencentyun/cos-go-sdk-v5"
)

// CosService 腾讯云 COS 服务
type CosService struct {
	config config.COSConfig
	client *cos.Client
}

// NewCosService 创建 COS 服务
func NewCosService(cfg config.COSConfig) *CosService {
	// 构建 COS URL
	cosURL, _ := url.Parse(fmt.Sprintf("https://%s.cos.%s.myqcloud.com", cfg.Bucket, cfg.Region))
	baseURL := &cos.BaseURL{BucketURL: cosURL}

	// 创建客户端
	client := cos.NewClient(baseURL, &http.Client{
		Transport: &cos.AuthorizationTransport{
			SecretID:  cfg.SecretID,
			SecretKey: cfg.SecretKey,
		},
	})

	return &CosService{
		config: cfg,
		client: client,
	}
}

// UploadImageData 上传图片数据到 COS
func (s *CosService) UploadImageData(imageData *model.ImageData, folder string) (string, error) {
	if imageData == nil || !imageData.IsValid() {
		return "", fmt.Errorf("ImageData 无效")
	}

	// 处理字节数据
	if len(imageData.Bytes) > 0 {
		return s.uploadBytes(imageData.Bytes, imageData.MimeType, folder)
	}

	// 处理 URL
	if imageData.URL != "" {
		return s.uploadFromURL(imageData.URL, folder)
	}

	return "", fmt.Errorf("ImageData 无数据")
}

// uploadBytes 上传字节数据到 COS
func (s *CosService) uploadBytes(data []byte, mimeType, folder string) (string, error) {
	if len(data) == 0 {
		return "", fmt.Errorf("字节数据为空")
	}

	// 生成文件名
	extension := s.getExtensionFromMimeType(mimeType)
	fileName := folder + "/" + uuid.New().String() + extension

	// 上传到 COS
	ctx := context.Background()
	reader := bytes.NewReader(data)

	_, err := s.client.Object.Put(ctx, fileName, reader, &cos.ObjectPutOptions{
		ObjectPutHeaderOptions: &cos.ObjectPutHeaderOptions{
			ContentType:   mimeType,
			ContentLength: int64(len(data)),
		},
	})
	if err != nil {
		return "", fmt.Errorf("上传到COS失败: %w", err)
	}

	cosURL := s.buildCosURL(fileName)
	log.Printf("字节数据上传成功, size=%d bytes, url=%s", len(data), cosURL)
	return cosURL, nil
}

// uploadFromURL 从 URL 下载并上传到 COS
func (s *CosService) uploadFromURL(imageURL, folder string) (string, error) {
	// 下载图片
	resp, err := http.Get(imageURL)
	if err != nil {
		return "", fmt.Errorf("下载图片失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("下载图片失败, status=%d", resp.StatusCode)
	}

	// 读取数据
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("读取图片数据失败: %w", err)
	}

	// 获取 MIME 类型
	mimeType := resp.Header.Get("Content-Type")
	if mimeType == "" {
		mimeType = "image/png"
	}

	// 上传
	return s.uploadBytes(data, mimeType, folder)
}

// buildCosURL 构建 COS URL
func (s *CosService) buildCosURL(fileName string) string {
	if s.config.Domain != "" {
		// 使用 CDN 域名
		return fmt.Sprintf("https://%s/%s", s.config.Domain, fileName)
	}
	// 使用默认 COS 域名
	return fmt.Sprintf("https://%s.cos.%s.myqcloud.com/%s",
		s.config.Bucket, s.config.Region, fileName)
}

// getExtensionFromMimeType 根据 MIME 类型获取文件扩展名
func (s *CosService) getExtensionFromMimeType(mimeType string) string {
	switch strings.ToLower(mimeType) {
	case "image/png":
		return ".png"
	case "image/jpeg", "image/jpg":
		return ".jpg"
	case "image/gif":
		return ".gif"
	case "image/webp":
		return ".webp"
	case "image/svg+xml":
		return ".svg"
	case "application/pdf":
		return ".pdf"
	default:
		return ".png"
	}
}

// UseDirectURL 已废弃，使用 UploadImageData 替代
// Deprecated: 使用 UploadImageData 替代
func (s *CosService) UseDirectURL(imageURL string) string {
	return imageURL
}
