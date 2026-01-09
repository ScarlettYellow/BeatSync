# 修复重复CORS头问题

> **问题**：CORS头重复，导致浏览器拒绝请求

---

## 问题分析

**错误信息**：
```
The 'Access-Control-Allow-Origin' header contains multiple values '*, *', 
but only one is allowed.
```

**原因**：
- ✅ Nginx添加了CORS头：`Access-Control-Allow-Origin: *`
- ✅ 后端FastAPI也添加了CORS头：`Access-Control-Allow-Origin: *`
- ❌ 结果：浏览器收到两个CORS头，拒绝请求

**解决方案**：
- 移除Nginx的CORS头，让后端处理CORS（推荐）
- 后端已经正确配置了CORS，不需要Nginx再添加

---

## 修复方案：移除Nginx的CORS头

### 更新Nginx配置

在服务器上执行：

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
        
        # 注意：不在这里添加CORS头，让后端FastAPI处理CORS
        # 后端已经正确配置了CORS，不需要Nginx重复添加
    }
}
EOFNGINX
' && sudo nginx -t && sudo systemctl restart nginx && echo "✅ Nginx配置已更新！已移除重复的CORS头"
```

---

## 验证修复

### 步骤1：检查Nginx配置

执行命令后，应该看到：
```
syntax is ok
test is successful
✅ Nginx配置已更新！已移除重复的CORS头
```

### 步骤2：测试连接

1. 刷新前端页面：https://scarlettyellow.github.io/BeatSync/
2. 打开浏览器开发者工具（F12）→ Console标签
3. 尝试上传视频文件
4. 应该不再出现CORS错误

---

## 配置说明

### 为什么移除Nginx的CORS头？

1. **后端已配置CORS**：FastAPI的CORSMiddleware已经正确配置
2. **避免重复**：Nginx和后端都添加CORS头会导致重复
3. **让后端处理**：后端可以更灵活地处理CORS逻辑

### 保留的配置

- ✅ **文件大小限制**：`client_max_body_size 500M`（解决413错误）
- ✅ **HTTPS支持**：SSL证书配置
- ✅ **反向代理**：将HTTPS请求转发到后端HTTP

---

## 如果仍然有问题

### 检查后端CORS配置

```bash
# 在服务器上检查
grep -A 10 "CORSMiddleware" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
```python
allow_origins=allow_origins_list,  # 应该是 ["*"]
```

### 检查Nginx日志

```bash
sudo tail -f /var/log/nginx/error.log
```

### 检查后端日志

```bash
sudo journalctl -u beatsync -f
```

---

## 总结

**问题根源**：Nginx和后端都添加了CORS头，导致重复

**修复方案**：移除Nginx的CORS头，让后端处理CORS

**保留功能**：
- ✅ 文件大小限制（500MB）
- ✅ HTTPS支持
- ✅ 反向代理

---

**最后更新**：2025-12-01












