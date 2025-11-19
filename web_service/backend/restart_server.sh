#!/bin/bash
# 重启后端服务脚本

cd "$(dirname "$0")"

echo "正在停止现有服务..."
./stop_server.sh

echo ""
echo "等待2秒..."
sleep 2

echo ""
echo "正在启动新服务..."
./start_server.sh
