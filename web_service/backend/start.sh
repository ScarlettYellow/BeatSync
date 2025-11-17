#!/bin/bash
# Render部署启动脚本

# 确保在正确的目录
cd "$(dirname "$0")"

# 启动FastAPI应用
# Render会自动设置PORT环境变量
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}

