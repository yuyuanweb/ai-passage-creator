package handler

import (
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
	"github.com/yupi/ai-passage-creator/internal/service"
)

// UserHandler 用户处理器
type UserHandler struct {
	svc *service.UserService
}

// NewUserHandler 创建用户处理器
func NewUserHandler(svc *service.UserService) *UserHandler {
	return &UserHandler{svc: svc}
}

// Register 用户注册
func (h *UserHandler) Register(c *gin.Context) {
	var req model.RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	userID, err := h.svc.Register(&req)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(userID))
}

// Login 用户登录
func (h *UserHandler) Login(c *gin.Context) {
	var req model.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	session := sessions.Default(c)
	loginUser, err := h.svc.Login(&req, session)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(loginUser))
}

// GetLoginUser 获取当前登录用户
func (h *UserHandler) GetLoginUser(c *gin.Context) {
	session := sessions.Default(c)
	user, err := h.svc.GetLoginUser(session)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(user.ToLoginUser()))
}

// Logout 用户注销
func (h *UserHandler) Logout(c *gin.Context) {
	session := sessions.Default(c)
	if err := h.svc.Logout(session); err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(true))
}

// Add 创建用户（管理员）
func (h *UserHandler) Add(c *gin.Context) {
	var req model.AddUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	userID, err := h.svc.Create(&req)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(userID))
}

// Get 根据 ID 获取用户（管理员）
func (h *UserHandler) Get(c *gin.Context) {
	var req struct {
		ID int64 `form:"id" binding:"required,gt=0"`
	}
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	user, err := h.svc.GetByID(req.ID)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(user))
}

// GetVO 根据 ID 获取用户信息
func (h *UserHandler) GetVO(c *gin.Context) {
	var req struct {
		ID int64 `form:"id" binding:"required,gt=0"`
	}
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	user, err := h.svc.GetByID(req.ID)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(user.ToUserInfo()))
}

// Delete 删除用户（管理员）
func (h *UserHandler) Delete(c *gin.Context) {
	var req model.DeleteRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	if err := h.svc.Delete(req.ID); err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(true))
}

// Update 更新用户（管理员）
func (h *UserHandler) Update(c *gin.Context) {
	var req model.UpdateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	if err := h.svc.Update(&req); err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(true))
}

// ListPageVO 分页查询用户列表（管理员）
func (h *UserHandler) ListPageVO(c *gin.Context) {
	var req model.QueryUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	// 设置默认值
	if req.PageNum <= 0 {
		req.PageNum = common.DefaultPageNum
	}
	if req.PageSize <= 0 {
		req.PageSize = common.DefaultPageSize
	}
	if req.PageSize > common.MaxPageSize {
		req.PageSize = common.MaxPageSize
	}

	page, err := h.svc.ListByPage(&req)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(page))
}

// handleError 统一错误处理
func handleError(c *gin.Context, err error) {
	if appErr, ok := err.(*common.AppError); ok {
		c.JSON(http.StatusOK, common.Error(appErr))
	} else {
		c.JSON(http.StatusOK, common.Error(common.ErrSystem))
	}
}
