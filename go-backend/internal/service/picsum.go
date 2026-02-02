package service

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
)

// PicsumService Picsum 随机图片服务（降级方案）
type PicsumService struct{}

// NewPicsumService 创建 Picsum 服务
func NewPicsumService() *PicsumService {
	rand.Seed(time.Now().UnixNano())
	return &PicsumService{}
}

// GetMethod 返回方法名
func (s *PicsumService) GetMethod() string {
	return common.ImageMethodPicsum
}

// IsAvailable 是否可用（Picsum 始终可用）
func (s *PicsumService) IsAvailable() bool {
	return true
}

// SearchImage 获取随机图片 URL
func (s *PicsumService) SearchImage(keywords string) (string, error) {
	// 使用随机数生成不同的图片
	randomNum := rand.Intn(1000)
	url := fmt.Sprintf(common.PicsumURLTemplate, randomNum)
	return url, nil
}

// GetImageData 获取图片数据（Picsum 是检索类服务，使用 SearchImage）
func (s *PicsumService) GetImageData(req *model.ImageRequest) (*model.ImageData, error) {
	// 使用 position 作为随机种子，确保同一位置的图片一致
	url := fmt.Sprintf(common.PicsumURLTemplate, req.Position)
	return model.FromURL(url), nil
}
