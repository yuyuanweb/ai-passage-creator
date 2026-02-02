package middleware

import (
	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/redis"
	"github.com/gin-gonic/gin"
	"github.com/yupi/ai-passage-creator/internal/config"
)

// SetupSession 配置 Session 中间件
func SetupSession(r *gin.Engine, cfg *config.Config) error {
	// 创建 Redis 存储
	// 参数：size, network, address, username, password, keyPairs...
	store, err := redis.NewStore(
		10,                         // Redis 连接池大小
		"tcp",                      // 网络类型
		cfg.Redis.GetRedisAddr(),   // Redis 地址
		"",                         // Redis 用户名（通常为空）
		cfg.Redis.Password,         // Redis 密码
		[]byte(cfg.Session.Secret), // 加密密钥
	)
	if err != nil {
		return err
	}

	// 设置 Session 选项
	store.Options(sessions.Options{
		MaxAge:   cfg.Session.MaxAge,
		Path:     "/",
		HttpOnly: true,
	})

	// 使用 Session 中间件
	r.Use(sessions.Sessions("session", store))
	return nil
}
