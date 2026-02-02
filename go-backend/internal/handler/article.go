package handler

import (
	"io"
	"net/http"
	"time"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
	"github.com/yupi/ai-passage-creator/internal/service"
)

// ArticleHandler 文章处理器
type ArticleHandler struct {
	svc        *service.ArticleService
	userSvc    *service.UserService
	sseManager *common.SSEManager
}

// NewArticleHandler 创建文章处理器
func NewArticleHandler(svc *service.ArticleService, userSvc *service.UserService, sseManager *common.SSEManager) *ArticleHandler {
	return &ArticleHandler{
		svc:        svc,
		userSvc:    userSvc,
		sseManager: sseManager,
	}
}

// Create 创建文章任务
func (h *ArticleHandler) Create(c *gin.Context) {
	var req model.CreateArticleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	// 校验风格参数（允许为空）
	if !common.IsValidArticleStyle(req.Style) {
		c.JSON(http.StatusOK, common.Error(common.ErrParams.WithMessage("无效的文章风格")))
		return
	}

	// 获取当前用户
	session := sessions.Default(c)
	user, err := h.userSvc.GetLoginUser(session)
	if err != nil {
		handleError(c, err)
		return
	}

	// 创建文章任务（包含配额检查）
	taskID, err := h.svc.Create(user, &req)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(taskID))
}

// GetProgress SSE 获取生成进度
func (h *ArticleHandler) GetProgress(c *gin.Context) {
	taskID := c.Param("taskId")
	if taskID == "" {
		c.JSON(http.StatusBadRequest, common.Error(common.ErrParams.WithMessage("任务ID不能为空")))
		return
	}

	// 获取当前用户
	session := sessions.Default(c)
	user, err := h.userSvc.GetLoginUser(session)
	if err != nil {
		c.JSON(http.StatusUnauthorized, common.Error(common.ErrNotLogin))
		return
	}

	// 校验权限（检查任务是否存在以及用户是否有权限访问）
	isAdmin := user.UserRole == common.AdminRole
	_, err = h.svc.GetByTaskID(taskID, user.ID, isAdmin)
	if err != nil {
		c.JSON(http.StatusForbidden, common.Error(err.(*common.AppError)))
		return
	}

	// 设置 SSE 响应头
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("X-Accel-Buffering", "no")
	c.Header("Access-Control-Allow-Origin", "http://localhost:5173")
	c.Header("Access-Control-Allow-Credentials", "true")

	// 注册 SSE 客户端
	messageChan := h.sseManager.Register(taskID)
	defer h.sseManager.Unregister(taskID)

	// 流式推送
	c.Stream(func(w io.Writer) bool {
		select {
		case msg, ok := <-messageChan:
			if !ok {
				return false
			}
			c.SSEvent("message", msg)
			c.Writer.Flush()
			return true
		case <-c.Request.Context().Done():
			// 客户端断开连接
			return false
		case <-time.After(30 * time.Minute):
			// 超时
			return false
		}
	})
}

// Get 获取文章详情
func (h *ArticleHandler) Get(c *gin.Context) {
	taskID := c.Param("taskId")
	if taskID == "" {
		c.JSON(http.StatusOK, common.Error(common.ErrParams.WithMessage("任务ID不能为空")))
		return
	}

	// 获取当前用户
	session := sessions.Default(c)
	user, err := h.userSvc.GetLoginUser(session)
	if err != nil {
		handleError(c, err)
		return
	}

	// 判断是否管理员
	isAdmin := user.UserRole == common.AdminRole

	// 获取文章
	article, err := h.svc.GetByTaskID(taskID, user.ID, isAdmin)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(article))
}

// List 分页查询文章列表
func (h *ArticleHandler) List(c *gin.Context) {
	var req model.QueryArticleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	// 获取当前用户
	session := sessions.Default(c)
	user, err := h.userSvc.GetLoginUser(session)
	if err != nil {
		handleError(c, err)
		return
	}

	// 判断是否管理员
	isAdmin := user.UserRole == common.AdminRole

	// 查询文章列表
	page, err := h.svc.ListByPage(&req, user.ID, isAdmin)
	if err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(page))
}

// Delete 删除文章
func (h *ArticleHandler) Delete(c *gin.Context) {
	var req model.DeleteRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, common.Error(common.ErrParams))
		return
	}

	// 获取当前用户
	session := sessions.Default(c)
	user, err := h.userSvc.GetLoginUser(session)
	if err != nil {
		handleError(c, err)
		return
	}

	// 判断是否管理员
	isAdmin := user.UserRole == common.AdminRole

	// 删除文章
	if err := h.svc.Delete(req.ID, user.ID, isAdmin); err != nil {
		handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, common.Success(true))
}
