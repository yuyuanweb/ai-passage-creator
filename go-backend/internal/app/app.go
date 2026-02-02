package app

import (
	"fmt"
	"log"

	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/config"
	"github.com/yupi/ai-passage-creator/internal/handler"
	"github.com/yupi/ai-passage-creator/internal/service"
	"github.com/yupi/ai-passage-creator/internal/store"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// App 应用程序
type App struct {
	Config *config.Config
	DB     *gorm.DB

	// Handlers
	UserHandler    *handler.UserHandler
	ArticleHandler *handler.ArticleHandler
	HealthHandler  *handler.HealthHandler

	// Services (用于中间件)
	UserService *service.UserService
}

// New 创建应用实例
func New(cfg *config.Config) (*App, error) {
	// 初始化数据库
	db, err := initDB(cfg)
	if err != nil {
		return nil, fmt.Errorf("init database: %w", err)
	}

	// 初始化各层
	userStore := store.NewUserStore(db)
	articleStore := store.NewArticleStore(db)

	// SSE 管理器
	sseManager := common.NewSSEManager()

	// 服务层
	userService := service.NewUserService(userStore)
	quotaService := service.NewQuotaService(userStore)

	// COS 服务（判断是否已配置）
	cosEnabled := cfg.COS.Bucket != "" && cfg.COS.SecretID != "" && cfg.COS.SecretKey != ""
	var cosService *service.CosService
	if cosEnabled {
		cosService = service.NewCosService(cfg.COS)
		log.Printf("COS 服务已启用, bucket=%s, region=%s", cfg.COS.Bucket, cfg.COS.Region)
	} else {
		log.Println("COS 服务未配置，图片将使用原始 URL")
	}

	// 初始化所有图片服务
	pexelsService := service.NewPexelsService(cfg)
	iconifyService := service.NewIconifyService(cfg.Iconify)
	mermaidService := service.NewMermaidService(cfg.Mermaid)
	nanoBananaService := service.NewNanoBananaService(cfg.NanoBanana)
	svgDiagramService := service.NewSVGDiagramService(cfg.SVGDiagram, cfg.AI)
	emojiPackService := service.NewEmojiPackService(cfg.EmojiPack)
	picsumService := service.NewPicsumService() // 降级服务

	// 初始化图片服务策略
	imageStrategy := service.NewImageServiceStrategy(cosService, cosEnabled)
	imageStrategy.RegisterService(pexelsService)
	imageStrategy.RegisterService(iconifyService)
	imageStrategy.RegisterService(mermaidService)
	imageStrategy.RegisterService(nanoBananaService)
	imageStrategy.RegisterService(svgDiagramService)
	imageStrategy.RegisterService(emojiPackService)
	imageStrategy.RegisterService(picsumService) // 注册降级服务

	log.Println("图片服务策略初始化完成，已注册 7 个图片服务（含降级服务）")

	// 智能体服务
	agentService, err := service.NewArticleAgentService(cfg, imageStrategy, sseManager)
	if err != nil {
		return nil, fmt.Errorf("init agent service: %w", err)
	}

	articleService := service.NewArticleService(articleStore, agentService, quotaService, sseManager)

	// 处理器层
	userHandler := handler.NewUserHandler(userService)
	articleHandler := handler.NewArticleHandler(articleService, userService, sseManager)
	healthHandler := handler.NewHealthHandler()

	return &App{
		Config:         cfg,
		DB:             db,
		UserHandler:    userHandler,
		ArticleHandler: articleHandler,
		HealthHandler:  healthHandler,
		UserService:    userService,
	}, nil
}

// initDB 初始化数据库
func initDB(cfg *config.Config) (*gorm.DB, error) {
	dsn := cfg.Database.GetDSN()

	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, fmt.Errorf("connect database: %w", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("get database instance: %w", err)
	}

	sqlDB.SetMaxIdleConns(cfg.Database.MaxIdleConns)
	sqlDB.SetMaxOpenConns(cfg.Database.MaxOpenConns)

	log.Println("database connected")
	return db, nil
}

// Close 关闭资源
func (a *App) Close() error {
	sqlDB, err := a.DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}
