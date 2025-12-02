# HTTPS配置分步执行指南

> **目的**：配置Nginx反向代理 + 自签名SSL证书，解决Mixed Content错误

---

## 步骤1：安装Nginx

**目的**：安装Nginx作为反向代理服务器

```bash
sudo apt update
sudo apt install -y nginx
```

**验证**：
```bash
nginx -v
```

**预期输出**：显示Nginx版本号（如：nginx version: nginx/1.18.0）

---

## 步骤2：生成SSL证书

**目的**：生成自签名SSL证书用于HTTPS

```bash
# 创建SSL证书目录
sudo mkdir -p /etc/nginx/ssl

# 生成自签名证书（有效期1年）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=124.221.58.149"
```

**验证**：
```bash
ls -la /etc/nginx/ssl/
```

**预期输出**：应该显示 `beatsync.key` 和 `beatsync.crt` 两个文件

---

## 步骤3：创建Nginx配置文件

**目的**：配置Nginx反向代理和HTTPS

```bash
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name 124.221.58.149;
    
    # HTTP重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 124.221.58.149;

    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;
    
    # SSL配置（提高安全性）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 文件上传大小限制（1GB）
    client_max_body_size 1G;

    # 反向代理到后端服务
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOFNGINX
```

**验证**：
```bash
cat /etc/nginx/sites-available/beatsync
```

**预期输出**：应该显示完整的Nginx配置内容

---

## 步骤4：启用Nginx配置

**目的**：启用beatsync配置，禁用默认配置

```bash
# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/

# 删除默认配置（如果存在）
sudo rm -f /etc/nginx/sites-enabled/default
```

**验证**：
```bash
ls -la /etc/nginx/sites-enabled/
```

**预期输出**：应该显示 `beatsync` 符号链接

---

## 步骤5：测试Nginx配置

**目的**：检查Nginx配置文件是否有语法错误

```bash
sudo nginx -t
```

**预期输出**：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**如果测试失败，检查错误信息并修复**

---

## 步骤6：启动Nginx服务

**目的**：启动并启用Nginx服务

```bash
# 启动Nginx
sudo systemctl start nginx

# 设置开机自启
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

**预期输出**：应该显示 `active (running)`

**如果启动失败，查看日志**：
```bash
sudo journalctl -u nginx -n 50
```

---

## 步骤7：配置系统防火墙（UFW）

**目的**：开放443端口（如果UFW已启用）

```bash
# 检查UFW状态
sudo ufw status
```

**如果UFW已启用，执行**：
```bash
# 开放443端口
sudo ufw allow 443/tcp

# 重新加载
sudo ufw reload

# 验证
sudo ufw status | grep 443
```

**预期输出**：应该显示 `443/tcp ALLOW Anywhere`

**如果UFW未启用，跳过此步骤，直接执行步骤8**

---

## 步骤8：配置腾讯云防火墙（重要）

**目的**：在腾讯云控制台开放443端口

**操作步骤**：

1. **登录腾讯云控制台**
   - 访问：https://console.cloud.tencent.com/
   - 使用您的账号登录

2. **进入轻量应用服务器**
   - 左侧菜单 → "轻量应用服务器"（Lighthouse）
   - 找到实例：`124.221.58.149`

3. **配置防火墙**
   - 点击实例名称进入详情页
   - 点击"防火墙"标签
   - 点击"添加规则"按钮
   - 填写规则：
     - **应用类型**：自定义
     - **协议**：TCP
     - **端口**：443
     - **策略**：允许
     - **来源**：0.0.0.0/0
   - 点击"确定"

4. **验证规则**
   - 应该看到新添加的规则
   - 状态应该是"已启用"

---

## 步骤9：验证HTTPS配置

**目的**：测试HTTPS是否正常工作

### 在服务器上测试

```bash
# 测试HTTPS访问
curl -k https://124.221.58.149/api/health
```

**预期输出**：
```json
{"status":"healthy","timestamp":"2025-12-02T14:13:43.048160"}
```

### 在浏览器中测试

**访问**：
- `https://124.221.58.149/api/health`
- `https://124.221.58.149/docs`

**注意**：浏览器会显示"不安全"警告（因为是自签名证书），点击"高级" → "继续访问"即可。

---

## 故障排查

### 如果步骤5（测试配置）失败

**查看错误信息**：
```bash
sudo nginx -t
```

**常见错误**：
1. **证书文件不存在**：返回步骤2，确保证书已生成
2. **语法错误**：检查配置文件格式
3. **端口被占用**：检查是否有其他服务占用443端口

---

### 如果步骤6（启动Nginx）失败

**查看日志**：
```bash
sudo journalctl -u nginx -n 50
```

**常见错误**：
1. **端口被占用**：
   ```bash
   sudo lsof -i :443
   # 如果有输出，停止占用进程
   ```

2. **证书文件权限问题**：
   ```bash
   sudo chmod 600 /etc/nginx/ssl/beatsync.key
   sudo chmod 644 /etc/nginx/ssl/beatsync.crt
   ```

3. **配置文件错误**：返回步骤3，检查配置

---

### 如果步骤9（验证）失败

**检查Nginx状态**：
```bash
sudo systemctl status nginx
```

**检查端口监听**：
```bash
sudo netstat -tlnp | grep 443
```

**检查防火墙**：
- 确认腾讯云防火墙已开放443端口
- 确认UFW已开放443端口（如果启用）

**查看Nginx错误日志**：
```bash
sudo tail -f /var/log/nginx/error.log
```

---

## 完整验证清单

- [ ] 步骤1：Nginx已安装
- [ ] 步骤2：SSL证书已生成
- [ ] 步骤3：Nginx配置文件已创建
- [ ] 步骤4：配置已启用
- [ ] 步骤5：配置测试通过
- [ ] 步骤6：Nginx服务运行正常
- [ ] 步骤7：UFW已配置（如果启用）
- [ ] 步骤8：腾讯云防火墙已配置（443端口）
- [ ] 步骤9：HTTPS访问正常

---

## 快速参考命令

**如果某个步骤失败，可以单独重新执行**：

```bash
# 重新生成证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=124.221.58.149"

# 重新测试配置
sudo nginx -t

# 重新加载配置（不重启服务）
sudo nginx -s reload

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx状态
sudo systemctl status nginx

# 查看Nginx日志
sudo journalctl -u nginx -f
```

---

**最后更新**：2025-12-02

