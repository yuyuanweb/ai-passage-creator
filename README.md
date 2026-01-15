# AI 爆款文章创作器

基于 Spring AI Alibaba 构建的智能文章生成系统，支持从选题到图文文章的全自动生成。

## 项目介绍

本项目是一个 AI 驱动的爆款文章创作平台，通过5个智能体协作完成文章创作：
1. 智能体1：生成标题
2. 智能体2：生成大纲  
3. 智能体3：生成正文
4. 智能体4：配图需求分析
5. 智能体5：配图生成

## 技术栈

### 后端
- Spring Boot 3.5
- Spring AI Alibaba 1.1.0
- MyBatis-Flex  
- MySQL 8.0
- Redis 7.0

### 前端
- Vue 3
- TypeScript
- Ant Design Vue
- Vite

## 快速开始

### 1. 环境准备

- JDK 21
- Maven 3.8+
- MySQL 8.0+
- Redis 7.0+
- Node.js 18+

### 2. 数据库初始化

```bash
# 执行 SQL 脚本创建数据库和表
mysql -uroot -p < sql/create_table.sql
```

### 3. 配置 API Key

复制配置文件并填写 API Key:

```bash
cp src/main/resources/application-local.yml.example src/main/resources/application-local.yml
```

编辑 `application-local.yml`，配置以下信息：
- `spring.ai.alibaba.dashscope.api-key`: 通义千问 API Key
- `pexels.api-key`: Pexels API Key  
- `tencent.cos.*`: 腾讯云 COS 配置（可选）

### 4. 启动后端

```bash
mvn spring-boot:run
```

后端服务启动在 `http://localhost:8080`

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端服务启动在 `http://localhost:5173`

## API 文档

启动后端服务后，访问 Knife4j 接口文档：

```
http://localhost:8080/api/doc.html
```

## 核心功能

- [x] 用户注册/登录
- [x] 文章创作（SSE 实时推送）
- [x] 文章列表管理
- [x] 文章详情查看
- [x] Markdown 导出

## 项目结构

```
.
├── src/main/java/com/yupi/template/
│   ├── controller/          # 控制器
│   ├── service/             # 业务服务
│   ├── mapper/              # 数据访问层
│   ├── model/               # 实体类
│   ├── config/              # 配置类
│   ├── manager/             # 管理器（如 SSE）
│   └── constant/            # 常量
├── frontend/                # 前端项目
└── sql/                     # SQL 脚本
```

## 作者

<a href="https://codefather.cn">编程导航学习圈</a>

## 许可证

MIT
