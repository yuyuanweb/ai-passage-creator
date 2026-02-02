package common

// Session 相关常量
const (
	UserLoginState = "userLoginState"
	AdminRole      = "admin"
	UserRole       = "user"
)

// 密码相关常量
const (
	PasswordSalt      = "yupi"
	DefaultPassword   = "12345678"
	MinAccountLength  = 4
	MinPasswordLength = 8
)

// 分页相关常量
const (
	DefaultPageNum  = 1
	DefaultPageSize = 10
	MaxPageSize     = 100
)

// 配额相关常量
const (
	DefaultQuota = 5 // 新用户默认配额
)

// SSE 相关常量
const (
	SSETimeoutMS       = 30 * 60 * 1000 // SSE 连接超时时间（毫秒）：30分钟
	SSEReconnectTimeMS = 3000           // SSE 重连时间（毫秒）：3秒
)

// Pexels 相关常量
const (
	PexelsAPIURL               = "https://api.pexels.com/v1/search"
	PexelsPerPage              = 1
	PexelsOrientationLandscape = "landscape"
)

// Picsum 相关常量
const (
	PicsumURLTemplate = "https://picsum.photos/800/600?random=%d"
)

// Bing 表情包相关常量
const (
	BingImageSearchURL = "https://cn.bing.com/images/async"
	EmojiPackSuffix    = "表情包"
	BingMaxImages      = 30
)

// SVG 相关常量
const (
	SVGFilePrefix    = "svg-chart"
	SVGDefaultWidth  = 800
	SVGDefaultHeight = 600
)
