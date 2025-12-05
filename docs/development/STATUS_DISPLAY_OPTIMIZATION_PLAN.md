# 处理状态显示优化方案

> **目标**：优化处理状态信息的显示，提升用户体验  
> **日期**：2025-12-04

---

## 问题分析

### 问题1：正在下载时显示版本名称

**当前问题**：
- 下载时只显示"正在下载..."，用户不知道在下载哪个版本

**解决方案**：
- 修改 `downloadFile` 函数，添加 `version` 参数（'modular' 或 'v2'）
- 在调用 `downloadFile` 时传递版本信息
- 更新状态为"正在下载Modular版本结果..."或"正在下载V2版本结果..."

**实现**：
```javascript
// 修改函数签名
async function downloadFile(url, filename, version = null)

// 更新状态
if (version) {
    const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
    updateStatus(`正在下载${versionName}结果...`, 'processing');
}
```

---

### 问题2：状态切换冲突

**当前问题**：
- 用户点击下载某个版本时，状态显示"正在下载..."
- 但 `pollTaskStatus` 仍在运行，会覆盖为"正在处理... (已等待XX秒)"
- 导致状态频繁切换，体验不好

**解决方案**：
- 添加全局标志位 `isDownloading` 和 `downloadingVersion`
- 当开始下载时，设置标志位
- 在 `pollTaskStatus` 中，如果 `isDownloading` 为 true，不更新状态
- 下载完成后，重置标志位

**实现**：
```javascript
// 全局状态
let isDownloading = false;
let downloadingVersion = null;

// 在 downloadFile 开始时
isDownloading = true;
downloadingVersion = version;

// 在 downloadFile 结束时（成功或失败）
isDownloading = false;
downloadingVersion = null;

// 在 pollTaskStatus 中
if (isDownloading) {
    // 不更新状态，保持下载状态显示
    return;
}
```

---

### 问题3：隐藏不需要的信息

**当前问题**：
- 一些技术细节对用户不友好
- 状态信息过于详细

**优化建议**：

1. **简化状态消息**：
   - "任务已提交，正在处理..." → "正在处理..."
   - "正在检查后端服务..." → 保留（用户需要知道）
   - "正在上传原始视频..." → "正在上传视频..."（简化）

2. **隐藏技术细节**：
   - 移除不必要的技术术语
   - 简化错误消息（详细错误仍在控制台显示）

3. **优化等待时间显示**：
   - "正在处理，请稍候... (已等待XX秒)" → "正在处理... (已等待XX秒)"
   - 简化消息，保留关键信息

**具体优化列表**：

| 当前消息 | 优化后 | 说明 |
|---------|--------|------|
| "任务已提交，正在处理..." | "正在处理..." | 简化 |
| "正在上传原始视频..." | "正在上传视频..." | 简化 |
| "正在上传音源视频..." | "正在上传视频..." | 简化 |
| "正在检查后端服务..." | 保留 | 用户需要知道 |
| "正在处理，请稍候... (已等待XX秒)" | "正在处理... (已等待XX秒)" | 简化 |
| "处理完成！两个版本都已成功生成。" | "处理完成！" | 简化（按钮状态已显示） |

---

## 实现方案

### 步骤1：添加全局状态标志

```javascript
// 在文件顶部添加
let isDownloading = false;
let downloadingVersion = null;
```

### 步骤2：修改 downloadFile 函数

```javascript
async function downloadFile(url, filename, version = null) {
    try {
        // 设置下载标志
        isDownloading = true;
        downloadingVersion = version;
        
        // 根据版本显示状态
        if (version) {
            const versionName = version === 'modular' ? 'Modular版本' : 'V2版本';
            updateStatus(`正在下载${versionName}结果...`, 'processing');
        } else {
            updateStatus('正在下载...', 'processing');
        }
        
        // ... 下载逻辑 ...
        
    } finally {
        // 重置标志（无论成功或失败）
        isDownloading = false;
        downloadingVersion = null;
    }
}
```

### 步骤3：修改 pollTaskStatus 函数

```javascript
async function pollTaskStatus(taskId) {
    // ...
    
    const poll = async () => {
        // 如果正在下载，不更新状态
        if (isDownloading) {
            return; // 跳过本次轮询的状态更新
        }
        
        // ... 原有逻辑 ...
    };
}
```

### 步骤4：优化状态消息

```javascript
// 简化状态消息
updateStatus('正在处理...', 'processing'); // 而不是 "任务已提交，正在处理..."
updateStatus('正在上传视频...', 'processing'); // 而不是 "正在上传原始视频..."
```

---

## 预期效果

### 优化前

1. 下载时：显示"正在下载..."（不知道哪个版本）
2. 状态切换：下载时状态被轮询覆盖，频繁切换
3. 信息过多：显示很多技术细节

### 优化后

1. 下载时：显示"正在下载Modular版本结果..."或"正在下载V2版本结果..."
2. 状态稳定：下载时状态不会被轮询覆盖，保持显示下载状态
3. 信息精简：只显示用户需要的关键信息

---

## 测试建议

1. **测试下载状态显示**：
   - 点击下载Modular版本，确认显示"正在下载Modular版本结果..."
   - 点击下载V2版本，确认显示"正在下载V2版本结果..."

2. **测试状态稳定性**：
   - 当一个版本完成，另一个版本还在处理时
   - 点击下载已完成的版本
   - 确认状态保持为下载状态，不被轮询覆盖

3. **测试消息简化**：
   - 确认状态消息简洁明了
   - 确认没有不必要的技术细节

---

## 注意事项

1. **错误处理**：
   - 下载失败时，也要重置 `isDownloading` 标志
   - 使用 `try...finally` 确保标志总是被重置

2. **并发下载**：
   - 当前设计不支持同时下载两个版本
   - 如果用户快速点击两个下载按钮，第二个会等待第一个完成
   - 这是合理的，避免冲突

3. **状态恢复**：
   - 如果下载失败，状态应该恢复到处理状态
   - 或者显示错误信息

---

**请确认此方案是否符合您的需求，确认后我将开始实施。**

