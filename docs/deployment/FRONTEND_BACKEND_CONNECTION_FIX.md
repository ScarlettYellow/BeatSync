# 前端无法连接后端问题修复

> **问题**：前端显示"后端服务不可用(5秒内无响应)"，但健康检查正常

---

## 问题分析

**现象**：
- ✅ 健康检查 http://1.12.239.225:8000/api/health 正常
- ❌ 前端无法上传视频，显示"后端服务不可用"

**可能原因**：
1. **CORS问题**：前端从GitHub Pages访问，后端需要允许跨域
2. **健康检查超时**：5秒超时可能不够（网络延迟）
3. **前端代码中的API地址不正确**

---

## 解决方案

### 方案1：检查CORS配置（最可能的原因）

后端需要允许来自GitHub Pages的跨域请求。

**在服务器上检查后端CORS配置**：

```bash
# 查看后端main.py中的CORS配置
grep -A 10 "CORS" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
```python
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"]:
    allow_origins_list = ["*"]
```

**如果CORS配置正确（允许所有来源），继续检查其他原因。**

### 方案2：增加健康检查超时时间

前端健康检查默认5秒超时，可能不够。需要修改前端代码：

**修改 `web_service/frontend/script.js`**：

找到 `checkBackendHealth` 函数（大约第131行），将超时时间从5秒增加到10秒：

```javascript
async function checkBackendHealth() {
    const healthUrl = `${API_BASE_URL}/api/health`;
    const timeoutMs = 10000; // 从5000改为10000（10秒）
    // ... 其余代码
}
```

### 方案3：检查浏览器控制台错误

打开浏览器开发者工具（F12），查看Console标签，检查是否有：
- CORS错误
- 网络错误
- 其他错误信息

---

## 快速修复步骤

### 步骤1：检查浏览器控制台

1. 打开前端页面：https://scarlettyellow.github.io/BeatSync/
2. 按F12打开开发者工具
3. 切换到Console标签
4. 尝试上传文件
5. 查看错误信息

**常见错误**：
- `CORS policy: No 'Access-Control-Allow-Origin' header` → CORS问题
- `Failed to fetch` → 网络连接问题
- `Timeout` → 超时问题

### 步骤2：根据错误类型修复

#### 如果是CORS错误

**检查后端CORS配置**（在服务器上）：

```bash
# 查看CORS配置
grep -A 15 "CORSMiddleware" /opt/beatsync/web_service/backend/main.py
```

**如果CORS配置为`*`（允许所有来源），应该没问题。**

**如果CORS配置限制了来源，需要添加GitHub Pages域名**：

```python
allowed_origins = [
    "https://scarlettyellow.github.io",
    "http://localhost:8080",
    "*"
]
```

**修改后重启服务**：

```bash
sudo systemctl restart beatsync
```

#### 如果是超时错误

**修改前端代码，增加超时时间**：

```javascript
// 在 checkBackendHealth 函数中
const timeoutMs = 10000; // 改为10秒
```

**然后提交更新**：

```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "fix: 增加后端健康检查超时时间到10秒"
git push origin main
```

#### 如果是网络连接错误

**检查防火墙配置**：
- 确认8000端口已开放
- 确认来源设置为"全部IPv4地址"

**测试连接**：

```bash
# 从本地机器测试
curl -v http://1.12.239.225:8000/api/health
```

---

## 临时测试方案

### 直接测试API

在浏览器中直接访问：
- http://1.12.239.225:8000/api/health

**如果可以直接访问，说明**：
- 防火墙配置正确
- 后端服务正常
- 问题可能是CORS或前端代码

### 使用curl测试上传

```bash
# 从本地机器测试上传
curl -X POST http://1.12.239.225:8000/api/upload \
  -F "file=@test.mp4" \
  -F "file_type=dance"
```

---

## 推荐修复流程

1. **检查浏览器控制台错误**（最重要）
2. **根据错误类型修复**：
   - CORS错误 → 检查后端CORS配置
   - 超时错误 → 增加超时时间
   - 网络错误 → 检查防火墙
3. **测试修复**：刷新前端页面，重新尝试上传

---

## 验证修复

修复后，应该能够：
- ✅ 前端可以检查后端健康状态
- ✅ 前端可以上传视频文件
- ✅ 前端可以提交处理任务

---

**最后更新**：2025-12-01



