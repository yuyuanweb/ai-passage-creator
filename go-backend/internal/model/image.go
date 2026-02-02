package model

// ImageData 图片数据（可以是字节数据或URL）
type ImageData struct {
	Bytes    []byte // 图片字节数据
	URL      string // 图片URL
	MimeType string // MIME类型（如 image/png, image/svg+xml）
}

// IsValid 检查图片数据是否有效
func (d *ImageData) IsValid() bool {
	return (len(d.Bytes) > 0) || (d.URL != "")
}

// FromBytes 从字节数据创建 ImageData
func FromBytes(bytes []byte, mimeType string) *ImageData {
	return &ImageData{
		Bytes:    bytes,
		MimeType: mimeType,
	}
}

// FromURL 从 URL 创建 ImageData
func FromURL(url string) *ImageData {
	return &ImageData{
		URL: url,
	}
}

// ImageRequest 图片请求
type ImageRequest struct {
	Keywords string // 关键词（用于图片检索类服务）
	Prompt   string // 提示词（用于 AI 生成类服务）
	Position int    // 位置
	Type     string // 类型：cover/section/conclusion
}

// GetEffectiveParam 获取有效参数（优先使用 Prompt，其次 Keywords）
// usePromptFirst 为 true 时优先返回 Prompt
func (r *ImageRequest) GetEffectiveParam(usePromptFirst bool) string {
	if usePromptFirst {
		if r.Prompt != "" {
			return r.Prompt
		}
		return r.Keywords
	}
	if r.Keywords != "" {
		return r.Keywords
	}
	return r.Prompt
}

// ImageStrategyResult 图片策略结果
type ImageStrategyResult struct {
	URL    string // COS URL
	Method string // 图片方法
}
