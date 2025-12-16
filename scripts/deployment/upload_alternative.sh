#!/bin/bash
# 替代上传方案：使用Git克隆（如果项目在GitHub）
# 在服务器上执行此脚本

set -e

PROJECT_DIR="/opt/beatsync"
GIT_REPO="https://github.com/scarlettyellow/BeatSync.git"

echo "=========================================="
echo "BeatSync 项目Git克隆脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "错误：请使用root用户运行此脚本"
    echo "使用: sudo $0"
    exit 1
fi

echo "步骤1: 安装Git..."
apt update
apt install -y git

echo "步骤2: 克隆项目..."
mkdir -p $(dirname $PROJECT_DIR)
cd $(dirname $PROJECT_DIR)
if [ -d "$PROJECT_DIR" ]; then
    echo "目录已存在，先删除..."
    rm -rf $PROJECT_DIR
fi
git clone $GIT_REPO $PROJECT_DIR

echo "步骤3: 设置权限..."
chown -R $SUDO_USER:$SUDO_USER $PROJECT_DIR

echo ""
echo "✅ 克隆完成！"
echo "项目目录: $PROJECT_DIR"
echo ""
echo "下一步：运行部署脚本"
echo "cd $PROJECT_DIR"
echo "sudo bash scripts/deployment/deploy_to_tencent_cloud.sh"
echo ""



