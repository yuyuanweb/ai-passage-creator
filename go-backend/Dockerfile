# ========================================
# AI 爆款文章创作器 - Go 后端 Dockerfile
# ========================================

# ============ 构建阶段 ============
# 如果拉取失败，请配置 Docker 镜像加速器，或使用以下国内镜像：
# FROM m.daocloud.io/docker.io/golang:1.25-alpine AS build
FROM golang:1.25-alpine AS build

WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache git

# 配置 Go 环境（国内用户可以使用 GOPROXY）
# ENV GOPROXY=https://goproxy.cn,direct
ENV GOPROXY=https://proxy.golang.org,direct
ENV CGO_ENABLED=0
ENV GOOS=linux
ENV GOARCH=amd64

# 1. 先复制 go.mod 和 go.sum 并下载依赖（利用 Docker 缓存）
COPY go.mod go.sum ./
RUN go mod download

# 2. 复制源代码并构建
COPY . .
RUN go build -ldflags="-s -w" -o /app/bin/server ./cmd/server/

# ============ 运行阶段 ============
# 如果拉取失败，请配置 Docker 镜像加速器，或使用以下国内镜像：
# FROM m.daocloud.io/docker.io/alpine:3.19
FROM alpine:3.19

WORKDIR /app

# 安装必要工具和依赖
# - ca-certificates: HTTPS 请求所需
# - tzdata: 时区数据
# - curl: 健康检查
# - nodejs npm: Mermaid CLI 依赖（用于生成流程图）
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    curl \
    nodejs \
    npm && \
    npm install -g @mermaid-js/mermaid-cli

# 设置时区
ENV TZ=Asia/Shanghai

# 从构建阶段复制可执行文件
COPY --from=build /app/bin/server /app/server

# 复制配置文件示例（实际配置通过挂载卷提供）
COPY config.yaml.example /app/config.yaml.example

# 创建非 root 用户运行应用（安全最佳实践）
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8123

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8123/api/health/ || exit 1

# 启动命令
# 注意：config.yaml 需要通过挂载卷提供，或者在运行时指定
CMD ["/app/server", "-config", "/app/config.yaml"]
