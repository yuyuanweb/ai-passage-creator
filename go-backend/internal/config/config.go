package config

import (
	"fmt"
	"os"

	"github.com/spf13/viper"
)

// Config 应用配置
type Config struct {
	Server     ServerConfig     `mapstructure:"server"`
	Database   DatabaseConfig   `mapstructure:"database"`
	Redis      RedisConfig      `mapstructure:"redis"`
	Session    SessionConfig    `mapstructure:"session"`
	AI         AIConfig         `mapstructure:"ai"`
	Agent      AgentConfig      `mapstructure:"agent"`
	Pexels     PexelsConfig     `mapstructure:"pexels"`
	Iconify    IconifyConfig    `mapstructure:"iconify"`
	Mermaid    MermaidConfig    `mapstructure:"mermaid"`
	NanoBanana NanoBananaConfig `mapstructure:"nano_banana"`
	SVGDiagram SVGDiagramConfig `mapstructure:"svg_diagram"`
	EmojiPack  EmojiPackConfig  `mapstructure:"emoji_pack"`
	COS        COSConfig        `mapstructure:"cos"`
	Stripe     StripeConfig     `mapstructure:"stripe"`
	Log        LogConfig        `mapstructure:"log"`
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Port        int    `mapstructure:"port"`
	ContextPath string `mapstructure:"context_path"`
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	Host         string `mapstructure:"host"`
	Port         int    `mapstructure:"port"`
	Name         string `mapstructure:"name"`
	User         string `mapstructure:"user"`
	Password     string `mapstructure:"password"`
	MaxIdleConns int    `mapstructure:"max_idle_conns"`
	MaxOpenConns int    `mapstructure:"max_open_conns"`
}

// RedisConfig Redis配置
type RedisConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	DB       int    `mapstructure:"db"`
	Password string `mapstructure:"password"`
}

// SessionConfig Session配置
type SessionConfig struct {
	Secret string `mapstructure:"secret"`
	MaxAge int    `mapstructure:"max_age"`
}

// AIConfig AI 配置
type AIConfig struct {
	DashScope DashScopeConfig `mapstructure:"dashscope"`
}

// DashScopeConfig 阿里云 DashScope 配置
type DashScopeConfig struct {
	APIKey string `mapstructure:"api_key"`
	Model  string `mapstructure:"model"`
}

// AgentConfig 智能体配置
type AgentConfig struct {
	Orchestrator  OrchestratorConfig `mapstructure:"orchestrator"`
	MaxIterations int                `mapstructure:"max_iterations"`
}

// OrchestratorConfig 智能体编排器配置
type OrchestratorConfig struct {
	Enabled bool `mapstructure:"enabled"` // 是否启用多智能体编排模式
}

// PexelsConfig Pexels 配置
type PexelsConfig struct {
	APIKey string `mapstructure:"api_key"`
}

// IconifyConfig Iconify 配置
type IconifyConfig struct {
	BaseURL string `mapstructure:"base_url"`
	Timeout int    `mapstructure:"timeout"` // 毫秒
}

// MermaidConfig Mermaid 配置
type MermaidConfig struct {
	CLI          string `mapstructure:"cli"`           // mmdc 命令路径
	OutputFormat string `mapstructure:"output_format"` // png/svg/pdf
	Theme        string `mapstructure:"theme"`         // default/dark/forest
	Width        int    `mapstructure:"width"`
	Height       int    `mapstructure:"height"`
	Timeout      int    `mapstructure:"timeout"` // 毫秒
}

// NanoBananaConfig Nano Banana (Gemini) 配置
type NanoBananaConfig struct {
	APIKey      string `mapstructure:"api_key"`
	Model       string `mapstructure:"model"`        // gemini-2.5-flash-image
	AspectRatio string `mapstructure:"aspect_ratio"` // 16:9/1:1/9:16
	ImageSize   string `mapstructure:"image_size"`   // 1024x1024
}

// SVGDiagramConfig SVG 示意图配置
type SVGDiagramConfig struct {
	Enabled bool `mapstructure:"enabled"`
}

// EmojiPackConfig 表情包配置
type EmojiPackConfig struct {
	Suffix  string `mapstructure:"suffix"`  // "表情包"
	Timeout int    `mapstructure:"timeout"` // 毫秒
}

// COSConfig 腾讯云 COS 配置
type COSConfig struct {
	SecretID  string `mapstructure:"secret_id"`
	SecretKey string `mapstructure:"secret_key"`
	Region    string `mapstructure:"region"`
	Bucket    string `mapstructure:"bucket"`
	Domain    string `mapstructure:"domain"` // CDN 域名（可选）
}

// StripeConfig Stripe 支付配置
type StripeConfig struct {
	APIKey        string `mapstructure:"api_key"`
	WebhookSecret string `mapstructure:"webhook_secret"`
	SuccessURL    string `mapstructure:"success_url"`
	CancelURL     string `mapstructure:"cancel_url"`
}

// LogConfig 日志配置
type LogConfig struct {
	Level    string `mapstructure:"level"`
	FilePath string `mapstructure:"file_path"`
}

// LoadConfig 加载配置文件
// 支持通过环境变量覆盖配置（Docker 部署时使用）
func LoadConfig(configPath string) (*Config, error) {
	v := viper.New()
	v.SetConfigFile(configPath)
	v.SetConfigType("yaml")

	// 读取配置文件
	if err := v.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("读取配置文件失败: %w", err)
	}

	var config Config
	if err := v.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("解析配置文件失败: %w", err)
	}

	// 环境变量覆盖配置（Docker 部署时使用）
	applyEnvOverrides(&config)

	return &config, nil
}

// applyEnvOverrides 使用环境变量覆盖配置
// 参考 Spring Boot 的 ${VAR:default} 机制
func applyEnvOverrides(cfg *Config) {
	// 数据库配置
	if val := getEnv("DB_HOST", ""); val != "" {
		cfg.Database.Host = val
	}
	if val := getEnv("DB_PORT", ""); val != "" {
		fmt.Sscanf(val, "%d", &cfg.Database.Port)
	}
	if val := getEnv("DB_NAME", ""); val != "" {
		cfg.Database.Name = val
	}
	if val := getEnv("DB_USER", ""); val != "" {
		cfg.Database.User = val
	}
	if val := getEnv("DB_PASSWORD", ""); val != "" {
		cfg.Database.Password = val
	}

	// Redis 配置
	if val := getEnv("REDIS_HOST", ""); val != "" {
		cfg.Redis.Host = val
	}
	if val := getEnv("REDIS_PORT", ""); val != "" {
		fmt.Sscanf(val, "%d", &cfg.Redis.Port)
	}
	if val := getEnv("REDIS_PASSWORD", ""); val != "" {
		cfg.Redis.Password = val
	}

	// AI 配置
	if val := getEnv("DASHSCOPE_API_KEY", ""); val != "" {
		cfg.AI.DashScope.APIKey = val
	}

	// Pexels 配置
	if val := getEnv("PEXELS_API_KEY", ""); val != "" {
		cfg.Pexels.APIKey = val
	}

	// Nano Banana 配置
	if val := getEnv("NANO_BANANA_API_KEY", ""); val != "" {
		cfg.NanoBanana.APIKey = val
	}

	// Stripe 配置
	if val := getEnv("STRIPE_API_KEY", ""); val != "" {
		cfg.Stripe.APIKey = val
	}
	if val := getEnv("STRIPE_WEBHOOK_SECRET", ""); val != "" {
		cfg.Stripe.WebhookSecret = val
	}

	// 腾讯云 COS 配置
	if val := getEnv("TENCENT_COS_SECRET_ID", ""); val != "" {
		cfg.COS.SecretID = val
	}
	if val := getEnv("TENCENT_COS_SECRET_KEY", ""); val != "" {
		cfg.COS.SecretKey = val
	}
	if val := getEnv("TENCENT_COS_REGION", ""); val != "" {
		cfg.COS.Region = val
	}
	if val := getEnv("TENCENT_COS_BUCKET", ""); val != "" {
		cfg.COS.Bucket = val
	}
}

// getEnv 获取环境变量，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// GetDSN 获取数据库连接字符串
func (c *DatabaseConfig) GetDSN() string {
	return fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=utf8mb4&parseTime=True&loc=Local",
		c.User,
		c.Password,
		c.Host,
		c.Port,
		c.Name,
	)
}

// GetRedisAddr 获取 Redis 地址
func (c *RedisConfig) GetRedisAddr() string {
	return fmt.Sprintf("%s:%d", c.Host, c.Port)
}
