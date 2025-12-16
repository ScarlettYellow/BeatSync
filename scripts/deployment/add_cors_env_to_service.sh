#!/bin/bash
# 在 systemd 服务文件中添加 CORS 环境变量

set -e

SERVICE_FILE="/etc/systemd/system/beatsync.service"
ENV_VAR='Environment="ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000"'

echo "=========================================="
echo "添加 CORS 环境变量到 systemd 服务"
echo "=========================================="
echo ""

# 1. 备份服务文件
echo "步骤 1: 备份服务文件..."
if [ -f "$SERVICE_FILE" ]; then
    sudo cp "$SERVICE_FILE" "${SERVICE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已备份"
else
    echo "❌ 服务文件不存在: $SERVICE_FILE"
    exit 1
fi
echo ""

# 2. 检查是否已存在 ALLOWED_ORIGINS
echo "步骤 2: 检查现有配置..."
if grep -q "ALLOWED_ORIGINS" "$SERVICE_FILE"; then
    echo "⚠️  服务文件中已存在 ALLOWED_ORIGINS 配置"
    echo "当前配置："
    grep "ALLOWED_ORIGINS" "$SERVICE_FILE"
    echo ""
    read -p "是否要替换现有配置？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    # 删除旧配置
    sudo sed -i '/ALLOWED_ORIGINS/d' "$SERVICE_FILE"
    echo "✅ 已删除旧配置"
else
    echo "✅ 未找到现有配置，将添加新配置"
fi
echo ""

# 3. 添加环境变量（在 Environment="PATH=..." 之后）
echo "步骤 3: 添加环境变量..."
if grep -q 'Environment="PATH=' "$SERVICE_FILE"; then
    # 在 PATH 环境变量之后添加
    sudo sed -i '/Environment="PATH=/a '"$ENV_VAR"'' "$SERVICE_FILE"
    echo "✅ 已在 PATH 环境变量之后添加"
else
    # 如果没有 PATH，在 [Service] 部分后添加
    sudo sed -i '/\[Service\]/a '"$ENV_VAR"'' "$SERVICE_FILE"
    echo "✅ 已在 [Service] 部分添加"
fi
echo ""

# 4. 验证配置
echo "步骤 4: 验证配置..."
if grep -q "ALLOWED_ORIGINS" "$SERVICE_FILE"; then
    echo "✅ 配置已添加："
    grep "ALLOWED_ORIGINS" "$SERVICE_FILE"
else
    echo "❌ 配置添加失败"
    exit 1
fi
echo ""

# 5. 重新加载 systemd
echo "步骤 5: 重新加载 systemd..."
sudo systemctl daemon-reload
echo "✅ systemd 已重新加载"
echo ""

# 6. 重启服务
echo "步骤 6: 重启服务..."
sudo systemctl restart beatsync.service
echo "✅ 服务已重启"
echo ""

# 7. 检查服务状态
echo "步骤 7: 检查服务状态..."
sudo systemctl status beatsync.service --no-pager | head -10
echo ""

# 8. 验证环境变量
echo "步骤 8: 验证环境变量..."
ENV_CHECK=$(sudo systemctl show beatsync.service | grep ALLOWED_ORIGINS || echo "未找到")
if [ "$ENV_CHECK" != "未找到" ]; then
    echo "✅ 环境变量已加载："
    echo "$ENV_CHECK"
else
    echo "⚠️  环境变量未在 systemd 中显示（可能需要检查服务日志）"
fi
echo ""

echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 测试 CORS 配置："
echo "   curl -I -H \"Origin: https://beatsync.site\" https://beatsync.site/api/health"
echo ""
echo "2. 应该看到："
echo "   access-control-allow-origin: https://beatsync.site"
echo ""
