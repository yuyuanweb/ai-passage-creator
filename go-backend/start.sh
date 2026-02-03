#!/bin/bash
set -e

echo "🚀 AI 爆款文章创作器 - 启动中..."

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 未安装 Docker"
    exit 1
fi

# 检查 .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env，请填写 API Key 后重新运行"
    exit 1
fi

# 检查 config.yaml
if [ ! -f config.yaml ]; then
    cp config.yaml.example config.yaml
fi

# 清理旧容器
docker compose down 2>/dev/null || true
docker stop ai-passage-mysql ai-passage-redis 2>/dev/null || true
docker rm ai-passage-mysql ai-passage-redis 2>/dev/null || true

# 启动
echo "🚀 启动服务..."
docker compose up -d --build

echo ""
echo "✅ 启动完成！"
echo "   前端: http://localhost"
echo "   后端: http://localhost:8123/api"
echo ""
echo "查看日志: docker compose logs -f"
