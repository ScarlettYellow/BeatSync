# 完成 CORS 配置

> **当前状态**：CORS 配置已生效，但显示 `access-control-allow-origin: *`（允许所有来源）  
> **目标**：限制为具体域名 `https://beatsync.site`，提高安全性

---

## 当前状态

✅ CORS 配置已生效：
- `access-control-allow-origin: *` - 允许所有来源
- `access-control-allow-credentials: true` - 允许携带凭证
- HTTPS 连接正常（HTTP/2 200）

⚠️ 安全建议：将 `*` 改为具体域名 `https://beatsync.site`

---

## 检查后端服务状态

### 1. 找到后端服务

```bash
# 查找所有相关服务
sudo systemctl list-units --type=service | grep -E "beat|python|api|uvicorn|fastapi"

# 查找进程
ps aux | grep -E "python|uvicorn|fastapi" | grep -v grep

# 查找 supervisor（如果使用）
sudo supervisorctl status
```

### 2. 检查环境变量是否已加载

```bash
# 检查 .env 文件内容
cat /opt/beatsync/.env | grep ALLOWED_ORIGINS

# 应该看到：
# ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000
```

### 3. 重启后端服务

根据找到的服务类型，选择相应方法：

#### 方法 1：systemd 服务

```bash
# 找到服务名称（例如：beatsync-api.service）
sudo systemctl restart <服务名称>

# 检查服务状态
sudo systemctl status <服务名称>
```

#### 方法 2：supervisor

```bash
sudo supervisorctl restart <服务名称>
sudo supervisorctl status
```

#### 方法 3：直接运行的进程

```bash
# 找到进程 ID
ps aux | grep -E "python|uvicorn|fastapi" | grep -v grep

# 重启（根据实际启动方式）
# 如果使用 screen/tmux，进入会话重启
# 如果使用 nohup，需要找到进程并重启
```

---

## 验证 CORS 配置更新

重启后端服务后，再次测试：

```bash
# 测试 CORS 响应头
curl -I -H "Origin: https://beatsync.site" https://beatsync.site/api/health
```

**预期输出**（如果配置正确）：
```
HTTP/2 200
...
access-control-allow-origin: https://beatsync.site
access-control-allow-credentials: true
```

**如果仍然显示 `*`**，可能原因：
1. 环境变量未正确加载
2. 后端代码中使用了默认值 `*`
3. 需要检查后端代码的 CORS 配置逻辑

---

## 检查后端代码 CORS 配置

如果重启后仍显示 `*`，检查后端代码：

```bash
# 查看后端 main.py 中的 CORS 配置
cat /opt/beatsync/web_service/backend/main.py | grep -A 10 "CORS\|allowed_origins"
```

**后端代码应该类似**：
```python
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"]:
    allow_origins_list = ["*"]
else:
    allow_origins_list = [origin.strip() for origin in allowed_origins]
```

**如果环境变量未正确读取**，可能需要：
1. 检查 `.env` 文件路径是否正确
2. 检查后端代码如何加载 `.env` 文件
3. 可能需要使用 `python-dotenv` 库加载 `.env` 文件

---

## 如果使用 `*` 也可以接受

如果当前配置使用 `*` 且功能正常，也可以暂时保持。但建议：

1. **生产环境**：限制为具体域名（更安全）
2. **开发环境**：可以使用 `*`（方便开发）

---

## 完整验证清单

完成所有配置后，验证以下项目：

### HTTPS 配置
- [x] Nginx 监听 443 端口
- [x] HTTP 自动跳转到 HTTPS
- [x] HTTPS 可以正常访问
- [x] SSL 证书有效

### CORS 配置
- [x] CORS 响应头存在
- [ ] CORS 限制为具体域名（可选，更安全）
- [x] 允许携带凭证

### 功能测试
- [ ] Web 端可以正常访问 `https://beatsync.site`
- [ ] 可以上传文件
- [ ] 可以处理任务
- [ ] 可以下载结果

---

## 下一步

1. **重启后端服务**（如果还未重启）
2. **验证 CORS 配置**（确认是否限制为具体域名）
3. **测试完整功能**（上传、处理、下载）
4. **配置 CDN**（可选，提升下载速度）

---

**最后更新**：2025-12-16
