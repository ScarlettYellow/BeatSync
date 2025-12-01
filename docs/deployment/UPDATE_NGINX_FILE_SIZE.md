# 更新Nginx文件大小限制到1GB

> **目的**：将上传文件大小限制从500MB增加到1GB

---

## 更新Nginx配置

### 在服务器上执行以下命令

```bash
sudo bash -c 'cat > /etc/nginx/sites-available/beatsync << "EOFNGINX"
server {
    listen 80;
    server_name 1.12.239.225;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name 1.12.239.225;

    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;

    # 增加文件大小限制（1GB）
    client_max_body_size 1G;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 注意：不在这里添加CORS头，让后端FastAPI处理CORS
        # 后端已经正确配置了CORS，不需要Nginx重复添加
    }
}
EOFNGINX
' && sudo nginx -t && sudo systemctl restart nginx && echo "✅ Nginx配置已更新！文件大小限制已增加到1GB"
```

---

## 验证

### 检查配置

```bash
sudo nginx -t
```

**应该显示**：`syntax is ok` 和 `test is successful`

### 测试上传

1. 刷新前端页面
2. 尝试上传大于500MB的文件
3. 应该不再出现413错误

---

## 配置说明

### client_max_body_size

- **之前**：500MB
- **现在**：1GB
- **可以根据需要调整**：如果文件更大，可以增加到2G或更大

---

**最后更新**：2025-12-01

