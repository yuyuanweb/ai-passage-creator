package model

import "time"

// Article 文章实体
type Article struct {
	ID                  int64      `gorm:"primaryKey;autoIncrement" json:"id"`
	TaskID              string     `gorm:"column:taskId;uniqueIndex:uk_taskId" json:"taskId"`
	UserID              int64      `gorm:"column:userId;index:idx_userId" json:"userId"`
	Topic               string     `gorm:"column:topic" json:"topic"`
	MainTitle           *string    `gorm:"column:mainTitle" json:"mainTitle"`
	SubTitle            *string    `gorm:"column:subTitle" json:"subTitle"`
	Outline             *string    `gorm:"column:outline;type:json" json:"outline"`
	Content             *string    `gorm:"column:content;type:text" json:"content"`
	FullContent         *string    `gorm:"column:fullContent;type:text" json:"fullContent"`
	Images              *string    `gorm:"column:images;type:json" json:"images"`
	Status              string     `gorm:"column:status;default:PENDING;index:idx_status" json:"status"`
	ErrorMessage        *string    `gorm:"column:errorMessage;type:text" json:"errorMessage"`
	Style               string     `gorm:"column:style" json:"style"`                                       // 文章风格：tech/emotional/educational/humorous
	EnabledImageMethods string     `gorm:"column:enabledImageMethods;type:text" json:"enabledImageMethods"` // 允许的配图方式列表（JSON格式）
	CreateTime          time.Time  `gorm:"column:createTime;autoCreateTime;index:idx_createTime" json:"createTime"`
	CompletedTime       *time.Time `gorm:"column:completedTime" json:"completedTime"`
	UpdateTime          time.Time  `gorm:"column:updateTime;autoUpdateTime" json:"updateTime"`
	IsDelete            int        `gorm:"column:isDelete;default:0" json:"-"`
}

func (Article) TableName() string {
	return "article"
}

// ArticleStatus 文章状态
const (
	StatusPending    = "PENDING"
	StatusProcessing = "PROCESSING"
	StatusCompleted  = "COMPLETED"
	StatusFailed     = "FAILED"
)

// ArticleInfo 文章信息（响应）
type ArticleInfo struct {
	ID                  int64            `json:"id"`
	TaskID              string           `json:"taskId"`
	UserID              int64            `json:"userId"`
	Topic               string           `json:"topic"`
	MainTitle           *string          `json:"mainTitle"`
	SubTitle            *string          `json:"subTitle"`
	Outline             []OutlineSection `json:"outline"`
	Content             *string          `json:"content"`
	FullContent         *string          `json:"fullContent"`
	Images              []ImageResult    `json:"images"`
	Status              string           `json:"status"`
	ErrorMessage        *string          `json:"errorMessage"`
	Style               string           `json:"style"`               // 文章风格
	EnabledImageMethods []string         `json:"enabledImageMethods"` // 允许的配图方式列表
	CreateTime          time.Time        `json:"createTime"`
	CompletedTime       *time.Time       `json:"completedTime"`
}

// ToArticleInfo 转换为文章信息
func (a *Article) ToArticleInfo() *ArticleInfo {
	if a == nil {
		return nil
	}

	info := &ArticleInfo{
		ID:            a.ID,
		TaskID:        a.TaskID,
		UserID:        a.UserID,
		Topic:         a.Topic,
		MainTitle:     a.MainTitle,
		SubTitle:      a.SubTitle,
		Content:       a.Content,
		FullContent:   a.FullContent,
		Status:        a.Status,
		ErrorMessage:  a.ErrorMessage,
		Style:         a.Style,
		CreateTime:    a.CreateTime,
		CompletedTime: a.CompletedTime,
	}

	// 解析 JSON 字段
	if a.Outline != nil {
		parseJSON(*a.Outline, &info.Outline)
	}
	if a.Images != nil {
		parseJSON(*a.Images, &info.Images)
	}
	if a.EnabledImageMethods != "" {
		parseJSON(a.EnabledImageMethods, &info.EnabledImageMethods)
	}

	return info
}

// ArticleState 文章生成状态（智能体间共享）
type ArticleState struct {
	TaskID                  string             `json:"taskId"`
	Topic                   string             `json:"topic"`
	Style                   string             `json:"style"`               // 文章风格
	EnabledImageMethods     []string           `json:"enabledImageMethods"` // 允许的配图方式列表
	Title                   *TitleResult       `json:"title"`
	Outline                 *OutlineResult     `json:"outline"`
	Content                 string             `json:"content"`
	ContentWithPlaceholders string             `json:"contentWithPlaceholders"` // 包含占位符的正文
	FullContent             string             `json:"fullContent"`
	ImageRequirements       []ImageRequirement `json:"imageRequirements"`
	Images                  []ImageResult      `json:"images"`
}

// TitleResult 标题结果
type TitleResult struct {
	MainTitle string `json:"mainTitle"`
	SubTitle  string `json:"subTitle"`
}

// OutlineResult 大纲结果
type OutlineResult struct {
	Sections []OutlineSection `json:"sections"`
}

// OutlineSection 大纲章节
type OutlineSection struct {
	Section int      `json:"section"`
	Title   string   `json:"title"`
	Points  []string `json:"points"`
}

// ImageRequirement 配图需求
type ImageRequirement struct {
	Position      int    `json:"position"`
	Type          string `json:"type"`
	SectionTitle  string `json:"sectionTitle"`
	ImageSource   string `json:"imageSource"` // PEXELS/NANO_BANANA/MERMAID/ICONIFY/EMOJI_PACK/SVG_DIAGRAM
	Keywords      string `json:"keywords"`
	Prompt        string `json:"prompt"`
	PlaceholderID string `json:"placeholderId"` // {{IMAGE_PLACEHOLDER_N}}
}

// ImageResult 配图结果
type ImageResult struct {
	Position      int    `json:"position"`
	URL           string `json:"url"`
	Method        string `json:"method"`
	Keywords      string `json:"keywords"`
	SectionTitle  string `json:"sectionTitle"`
	Description   string `json:"description"`
	PlaceholderID string `json:"placeholderId"` // {{IMAGE_PLACEHOLDER_N}}
}
