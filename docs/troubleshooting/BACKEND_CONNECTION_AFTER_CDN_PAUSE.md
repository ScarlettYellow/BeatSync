# CDN 关闭后后端服务连接问题排查

## 问题现象

CDN 关闭后，网页测试显示"无法连接后端服务"。

## 可能的原因

### 1. CDN 关闭过程中的临时问题

CDN 关闭操作需要时间生效，在这个过渡期间可能出现：
- CDN 节点配置不一致
- 部分请求无法正确转发到源站
- 临时的服务中断

### 2. 后端服务状态问题

需要确认后端服务是否正常运行。

### 3. CORS 配置问题

需要确认后端 CORS 配置是否正确。

## 排查步骤

### 步骤 1: 验证后端服务是否运行（最重要）

在服务器上执行：

```bash
# 检查后端服务状态
sudo systemctl status beatsync.service

# 查看服务日志
sudo journalctl -u beatsync.service -n 50 --no-pager

# 检查服务是否在监听端口
sudo netstat -tlnp | grep 8000
# 或
sudo ss -tlnp | grep 8000
```

**预期结果**：
- 服务状态应该是 `active (running)`
- 应该看到服务在监听 `8000` 端口

### 步骤 2: 在服务器上直接测试后端 API

```bash
# 测试健康检查端点
curl http://localhost:8000/api/health

# 测试通过 Nginx
curl -I http://localhost/api/health

# 测试 HTTPS 通过 Nginx
curl -I -k https://localhost/api/health
```

**预期结果**：
- 应该返回 200 状态码
- 应该看到正常的 JSON 响应或 HTTP 响应头

### 步骤 3: 测试从外部访问（绕过 CDN）

```bash
# 直接访问服务器 IP
curl -I -k -H "Host: beatsync.site" https://124.221.58.149/api/health

# 查看完整响应
curl -k -H "Host: beatsync.site" https://124.221.58.149/api/health
```

**预期结果**：
- 应该返回 200 状态码
- 应该看到正常的 API 响应

### 步骤 3.5: 测试 HTTPS 通过 Nginx（在服务器上）

```bash
# 测试 HTTPS API（通过 Nginx）
curl -I -k https://localhost/api/health

# 或使用 Host 头
curl -I -k -H "Host: beatsync.site" https://localhost/api/health

# 查看完整响应
curl -k https://localhost/api/health
```

**注意**：如果看到 301 重定向，这是正常的（HTTP 到 HTTPS 重定向）。

### 步骤 4: 检查 CORS 配置

在服务器上检查后端服务的 CORS 配置：

```bash
# 查看后端服务配置
sudo systemctl cat beatsync.service | grep -i "ALLOWED_ORIGINS"

# 应该包含以下域名：
# ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000,capacitor://localhost
```

### 步骤 5: 检查 Nginx 配置

```bash
# 验证 Nginx 配置
sudo nginx -t

# 查看 Nginx 状态
sudo systemctl status nginx

# 查看 Nginx 错误日志
sudo tail -n 50 /var/log/nginx/error.log
```

### 步骤 6: 检查浏览器控制台错误

在浏览器中：
1. 打开开发者工具（F12）
2. 切换到 Console 标签
3. 查看是否有错误信息
4. 切换到 Network 标签
5. 刷新页面，查看 API 请求的状态

**常见错误**：
- `CORS policy: No 'Access-Control-Allow-Origin' header` → CORS 配置问题
- `Failed to fetch` → 网络连接问题
- `404 Not Found` → API 路径问题
- `502 Bad Gateway` → 后端服务未运行或 Nginx 配置问题

## 快速诊断命令汇总

在服务器上执行以下命令进行快速诊断：

```bash
# 1. 检查后端服务
echo "=== 后端服务状态 ==="
sudo systemctl status beatsync.service | head -10

# 2. 测试本地 API
echo "=== 本地 API 测试 ==="
curl -s http://localhost:8000/api/health

# 3. 测试通过 Nginx (HTTP)
echo "=== Nginx API 测试 (HTTP) ==="
curl -I http://localhost/api/health

# 3.5. 测试通过 Nginx (HTTPS)
echo "=== Nginx API 测试 (HTTPS) ==="
curl -I -k https://localhost/api/health

# 4. 检查端口监听
echo "=== 端口监听状态 ==="
sudo ss -tlnp | grep 8000

# 5. 查看最近日志
echo "=== 最近日志 ==="
sudo journalctl -u beatsync.service -n 20 --no-pager | tail -10

# 6. 测试从外部直接访问（绕过 CDN）
echo "=== 外部访问测试（绕过 CDN）==="
curl -k -H "Host: beatsync.site" https://124.221.58.149/api/health
```

**注意**：步骤 3 可能返回 301 重定向（HTTP → HTTPS），这是正常的。重点看步骤 3.5 和步骤 6 的结果。

## 可能的问题和解决方案

### 问题 1: 后端服务未运行

**症状**：`systemctl status beatsync.service` 显示 `inactive` 或 `failed`

**解决**：
```bash
# 启动服务
sudo systemctl start beatsync.service

# 如果失败，查看日志
sudo journalctl -u beatsync.service -n 50 --no-pager
```

### 问题 2: CORS 配置缺失

**症状**：浏览器控制台显示 CORS 错误

**解决**：
```bash
# 检查并更新 CORS 配置
sudo systemctl cat beatsync.service | grep ALLOWED_ORIGINS

# 如果需要修改，编辑服务配置
sudo systemctl edit beatsync.service
# 添加：
# [Service]
# Environment="ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000,capacitor://localhost"

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart beatsync.service
```

### 问题 3: Nginx 配置问题

**症状**：访问返回 502 Bad Gateway

**解决**：
```bash
# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -n 50 /var/log/nginx/error.log

# 重启 Nginx
sudo systemctl restart nginx
```

### 问题 4: CDN 关闭过程中的临时问题

**症状**：通过域名访问失败，但直接访问 IP 成功

**说明**：这是正常的，需要等待 CDN 完全关闭

**解决**：
- 等待 30-60 分钟让 CDN 关闭完全生效
- 或临时使用服务器 IP 直接访问（仅用于测试）

## 紧急临时解决方案

如果需要立即恢复服务，可以：

### 方案 1: 重启后端服务

```bash
sudo systemctl restart beatsync.service
sudo systemctl restart nginx
```

### 方案 2: 检查并修复配置

```bash
# 检查所有服务状态
sudo systemctl status beatsync.service nginx

# 查看错误日志
sudo journalctl -u beatsync.service -n 50 --no-pager
sudo tail -n 50 /var/log/nginx/error.log
```

## 验证清单

完成排查后，确认以下各项：

- [ ] 后端服务正在运行（`systemctl status` 显示 `active`）
- [ ] 后端服务监听 8000 端口（`ss -tlnp | grep 8000`）
- [ ] 本地 API 可访问（`curl http://localhost:8000/api/health`）
- [ ] Nginx 可访问（`curl http://localhost/api/health`）
- [ ] CORS 配置正确（包含所需域名）
- [ ] Nginx 配置正确（`nginx -t` 通过）
- [ ] 浏览器控制台无错误

## 下一步

1. **立即执行步骤 1**：在服务器上检查后端服务状态
2. **执行快速诊断命令**：获取完整诊断信息
3. **根据诊断结果**：应用相应的解决方案

## 相关文档

- [CDN 关闭验证清单](../deployment/CDN_VERIFICATION_CHECKLIST.md)
- [CDN 仍在运行的处理](../deployment/CDN_STILL_ACTIVE.md)

---

**最后更新**：2025-12-21






