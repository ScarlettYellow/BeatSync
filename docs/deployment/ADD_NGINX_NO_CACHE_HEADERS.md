# 为 Nginx API 路径添加禁止缓存头

> **问题**：CDN 缓存了 API 响应，导致前端获取到旧状态  
> **解决**：在 Nginx 配置中为 `/api/` 路径添加 `Cache-Control: no-cache` 头

---

## 修改 Nginx 配置

### 1. 备份当前配置

```bash
sudo cp /etc/nginx/sites-available/beatsync /etc/nginx/sites-available/beatsync.backup-$(date +%Y%m%d-%H%M%S)
```

### 2. 修改配置文件

在 HTTPS server 块中，找到 `location /` 块，在它**之前**添加新的 `location /api/` 块：

```bash
sudo tee -a /tmp/beatsync_nginx_temp.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name beatsync.site;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 上传大小限制
    client_max_body_size 500M;

    # API 路径：禁止缓存
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 禁止缓存 API 响应
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";

        # 超时设置
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # 其他路径
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # 健康检查
    location /api/health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
EOF

# 替换配置文件
sudo mv /tmp/beatsync_nginx_temp.conf /etc/nginx/sites-available/beatsync
```

### 3. 验证配置

```bash
sudo nginx -t
```

应该输出：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4. 重启 Nginx

```bash
sudo systemctl restart nginx
```

### 5. 验证生效

```bash
# 测试 API 响应头
curl -I https://beatsync.site/api/health

# 应该看到：
# Cache-Control: no-cache, no-store, must-revalidate
# Pragma: no-cache
# Expires: 0
```

---

## 完成后操作

1. **刷新 CDN 缓存**（清除旧的缓存响应）
2. **测试功能**：提交新任务，验证状态实时更新
3. **监控**：观察一段时间，确保问题解决

---

## 说明

### 为什么要单独配置 `/api/` location？

Nginx 的 location 匹配规则：
- 优先级：`location /api/` > `location /`
- 请求 `/api/status` 会匹配到 `/api/` 块
- 请求 `/` 会匹配到 `/` 块

这样可以为 API 请求单独配置不缓存头，而不影响其他资源。

### 为什么 CDN 配置了不缓存还会缓存？

1. CDN 配置的是"节点缓存时间"和"缓存键"
2. 但如果源站（Nginx）没有返回正确的 `Cache-Control` 头，CDN 可能仍会使用默认缓存策略
3. 明确在源站设置 `no-cache` 头，CDN 会遵守这个指示

---

**最后更新**：2025-12-18








