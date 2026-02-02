package middleware

import (
	"net/http"

	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
	"github.com/yupi/ai-passage-creator/internal/service"
)

// AuthCheck 权限校验中间件
func AuthCheck(userSvc *service.UserService, mustRole string) gin.HandlerFunc {
	return func(c *gin.Context) {
		session := sessions.Default(c)

		// 获取当前登录用户
		loginUser, err := userSvc.GetLoginUser(session)
		if err != nil {
			c.JSON(http.StatusUnauthorized, common.Error(common.ErrNotLogin))
			c.Abort()
			return
		}

		// 不需要权限，直接放行
		if mustRole == "" {
			c.Set("loginUser", loginUser)
			c.Next()
			return
		}

		// 检查角色权限
		mustRoleEnum := model.UserRole(mustRole)
		if !mustRoleEnum.IsValid() {
			c.Set("loginUser", loginUser)
			c.Next()
			return
		}

		userRoleEnum := model.UserRole(loginUser.UserRole)
		if !userRoleEnum.IsValid() {
			c.JSON(http.StatusForbidden, common.Error(common.ErrNoAuth))
			c.Abort()
			return
		}

		// 要求管理员权限，但用户不是管理员
		if mustRoleEnum == model.RoleAdmin && userRoleEnum != model.RoleAdmin {
			c.JSON(http.StatusForbidden, common.Error(common.ErrNoAuth))
			c.Abort()
			return
		}

		// 通过权限校验
		c.Set("loginUser", loginUser)
		c.Next()
	}
}
