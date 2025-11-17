#!/bin/bash
# 停止文件监控

# 获取项目根目录（脚本在scripts/git/目录下）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PID_FILE="$PROJECT_ROOT/.git_monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️  监控未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    kill "$PID"
    rm -f "$PID_FILE"
    echo "✅ 监控已停止 (PID: $PID)"
else
    rm -f "$PID_FILE"
    echo "ℹ️  监控进程不存在，已清理PID文件"
fi

