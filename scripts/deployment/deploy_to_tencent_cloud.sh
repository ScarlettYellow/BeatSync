#!/bin/bash
# BeatSync 腾讯云服务器快速部署脚本
# 使用方法：在服务器上执行此脚本

set -e

echo "=========================================="
echo "BeatSync 腾讯云服务器部署脚本"
echo "=========================================="
echo ""

# 配置变量
PROJECT_DIR="/opt/beatsync"
SERVICE_NAME="beatsync"
SERVICE_PORT=8000
SERVER_IP="124.221.58.149"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}错误：请使用root用户运行此脚本${NC}"
    echo "使用: sudo $0"
    exit 1
fi

echo -e "${GREEN}步骤1: 更新系统...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}步骤2: 安装基础工具...${NC}"
apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev

echo -e "${GREEN}步骤3: 检查Python版本...${NC}"
python3 --version
if ! command -v pip3 &> /dev/null; then
    echo "安装pip..."
    apt install -y python3-pip
fi
pip3 install --upgrade pip

echo -e "${GREEN}步骤4: 安装FFmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    apt install -y ffmpeg
fi
ffmpeg -version | head -1

echo -e "${GREEN}步骤5: 检查项目目录...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}警告: 项目目录不存在: $PROJECT_DIR${NC}"
    echo "请先上传项目代码到此目录，或使用Git克隆："
    echo "  mkdir -p $PROJECT_DIR"
    echo "  cd $PROJECT_DIR"
    echo "  git clone https://github.com/scarlettyellow/BeatSync.git ."
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

cd "$PROJECT_DIR"

echo -e "${GREEN}步骤6: 安装Python依赖...${NC}"
cd web_service/backend
pip3 install -r requirements.txt

echo -e "${GREEN}步骤7: 创建必要目录...${NC}"
cd "$PROJECT_DIR"
mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs
chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs

echo -e "${GREEN}步骤8: 创建systemd服务...${NC}"
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=BeatSync Web Service Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_DIR}/web_service/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port ${SERVICE_PORT}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}步骤9: 启用并启动服务...${NC}"
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo -e "${GREEN}步骤10: 检查服务状态...${NC}"
sleep 2
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ 服务运行正常！${NC}"
else
    echo -e "${RED}❌ 服务启动失败，查看日志：${NC}"
    journalctl -u ${SERVICE_NAME} -n 20
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "服务信息："
echo "  - 服务地址: http://${SERVER_IP}:${SERVICE_PORT}"
echo "  - 健康检查: http://${SERVER_IP}:${SERVICE_PORT}/api/health"
echo "  - API文档: http://${SERVER_IP}:${SERVICE_PORT}/docs"
echo ""
echo "常用命令："
echo "  - 查看状态: systemctl status ${SERVICE_NAME}"
echo "  - 查看日志: journalctl -u ${SERVICE_NAME} -f"
echo "  - 重启服务: systemctl restart ${SERVICE_NAME}"
echo "  - 停止服务: systemctl stop ${SERVICE_NAME}"
echo ""
echo -e "${YELLOW}重要提醒：${NC}"
echo "1. 请在腾讯云控制台配置防火墙，开放端口 ${SERVICE_PORT}"
echo "2. 更新前端配置，将API地址改为: http://${SERVER_IP}:${SERVICE_PORT}"
echo ""

