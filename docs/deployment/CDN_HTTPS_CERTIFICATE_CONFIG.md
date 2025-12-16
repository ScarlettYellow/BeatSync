# CDN HTTPS 证书配置指南

> **目标**：在 CDN 控制台配置 HTTPS 证书  
> **证书来源**：使用源站的 Let's Encrypt 证书

---

## 配置步骤

### 步骤 1：从服务器获取证书内容

在服务器上执行以下命令获取证书内容：

```bash
# 1. 获取证书内容（fullchain.pem）
sudo cat /etc/letsencrypt/live/beatsync.site/fullchain.pem

# 2. 获取私钥内容（privkey.pem）
sudo cat /etc/letsencrypt/live/beatsync.site/privkey.pem
```

**注意**：
- 证书内容通常包含多行，需要完整复制
- 私钥内容也需要完整复制
- 确保包含 `-----BEGIN CERTIFICATE-----` 和 `-----END CERTIFICATE-----` 标记

---

### 步骤 2：在 CDN 控制台配置证书

1. **选择证书来源**：
   - 选择 **"新上传证书"** ✅（当前已选择）

2. **填写证书内容**：
   - 在"证书内容"文本框中，粘贴完整的证书内容（fullchain.pem）
   - 格式应该是 PEM 编码，包含：
     ```
     -----BEGIN CERTIFICATE-----
     [证书内容]
     -----END CERTIFICATE-----
     -----BEGIN CERTIFICATE-----
     [中间证书内容]
     -----END CERTIFICATE-----
     ```

3. **填写私钥内容**：
   - 在"私钥内容"文本框中，粘贴完整的私钥内容（privkey.pem）
   - 格式应该是 PEM 编码，包含：
     ```
     -----BEGIN PRIVATE KEY-----
     [私钥内容]
     -----END PRIVATE KEY-----
     ```

4. **填写备注（可选）**：
   - 可以填写：`beatsync.site Let's Encrypt 证书`
   - 或留空

5. **点击"确定"**：
   - 证书将被上传并托管到 SSL 控制台

---

### 步骤 3：开启 HTTPS 服务

1. 在"HTTPS服务"部分
2. 将"配置状态"开关**开启**（从灰色变为蓝色）
3. 等待配置生效（通常几分钟）

---

## 详细操作步骤

### 方法 1：使用 SSH 连接服务器获取证书

```bash
# 连接到服务器
ssh ubuntu@124.221.58.149

# 获取证书内容（完整复制输出）
sudo cat /etc/letsencrypt/live/beatsync.site/fullchain.pem

# 获取私钥内容（完整复制输出）
sudo cat /etc/letsencrypt/live/beatsync.site/privkey.pem
```

### 方法 2：使用 SCP 下载证书文件（推荐）

```bash
# 在本地执行，下载证书文件
scp ubuntu@124.221.58.149:/etc/letsencrypt/live/beatsync.site/fullchain.pem ~/Downloads/
scp ubuntu@124.221.58.149:/etc/letsencrypt/live/beatsync.site/privkey.pem ~/Downloads/

# 然后打开文件复制内容
cat ~/Downloads/fullchain.pem
cat ~/Downloads/privkey.pem
```

---

## 证书内容格式示例

### 证书内容（fullchain.pem）格式

```
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
[更多证书内容...]
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIQCgFBQgAAAVOFc2oLhc...
[中间证书内容...]
-----END CERTIFICATE-----
```

### 私钥内容（privkey.pem）格式

```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
[私钥内容...]
-----END PRIVATE KEY-----
```

---

## 注意事项

### ⚠️ 重要提示

1. **完整复制**：
   - 必须包含 `-----BEGIN` 和 `-----END` 标记
   - 不能遗漏任何行
   - 不能有多余的空格或换行

2. **证书格式**：
   - 必须是 PEM 编码格式
   - 不能是 DER 或其他格式

3. **私钥安全**：
   - 私钥内容敏感，不要在不安全的地方存储
   - 配置完成后，可以删除本地下载的文件

4. **证书有效期**：
   - Let's Encrypt 证书有效期为 90 天
   - 需要定期更新证书（源站会自动更新）
   - CDN 证书也需要同步更新

---

## 验证配置

配置完成后，测试 HTTPS 访问：

```bash
# 测试 CDN HTTPS 访问
curl -I https://beatsync.site/api/health

# 检查证书信息
curl -v https://beatsync.site/api/health 2>&1 | grep -i "certificate\|ssl"
```

**预期结果**：
- 返回 HTTP/2 200
- 证书信息正确
- 浏览器显示 🔒（安全连接）

---

## 证书更新

### 自动更新（推荐）

源站的 Let's Encrypt 证书会自动更新（每 90 天），但 CDN 证书需要手动更新：

1. **在源站证书更新后**（通常自动完成）
2. **重新获取证书内容**：
   ```bash
   sudo cat /etc/letsencrypt/live/beatsync.site/fullchain.pem
   sudo cat /etc/letsencrypt/live/beatsync.site/privkey.pem
   ```
3. **在 CDN 控制台更新证书**：
   - 进入域名配置 → HTTPS配置
   - 点击"配置证书"
   - 更新证书内容和私钥内容

### 设置提醒

建议设置日历提醒，在证书到期前 30 天更新 CDN 证书。

---

## 常见问题

### Q1：证书内容太长，复制不方便怎么办？

A：可以使用 SCP 下载文件，然后在本地打开文件复制内容。

### Q2：证书格式错误怎么办？

A：确保：
- 包含完整的 `-----BEGIN` 和 `-----END` 标记
- 没有多余的空格或换行
- 使用 PEM 编码格式

### Q3：HTTPS 服务开启后仍无法访问？

A：检查：
1. 证书是否正确上传
2. 域名是否正确配置
3. 等待几分钟让配置生效
4. 检查 CDN 状态

### Q4：可以使用腾讯云托管证书吗？

A：可以。如果选择"已托管证书"，需要先在 SSL 控制台申请或上传证书，然后在 CDN 中选择已托管的证书。

---

## 完整配置流程

1. ✅ 从服务器获取证书内容（fullchain.pem 和 privkey.pem）
2. ✅ 在 CDN 控制台填写证书内容
3. ✅ 填写私钥内容
4. ✅ 点击"确定"上传证书
5. ✅ 开启"HTTPS服务"开关
6. ✅ 等待配置生效（几分钟）
7. ✅ 测试 HTTPS 访问

---

**最后更新**：2025-12-16
