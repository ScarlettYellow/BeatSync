#!/bin/bash
# 快速测试 /api/process 接口

echo "测试 /api/process 接口..."
echo ""

# 获取脚本所在目录的父目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
UPLOAD_DIR="$PROJECT_ROOT/outputs/web_uploads"

echo "项目根目录: $PROJECT_ROOT"
echo "上传目录: $UPLOAD_DIR"
echo ""

if [ ! -d "$UPLOAD_DIR" ]; then
    echo "错误: 上传目录不存在: $UPLOAD_DIR"
    echo "提示: 请先通过前端上传文件，或手动创建目录: mkdir -p $UPLOAD_DIR"
    exit 1
fi

# 查找最近的两个文件
DANCE_FILE=$(ls -t "$UPLOAD_DIR"/*_dance.* 2>/dev/null | head -1)
BGM_FILE=$(ls -t "$UPLOAD_DIR"/*_bgm.* 2>/dev/null | head -1)

if [ -z "$DANCE_FILE" ] || [ -z "$BGM_FILE" ]; then
    echo "错误: 找不到上传的文件"
    echo "请先通过前端上传文件"
    exit 1
fi

# 提取文件ID
DANCE_ID=$(basename "$DANCE_FILE" | sed 's/_dance\..*//')
BGM_ID=$(basename "$BGM_FILE" | sed 's/_bgm\..*//')

echo "找到文件:"
echo "  dance_file_id: $DANCE_ID"
echo "  bgm_file_id: $BGM_ID"
echo ""

echo "发送请求到 http://localhost:8000/api/process ..."
echo ""

# 发送请求并显示耗时
time curl -X POST http://localhost:8000/api/process \
    -F "dance_file_id=$DANCE_ID" \
    -F "bgm_file_id=$BGM_ID" \
    -w "\n\nHTTP状态码: %{http_code}\n总耗时: %{time_total}s\n" \
    -v 2>&1 | head -50

echo ""
echo "测试完成"

