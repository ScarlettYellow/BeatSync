#!/bin/bash
# 快速启动脚本 - 直接启动并显示输出

cd "$(dirname "$0")"

echo "🚀 启动后端服务..."
echo "工作目录: $(pwd)"
echo ""

# 直接启动，不后台运行，立即看到输出
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000

