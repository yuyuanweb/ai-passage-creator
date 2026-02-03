# Docker 部署指南

## 快速开始

### 1. 准备配置

```bash
# 复制环境变量配置
cp .env.example .env

# 编辑 .env，填写必需的 API Key
vim .env
# ⚠️ 必需：
# - DASHSCOPE_API_KEY（阿里云通义千问）
# - PEXELS_API_KEY（Pexels 图片）
# 可选：
# - MYSQL_ROOT_PASSWORD（建议修改默认密码）

# 复制配置文件（使用默认配置即可）
cp config.yaml.example config.yaml
```

### 2. 启动服务

```bash
# Linux/macOS
./start.sh

# Windows  
start.bat

# 或手动启动
docker compose up -d --build
```

### 3. 访问

- **前端**: http://localhost
- **后端**: http://localhost:8123/api

## 常用命令

```bash
# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

## 注意事项

1. 首次启动等待约 60 秒（数据库初始化）
2. 所有敏感配置通过 `.env` 文件管理
3. MySQL 和 Redis 不暴露到宿主机端口
