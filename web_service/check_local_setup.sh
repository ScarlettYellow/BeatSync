#!/bin/bash
# 本地开发环境诊断脚本

echo "=========================================="
echo "BeatSync 本地开发环境诊断"
echo "=========================================="
echo ""

# 检查Python
echo "1. 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python: $PYTHON_VERSION"
else
    echo "   ❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo ""
echo "2. 检查Python依赖..."
cd "$(dirname "$0")/backend" || exit 1

MISSING_DEPS=()
# 注意：opencv-python的导入名称是cv2，不是opencv-python
REQUIRED_DEPS=("fastapi:fastapi" "uvicorn:uvicorn" "numpy:numpy" "soundfile:soundfile" "librosa:librosa" "opencv-python:cv2" "psutil:psutil")

for dep_info in "${REQUIRED_DEPS[@]}"; do
    dep_name="${dep_info%%:*}"
    import_name="${dep_info##*:}"
    if python3 -c "import ${import_name}" 2>/dev/null; then
        echo "   ✅ $dep_name"
    else
        echo "   ❌ $dep_name 未安装"
        MISSING_DEPS+=("$dep_name")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo ""
    echo "   缺少依赖，请运行："
    echo "   cd web_service/backend && pip install -r requirements.txt"
fi

# 检查ffmpeg
echo ""
echo "3. 检查ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
    echo "   ✅ ffmpeg: $FFMPEG_VERSION"
else
    echo "   ❌ ffmpeg 未安装（视频处理必需）"
    echo "   安装方法："
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt-get install ffmpeg"
    echo "   Windows: 下载 https://ffmpeg.org/download.html"
fi

# 检查后端服务
echo ""
echo "4. 检查后端服务..."
if lsof -i :8000 &> /dev/null; then
    echo "   ✅ 端口8000已被占用（后端可能正在运行）"
    lsof -i :8000 | grep LISTEN
else
    echo "   ⚠️  端口8000未被占用（后端可能未启动）"
    echo "   启动方法："
    echo "   cd web_service/backend && ./start_server.sh"
fi

# 检查前端服务
echo ""
echo "5. 检查前端服务..."
if lsof -i :8080 &> /dev/null; then
    echo "   ✅ 端口8080已被占用（前端可能正在运行）"
    lsof -i :8080 | grep LISTEN
else
    echo "   ⚠️  端口8080未被占用（前端可能未启动）"
    echo "   启动方法："
    echo "   cd web_service/frontend && python3 -m http.server 8080"
fi

# 检查输出目录
echo ""
echo "6. 检查输出目录..."
cd "$(dirname "$0")/.." || exit 1
if [ -d "outputs" ]; then
    echo "   ✅ outputs/ 目录存在"
    if [ -w "outputs" ]; then
        echo "   ✅ outputs/ 目录可写"
    else
        echo "   ❌ outputs/ 目录不可写"
    fi
else
    echo "   ⚠️  outputs/ 目录不存在，将自动创建"
fi

# 检查日志目录
if [ -d "outputs/logs" ]; then
    echo "   ✅ outputs/logs/ 目录存在"
else
    echo "   ⚠️  outputs/logs/ 目录不存在，将自动创建"
fi

# 测试后端API
echo ""
echo "7. 测试后端API..."
if lsof -i :8000 &> /dev/null; then
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "   ✅ 后端API可访问"
    else
        echo "   ❌ 后端API无法访问"
        echo "   请检查后端服务是否正常启动"
    fi
else
    echo "   ⚠️  后端服务未运行，跳过API测试"
fi

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果发现问题，请："
echo "1. 查看后端日志（启动后端的终端）"
echo "2. 查看浏览器控制台（F12 -> Console）"
echo "3. 查看性能日志：outputs/logs/performance_*.log"
echo ""

