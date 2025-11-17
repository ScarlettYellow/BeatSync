#!/bin/bash
# 启动文件监控

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "启动文件监控..."
cd "$SCRIPT_DIR" && ./AUTO_COMMIT_MONITOR.sh --background

