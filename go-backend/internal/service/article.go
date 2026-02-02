package service

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"time"

	"github.com/google/uuid"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
	"github.com/yupi/ai-passage-creator/internal/store"
	"gorm.io/gorm"
)

// ArticleService 文章服务
type ArticleService struct {
	store      *store.ArticleStore
	agentSvc   *ArticleAgentService
	quotaSvc   *QuotaService
	sseManager *common.SSEManager
}

// NewArticleService 创建文章服务
func NewArticleService(st *store.ArticleStore, agentSvc *ArticleAgentService, quotaSvc *QuotaService, sseManager *common.SSEManager) *ArticleService {
	return &ArticleService{
		store:      st,
		agentSvc:   agentSvc,
		quotaSvc:   quotaSvc,
		sseManager: sseManager,
	}
}

// Create 创建文章任务
func (s *ArticleService) Create(user *model.User, req *model.CreateArticleRequest) (string, error) {
	if req.Topic == "" {
		return "", common.ErrParams.WithMessage("选题不能为空")
	}

	// 检查并消耗配额（原子操作）
	if err := s.quotaSvc.CheckAndConsumeQuota(user); err != nil {
		return "", err
	}

	// 生成任务 ID
	taskID := uuid.NewString()

	// 将 enabledImageMethods 转为 JSON
	methodsJSON := ""
	if len(req.EnabledImageMethods) > 0 {
		methodsBytes, _ := json.Marshal(req.EnabledImageMethods)
		methodsJSON = string(methodsBytes)
	}

	// 创建文章记录
	article := &model.Article{
		TaskID:              taskID,
		UserID:              user.ID,
		Topic:               req.Topic,
		Style:               req.Style,
		EnabledImageMethods: methodsJSON,
		Status:              model.StatusPending,
		CreateTime:          time.Now(),
	}

	if err := s.store.Create(article); err != nil {
		return "", common.ErrOperation
	}

	// 异步执行文章生成
	go s.executeAsync(taskID, req.Topic, req.Style, req.EnabledImageMethods)

	log.Printf("文章任务已创建, taskId=%s, userId=%d, style=%s", taskID, user.ID, req.Style)
	return taskID, nil
}

// GetByTaskID 根据任务ID获取文章
func (s *ArticleService) GetByTaskID(taskID string, userID int64, isAdmin bool) (*model.ArticleInfo, error) {
	article, err := s.store.GetByTaskID(taskID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, common.ErrNotFound.WithMessage("文章不存在")
		}
		return nil, common.ErrSystem
	}

	// 权限校验：只能查看自己的文章（管理员除外）
	if !isAdmin && article.UserID != userID {
		return nil, common.ErrNoAuth
	}

	return article.ToArticleInfo(), nil
}

// ListByPage 分页查询文章列表
func (s *ArticleService) ListByPage(req *model.QueryArticleRequest, userID int64, isAdmin bool) (*model.PageResult, error) {
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

	// 非管理员查询时，强制使用当前用户ID
	queryUserID := &userID
	if isAdmin && req.UserID != nil {
		queryUserID = req.UserID
	}

	articles, total, err := s.store.List(queryUserID, req.Status, isAdmin, req.PageNum, req.PageSize)
	if err != nil {
		return nil, common.ErrSystem
	}

	// 转换为响应
	articleInfos := make([]model.ArticleInfo, 0, len(articles))
	for i := range articles {
		if info := articles[i].ToArticleInfo(); info != nil {
			articleInfos = append(articleInfos, *info)
		}
	}

	return &model.PageResult{
		Total:    total,
		Records:  articleInfos,
		PageNum:  req.PageNum,
		PageSize: req.PageSize,
	}, nil
}

// Delete 删除文章
func (s *ArticleService) Delete(id int64, userID int64, isAdmin bool) error {
	article, err := s.store.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return common.ErrNotFound
		}
		return common.ErrSystem
	}

	// 权限校验：只能删除自己的文章（管理员除外）
	if !isAdmin && article.UserID != userID {
		return common.ErrNoAuth
	}

	if err := s.store.Delete(id); err != nil {
		return common.ErrOperation
	}

	return nil
}

// executeAsync 异步执行文章生成
func (s *ArticleService) executeAsync(taskID, topic, style string, enabledImageMethods []string) {
	log.Printf("异步任务开始, taskId=%s, topic=%s, style=%s, enabledImageMethods=%v",
		taskID, topic, style, enabledImageMethods)

	// 更新状态为处理中
	_ = s.store.UpdateStatus(taskID, model.StatusProcessing, nil)

	// 创建状态对象
	state := &model.ArticleState{
		TaskID:              taskID,
		Topic:               topic,
		Style:               style,
		EnabledImageMethods: enabledImageMethods,
	}

	// 执行智能体编排
	ctx := context.Background()
	err := s.agentSvc.Execute(ctx, state)

	if err != nil {
		log.Printf("异步任务失败, taskId=%s, error=%v", taskID, err)

		// 更新状态为失败
		errMsg := err.Error()
		_ = s.store.UpdateStatus(taskID, model.StatusFailed, &errMsg)

		// 推送错误消息
		s.sseManager.Send(taskID, map[string]interface{}{
			"type":    "ERROR",
			"message": errMsg,
		})
		s.sseManager.Complete(taskID)
		return
	}

	// 保存文章到数据库
	if err := s.saveArticle(taskID, state); err != nil {
		log.Printf("保存文章失败, taskId=%s, error=%v", taskID, err)
		errMsg := "保存文章失败"
		_ = s.store.UpdateStatus(taskID, model.StatusFailed, &errMsg)
		return
	}

	// 更新状态为已完成
	_ = s.store.UpdateStatus(taskID, model.StatusCompleted, nil)

	// 推送完成消息
	s.sseManager.Send(taskID, map[string]interface{}{
		"type":   "ALL_COMPLETE",
		"taskId": taskID,
	})
	s.sseManager.Complete(taskID)

	log.Printf("异步任务完成, taskId=%s", taskID)
}

// saveArticle 保存文章到数据库
func (s *ArticleService) saveArticle(taskID string, state *model.ArticleState) error {
	article, err := s.store.GetByTaskID(taskID)
	if err != nil {
		return err
	}

	outlineJSON, _ := json.Marshal(state.Outline.Sections)
	imagesJSON, _ := json.Marshal(state.Images)
	outlineStr := string(outlineJSON)
	imagesStr := string(imagesJSON)
	now := time.Now()

	article.MainTitle = &state.Title.MainTitle
	article.SubTitle = &state.Title.SubTitle
	article.Outline = &outlineStr
	article.Content = &state.Content
	article.FullContent = &state.FullContent
	article.Images = &imagesStr
	article.CompletedTime = &now

	return s.store.Update(article)
}
