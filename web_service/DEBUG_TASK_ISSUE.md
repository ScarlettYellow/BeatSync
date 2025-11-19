# "任务不存在"错误排查指南

## 问题分析

"任务不存在"错误通常发生在以下情况：

1. **任务提交失败**：前端收到了task_id，但后端实际上没有创建任务
2. **任务状态丢失**：后端重启导致内存中的任务状态丢失
3. **任务ID不匹配**：前端使用的task_id与后端存储的不一致
4. **文件路径问题**：任务状态文件路径不正确

## 排查步骤

### 步骤1：检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到 **Console** 标签
3. 查看是否有错误信息
4. 特别关注：
   - `🔵 本地开发环境检测` 和 `后端URL: http://localhost:8000`
   - 任何红色错误信息

### 步骤2：检查网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 点击"开始处理"
4. 查看以下请求：

#### 请求1：`/api/process` (POST)
- **状态码**：应该是 `200`
- **响应**：应该包含 `task_id`
- **如果失败**：查看Response中的错误信息

#### 请求2：`/api/status/{task_id}` (GET)
- **状态码**：如果是 `404`，说明任务不存在
- **响应**：查看错误详情

### 步骤3：检查后端日志

查看启动后端的终端窗口，查找：

1. **任务提交日志**：
   ```
   ✅ 已加载 X 个任务状态
   ```

2. **任务创建日志**：
   - 应该看到任务ID被创建
   - 应该看到任务状态被保存

3. **错误日志**：
   - `ERROR` 开头的错误
   - `WARNING` 开头的警告

### 步骤4：检查任务状态文件

```bash
# 检查任务状态文件
ls -la outputs/task_status.json

# 查看任务状态内容（如果有）
cat outputs/task_status.json
```

### 步骤5：检查上传的文件

```bash
# 检查上传目录
ls -la outputs/web_uploads/

# 应该看到类似这样的文件：
# {file_id}_dance.mp4
# {file_id}_bgm.mp4
```

## 常见原因和解决方案

### 原因1：任务提交失败，但前端仍尝试轮询

**症状**：
- `/api/process` 返回错误
- 但前端仍然尝试轮询状态

**解决**：
- 检查 `/api/process` 的响应
- 确保任务提交成功后再开始轮询

### 原因2：后端重启导致任务状态丢失

**症状**：
- 任务提交成功
- 但后端重启后，任务状态丢失

**解决**：
- 检查 `outputs/task_status.json` 文件是否存在
- 确保任务状态已保存到文件

### 原因3：文件上传失败

**症状**：
- 前端显示文件已上传
- 但后端找不到文件

**解决**：
```bash
# 检查上传目录
ls -la outputs/web_uploads/

# 检查文件权限
chmod -R 755 outputs/
```

### 原因4：任务状态文件路径问题

**症状**：
- 任务状态文件不存在
- 或路径不正确

**解决**：
- 检查 `TASK_STATUS_FILE` 路径
- 确保 `outputs/` 目录存在且可写

## 调试技巧

### 1. 添加调试日志

在浏览器控制台运行：

```javascript
// 查看当前状态
console.log('当前状态:', state);

// 查看API_BASE_URL
console.log('API_BASE_URL:', API_BASE_URL);
```

### 2. 直接测试API

使用curl测试：

```bash
# 测试健康检查
curl http://localhost:8000/

# 测试API文档
open http://localhost:8000/docs
```

### 3. 查看任务状态文件

```bash
# 实时查看任务状态
tail -f outputs/task_status.json
```

## 快速修复

如果问题持续，尝试：

1. **重启后端服务**：
   ```bash
   # 停止后端（Ctrl+C）
   # 重新启动
   cd web_service/backend
   ./start_server.sh
   ```

2. **清除任务状态**：
   ```bash
   # 删除任务状态文件（会丢失所有任务状态）
   rm outputs/task_status.json
   ```

3. **清除上传文件**：
   ```bash
   # 清除所有上传文件（谨慎操作）
   rm -rf outputs/web_uploads/*
   ```

4. **强制刷新前端**：
   - Cmd+Shift+R (macOS)
   - Ctrl+Shift+R (Windows/Linux)

