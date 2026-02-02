package common

// 文章风格枚举常量
const (
	ArticleStyleTech        = "tech"
	ArticleStyleEmotional   = "emotional"
	ArticleStyleEducational = "educational"
	ArticleStyleHumorous    = "humorous"
)

// GetAllArticleStyles 获取所有文章风格
func GetAllArticleStyles() []string {
	return []string{
		ArticleStyleTech,
		ArticleStyleEmotional,
		ArticleStyleEducational,
		ArticleStyleHumorous,
	}
}

// IsValidArticleStyle 校验是否为有效的文章风格
func IsValidArticleStyle(style string) bool {
	if style == "" {
		return true // 允许为空
	}
	for _, s := range GetAllArticleStyles() {
		if s == style {
			return true
		}
	}
	return false
}

// GetArticleStyleText 获取风格描述
func GetArticleStyleText(style string) string {
	switch style {
	case ArticleStyleTech:
		return "科技风格"
	case ArticleStyleEmotional:
		return "情感风格"
	case ArticleStyleEducational:
		return "教育风格"
	case ArticleStyleHumorous:
		return "轻松幽默风格"
	default:
		return ""
	}
}
