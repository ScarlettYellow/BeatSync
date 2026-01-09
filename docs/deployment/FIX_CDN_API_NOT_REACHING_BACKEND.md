# 修复 CDN 导致 API 请求未到达后端问题

> **问题**：线上网页任务一直处于处理状态，但后端日志中没有任何处理记录  
> **原因**：请求可能被 CDN 拦截或代理，未真正到达后端  
> **解决**：检查 CDN 配置并修复回源问题

---

## 问题确认

### 症状

1. **前端**：任务状态一直是 `processing`，output 为 `undefined`
2. **后端日志**：没有任何 `/api/process` 或 `/api/status` 请求记录
3. **CDN 缓存**：已清除（`Cache Miss`），但问题仍存在

### 结论

请求可能被 CDN 拦截或处理，未真正回源到后端。

---

## 立即排查步骤

### 1. 查看后端日志，搜索新任务 ID

```bash
# 搜索任务 ID：961792ee-c3ba-4fe3-8ed1-fa4c4bcda630
sudo journalctl -u beatsync.service --since "10 minutes ago" | grep -E "961792ee|/api/process|/api/status|/api/upload"

# 或查看所有最近的 API 请求
sudo journalctl -u beatsync.service --since "10 minutes ago" | grep "INFO.*api"
```

### 2. 直接访问源站查询任务状态

```bash
# 绕过 CDN，直接访问源站
curl -s -H "Host: beatsync.site" http://124.221.58.149:8000/api/status/961792ee-c3ba-4fe3-8ed1-fa4c4bcda630
```

### 3. 查看 Nginx 访问日志

```bash
# 查看最近的 API 请求
sudo tail -100 /var/log/nginx/access.log | grep -E "/api/process|/api/status|/api/upload"

# 或实时查看
sudo tail -f /var/log/nginx/access.log | grep "/api/"
```

### 4. 检查是否有 ffmpeg 处理进程

```bash
# 查看是否有处理进程
ps aux | grep ffmpeg

# 查看是否有 Python 子进程
ps aux | grep python | grep -v "uvicorn\|grep"
```

---

## 临时解决方案：关闭 CDN

如果急需恢复服务，可以暂时关闭 CDN：

### 方法 1：在 CDN 控制台关闭域名

1. 进入 CDN 控制台 → 域名管理
2. 找到 `beatsync.site`
3. 点击"关闭"

### 方法 2：在 DNSPod 修改 DNS

1. 进入 DNSPod 控制台
2. 删除 CNAME 记录（`@` → `beatsync.site.cdn.dnsv1.com`）
3. 恢复 A 记录（`@` → `124.221.58.149`）
4. 等待 DNS 生效（几分钟）

---

**最后更新**：2025-12-18








