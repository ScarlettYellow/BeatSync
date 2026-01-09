# CDN API 缓存问题解决方案

> **日期**：2025-12-18  
> **状态**：✅ 已解决

---

## 问题描述

### 症状
- 线上网页（`https://app.beatsync.site`）提交任务后，状态一直显示 "processing"
- 等待 5 分钟以上仍无法完成
- 本地测试同样的任务只需 15 秒

### 根本原因
1. **CDN 缓存了 API 响应**
   - 首次 `/api/status` 请求返回 "processing" 状态
   - 这个响应被 CDN 缓存了
   - 前端后续轮询都从 CDN 缓存获取，而不是访问源站
   - 源站任务已完成，但 CDN 仍返回缓存的 "processing" 状态

2. **CDN 配置不完善**
   - 虽然在 CDN 控制台配置了"不缓存 API"规则
   - 但源站（Nginx）没有返回 `Cache-Control: no-cache` 头
   - CDN 可能仍使用默认缓存策略

---

## 解决方案

### 1. 修改 Nginx 配置

在 Nginx 配置中为 `/api/` 路径添加禁止缓存头：

```nginx
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
```

**关键点**：
- 删除了单独的 `location /api/health` 块
- 让所有 `/api/*` 路径使用统一的配置
- 添加了三个禁止缓存的响应头

### 2. 刷新 CDN 缓存

- **目录刷新**：`https://beatsync.site/api/`
- **刷新方式**：刷新全部资源

### 3. 清除浏览器缓存

- 强制刷新：`Cmd + Shift + R`（macOS）或 `Ctrl + Shift + R`（Windows/Linux）

---

## 验证步骤

### 1. 验证 Nginx 配置生效

```bash
# 在服务器上执行
curl -I -k https://127.0.0.1/api/health

# 应该看到：
# cache-control: no-cache, no-store, must-revalidate
# pragma: no-cache
# expires: 0
```

### 2. 验证 CDN 行为

```bash
# 通过 CDN 访问
curl -I https://beatsync.site/api/health

# CDN 应该遵守 Cache-Control 指令，不缓存响应
```

### 3. 验证功能

1. 访问 `https://app.beatsync.site`
2. 上传测试文件
3. 提交任务
4. 观察状态实时更新
5. 确认任务正常完成

---

## 技术细节

### Nginx location 匹配优先级

Nginx 会优先匹配更具体的路径：
- `location /api/health` > `location /api/` > `location /`
- 因此需要确保没有更具体的 location 覆盖通用配置

### Cache-Control 头说明

- `no-cache`：缓存前必须向源站验证
- `no-store`：完全不缓存
- `must-revalidate`：过期后必须重新验证
- `Pragma: no-cache`：HTTP/1.0 兼容
- `Expires: 0`：立即过期

### CDN 缓存策略

即使在 CDN 控制台配置了"不缓存"规则，仍建议在源站设置 `Cache-Control` 头：
1. **多层防护**：CDN 配置可能失效或被覆盖
2. **标准兼容**：遵循 HTTP 缓存标准
3. **中间代理**：其他中间代理也会遵守这些头

---

## 完整的 Nginx 配置文件

```nginx
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
}
```

---

## 后续监控

### 日常监控项

1. **API 响应时间**
   ```bash
   curl -w "\nTime: %{time_total}s\n" https://beatsync.site/api/health
   ```

2. **CDN 缓存行为**
   ```bash
   curl -I https://beatsync.site/api/status/<task_id> | grep "X-Cache-Lookup"
   ```

3. **Nginx 日志**
   ```bash
   sudo tail -f /var/log/nginx/access.log | grep "/api/"
   ```

### 定期检查（每月）

- [ ] SSL 证书到期时间（提前 30 天续期）
- [ ] CDN 流量使用情况
- [ ] 后端服务日志（是否有异常）
- [ ] Nginx 配置文件备份

---

## 经验总结

### ✅ 最佳实践

1. **API 永远不要缓存**：动态内容必须实时获取
2. **多层防护**：CDN 规则 + Nginx 头 + 后端头
3. **充分测试**：本地测试 → 源站测试 → CDN 测试
4. **完善日志**：保留足够的日志便于排查

### ⚠️ 注意事项

1. **CDN 刷新有延迟**：通常 1-5 分钟生效
2. **浏览器缓存**：用户可能需要强制刷新
3. **配置优先级**：Nginx location 匹配规则很重要
4. **SSL 证书续期**：提前 30 天，避免服务中断

### 🔧 排查流程

遇到类似问题时：
1. 先检查后端是否正常（直接访问源站）
2. 查看 Nginx 日志（请求是否到达）
3. 测试 CDN 缓存（`X-Cache-Lookup` 头）
4. 检查 Nginx 配置（响应头是否正确）
5. 刷新 CDN 缓存
6. 清除浏览器缓存

---

**最后更新**：2025-12-18  
**问题状态**：✅ 已解决  
**测试状态**：✅ 功能正常








