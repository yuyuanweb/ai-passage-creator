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
