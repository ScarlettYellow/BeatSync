# 修复Nginx显示默认页面问题

> **问题**：访问 `https://beatsync.site` 显示 "Welcome to nginx!" 默认页面  
> **原因**：Nginx配置未正确代理到FastAPI后端，或server_name配置不正确  
> **解决**：检查并更新Nginx配置，确保正确代理到FastAPI

---

## 问题分析

### 当前状态
- ✅ HTTPS证书工作正常（可以访问HTTPS）
- ✅ Nginx正在运行
- ❌ Nginx显示默认页面，未代理到FastAPI后端

### 可能原因
1. **Certbot修改了默认配置**：可能修改了 `/etc/nginx/sites-enabled/default` 而不是BeatSync专用配置
2. **server_name配置错误**：可能没有正确配置 `beatsync.site`
3. **代理配置缺失**：可能没有配置代理到FastAPI后端（127.0.0.1:8000）

---

## 解决步骤

### 步骤1：检查当前Nginx配置

**在服务器上执行**：
```bash
# 查看当前启用的配置
sudo ls -la /etc/nginx/sites-enabled/

# 查看默认配置内容
sudo cat /etc/nginx/sites-enabled/default

# 查看是否有BeatSync专用配置
sudo ls -la /etc/nginx/sites-available/ | grep beatsync
```

---

### 步骤2：检查FastAPI后端状态

**确认后端服务正在运行**：
```bash
# 检查FastAPI服务状态
sudo systemctl status beatsync

# 检查端口8000是否被占用
sudo netstat -tlnp | grep :8000

# 测试本地API
curl http://localhost:8000/api/health
```

**预期结果**：
- FastAPI服务状态：`active (running)`
- 端口8000被占用（FastAPI正在监听）
- `/api/health` 返回：`{"status":"healthy"}`

---

### 步骤3：创建/更新BeatSync Nginx配置

**创建BeatSync专用配置**：
```bash
# 创建配置文件
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name beatsync.site;
    
    # 重定向HTTP到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name beatsync.site;

    # SSL证书配置（Certbot自动配置）
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 文件上传大小限制
    client_max_body_size 500M;

    # 代理到FastAPI后端
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API文档（可选）
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOFNGINX
```

---

### 步骤4：启用BeatSync配置并禁用默认配置

**启用BeatSync配置**：
```bash
# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/beatsync

# 禁用默认配置（如果存在）
sudo rm -f /etc/nginx/sites-enabled/default

# 或者重命名默认配置（保留备份）
sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak
```

---

### 步骤5：测试Nginx配置

**验证配置语法**：
```bash
sudo nginx -t
```

**预期输出**：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### 步骤6：重新加载Nginx

**应用新配置**：
```bash
sudo systemctl reload nginx
# 或
sudo systemctl restart nginx
```

**检查Nginx状态**：
```bash
sudo systemctl status nginx
```

---

### 步骤7：验证访问

**在浏览器中访问**：
```
https://beatsync.site/api/health
```

**预期结果**：
- ✅ 返回：`{"status":"healthy"}`
- ✅ 不再显示默认页面

**访问API文档**：
```
https://beatsync.site/docs
```

**预期结果**：
- ✅ 显示FastAPI文档页面

---

## 一键修复命令（完整）

**如果步骤3-6需要一次性执行**：

```bash
# 1. 创建BeatSync配置
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name beatsync.site;

    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOFNGINX

# 2. 启用配置并禁用默认配置
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/beatsync
sudo rm -f /etc/nginx/sites-enabled/default

# 3. 测试配置
sudo nginx -t

# 4. 重新加载Nginx
sudo systemctl reload nginx

# 5. 验证访问
curl https://beatsync.site/api/health
```

---

## 常见问题

### Q1：Nginx配置测试失败

**错误**：`nginx: configuration file /etc/nginx/nginx.conf test failed`

**解决**：
1. 检查配置文件语法
2. 查看详细错误信息：`sudo nginx -t`
3. 检查SSL证书路径是否正确

---

### Q2：访问后仍然显示默认页面

**可能原因**：
- Nginx配置未正确加载
- 默认配置仍然启用
- server_name配置错误

**解决**：
```bash
# 检查启用的配置
sudo ls -la /etc/nginx/sites-enabled/

# 确认只有beatsync配置
# 重新加载Nginx
sudo systemctl restart nginx
```

---

### Q3：访问后显示502 Bad Gateway

**可能原因**：
- FastAPI后端未运行
- 端口8000未监听
- 代理配置错误

**解决**：
```bash
# 检查FastAPI服务
sudo systemctl status beatsync

# 检查端口
sudo netstat -tlnp | grep :8000

# 测试本地API
curl http://localhost:8000/api/health
```

---

## 验证清单

- [ ] FastAPI后端服务正在运行
- [ ] Nginx配置已创建
- [ ] BeatSync配置已启用
- [ ] 默认配置已禁用
- [ ] Nginx配置测试通过
- [ ] Nginx已重新加载
- [ ] HTTPS可以访问API
- [ ] 不再显示默认页面

---

**最后更新**：2025-12-04

