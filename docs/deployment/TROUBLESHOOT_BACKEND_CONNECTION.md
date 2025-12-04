# 后端服务连接问题排查

> **错误**：`ERR_CONNECTION_CLOSED` - 后端服务无法连接  
> **可能原因**：服务未运行、Nginx配置错误、防火墙未开放、SSL证书问题  
> **解决**：逐步检查服务状态、配置和网络

---

## 问题分析

### 错误信息

- **前端错误**：`后端服务不可用(已尝试多次连接)`
- **浏览器错误**：`ERR_CONNECTION_CLOSED`
- **访问地址**：`https://beatsync.site/api/health`

### 可能原因

1. **后端服务未运行**
2. **Nginx配置错误**
3. **防火墙未开放443端口**
4. **SSL证书配置问题**
5. **Nginx服务未运行**

---

## 排查步骤

### 步骤1：检查后端服务状态

**在服务器上执行**：
```bash
# 检查FastAPI服务状态
sudo systemctl status beatsync

# 检查服务日志
sudo journalctl -u beatsync -n 50 --no-pager
```

**预期结果**：
- 服务状态：`active (running)`
- 端口8000被占用

**如果服务未运行**：
```bash
# 启动服务
sudo systemctl start beatsync

# 检查状态
sudo systemctl status beatsync
```

---

### 步骤2：检查Nginx服务状态

**在服务器上执行**：
```bash
# 检查Nginx服务状态
sudo systemctl status nginx

# 检查Nginx配置
sudo nginx -t

# 检查Nginx日志
sudo tail -n 50 /var/log/nginx/error.log
```

**预期结果**：
- Nginx状态：`active (running)`
- 配置测试：`syntax is ok` 和 `test is successful`

**如果Nginx未运行**：
```bash
# 启动Nginx
sudo systemctl start nginx

# 检查状态
sudo systemctl status nginx
```

---

### 步骤3：检查端口监听状态

**在服务器上执行**：
```bash
# 检查443端口是否监听
sudo netstat -tlnp | grep :443

# 检查8000端口是否监听
sudo netstat -tlnp | grep :8000
```

**预期结果**：
- 443端口：Nginx正在监听
- 8000端口：FastAPI正在监听

---

### 步骤4：检查防火墙配置

**在服务器上执行**：
```bash
# 检查防火墙状态
sudo ufw status

# 检查443端口是否开放
sudo ufw status | grep 443
```

**预期结果**：
- 443端口：`ALLOW` 或 `443/tcp`

**如果443端口未开放**：
```bash
# 开放443端口
sudo ufw allow 443/tcp

# 重新加载防火墙
sudo ufw reload

# 检查状态
sudo ufw status
```

---

### 步骤5：检查Nginx配置

**在服务器上执行**：
```bash
# 查看Nginx配置
sudo cat /etc/nginx/sites-available/beatsync

# 检查SSL证书路径
sudo ls -la /etc/letsencrypt/live/beatsync.site/
```

**预期结果**：
- 配置文件存在且正确
- SSL证书文件存在

---

### 步骤6：测试本地连接

**在服务器上执行**：
```bash
# 测试本地FastAPI服务
curl http://localhost:8000/api/health

# 测试本地Nginx HTTPS
curl -k https://localhost/api/health
```

**预期结果**：
- 本地FastAPI：返回 `{"status":"healthy"}`
- 本地Nginx HTTPS：返回 `{"status":"healthy"}`

---

### 步骤7：检查SSL证书

**在服务器上执行**：
```bash
# 检查证书文件
sudo ls -la /etc/letsencrypt/live/beatsync.site/

# 检查证书有效期
sudo certbot certificates
```

**预期结果**：
- 证书文件存在：`fullchain.pem` 和 `privkey.pem`
- 证书有效：未过期

---

## 常见问题和解决方案

### 问题1：后端服务未运行

**错误**：`systemctl status beatsync` 显示 `inactive`

**解决**：
```bash
# 启动服务
sudo systemctl start beatsync

# 检查状态
sudo systemctl status beatsync

# 如果启动失败，查看日志
sudo journalctl -u beatsync -n 50 --no-pager
```

---

### 问题2：Nginx配置错误

**错误**：`nginx -t` 显示配置错误

**解决**：
```bash
# 检查配置语法
sudo nginx -t

# 查看详细错误信息
# 根据错误信息修复配置文件

# 重新加载Nginx
sudo systemctl reload nginx
```

---

### 问题3：防火墙未开放443端口

**错误**：`ufw status` 显示443端口未开放

**解决**：
```bash
# 开放443端口
sudo ufw allow 443/tcp

# 重新加载防火墙
sudo ufw reload

# 验证
sudo ufw status | grep 443
```

---

### 问题4：SSL证书配置错误

**错误**：Nginx无法读取SSL证书

**解决**：
```bash
# 检查证书文件权限
sudo ls -la /etc/letsencrypt/live/beatsync.site/

# 检查Nginx配置中的证书路径
sudo grep -r "ssl_certificate" /etc/nginx/sites-available/beatsync

# 如果证书路径错误，修复Nginx配置
```

---

### 问题5：Nginx服务未运行

**错误**：`systemctl status nginx` 显示 `inactive`

**解决**：
```bash
# 启动Nginx
sudo systemctl start nginx

# 检查状态
sudo systemctl status nginx

# 如果启动失败，查看日志
sudo tail -n 50 /var/log/nginx/error.log
```

---

## 一键诊断命令

**在服务器上执行以下命令进行完整诊断**：

```bash
echo "=== 1. 检查后端服务 ==="
sudo systemctl status beatsync --no-pager | head -10

echo ""
echo "=== 2. 检查Nginx服务 ==="
sudo systemctl status nginx --no-pager | head -10

echo ""
echo "=== 3. 检查端口监听 ==="
echo "443端口:"
sudo netstat -tlnp | grep :443
echo "8000端口:"
sudo netstat -tlnp | grep :8000

echo ""
echo "=== 4. 检查防火墙 ==="
sudo ufw status | grep -E "(Status|443)"

echo ""
echo "=== 5. 检查Nginx配置 ==="
sudo nginx -t

echo ""
echo "=== 6. 测试本地连接 ==="
echo "FastAPI本地:"
curl -s http://localhost:8000/api/health || echo "连接失败"
echo ""
echo "Nginx HTTPS本地:"
curl -sk https://localhost/api/health || echo "连接失败"

echo ""
echo "=== 7. 检查SSL证书 ==="
sudo certbot certificates 2>/dev/null | grep -A 5 "beatsync.site" || echo "证书检查失败"
```

---

## 快速修复命令

### 如果服务未运行

```bash
# 启动后端服务
sudo systemctl start beatsync
sudo systemctl enable beatsync

# 启动Nginx服务
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 如果防火墙未开放

```bash
# 开放443端口
sudo ufw allow 443/tcp
sudo ufw reload
```

### 如果Nginx配置错误

```bash
# 检查配置
sudo nginx -t

# 如果配置错误，需要修复配置文件
# 然后重新加载
sudo systemctl reload nginx
```

---

## 验证清单

- [ ] 后端服务正在运行（`systemctl status beatsync`）
- [ ] Nginx服务正在运行（`systemctl status nginx`）
- [ ] 443端口正在监听（`netstat -tlnp | grep :443`）
- [ ] 8000端口正在监听（`netstat -tlnp | grep :8000`）
- [ ] 防火墙已开放443端口（`ufw status | grep 443`）
- [ ] Nginx配置正确（`nginx -t`）
- [ ] SSL证书存在且有效（`certbot certificates`）
- [ ] 本地连接测试成功（`curl http://localhost:8000/api/health`）

---

## 相关文档

- `docs/deployment/SSL_CERTIFICATE_DEPLOYMENT_SUCCESS.md` - SSL证书部署记录
- `docs/deployment/FIX_NGINX_DEFAULT_PAGE.md` - Nginx配置修复

---

**最后更新**：2025-12-04

