package model

import "time"

// User 用户实体（数据库模型）
type User struct {
	ID           int64      `gorm:"primaryKey;autoIncrement" json:"id"`
	UserAccount  string     `gorm:"column:userAccount;uniqueIndex:uk_userAccount" json:"userAccount"`
	UserPassword string     `gorm:"column:userPassword" json:"-"`
	UserName     *string    `gorm:"column:userName;index:idx_userName" json:"userName"`
	UserAvatar   *string    `gorm:"column:userAvatar" json:"userAvatar"`
	UserProfile  *string    `gorm:"column:userProfile" json:"userProfile"`
	UserRole     string     `gorm:"column:userRole;default:user" json:"userRole"`
	EditTime     *time.Time `gorm:"column:editTime" json:"editTime"`
	CreateTime   time.Time  `gorm:"column:createTime;autoCreateTime" json:"createTime"`
	UpdateTime   time.Time  `gorm:"column:updateTime;autoUpdateTime" json:"updateTime"`
	IsDelete     int        `gorm:"column:isDelete;default:0" json:"-"`
}

// TableName 指定表名
func (User) TableName() string {
	return "user"
}

// LoginUser 登录用户信息（响应）
type LoginUser struct {
	ID          int64      `json:"id"`
	UserAccount string     `json:"userAccount"`
	UserName    *string    `json:"userName"`
	UserAvatar  *string    `json:"userAvatar"`
	UserProfile *string    `json:"userProfile"`
	UserRole    string     `json:"userRole"`
	CreateTime  time.Time  `json:"createTime"`
	UpdateTime  time.Time  `json:"updateTime"`
	EditTime    *time.Time `json:"editTime"`
}

// UserInfo 用户信息（响应）
type UserInfo struct {
	ID          int64      `json:"id"`
	UserAccount string     `json:"userAccount"`
	UserName    *string    `json:"userName"`
	UserAvatar  *string    `json:"userAvatar"`
	UserProfile *string    `json:"userProfile"`
	UserRole    string     `json:"userRole"`
	CreateTime  time.Time  `json:"createTime"`
	UpdateTime  time.Time  `json:"updateTime"`
	EditTime    *time.Time `json:"editTime"`
}

// ToLoginUser 转换为登录用户信息
func (u *User) ToLoginUser() *LoginUser {
	if u == nil {
		return nil
	}
	return &LoginUser{
		ID:          u.ID,
		UserAccount: u.UserAccount,
		UserName:    u.UserName,
		UserAvatar:  u.UserAvatar,
		UserProfile: u.UserProfile,
		UserRole:    u.UserRole,
		CreateTime:  u.CreateTime,
		UpdateTime:  u.UpdateTime,
		EditTime:    u.EditTime,
	}
}

// ToUserInfo 转换为用户信息
func (u *User) ToUserInfo() *UserInfo {
	if u == nil {
		return nil
	}
	return &UserInfo{
		ID:          u.ID,
		UserAccount: u.UserAccount,
		UserName:    u.UserName,
		UserAvatar:  u.UserAvatar,
		UserProfile: u.UserProfile,
		UserRole:    u.UserRole,
		CreateTime:  u.CreateTime,
		UpdateTime:  u.UpdateTime,
		EditTime:    u.EditTime,
	}
}

// UserRole 用户角色
type UserRole string

const (
	RoleUser  UserRole = "user"
	RoleAdmin UserRole = "admin"
)

// IsValid 判断角色是否有效
func (r UserRole) IsValid() bool {
	return r == RoleUser || r == RoleAdmin
}
