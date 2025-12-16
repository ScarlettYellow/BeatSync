#!/bin/bash
# 从本地机器上传项目到腾讯云服务器
# 使用方法：在本地机器上执行此脚本

set -e

# 配置变量
SERVER_IP="1.12.239.225"
SERVER_USER="ubuntu"  # 根据实际情况修改（可能是 root 或 ubuntu）
# 注意：如果使用root用户，改为 "root"
PROJECT_DIR="/opt/beatsync"
LOCAL_PROJECT_DIR="/Users/scarlett/Projects/BeatSync"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "BeatSync 项目上传脚本"
echo "=========================================="
echo ""
echo "服务器: ${SERVER_USER}@${SERVER_IP}"
echo "目标目录: ${PROJECT_DIR}"
echo "本地目录: ${LOCAL_PROJECT_DIR}"
echo ""

# 检查本地目录
if [ ! -d "$LOCAL_PROJECT_DIR" ]; then
    echo "错误: 本地项目目录不存在: $LOCAL_PROJECT_DIR"
    exit 1
fi

# 确认
read -p "确认上传到服务器？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo -e "${GREEN}步骤1: 在服务器上创建目录...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${PROJECT_DIR}"

echo -e "${GREEN}步骤2: 上传项目文件（排除不必要的文件）...${NC}"
rsync -avz --progress \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.beatsync_cache' \
  --exclude 'outputs/web_uploads/*' \
  --exclude 'outputs/web_outputs/*' \
  --exclude 'outputs/logs/*' \
  --exclude 'node_modules' \
  --exclude '.env' \
  --exclude '*.log' \
  "${LOCAL_PROJECT_DIR}/" ${SERVER_USER}@${SERVER_IP}:${PROJECT_DIR}/

echo ""
echo -e "${GREEN}✅ 上传完成！${NC}"
echo ""
echo "下一步："
echo "1. SSH连接到服务器: ssh ${SERVER_USER}@${SERVER_IP}"
echo "2. 运行部署脚本: sudo ${PROJECT_DIR}/scripts/deployment/deploy_to_tencent_cloud.sh"
echo ""

