#!/bin/bash
# 一键启动本地开发环境（支持手机访问）

echo "=========================================="
echo "BeatSync 本地开发环境启动脚本（手机测试版）"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在 web_service/ 目录下运行此脚本"
    exit 1
fi

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装Python"
    exit 1
fi

# 检查uvicorn是否安装
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "⚠️  警告: uvicorn未安装，正在安装..."
    pip install uvicorn[standard]
fi

# 获取本机局域网IP地址
LOCAL_IP=$(ifconfig | grep -E "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$LOCAL_IP" ]; then
    echo "⚠️  警告: 无法自动获取IP地址，请手动设置"
    echo "   请运行: ifconfig | grep 'inet ' | grep -v 127.0.0.1"
    LOCAL_IP="YOUR_IP_HERE"
fi

echo "✅ 环境检查通过"
echo ""
echo "📱 手机访问地址:"
echo "   http://${LOCAL_IP}:8080"
echo ""
echo "💻 电脑访问地址:"
echo "   后端: http://localhost:8000"
echo "   前端: http://localhost:8080"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=========================================="
echo ""

# 创建日志目录
mkdir -p ../outputs/logs

# 启动后端（后台运行）
echo "🚀 启动后端服务..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 2

# 启动前端
echo "🚀 启动前端服务..."
cd frontend
python3 -m http.server 8080 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 服务已启动！"
echo ""
echo "后端PID: $BACKEND_PID"
echo "前端PID: $FRONTEND_PID"
echo ""
echo "📱 在手机上访问: http://${LOCAL_IP}:8080"
echo ""
echo "查看日志:"
echo "  后端: tail -f backend.log"
echo "  前端: tail -f frontend.log"
echo ""
echo "停止服务:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  或按 Ctrl+C"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit" INT TERM

# 保持脚本运行，定期检查服务状态
echo "服务正在运行中，按 Ctrl+C 停止..."
while true; do
    # 检查后端进程是否还在运行
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  后端服务已停止 (PID: $BACKEND_PID)"
        break
    fi
    # 检查前端进程是否还在运行
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  前端服务已停止 (PID: $FRONTEND_PID)"
        break
    fi
    # 等待1秒后再次检查
    sleep 1
done

