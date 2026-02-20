# ========================================
# AI 爆款文章创作器 - Python 后端 Dockerfile
# ========================================

# ============ 构建阶段 ============
FROM python:3.12-slim AS build

WORKDIR /app

# 系统依赖（构建某些 Python 包和 Mermaid CLI 依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 安装 Mermaid CLI（用于生成流程图）
RUN npm install -g @mermaid-js/mermaid-cli

# 安装 uv
RUN pip install --no-cache-dir uv

# 先拷贝依赖清单，利用 Docker 缓存
COPY pyproject.toml uv.lock ./

# 安装生产依赖
RUN uv sync --frozen --no-dev

# 拷贝业务代码
COPY app ./app
COPY .env.example ./.env.example

# ============ 运行阶段 ============
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 运行时同样提供 Mermaid CLI
RUN npm install -g @mermaid-js/mermaid-cli

# 从构建阶段复制环境与代码
COPY --from=build /app /app

# 创建非 root 用户
RUN groupadd -g 1000 appuser \
    && useradd -u 1000 -g appuser -m appuser \
    && chown -R appuser:appuser /app

USER appuser

# 容器内固定使用 8123，与前端 nginx 反代保持一致
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8123

EXPOSE 8123

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8123/api/health/ || exit 1

CMD ["./.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8123"]
