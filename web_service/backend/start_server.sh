#!/bin/bash
# 启动后端服务脚本（本地开发用）

cd "$(dirname "$0")"

echo "启动BeatSync Web服务后端..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 使用uvicorn启动，支持热重载
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

