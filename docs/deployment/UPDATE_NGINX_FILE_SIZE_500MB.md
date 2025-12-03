# 更新Nginx文件大小限制到500MB

> **目的**：将上传文件大小限制从1GB降低到500MB，以节省服务器资源

---

## 更新步骤

### 1. 更新Nginx配置

**在腾讯云服务器上执行（一键命令）**：

```bash
sudo sed -i 's/client_max_body_size 1G;/client_max_body_size 500M;/g' /etc/nginx/sites-available/beatsync && sudo nginx -t && sudo systemctl restart nginx && echo "✅ Nginx配置已更新！文件大小限制已降低到500MB"
```

**或手动编辑**：

```bash
sudo nano /etc/nginx/sites-available/beatsync
```

找到以下行：
```nginx
client_max_body_size 1G;
```

改为：
```nginx
client_max_body_size 500M;
```

然后测试并重启：
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 验证

### 1. 检查配置

```bash
grep client_max_body_size /etc/nginx/sites-available/beatsync
```

应该显示：
```
client_max_body_size 500M;
```

### 2. 测试上传

1. 尝试上传大于500MB的文件
2. 前端应该显示错误提示："文件大小超过限制（最大500MB）"
3. 如果绕过前端检查，后端应该返回413错误（Request Entity Too Large）

---

## 配置说明

### client_max_body_size

- **之前**：1GB
- **现在**：500MB
- **原因**：节省服务器资源，降低处理负担

### 前端文件大小检查

- **限制**：500MB
- **提示**：如果文件超过限制，会显示错误提示
- **位置**：`web_service/frontend/script.js` 的 `uploadFile` 函数

---

## 注意事项

- ⚠️ 如果用户需要上传大于500MB的文件，需要先压缩或裁剪
- ⚠️ 前端和后端都需要更新（前端已更新，后端需要更新Nginx配置）

---

**最后更新**：2025-12-02
