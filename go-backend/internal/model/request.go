package model

// RegisterRequest 用户注册请求
type RegisterRequest struct {
	UserAccount   string `json:"userAccount" binding:"required,min=4"`
	UserPassword  string `json:"userPassword" binding:"required,min=8"`
	CheckPassword string `json:"checkPassword" binding:"required,min=8"`
}

// LoginRequest 用户登录请求
type LoginRequest struct {
	UserAccount  string `json:"userAccount" binding:"required,min=4"`
	UserPassword string `json:"userPassword" binding:"required,min=8"`
}

// AddUserRequest 创建用户请求（管理员）
type AddUserRequest struct {
	UserAccount string  `json:"userAccount" binding:"required"`
	UserName    *string `json:"userName"`
	UserAvatar  *string `json:"userAvatar"`
	UserProfile *string `json:"userProfile"`
	UserRole    string  `json:"userRole"`
}

// UpdateUserRequest 更新用户请求（管理员）
type UpdateUserRequest struct {
	ID          int64   `json:"id" binding:"required"`
	UserName    *string `json:"userName"`
	UserAvatar  *string `json:"userAvatar"`
	UserProfile *string `json:"userProfile"`
	UserRole    *string `json:"userRole"`
}

// QueryUserRequest 查询用户请求
type QueryUserRequest struct {
	ID          *int64  `json:"id"`
	UserAccount *string `json:"userAccount"`
	UserName    *string `json:"userName"`
	UserProfile *string `json:"userProfile"`
	UserRole    *string `json:"userRole"`
	PageNum     int64   `json:"pageNum"`
	PageSize    int64   `json:"pageSize"`
	SortField   *string `json:"sortField"`
	SortOrder   *string `json:"sortOrder"`
}

// DeleteRequest 删除请求
type DeleteRequest struct {
	ID int64 `json:"id" binding:"required,gt=0"`
}

// PageResult 分页结果
type PageResult struct {
	Total    int64       `json:"total"`
	Records  interface{} `json:"records"`
	PageNum  int64       `json:"pageNum"`
	PageSize int64       `json:"pageSize"`
}
