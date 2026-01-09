# SSL 证书自动续期配置完成

> **日期**：2025-12-18  
> **状态**：✅ 已配置完成并测试通过

---

## 配置概览

### 当前证书状态

- **域名**：`beatsync.site`
- **颁发机构**：Let's Encrypt
- **证书类型**：ECDSA
- **当前有效期**：2026-03-04（还有 75 天）
- **证书路径**：`/etc/letsencrypt/live/beatsync.site/fullchain.pem`
- **私钥路径**：`/etc/letsencrypt/live/beatsync.site/privkey.pem`

### 自动续期配置

- **安装方式**：snap（certbot 5.2.2）
- **定时任务**：`snap.certbot.renew.timer`
- **检查频率**：每天 2 次（凌晨 02:36）
- **续期时机**：证书到期前 30 天
- **下次检查**：2025-12-19 02:36

---

## 自动续期工作流程

```
1. 每天凌晨 02:36，snap.certbot.renew.timer 触发
   ↓
2. certbot 检查证书是否需要续期（距离到期 < 30 天）
   ↓
3. 如果需要续期：
   - 向 Let's Encrypt 请求新证书
   - 验证域名所有权（HTTP-01 或 DNS-01）
   - 下载并安装新证书
   ↓
4. 执行 renewal-hooks/deploy/ 中的脚本
   - reload-nginx.sh: 重启 Nginx 以加载新证书
   - 记录日志到 /var/log/certbot-nginx-reload.log
   ↓
5. 续期完成，服务继续运行
```

---

## 配置文件

### 1. Systemd Timer

```bash
# 查看 timer 状态
sudo systemctl status snap.certbot.renew.timer

# 查看下次运行时间
sudo systemctl list-timers | grep certbot
```

### 2. Renewal Hook 脚本

**位置**：`/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh`

```bash
#!/bin/bash
# 续期成功后重启 Nginx
systemctl reload nginx
echo "$(date): Nginx reloaded after certificate renewal" >> /var/log/certbot-nginx-reload.log
```

**权限**：`-rwxr-xr-x`（可执行）

### 3. Nginx 配置

**位置**：`/etc/nginx/sites-available/beatsync`

```nginx
server {
    listen 443 ssl http2;
    server_name beatsync.site;

    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # ... 其他配置
}
```

---

## 验证和测试

### 测试续期（模拟，不会真的续期）

```bash
sudo certbot renew --dry-run
```

**预期输出**：
```
Congratulations, all simulated renewals succeeded:
/etc/letsencrypt/live/beatsync.site/fullchain.pem (success)
```

### 查看证书信息

```bash
sudo certbot certificates
```

### 查看续期日志

```bash
# certbot 主日志
sudo tail -100 /var/log/letsencrypt/letsencrypt.log

# Nginx 重启日志（续期后才会有）
sudo cat /var/log/certbot-nginx-reload.log
```

### 查看 timer 状态

```bash
# 查看所有 timer
sudo systemctl list-timers

# 查看 certbot timer
sudo systemctl list-timers | grep certbot

# 查看详细状态
sudo systemctl status snap.certbot.renew.timer
```

---

## 预期时间线

| 日期 | 事件 | 说明 |
|------|------|------|
| 2025-12-18 | ✅ 配置完成 | 自动续期已启用 |
| 每天 02:36 | 🔄 自动检查 | 检查是否需要续期（< 30 天） |
| 2026-02-02 左右 | 🔄 开始续期 | 提前 30 天自动续期 |
| 2026-03-04 | 📅 原证书到期 | 但早已自动续期，无需担心 |
| 2026-06-02 左右 | 🔄 下次续期 | 新证书到期前 30 天再次续期 |

---

## 监控和维护

### 每月检查（推荐）

```bash
# 1. 检查证书有效期
sudo certbot certificates

# 2. 查看 timer 状态
sudo systemctl list-timers | grep certbot

# 3. 测试续期功能
sudo certbot renew --dry-run

# 4. 查看最近的日志
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

### 监控脚本（可选）

创建一个监控脚本：

```bash
#!/bin/bash
# /root/scripts/check-ssl.sh

echo "=========================================="
echo "SSL 证书检查 - $(date)"
echo "=========================================="
echo ""

# 1. 证书有效期
echo "1. 证书信息："
certbot certificates 2>&1 | grep -A 5 "beatsync.site"
echo ""

# 2. Timer 状态
echo "2. 自动续期 Timer："
systemctl list-timers | grep certbot
echo ""

# 3. 最近的续期尝试
echo "3. 最近的日志（最后 10 行）："
tail -10 /var/log/letsencrypt/letsencrypt.log
echo ""

# 4. Nginx 重启日志
if [ -f /var/log/certbot-nginx-reload.log ]; then
    echo "4. Nginx 重启记录："
    cat /var/log/certbot-nginx-reload.log
else
    echo "4. Nginx 重启记录：尚无记录（等待首次续期）"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
```

添加到 cron，每周发送报告：

```bash
# 每周日早上 8 点检查并发送邮件
0 8 * * 0 /root/scripts/check-ssl.sh | mail -s "SSL证书检查报告" your-email@example.com
```

---

## 故障排查

### 问题 1：续期失败

**症状**：证书即将到期，但自动续期失败

**排查步骤**：

1. **查看日志**
   ```bash
   sudo tail -100 /var/log/letsencrypt/letsencrypt.log
   ```

2. **检查网络连接**
   ```bash
   curl -I https://acme-v02.api.letsencrypt.org/directory
   ```

3. **检查 80 端口是否开放**（用于 HTTP-01 验证）
   ```bash
   sudo netstat -tlnp | grep :80
   curl -I http://beatsync.site/.well-known/acme-challenge/test
   ```

4. **手动续期**
   ```bash
   sudo certbot renew --force-renewal
   ```

### 问题 2：Nginx 未自动重启

**症状**：证书已续期，但 Nginx 仍使用旧证书

**排查步骤**：

1. **检查 hook 脚本**
   ```bash
   ls -l /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
   sudo cat /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
   ```

2. **检查日志**
   ```bash
   sudo cat /var/log/certbot-nginx-reload.log
   ```

3. **手动重启 Nginx**
   ```bash
   sudo systemctl reload nginx
   ```

4. **测试 hook**
   ```bash
   sudo /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
   ```

### 问题 3：Timer 未运行

**症状**：`systemctl list-timers` 中看不到 certbot timer

**解决方案**：

```bash
# 启用并启动 timer
sudo systemctl enable snap.certbot.renew.timer
sudo systemctl start snap.certbot.renew.timer

# 验证
sudo systemctl status snap.certbot.renew.timer
```

---

## 手动操作

### 手动续期（如果自动续期失败）

```bash
# 强制续期（即使还没到期）
sudo certbot renew --force-renewal

# 续期后重启 Nginx
sudo systemctl reload nginx
```

### 临时禁用自动续期

```bash
# 停止 timer
sudo systemctl stop snap.certbot.renew.timer

# 禁用 timer（开机不自动启动）
sudo systemctl disable snap.certbot.renew.timer
```

### 重新启用自动续期

```bash
# 启用并启动 timer
sudo systemctl enable snap.certbot.renew.timer
sudo systemctl start snap.certbot.renew.timer
```

---

## 安全建议

### 1. 备份证书

```bash
# 定期备份证书目录
sudo tar -czf ~/backups/letsencrypt-$(date +%Y%m%d).tar.gz /etc/letsencrypt/

# 或使用 rsync
sudo rsync -av /etc/letsencrypt/ ~/backups/letsencrypt/
```

### 2. 监控到期时间

设置告警：如果证书到期时间 < 15 天，发送紧急通知。

### 3. 保持系统更新

```bash
# 更新 snap 包
sudo snap refresh certbot

# 查看版本
certbot --version
```

---

## 相关文档

- [CDN_API_CACHE_ISSUE_RESOLVED.md](./CDN_API_CACHE_ISSUE_RESOLVED.md) - CDN 缓存问题解决
- [ADD_NGINX_NO_CACHE_HEADERS.md](./ADD_NGINX_NO_CACHE_HEADERS.md) - Nginx 禁止缓存配置
- [DOMAIN_MIGRATION_COMPLETE.md](./DOMAIN_MIGRATION_COMPLETE.md) - 域名迁移完成
- [VERIFY_HTTPS_SETUP.md](./VERIFY_HTTPS_SETUP.md) - HTTPS 设置验证

---

## 总结

✅ **自动续期已完全配置并测试通过**

- 每天自动检查 2 次
- 提前 30 天自动续期
- 续期后自动重启 Nginx
- 完整的日志记录

**无需手动干预，证书将永久保持有效！**

---

**最后更新**：2025-12-18  
**配置状态**：✅ 已完成  
**测试状态**：✅ 通过








