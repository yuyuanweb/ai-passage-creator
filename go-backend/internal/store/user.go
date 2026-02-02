package store

import (
	"github.com/yupi/ai-passage-creator/internal/model"
	"gorm.io/gorm"
)

// NotDeleted 软删除过滤 Scope
func NotDeleted(db *gorm.DB) *gorm.DB {
	return db.Where("isDelete = ?", 0)
}

// UserStore 用户数据存储
type UserStore struct {
	db *gorm.DB
}

// NewUserStore 创建用户存储实例
func NewUserStore(db *gorm.DB) *UserStore {
	return &UserStore{db: db}
}

// Create 创建用户
func (s *UserStore) Create(user *model.User) error {
	return s.db.Create(user).Error
}

// GetByID 根据 ID 获取用户
func (s *UserStore) GetByID(id int64) (*model.User, error) {
	var user model.User
	err := s.db.Scopes(NotDeleted).Where("id = ?", id).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetByAccount 根据账号获取用户
func (s *UserStore) GetByAccount(account string) (*model.User, error) {
	var user model.User
	err := s.db.Scopes(NotDeleted).Where("userAccount = ?", account).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetByAccountAndPassword 根据账号和密码获取用户
func (s *UserStore) GetByAccountAndPassword(account, password string) (*model.User, error) {
	var user model.User
	err := s.db.Scopes(NotDeleted).
		Where("userAccount = ? AND userPassword = ?", account, password).
		First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// Update 更新用户
func (s *UserStore) Update(user *model.User) error {
	return s.db.Scopes(NotDeleted).Where("id = ?", user.ID).Updates(user).Error
}

// Delete 删除用户（逻辑删除）
func (s *UserStore) Delete(id int64) error {
	return s.db.Model(&model.User{}).Where("id = ?", id).Update("isDelete", 1).Error
}

// CountByAccount 根据账号统计用户数
func (s *UserStore) CountByAccount(account string) (int64, error) {
	var count int64
	err := s.db.Model(&model.User{}).Scopes(NotDeleted).
		Where("userAccount = ?", account).Count(&count).Error
	return count, err
}

// List 分页查询用户列表
func (s *UserStore) List(query *gorm.DB, pageNum, pageSize int64) ([]model.User, int64, error) {
	var users []model.User
	var total int64

	// 统计总数
	if err := query.Model(&model.User{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// 分页查询
	offset := (pageNum - 1) * pageSize
	if err := query.Offset(int(offset)).Limit(int(pageSize)).Find(&users).Error; err != nil {
		return nil, 0, err
	}

	return users, total, nil
}

// BuildQuery 构建查询条件
func (s *UserStore) BuildQuery(id *int64, userAccount, userName, userProfile, userRole *string, sortField, sortOrder *string) *gorm.DB {
	query := s.db.Scopes(NotDeleted)

	if id != nil {
		query = query.Where("id = ?", *id)
	}
	if userRole != nil && *userRole != "" {
		query = query.Where("userRole = ?", *userRole)
	}
	if userAccount != nil && *userAccount != "" {
		query = query.Where("userAccount LIKE ?", "%"+*userAccount+"%")
	}
	if userName != nil && *userName != "" {
		query = query.Where("userName LIKE ?", "%"+*userName+"%")
	}
	if userProfile != nil && *userProfile != "" {
		query = query.Where("userProfile LIKE ?", "%"+*userProfile+"%")
	}

	// 排序
	if sortField != nil && *sortField != "" {
		order := "ASC"
		if sortOrder != nil && *sortOrder == "descend" {
			order = "DESC"
		}
		query = query.Order(*sortField + " " + order)
	}

	return query
}
