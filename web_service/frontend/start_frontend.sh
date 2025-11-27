#!/bin/bash
# 启动前端服务

cd "$(dirname "$0")"

echo "🌐 启动前端服务..."
echo "工作目录: $(pwd)"
echo "服务地址: http://localhost:8080"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 使用Python的http.server启动前端
python3 -m http.server 8080

