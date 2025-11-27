#!/bin/bash
# 启动后端服务脚本（本地开发用）

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 确保在正确的目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "启动BeatSync Web服务后端..."
echo "工作目录: $(pwd)"
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 使用uvicorn启动，支持热重载
# 使用 python3 -m uvicorn 确保使用正确的Python环境
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

