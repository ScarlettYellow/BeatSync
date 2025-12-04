# 验证DNS配置

> **域名**：beatsync.site  
> **检查日期**：2025-12-03

---

## DNS配置检查

### 当前配置

从截图看到：
- ✅ **主机记录**：`@`（主域名，正确）
- ✅ **记录类型**：`A`（正确）
- ✅ **线路类型**：`默认`（正确）
- ✅ **记录值**：`124.221.58.149`（正确，与服务器IP匹配）
- ✅ **TTL**：`600`（正确，10分钟）

**结论**：✅ **DNS配置完全正确！**

---

## 验证DNS解析

### 方法1：使用nslookup（推荐）

**在本地终端执行**：
```bash
nslookup beatsync.site
```

**预期结果**：
```
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	beatsync.site
Address: 124.221.58.149
```

**如果返回 `124.221.58.149`**：✅ DNS解析已生效

**如果返回其他IP或无法解析**：⏳ DNS解析还未生效，请等待几分钟到几小时

---

### 方法2：使用dig（如果已安装）

**在本地终端执行**：
```bash
dig beatsync.site +short
```

**预期结果**：
```
124.221.58.149
```

---

### 方法3：使用ping

**在本地终端执行**：
```bash
ping beatsync.site
```

**预期结果**：
```
PING beatsync.site (124.221.58.149): 56 data bytes
```

---

### 方法4：在线DNS检查工具

**访问在线工具**：
- https://dnschecker.org/
- https://www.whatsmydns.net/

**输入域名**：`beatsync.site`

**检查结果**：应该显示 `124.221.58.149`

---

## DNS生效时间

### 通常情况
- **本地DNS缓存**：几分钟
- **全球DNS传播**：几分钟到几小时
- **最长**：24-48小时（极端情况）

### 加速DNS生效

**清除本地DNS缓存**：

**macOS**：
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Windows**：
```bash
ipconfig /flushdns
```

**Linux**：
```bash
sudo systemd-resolve --flush-caches
```

---

## 下一步操作

### 如果DNS解析已生效

**可以继续申请SSL证书**：

```bash
# 在服务器上执行
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d beatsync.site
```

---

### 如果DNS解析还未生效

**请等待**：
1. 等待几分钟到几小时
2. 定期检查DNS解析（使用上面的命令）
3. 确认解析生效后再申请证书

---

## 常见问题

### 问题1：DNS解析返回其他IP

**可能原因**：
- DNS缓存未更新
- DNS传播未完成

**解决方法**：
- 清除本地DNS缓存
- 等待DNS传播完成
- 使用不同的DNS服务器检查（如8.8.8.8）

---

### 问题2：DNS解析返回空或错误

**可能原因**：
- DNS配置错误
- DNS服务器问题

**解决方法**：
- 检查DNS配置是否正确
- 确认记录值是否为 `124.221.58.149`
- 联系域名服务商

---

### 问题3：部分地区DNS未生效

**可能原因**：
- DNS全球传播需要时间
- 不同DNS服务器更新速度不同

**解决方法**：
- 等待DNS全球传播（通常几小时）
- 使用在线DNS检查工具查看全球DNS状态

---

## 验证清单

- [ ] DNS配置正确（主机记录：@，记录类型：A，记录值：124.221.58.149）
- [ ] DNS解析已生效（`nslookup beatsync.site`返回`124.221.58.149`）
- [ ] 可以ping通域名（`ping beatsync.site`）
- [ ] 准备申请SSL证书

---

**最后更新**：2025-12-03

