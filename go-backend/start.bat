@echo off
chcp 65001 >nul
echo 🚀 AI 爆款文章创作器 - 启动中...
echo.

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未安装 Docker
    pause
    exit /b 1
)

REM 检查 .env
if not exist .env (
    copy .env.example .env >nul
    echo ✅ 已创建 .env，请填写 API Key 后重新运行
    pause
    exit /b 1
)

REM 检查 config.yaml
if not exist config.yaml (
    copy config.yaml.example config.yaml >nul
)

REM 清理旧容器
docker compose down >nul 2>nul
docker stop ai-passage-mysql ai-passage-redis >nul 2>nul
docker rm ai-passage-mysql ai-passage-redis >nul 2>nul

REM 启动
echo 🚀 启动服务...
docker compose up -d --build

echo.
echo ✅ 启动完成！
echo    前端: http://localhost
echo    后端: http://localhost:8123/api
echo.
echo 查看日志: docker compose logs -f
pause
