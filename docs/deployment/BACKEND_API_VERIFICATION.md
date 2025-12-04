# 后端API验证指南

> **状态**：HTTPS和Nginx配置已成功，后端API正常运行  
> **说明**：后端只提供API服务，前端部署在GitHub Pages

---

## 当前状态

### ✅ 已完成的配置

- ✅ **HTTPS证书**：Let's Encrypt证书已部署
- ✅ **Nginx配置**：已正确代理到FastAPI后端
- ✅ **后端服务**：FastAPI正在运行
- ✅ **API访问**：可以通过HTTPS访问API

---

## 访问地址说明

### 后端API（beatsync.site）

**根路径**：`https://beatsync.site/`
- 返回：`{"name":"BeatSync API", "version":"1.0.0", "status":"running"}`
- 这是FastAPI的根路径响应，表示API服务正常运行 ✅

**健康检查**：`https://beatsync.site/api/health`
- 预期返回：`{"status":"healthy","timestamp":"..."}`

**API文档**：`https://beatsync.site/docs`
- 预期显示：FastAPI自动生成的API文档页面

---

### 前端页面（GitHub Pages）

**访问地址**：`https://scarlettyellow.github.io/BeatSync/`
- 这是用户实际使用的页面
- 前端会自动连接到后端API（`https://beatsync.site`）

---

## 验证API功能

### 1. 健康检查

**在浏览器中访问**：
```
https://beatsync.site/api/health
```

**预期返回**：
```json
{"status":"healthy","timestamp":"2025-12-04T..."}
```

---

### 2. API文档

**在浏览器中访问**：
```
https://beatsync.site/docs
```

**预期显示**：
- FastAPI自动生成的交互式API文档
- 可以测试各个API端点

---

### 3. 测试上传功能（通过前端）

**访问前端页面**：
```
https://scarlettyellow.github.io/BeatSync/
```

**测试步骤**：
1. 上传dance视频
2. 上传bgm视频
3. 点击"开始处理"
4. 查看处理状态
5. 下载处理结果

**预期结果**：
- ✅ 前端可以正常连接到后端API
- ✅ 上传功能正常
- ✅ 处理功能正常
- ✅ 下载功能正常

---

## 验证清单

### 后端API验证

- [x] HTTPS可以访问
- [x] 根路径返回API信息
- [ ] 健康检查端点正常（`/api/health`）
- [ ] API文档可以访问（`/docs`）
- [ ] 前端可以正常连接后端

---

### 前端功能验证

- [ ] 前端页面可以正常访问
- [ ] 上传功能正常
- [ ] 处理功能正常
- [ ] 下载功能正常

---

## 常见问题

### Q1：为什么访问beatsync.site显示JSON而不是网页？

**A**：这是正常的。`beatsync.site` 是后端API服务器，只提供API服务。前端页面部署在GitHub Pages上（`https://scarlettyellow.github.io/BeatSync/`）。

---

### Q2：用户应该访问哪个地址？

**A**：用户应该访问前端页面：
```
https://scarlettyellow.github.io/BeatSync/
```

前端会自动连接到后端API（`https://beatsync.site`）。

---

### Q3：如何验证后端API是否正常工作？

**A**：
1. 访问 `https://beatsync.site/api/health` 应该返回 `{"status":"healthy"}`
2. 访问 `https://beatsync.site/docs` 应该显示API文档
3. 通过前端页面测试上传和处理功能

---

## 下一步

### 1. 验证API端点

**在浏览器中访问以下地址**：

- **健康检查**：`https://beatsync.site/api/health`
- **API文档**：`https://beatsync.site/docs`

---

### 2. 测试前端功能

**访问前端页面**：
```
https://scarlettyellow.github.io/BeatSync/
```

**测试完整流程**：
1. 上传两个视频文件
2. 点击"开始处理"
3. 等待处理完成
4. 下载处理结果

---

### 3. 检查浏览器控制台

**打开开发者工具（F12）**：
- 查看Network标签，确认API请求正常
- 查看Console标签，确认无错误信息

---

## 相关文档

- `docs/deployment/SSL_CERTIFICATE_DEPLOYMENT_SUCCESS.md` - SSL证书部署记录
- `docs/deployment/FIX_NGINX_DEFAULT_PAGE.md` - Nginx配置修复指南

---

**最后更新**：2025-12-04

