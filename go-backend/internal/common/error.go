package common

import "fmt"

// AppError 应用错误
type AppError struct {
	HTTPCode int    // HTTP 状态码（内部使用）
	Code     int    // 业务错误码
	Message  string // 错误信息
}

func (e *AppError) Error() string {
	return fmt.Sprintf("[%d] %s", e.Code, e.Message)
}

// NewError 创建自定义错误
func NewError(httpCode, code int, message string) *AppError {
	return &AppError{
		HTTPCode: httpCode,
		Code:     code,
		Message:  message,
	}
}

// WithMessage 创建带自定义消息的错误
func (e *AppError) WithMessage(message string) *AppError {
	return &AppError{
		HTTPCode: e.HTTPCode,
		Code:     e.Code,
		Message:  message,
	}
}

// 预定义错误
var (
	ErrSuccess        = &AppError{HTTPCode: 200, Code: 0, Message: "ok"}
	ErrParams         = &AppError{HTTPCode: 400, Code: 40000, Message: "请求参数错误"}
	ErrNotLogin       = &AppError{HTTPCode: 401, Code: 40100, Message: "未登录"}
	ErrNoAuth         = &AppError{HTTPCode: 403, Code: 40101, Message: "无权限"}
	ErrTooManyRequest = &AppError{HTTPCode: 429, Code: 42900, Message: "请求过于频繁"}
	ErrNotFound       = &AppError{HTTPCode: 404, Code: 40400, Message: "请求数据不存在"}
	ErrForbidden      = &AppError{HTTPCode: 403, Code: 40300, Message: "禁止访问"}
	ErrSystem         = &AppError{HTTPCode: 500, Code: 50000, Message: "系统内部异常"}
	ErrOperation      = &AppError{HTTPCode: 500, Code: 50001, Message: "操作失败"}
)
