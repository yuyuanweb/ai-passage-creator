package common

// 图片方法枚举常量
const (
	ImageMethodPexels     = "PEXELS"
	ImageMethodNanoBanana = "NANO_BANANA"
	ImageMethodMermaid    = "MERMAID"
	ImageMethodIconify    = "ICONIFY"
	ImageMethodEmojiPack  = "EMOJI_PACK"
	ImageMethodSVGDiagram = "SVG_DIAGRAM"
	ImageMethodPicsum     = "PICSUM" // 降级方案
)

// IsAIGenerated 是否为 AI 生图方式
// true: 使用 prompt 生成图片（如 NANO_BANANA、MERMAID、SVG_DIAGRAM）
// false: 使用 keywords 检索图片（如 PEXELS、ICONIFY、EMOJI_PACK）
func IsAIGenerated(method string) bool {
	switch method {
	case ImageMethodNanoBanana, ImageMethodMermaid, ImageMethodSVGDiagram:
		return true
	default:
		return false
	}
}

// IsFallback 是否为降级方案
func IsFallback(method string) bool {
	return method == ImageMethodPicsum
}

// GetFolderName 获取 COS 文件夹名称
func GetFolderName(method string) string {
	switch method {
	case ImageMethodNanoBanana:
		return "nano-banana"
	case ImageMethodMermaid:
		return "mermaid"
	case ImageMethodIconify:
		return "iconify"
	case ImageMethodEmojiPack:
		return "emoji-pack"
	case ImageMethodSVGDiagram:
		return "svg-diagram"
	case ImageMethodPexels:
		return "pexels"
	case ImageMethodPicsum:
		return "picsum"
	default:
		return "images"
	}
}

// GetDescription 获取方法描述
func GetDescription(method string) string {
	switch method {
	case ImageMethodPexels:
		return "Pexels 图库"
	case ImageMethodNanoBanana:
		return "Nano Banana AI 生图"
	case ImageMethodMermaid:
		return "Mermaid 流程图生成"
	case ImageMethodIconify:
		return "Iconify 图标库"
	case ImageMethodEmojiPack:
		return "表情包检索"
	case ImageMethodSVGDiagram:
		return "SVG 概念示意图"
	case ImageMethodPicsum:
		return "Picsum 随机图片"
	default:
		return "未知方法"
	}
}

// GetDefaultSearchMethod 获取默认的图库检索方式
func GetDefaultSearchMethod() string {
	return ImageMethodPexels
}

// GetDefaultFallbackMethod 获取默认的降级方式
func GetDefaultFallbackMethod() string {
	return ImageMethodPicsum
}

// GetAllMethods 获取所有配图方式
func GetAllMethods() []string {
	return []string{
		ImageMethodPexels,
		ImageMethodNanoBanana,
		ImageMethodMermaid,
		ImageMethodIconify,
		ImageMethodEmojiPack,
		ImageMethodSVGDiagram,
		ImageMethodPicsum,
	}
}
