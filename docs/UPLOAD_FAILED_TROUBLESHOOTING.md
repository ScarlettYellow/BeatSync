# 上传失败 "Failed to fetch" 排查指南

## 问题描述

访问GitHub Pages网站后，尝试上传视频文件时出现错误："上传失败: Failed to fetch"。

## 可能的原因

### 1. 前端API地址配置错误 ⭐ **最常见**

前端可能还在使用 `localhost:8000`，而不是实际的Render后端URL。

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 查看Console标签
3. 查看Network标签，尝试上传文件
4. 查看失败的请求URL是什么

**解决方案**：
确认前端代码中的API地址是否正确指向Render后端。

### 2. CORS配置问题

后端CORS可能没有允许GitHub Pages域名。

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 查看Console标签
3. 查看是否有CORS错误信息（如 "Access-Control-Allow-Origin"）

**解决方案**：
在Render Dashboard中，检查 `ALLOWED_ORIGINS` 环境变量是否包含：
```
https://ScarlettYellow.github.io/BeatSync/,http://localhost:8000
```

### 3. 后端服务未运行或已休眠

Render免费层在15分钟无活动后会休眠，首次访问需要几秒唤醒。

**检查方法**：
1. 直接访问Render后端健康检查接口：
   ```
   https://你的Render后端URL/api/health
   ```
2. 如果返回 `{"status": "ok"}`，说明服务正常
3. 如果超时或404，说明服务未运行

**解决方案**：
- 等待几秒让服务唤醒
- 或使用免费监控服务（如UptimeRobot）定期ping后端

### 4. 网络连接问题

前端无法访问后端API。

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 查看Network标签
3. 查看失败的请求状态码（404、500、CORS错误等）

## 排查步骤

### 步骤1：检查前端API地址

1. **打开浏览器开发者工具**（F12）

2. **查看Console标签**
   - 查看是否有JavaScript错误
   - 查看API地址是什么

3. **查看Network标签**
   - 尝试上传文件
   - 查看失败的请求
   - 查看请求URL是否正确

### 步骤2：检查后端服务状态

1. **访问健康检查接口**
   ```
   https://你的Render后端URL/api/health
   ```
   - 如果返回 `{"status": "ok"}`，说明服务正常
   - 如果超时，说明服务可能已休眠

2. **等待服务唤醒**
   - Render免费层首次访问需要几秒唤醒
   - 等待10-20秒后重试

### 步骤3：检查CORS配置

1. **访问Render Dashboard**
   - 进入你的后端服务
   - 点击 "Environment"

2. **检查 `ALLOWED_ORIGINS` 环境变量**
   - 应该包含：`https://ScarlettYellow.github.io/BeatSync/`
   - 注意：末尾必须有斜杠 `/`

3. **如果不存在或错误**
   - 添加或更新环境变量
   - 值应该是：`https://ScarlettYellow.github.io/BeatSync/,http://localhost:8000`
   - 保存后，Render会自动重新部署

### 步骤4：检查浏览器控制台错误

1. **打开浏览器开发者工具**（F12）

2. **查看Console标签**
   - 查看具体的错误信息
   - 常见错误：
     - `Failed to fetch` - 网络连接问题
     - `CORS policy` - CORS配置问题
     - `404 Not Found` - API地址错误
     - `500 Internal Server Error` - 后端服务错误

3. **查看Network标签**
   - 查看失败的请求
   - 查看请求URL、状态码、响应内容

## 快速修复步骤

### 修复1：确认前端API地址

检查 `web_service/frontend/script.js` 中的API地址：

```javascript
const API_BASE_URL = (() => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    // 确认这里是你实际的Render后端URL
    return window.API_BASE_URL || 'https://beatsync-backend-asha.onrender.com';
})();
```

**重要**：确认 `beatsync-backend-asha.onrender.com` 是你的实际Render后端URL。

### 修复2：更新CORS配置

在Render Dashboard中：

1. 进入后端服务
2. 点击 "Environment"
3. 添加或更新 `ALLOWED_ORIGINS` 环境变量
4. 值：`https://ScarlettYellow.github.io/BeatSync/,http://localhost:8000`
5. 保存更改
6. 等待重新部署完成（约1-2分钟）

### 修复3：测试后端服务

1. **访问健康检查接口**
   ```
   https://你的Render后端URL/api/health
   ```

2. **如果返回 `{"status": "ok"}`**
   - 说明后端服务正常
   - 继续检查前端配置

3. **如果超时或404**
   - 检查Render服务状态
   - 等待服务唤醒（首次访问需要几秒）

## 验证步骤

完成修复后：

1. **清除浏览器缓存**
   - Mac: `Cmd+Shift+R`
   - Windows: `Ctrl+Shift+R`

2. **重新访问网站**
   - https://ScarlettYellow.github.io/BeatSync/

3. **尝试上传文件**
   - 选择一个小视频文件
   - 查看是否成功上传

4. **检查浏览器控制台**
   - 确认没有错误信息
   - 确认API请求成功

## 需要帮助？

如果问题仍然存在，请提供：

1. **浏览器控制台错误信息**（F12 → Console）
2. **Network标签的请求详情**（F12 → Network）
3. **Render后端健康检查结果**（访问 `/api/health`）
4. **Render后端URL**（确认是否正确）

