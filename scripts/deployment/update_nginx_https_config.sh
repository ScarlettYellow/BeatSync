#!/bin/bash
# 更新 Nginx 配置，添加 HTTPS 支持

set -e

NGINX_CONFIG="/etc/nginx/sites-available/beatsync"
BACKUP_FILE="${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "更新 Nginx HTTPS 配置"
echo "=========================================="
echo ""

# 1. 备份当前配置
echo "步骤 1: 备份当前配置..."
if [ -f "$NGINX_CONFIG" ]; then
    sudo cp "$NGINX_CONFIG" "$BACKUP_FILE"
    echo "✅ 已备份到: $BACKUP_FILE"
else
    echo "⚠️  配置文件不存在: $NGINX_CONFIG"
fi
echo ""

# 2. 创建新配置
echo "步骤 2: 创建新配置..."
sudo tee "$NGINX_CONFIG" > /dev/null << 'EOF'
# HTTP 服务器 - 自动跳转到 HTTPS
server {
    listen 80;
    server_name beatsync.site;
    
    # 所有 HTTP 请求自动跳转到 HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务器
server {
    listen 443 ssl http2;
    server_name beatsync.site;
    
    # SSL 证书配置（Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 文件上传大小限制
    client_max_body_size 500M;
    
    # 反向代理到 FastAPI 后端
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
    
    # 健康检查端点（可选）
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
EOF

echo "✅ 配置已写入"
echo ""

# 3. 验证配置
echo "步骤 3: 验证 Nginx 配置..."
if sudo nginx -t; then
    echo "✅ Nginx 配置语法正确"
else
    echo "❌ Nginx 配置语法错误，已恢复备份"
    if [ -f "$BACKUP_FILE" ]; then
        sudo cp "$BACKUP_FILE" "$NGINX_CONFIG"
    fi
    exit 1
fi
echo ""

# 4. 重新加载 Nginx
echo "步骤 4: 重新加载 Nginx..."
if sudo systemctl reload nginx; then
    echo "✅ Nginx 已重新加载"
else
    echo "⚠️  重新加载失败，尝试重启..."
    sudo systemctl restart nginx
    echo "✅ Nginx 已重启"
fi
echo ""

# 5. 检查端口监听
echo "步骤 5: 检查端口监听..."
echo "监听的端口："
sudo netstat -tlnp 2>/dev/null | grep nginx | grep -E ":(80|443)" || sudo ss -tlnp 2>/dev/null | grep nginx | grep -E ":(80|443)"
echo ""

# 6. 测试
echo "步骤 6: 测试配置..."
echo "测试 HTTP 跳转："
curl -I http://beatsync.site/api/health 2>&1 | head -3
echo ""
echo "测试 HTTPS 访问："
curl -I https://beatsync.site/api/health 2>&1 | head -3
echo ""

echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo ""
echo "备份文件: $BACKUP_FILE"
echo ""
echo "下一步："
echo "1. 检查防火墙: sudo ufw allow 443/tcp"
echo "2. 检查腾讯云安全组是否开放 443 端口"
echo "3. 测试访问: curl https://beatsync.site/api/health"
echo ""

