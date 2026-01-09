# Nginx CORS和文件大小限制修复

> **问题**：上传文件时出现CORS错误和413错误（文件太大）

---

## 问题分析

**错误1：CORS错误**
```
Access to fetch at 'https://1.12.239.225/api/upload' from origin 
'https://scarlettyellow.github.io' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**原因**：
- 健康检查（GET请求）成功，说明后端CORS配置正确
- 但POST请求时，Nginx没有转发CORS头
- 需要Nginx也配置CORS头

**错误2：413错误**
```
POST https://1.12.239.225/api/upload net::ERR_FAILED 413 (Request Entity Too Large)
```

**原因**：
- Nginx默认限制请求体大小为1MB
- 视频文件通常>1MB
- 需要增加Nginx的`client_max_body_size`

---

## 解决方案：更新Nginx配置

### 步骤1：更新Nginx配置

在服务器上执行：

```bash
sudo vim /etc/nginx/sites-available/beatsync
```

**更新配置内容**：

```nginx
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

    # 增加文件大小限制（500MB）
    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 添加CORS头
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;

        # 处理OPTIONS预检请求
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
}
```

### 步骤2：测试并重启Nginx

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 一键修复命令（推荐）

在服务器上执行以下完整命令：

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

    # 增加文件大小限制（500MB）
    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 添加CORS头
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;

        # 处理OPTIONS预检请求
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=utf-8";
            add_header Content-Length 0;
            return 204;
        }
    }
}
EOFNGINX
' && sudo nginx -t && sudo systemctl restart nginx && echo "✅ Nginx配置已更新！"
```

---

## 验证修复

### 测试1：检查Nginx配置

```bash
sudo nginx -t
```

**应该显示**：`syntax is ok` 和 `test is successful`

### 测试2：测试上传

1. 刷新前端页面
2. 尝试上传视频文件
3. 应该不再出现CORS和413错误

---

## 配置说明

### client_max_body_size

- **默认值**：1MB
- **当前设置**：500MB
- **可以根据需要调整**：如果视频文件更大，可以增加到1GB或更大

### CORS头

- **Access-Control-Allow-Origin**: `*`（允许所有来源）
- **Access-Control-Allow-Methods**: 允许的HTTP方法
- **Access-Control-Allow-Headers**: 允许的请求头
- **OPTIONS预检请求处理**: 浏览器会先发送OPTIONS请求检查CORS

---

## 如果仍然有问题

### 检查Nginx日志

```bash
sudo tail -f /var/log/nginx/error.log
```

### 检查后端日志

```bash
sudo journalctl -u beatsync -f
```

### 测试直接访问后端

```bash
# 在服务器上测试
curl -X POST http://127.0.0.1:8000/api/health
```

---

## 总结

**修复内容**：
1. ✅ 增加Nginx文件大小限制（500MB）
2. ✅ 添加CORS头支持
3. ✅ 处理OPTIONS预检请求

**下一步**：
1. 执行一键修复命令
2. 刷新前端页面
3. 重新尝试上传

---

**最后更新**：2025-12-01












