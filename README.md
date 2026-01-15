# Spring Boot + Vue 全栈项目模板

> 编程导航原创项目模板，用于快速初始化新项目

## 项目简介

这是一个基于 Spring Boot 3.5 + Vue 3 的全栈项目初始化模板，包含常用的基础功能和规范的代码结构，适合作为新项目的起点。

## 技术栈

### 后端

- Spring Boot 3.5.9
- MyBatis-Flex（数据库 ORM）
- MySQL（数据库）
- Redis（缓存 + Session）
- Redisson（分布式锁）
- Knife4j（接口文档）
- Hutool（工具库）

### 前端

- Vue 3
- Vite
- Ant Design Vue
- Axios
- Pinia
- Vue Router

## 功能模块

- ✅ 用户注册、登录、注销
- ✅ 用户管理（管理员）
- ✅ 权限校验（基于角色）
- ✅ 全局异常处理
- ✅ 统一响应格式
- ✅ 跨域配置
- ✅ 接口文档自动生成

## 项目结构

```
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── components/      # 公共组件
│   │   ├── config/          # 配置文件
│   │   ├── layouts/         # 布局组件
│   │   ├── pages/           # 页面
│   │   ├── router/          # 路由配置
│   │   └── stores/          # 状态管理
│   ├── Dockerfile           # 前端 Docker 配置
│   └── package.json
├── sql/                      # SQL 脚本
│   └── create_table.sql     # 建表语句
├── src/                      # 后端源码
│   └── main/
│       ├── java/com/yupi/template/
│       │   ├── annotation/  # 自定义注解
│       │   ├── aop/         # AOP 切面
│       │   ├── common/      # 通用类
│       │   ├── config/      # 配置类
│       │   ├── constant/    # 常量
│       │   ├── controller/  # 控制器
│       │   ├── exception/   # 异常处理
│       │   ├── mapper/      # 数据层
│       │   ├── model/       # 数据模型
│       │   ├── service/     # 业务逻辑
│       │   └── utils/       # 工具类
│       └── resources/
│           ├── application.yml
│           ├── application-local.yml
│           └── application-prod.yml
├── Dockerfile               # 后端 Docker 配置
├── docker-compose.yml       # Docker Compose 一键部署
└── pom.xml
```

## 快速开始

### 环境要求

- JDK 21+
- Node.js 22+
- MySQL 8.0+
- Redis 6.0+

### 后端启动

1. 执行 `sql/create_table.sql` 创建数据库和表
2. 修改 `application-local.yml` 中的数据库和 Redis 配置
3. 运行 `MainApplication` 启动后端服务
4. 访问 http://localhost:8123/api/doc.html 查看接口文档

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 查看前端页面

## Docker 部署

### 一键部署（推荐）

```bash
docker-compose up -d
```

访问：
- 前端：http://localhost
- 后端 API：http://localhost:8123/api
- 接口文档：http://localhost:8123/api/doc.html

### 单独构建

```bash
# 构建后端
docker build -t backend .

# 构建前端
cd frontend
docker build -t frontend .
```

## 使用说明

基于此模板开发新项目时：

1. 修改 `pom.xml` 中的项目信息（groupId、artifactId、name 等）
2. 修改包名（将 `com.yupi.template` 替换为你的包名）
3. 修改前端 `package.json` 中的项目名称
4. 修改 `application.yml` 中的应用名称和数据库名
5. 根据业务需求添加新的功能模块

## 作者

[编程导航学习圈](https://codefather.cn)
