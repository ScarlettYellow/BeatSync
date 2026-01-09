# CDN 长时间未关闭的问题排查

## 问题现象

CDN 控制台显示"已关闭"，但超过 1 小时后，访问域名时仍然显示 CDN 响应头。

## 可能的原因

### 1. CDN 关闭操作未完全生效

虽然控制台显示"已关闭"，但 CDN 节点可能还在运行。

### 2. DNS 解析仍然指向 CDN

DNS 仍然指向 CDN 的 CNAME 记录，即使 CDN 关闭，DNS 也需要时间来更新。

### 3. 本地或运营商 DNS 缓存

本地或运营商的 DNS 服务器缓存了旧的解析记录。

### 4. CDN 节点配置延迟

某些 CDN 节点可能需要更长时间才能完全关闭。

## 详细排查步骤

### 步骤 1: 再次确认 CDN 控制台状态

1. 登录腾讯云 CDN 控制台
2. 进入"域名管理"页面
3. 确认 `beatsync.site` 的状态：
   - 如果显示"已关闭" → 继续下一步
   - 如果显示"已启动"或"部署中" → **需要重新关闭**

### 步骤 2: 检查 DNS 解析

```bash
# 查看当前 DNS 解析
nslookup beatsync.site

# 或使用 dig 查看详细信息
dig beatsync.site

# 查看 CNAME 记录
dig beatsync.site CNAME
```

**预期结果分析**：
- 如果解析到 `beatsync.site.cdn.dnsv1.com` → DNS 仍然指向 CDN（正常）
- 如果解析到服务器 IP（124.221.58.149）→ DNS 已更新

### 步骤 3: 测试不同位置的访问

```bash
# 1. 通过域名访问（可能经过 CDN）
curl -I -k https://beatsync.site/ | grep -i "server"

# 2. 直接访问服务器 IP（绕过 CDN）
curl -I -k -H "Host: beatsync.site" https://124.221.58.149/ | grep -i "server"

# 3. 使用不同的 DNS 服务器测试
# 使用 Google DNS
dig @8.8.8.8 beatsync.site

# 使用 Cloudflare DNS
dig @1.1.1.1 beatsync.site
```

### 步骤 4: 检查完整响应头

```bash
# 查看完整响应头
curl -I -k https://beatsync.site/

# 重点关注：
# - Server: Lego Server（CDN）
# - Server: nginx/1.18.0 (Ubuntu)（源站）
# - X-NWS-LOG-UUID（CDN 标识）
# - X-Cache-Lookup（CDN 缓存标识）
```

### 步骤 5: 清除本地 DNS 缓存

```bash
# macOS
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Linux
sudo systemd-resolve --flush-caches
# 或
sudo service network-manager restart

# Windows
ipconfig /flushdns
```

## 解决方案

### 方案 1: 等待更长时间（如果确认控制台已关闭）

某些 CDN 节点可能需要更长时间（2-4 小时）才能完全关闭。

**建议**：
- 再等待 1-2 小时
- 每隔 30 分钟验证一次

### 方案 2: 删除并重新配置 CDN（如果控制台未真正关闭）

如果 CDN 控制台状态异常：

1. **删除 CDN 配置**（谨慎操作）：
   - 登录腾讯云 CDN 控制台
   - 找到 `beatsync.site`
   - 点击"删除"按钮
   - 确认删除操作

2. **重新配置（如果以后需要）**：
   - 重新添加域名
   - 配置源站和缓存规则

**⚠️ 注意**：删除 CDN 配置后，DNS 需要更新。如果 DNS 仍指向 CDN 的 CNAME，需要修改 DNS 解析。

### 方案 3: 修改 DNS 解析（改为直接指向源站）

如果 CDN 长时间未关闭，可以改为直接指向源站：

1. **登录域名注册商或 DNS 服务商控制台**

2. **修改 DNS 记录**：
   - **类型**：CNAME → A 记录
   - **主机记录**：@（或空）
   - **记录值**：124.221.58.149（服务器 IP）
   - **TTL**：600（10 分钟）

3. **等待 DNS 生效**（通常 5-10 分钟）

4. **验证**：
   ```bash
   # DNS 应该解析到服务器 IP
   nslookup beatsync.site
   
   # 访问应该显示源站
   curl -I -k https://beatsync.site/ | grep -i "server"
   ```

**优点**：
- 完全绕过 CDN
- 直接访问源站

**缺点**：
- 需要修改 DNS 配置
- 如果以后重新启用 CDN，需要再次修改 DNS

## 推荐的行动方案

### 立即执行

1. **再次确认 CDN 控制台状态**
   - 登录控制台
   - 确认是否真的显示"已关闭"

2. **检查 DNS 解析**
   ```bash
   dig beatsync.site
   ```

3. **查看完整响应头**
   ```bash
   curl -I -k https://beatsync.site/
   ```

4. **清除本地 DNS 缓存**
   ```bash
   sudo dscacheutil -flushcache
   sudo killall -HUP mDNSResponder
   ```

### 如果 2 小时后仍未生效

**选项 A**：修改 DNS 为 A 记录（直接指向源站）
- 优点：立即生效，完全绕过 CDN
- 缺点：需要修改 DNS，以后启用 CDN 需要再次修改

**选项 B**：联系腾讯云技术支持
- 提供域名：`beatsync.site`
- 说明情况：控制台显示已关闭，但访问仍显示 CDN

## 验证命令汇总

```bash
# 1. 检查 CDN 控制台状态
# 手动登录控制台检查

# 2. 检查 DNS 解析
dig beatsync.site
dig beatsync.site CNAME

# 3. 测试访问（通过域名）
curl -I -k https://beatsync.site/ | grep -i "server"

# 4. 测试访问（直接 IP）
curl -I -k -H "Host: beatsync.site" https://124.221.58.149/ | grep -i "server"

# 5. 使用不同 DNS 测试
dig @8.8.8.8 beatsync.site

# 6. 清除本地 DNS 缓存
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

## 当前状态

- **等待时间**：已超过 1 小时
- **CDN 控制台**：显示"已关闭"
- **访问响应**：仍显示 CDN（`Server: Lego Server`）
- **源站服务器**：正常工作（已验证）

## 下一步

1. **执行上述排查步骤**
2. **如果确认控制台已关闭但超过 2 小时仍未生效**：
   - 建议修改 DNS 为 A 记录直接指向源站
   - 或联系腾讯云技术支持

## 相关文档

- [CDN 关闭验证清单](../deployment/CDN_VERIFICATION_CHECKLIST.md)
- [CDN 关闭后的 DNS 配置](../deployment/CDN_DNS_CONFIGURATION.md)

---

**最后更新**：2025-12-21






