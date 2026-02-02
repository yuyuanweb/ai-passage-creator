package service

import "github.com/yupi/ai-passage-creator/internal/model"

// ImageService 图片服务接口
type ImageService interface {
	// GetMethod 返回方法名
	GetMethod() string

	// IsAvailable 是否可用
	IsAvailable() bool

	// SearchImage 搜索图片URL（适用于网络检索类服务，如 Pexels、Iconify、EmojiPack）
	// 返回图片 URL，失败返回 error
	SearchImage(keywords string) (string, error)

	// GetImageData 获取图片数据（适用于生成类服务，如 Mermaid、NanoBanana、SVG_DIAGRAM）
	// 返回 ImageData（包含字节数据或 URL），失败返回 error
	GetImageData(req *model.ImageRequest) (*model.ImageData, error)
}
