# 验证 HTTPS 配置

> **状态**：Nginx 已成功配置 HTTPS，正在监听 443 端口  
> **下一步**：验证 HTTP 跳转、HTTPS 访问，并完成后续配置

---

## ✅ 已完成的配置

- ✅ Nginx 配置已更新（包含 HTTP→HTTPS 跳转和 HTTPS 服务器块）
- ✅ Nginx 配置语法正确
- ✅ Nginx 已重新加载
- ✅ 80 端口正在监听
- ✅ 443 端口正在监听

---

## 验证步骤

### 1. 测试 HTTP 跳转到 HTTPS

```bash
curl -I http://beatsync.site/api/health
```

**预期输出**：
```
HTTP/1.1 301 Moved Permanently
Server: nginx/1.18.0 (Ubuntu)
Date: ...
Location: https://beatsync.site/api/health
...
```

### 2. 测试 HTTPS 访问

```bash
# 测试 HTTPS 连接
curl -I https://beatsync.site/api/health

# 测试 HTTPS 内容
curl https://beatsync.site/api/health
```

**预期输出**：
```
HTTP/2 200
...
{"status":"healthy"}
```

### 3. 检查防火墙（如果 HTTPS 仍无法连接）

```bash
# 检查防火墙状态
sudo ufw status

# 如果防火墙开启，确保 443 端口已开放
sudo ufw allow 443/tcp
sudo ufw reload
```

### 4. 检查腾讯云安全组

**在腾讯云控制台**：
1. 登录腾讯云控制台
2. 进入"云服务器 CVM" → "实例"
3. 找到服务器实例（IP: 124.221.58.149）
4. 点击"安全组" → "修改规则"
5. 检查入站规则是否有：
   - **协议端口**：TCP:443
   - **来源**：0.0.0.0/0
   - **策略**：允许
6. 如果没有，点击"添加规则"添加

---

## 如果 HTTPS 仍无法连接

### 检查 1：端口是否真的在监听

```bash
# 从服务器本地测试
curl -I https://127.0.0.1/api/health -k
# 或
curl -I https://localhost/api/health -k
```

如果本地可以访问，说明是防火墙/安全组问题。

### 检查 2：防火墙规则

```bash
# 查看防火墙规则
sudo ufw status numbered

# 查看 iptables 规则（如果使用）
sudo iptables -L -n | grep 443
```

### 检查 3：腾讯云安全组

确保安全组规则包含：
- **入站规则**：TCP:443，来源 0.0.0.0/0，允许

---

## 下一步：配置后端 CORS

### 找到后端服务

```bash
# 方法 1：查找 systemd 服务
sudo systemctl list-units --type=service | grep -E "beat|python|api|uvicorn|fastapi"

# 方法 2：查找进程
ps aux | grep -E "python|uvicorn|fastapi" | grep -v grep

# 方法 3：查找 supervisor（如果使用）
sudo supervisorctl status

# 方法 4：查找 systemd 服务文件
ls /etc/systemd/system/*.service | grep -E "beat|api|python"
```

### 检查 CORS 环境变量

```bash
# 检查环境变量
env | grep ALLOWED_ORIGINS

# 检查 .env 文件
cat /opt/beatsync/.env 2>/dev/null | grep ALLOWED_ORIGINS
# 或
cat ~/.env 2>/dev/null | grep ALLOWED_ORIGINS
# 或
cat /home/ubuntu/.env 2>/dev/null | grep ALLOWED_ORIGINS
```

### 更新 CORS 配置

根据找到的服务类型，选择相应方法：

#### 方法 1：使用 .env 文件

```bash
# 编辑 .env 文件
sudo nano /opt/beatsync/.env
# 或
sudo nano ~/.env

# 添加或修改：
ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000
```

#### 方法 2：使用 systemd 服务文件

```bash
# 找到服务文件
sudo find /etc/systemd/system -name "*.service" -exec grep -l "beatsync\|fastapi\|uvicorn" {} \;

# 编辑服务文件
sudo nano /etc/systemd/system/<服务名称>.service

# 在 [Service] 部分添加：
Environment="ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000"

# 重新加载并重启
sudo systemctl daemon-reload
sudo systemctl restart <服务名称>
```

#### 方法 3：使用 supervisor

```bash
# 编辑 supervisor 配置
sudo nano /etc/supervisor/conf.d/beatsync.conf

# 在 [program:beatsync] 部分添加：
environment=ALLOWED_ORIGINS="https://beatsync.site,http://localhost:8000"

# 重新加载并重启
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart beatsync
```

### 验证 CORS 配置

```bash
# 测试 CORS 响应头
curl -I -H "Origin: https://beatsync.site" https://beatsync.site/api/health

# 应该看到：
# Access-Control-Allow-Origin: https://beatsync.site
```

---

## 完整验证脚本

```bash
#!/bin/bash
echo "=========================================="
echo "HTTPS 配置验证"
echo "=========================================="
echo ""

echo "1. 测试 HTTP 跳转..."
curl -I http://beatsync.site/api/health 2>&1 | head -5
echo ""

echo "2. 测试 HTTPS 访问..."
curl -I https://beatsync.site/api/health 2>&1 | head -5
echo ""

echo "3. 测试 HTTPS 内容..."
curl https://beatsync.site/api/health 2>&1
echo ""

echo "4. 测试 CORS..."
curl -I -H "Origin: https://beatsync.site" https://beatsync.site/api/health 2>&1 | grep -i "access-control"
echo ""

echo "5. 检查端口监听..."
sudo netstat -tlnp | grep nginx | grep -E ":(80|443)"
echo ""

echo "=========================================="
echo "验证完成"
echo "=========================================="
```

保存为 `verify_https.sh`，然后运行：
```bash
chmod +x verify_https.sh
./verify_https.sh
```

---

**最后更新**：2025-12-16

