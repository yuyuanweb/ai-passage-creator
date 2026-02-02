package service

import (
	"crypto/md5"
	"encoding/hex"
	"errors"
	"time"

	"github.com/gin-contrib/sessions"
	"github.com/yupi/ai-passage-creator/internal/common"
	"github.com/yupi/ai-passage-creator/internal/model"
	"github.com/yupi/ai-passage-creator/internal/store"
	"gorm.io/gorm"
)

// UserService 用户服务
type UserService struct {
	store *store.UserStore
}

// NewUserService 创建用户服务
func NewUserService(store *store.UserStore) *UserService {
	return &UserService{store: store}
}

// Register 用户注册
func (s *UserService) Register(req *model.RegisterRequest) (int64, error) {
	// 校验参数
	if req.UserAccount == "" || req.UserPassword == "" || req.CheckPassword == "" {
		return 0, common.ErrParams.WithMessage("参数为空")
	}
	if len(req.UserAccount) < common.MinAccountLength {
		return 0, common.ErrParams.WithMessage("账号长度过短")
	}
	if len(req.UserPassword) < common.MinPasswordLength || len(req.CheckPassword) < common.MinPasswordLength {
		return 0, common.ErrParams.WithMessage("密码长度过短")
	}
	if req.UserPassword != req.CheckPassword {
		return 0, common.ErrParams.WithMessage("两次输入的密码不一致")
	}

	// 查询用户是否已存在
	count, err := s.store.CountByAccount(req.UserAccount)
	if err != nil {
		return 0, common.ErrSystem
	}
	if count > 0 {
		return 0, common.ErrParams.WithMessage("账号重复")
	}

	// 创建用户
	userName := "无名"
	now := time.Now()
	user := &model.User{
		UserAccount:  req.UserAccount,
		UserPassword: encryptPassword(req.UserPassword),
		UserName:     &userName,
		UserRole:     string(model.RoleUser),
		EditTime:     &now,
	}

	if err := s.store.Create(user); err != nil {
		return 0, common.ErrOperation.WithMessage("注册失败，数据库错误")
	}

	return user.ID, nil
}

// Login 用户登录
func (s *UserService) Login(req *model.LoginRequest, session sessions.Session) (*model.LoginUser, error) {
	// 校验参数
	if req.UserAccount == "" || req.UserPassword == "" {
		return nil, common.ErrParams.WithMessage("参数为空")
	}
	if len(req.UserAccount) < common.MinAccountLength {
		return nil, common.ErrParams.WithMessage("账号长度过短")
	}
	if len(req.UserPassword) < common.MinPasswordLength {
		return nil, common.ErrParams.WithMessage("密码长度过短")
	}

	// 查询用户
	user, err := s.store.GetByAccountAndPassword(req.UserAccount, encryptPassword(req.UserPassword))
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, common.ErrParams.WithMessage("用户不存在或密码错误")
		}
		return nil, common.ErrSystem
	}

	// 保存登录态
	session.Set(common.UserLoginState, user.ID)
	if err := session.Save(); err != nil {
		return nil, common.ErrSystem
	}

	return user.ToLoginUser(), nil
}

// GetLoginUser 获取当前登录用户
func (s *UserService) GetLoginUser(session sessions.Session) (*model.User, error) {
	userID := session.Get(common.UserLoginState)
	if userID == nil {
		return nil, common.ErrNotLogin
	}

	id, ok := userID.(int64)
	if !ok {
		return nil, common.ErrNotLogin
	}

	user, err := s.store.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, common.ErrNotLogin
		}
		return nil, common.ErrSystem
	}

	return user, nil
}

// Logout 用户注销
func (s *UserService) Logout(session sessions.Session) error {
	if session.Get(common.UserLoginState) == nil {
		return common.ErrOperation.WithMessage("用户未登录")
	}
	session.Delete(common.UserLoginState)
	return session.Save()
}

// Create 创建用户（管理员）
func (s *UserService) Create(req *model.AddUserRequest) (int64, error) {
	now := time.Now()
	user := &model.User{
		UserAccount:  req.UserAccount,
		UserPassword: encryptPassword(common.DefaultPassword),
		UserName:     req.UserName,
		UserAvatar:   req.UserAvatar,
		UserProfile:  req.UserProfile,
		UserRole:     req.UserRole,
		EditTime:     &now,
	}

	if err := s.store.Create(user); err != nil {
		return 0, common.ErrOperation
	}
	return user.ID, nil
}

// GetByID 根据 ID 获取用户
func (s *UserService) GetByID(id int64) (*model.User, error) {
	user, err := s.store.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, common.ErrNotFound
		}
		return nil, common.ErrSystem
	}
	return user, nil
}

// Update 更新用户
func (s *UserService) Update(req *model.UpdateUserRequest) error {
	user := &model.User{
		ID:          req.ID,
		UserName:    req.UserName,
		UserAvatar:  req.UserAvatar,
		UserProfile: req.UserProfile,
	}
	if req.UserRole != nil {
		user.UserRole = *req.UserRole
	}

	if err := s.store.Update(user); err != nil {
		return common.ErrOperation
	}
	return nil
}

// Delete 删除用户
func (s *UserService) Delete(id int64) error {
	if err := s.store.Delete(id); err != nil {
		return common.ErrOperation
	}
	return nil
}

// ListByPage 分页查询用户列表
func (s *UserService) ListByPage(req *model.QueryUserRequest) (*model.PageResult, error) {
	query := s.store.BuildQuery(
		req.ID,
		req.UserAccount,
		req.UserName,
		req.UserProfile,
		req.UserRole,
		req.SortField,
		req.SortOrder,
	)

	users, total, err := s.store.List(query, req.PageNum, req.PageSize)
	if err != nil {
		return nil, common.ErrSystem
	}

	// 转换为用户信息列表
	userInfos := make([]model.UserInfo, 0, len(users))
	for i := range users {
		if info := users[i].ToUserInfo(); info != nil {
			userInfos = append(userInfos, *info)
		}
	}

	return &model.PageResult{
		Total:    total,
		Records:  userInfos,
		PageNum:  req.PageNum,
		PageSize: req.PageSize,
	}, nil
}

// encryptPassword 加密密码
func encryptPassword(password string) string {
	hash := md5.Sum([]byte(password + common.PasswordSalt))
	return hex.EncodeToString(hash[:])
}
