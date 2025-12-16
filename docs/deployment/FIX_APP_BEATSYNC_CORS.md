# 修复 app.beatsync.site CORS 问题

> **问题**：`https://app.beatsync.site/` 无法连接后端  
> **原因**：后端 CORS 配置未允许 `app.beatsync.site` 域名  
> **解决**：在后端 CORS 配置中添加 `https://app.beatsync.site`

---

## 问题分析

### 错误信息

```
Access to fetch at 'https://beatsync.site/api/health' 
from origin 'https://app.beatsync.site' 
has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 问题原因

1. **前端域名**：`https://app.beatsync.site`
2. **后端域名**：`https://beatsync.site`
3. **CORS 配置**：后端只允许了 `https://beatsync.site`，没有允许 `https://app.beatsync.site`

---

## 解决方案

### 步骤 1：更新后端 CORS 配置

在服务器上执行：

```bash
# 1. 检查当前 CORS 配置
echo $ALLOWED_ORIGINS

# 或检查 .env 文件
cat /opt/beatsync/.env | grep ALLOWED_ORIGINS
```

### 步骤 2：修改环境变量

#### 方法 1：修改 .env 文件

```bash
# 编辑 .env 文件
sudo nano /opt/beatsync/.env

# 修改或添加：
ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000
```

#### 方法 2：修改 systemd 服务文件

```bash
# 编辑服务文件
sudo nano /etc/systemd/system/beatsync.service

# 在 [Service] 部分，修改 Environment 行：
Environment="ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000"
```

### 步骤 3：重启后端服务

```bash
# 如果使用 systemd
sudo systemctl daemon-reload
sudo systemctl restart beatsync.service

# 检查服务状态
sudo systemctl status beatsync.service
```

### 步骤 4：验证 CORS 配置

```bash
# 测试 CORS 响应头（从 app.beatsync.site 访问）
curl -I -H "Origin: https://app.beatsync.site" https://beatsync.site/api/health

# 应该看到：
# access-control-allow-origin: https://app.beatsync.site
```

---

## 快速修复脚本

```bash
#!/bin/bash
# 快速添加 app.beatsync.site 到 CORS 配置

SERVICE_FILE="/etc/systemd/system/beatsync.service"
ENV_FILE="/opt/beatsync/.env"

echo "=========================================="
echo "添加 app.beatsync.site 到 CORS 配置"
echo "=========================================="
echo ""

# 1. 检查当前配置
echo "步骤 1: 检查当前 CORS 配置..."
if [ -f "$ENV_FILE" ]; then
    CURRENT_ORIGINS=$(grep "ALLOWED_ORIGINS" "$ENV_FILE" | cut -d'=' -f2)
    echo "当前配置: $CURRENT_ORIGINS"
    
    # 检查是否已包含 app.beatsync.site
    if echo "$CURRENT_ORIGINS" | grep -q "app.beatsync.site"; then
        echo "✅ app.beatsync.site 已在配置中"
        exit 0
    fi
    
    # 添加 app.beatsync.site
    echo "添加 app.beatsync.site..."
    if grep -q "ALLOWED_ORIGINS" "$ENV_FILE"; then
        # 更新现有配置
        sudo sed -i 's|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000|' "$ENV_FILE"
    else
        # 添加新配置
        echo "ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000" | sudo tee -a "$ENV_FILE"
    fi
    echo "✅ 已更新 .env 文件"
else
    echo "⚠️  .env 文件不存在，将在 systemd 服务文件中配置"
fi

# 2. 更新 systemd 服务文件
if [ -f "$SERVICE_FILE" ]; then
    echo "步骤 2: 更新 systemd 服务文件..."
    
    if grep -q "ALLOWED_ORIGINS" "$SERVICE_FILE"; then
        # 更新现有配置
        sudo sed -i 's|Environment="ALLOWED_ORIGINS=.*|Environment="ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000"|' "$SERVICE_FILE"
    else
        # 添加新配置（在 Environment="PATH=..." 之后）
        sudo sed -i '/Environment="PATH=/a Environment="ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000"' "$SERVICE_FILE"
    fi
    echo "✅ 已更新服务文件"
    
    # 重新加载并重启
    echo "步骤 3: 重新加载并重启服务..."
    sudo systemctl daemon-reload
    sudo systemctl restart beatsync.service
    echo "✅ 服务已重启"
else
    echo "⚠️  服务文件不存在: $SERVICE_FILE"
fi

# 3. 验证配置
echo "步骤 4: 验证 CORS 配置..."
sleep 2
curl -I -H "Origin: https://app.beatsync.site" https://beatsync.site/api/health 2>&1 | grep -i "access-control"

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo ""
echo "请刷新 https://app.beatsync.site 测试连接"
echo ""
```

保存为 `fix_app_cors.sh`，然后执行：
```bash
chmod +x fix_app_cors.sh
./fix_app_cors.sh
```

---

## 验证步骤

### 1. 检查 CORS 配置

```bash
# 检查环境变量
env | grep ALLOWED_ORIGINS

# 或检查服务文件
sudo systemctl cat beatsync.service | grep ALLOWED_ORIGINS
```

### 2. 测试 CORS 响应头

```bash
# 测试从 app.beatsync.site 访问
curl -I -H "Origin: https://app.beatsync.site" https://beatsync.site/api/health

# 应该看到：
# access-control-allow-origin: https://app.beatsync.site
```

### 3. 在浏览器中测试

1. 访问 `https://app.beatsync.site`
2. 打开开发者工具（F12）→ Console
3. 检查是否还有 CORS 错误
4. 尝试上传文件，确认可以连接后端

---

## 如果使用 CDN

### 检查 CDN CORS 配置

如果 `app.beatsync.site` 也使用 CDN，需要确保：

1. **CDN 回源配置正确**：
   - 回源地址：`beatsync.site` 或 `124.221.58.149`
   - 回源 Host：`beatsync.site`
   - 回源协议：HTTPS

2. **CDN 不修改 CORS 头**：
   - 确保 CDN 不会覆盖或修改 CORS 响应头
   - 如果 CDN 有 CORS 配置，需要同步更新

---

## 完整配置示例

### .env 文件配置

```
ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000
```

### systemd 服务文件配置

```ini
[Service]
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000"
```

---

## 常见问题

### Q1：修改后仍然有 CORS 错误？

**检查项**：
1. 确认环境变量已正确设置
2. 确认服务已重启
3. 清除浏览器缓存
4. 检查是否有多个 CORS 配置冲突

### Q2：如何确认 CORS 配置已生效？

**方法**：
```bash
# 测试不同来源的 CORS
curl -I -H "Origin: https://beatsync.site" https://beatsync.site/api/health
curl -I -H "Origin: https://app.beatsync.site" https://beatsync.site/api/health

# 应该都返回对应的 access-control-allow-origin 头
```

### Q3：如果 app.beatsync.site 也使用 CDN？

**需要**：
1. 确保 CDN 回源配置正确
2. 确保 CDN 不修改 CORS 头
3. 如果 CDN 有 CORS 配置，需要同步更新

---

## 总结

### 问题原因

- 前端域名：`https://app.beatsync.site`
- 后端域名：`https://beatsync.site`
- CORS 配置：只允许了 `beatsync.site`，未允许 `app.beatsync.site`

### 解决方法

1. 在后端 CORS 配置中添加 `https://app.beatsync.site`
2. 重启后端服务
3. 验证 CORS 配置

### 配置格式

```
ALLOWED_ORIGINS=https://beatsync.site,https://app.beatsync.site,http://localhost:8000
```

---

**最后更新**：2025-12-16
