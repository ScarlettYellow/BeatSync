# 修复状态显示跳转问题

> **修复日期**：2025-12-05  
> **问题**：状态显示一会儿显示两行（下载状态+处理状态），一会儿只显示一行（只有下载状态）  
> **原因**：`downloadFile`函数直接调用`updateStatus`，与`pollTaskStatus`的`updateStatusWithMultiple`冲突

---

## 问题描述

**用户反馈**：
- 状态显示一会儿显示两行：
  - "正在下载Modular版本结果... 10%"
  - "modular版本已完成, V2版本处理中 (已等待70秒)"
- 一会儿只显示一行：
  - "正在下载Modular版本结果... 10%"
- 状态在单行和双行之间跳转

---

## 问题分析

### 代码逻辑冲突

**问题根源**：

1. **`downloadFile`函数**：
   - 在多个地方直接调用`updateStatus`更新状态
   - 只显示一行（只有下载状态）
   - 会覆盖掉`pollTaskStatus`显示的多行状态

2. **`pollTaskStatus`函数**：
   - 每5秒轮询一次
   - 如果正在下载，会使用`updateStatusWithMultiple`同时显示下载状态和处理状态（两行）
   - 会恢复多行显示

3. **冲突过程**：
   - `downloadFile`调用`updateStatus` → 显示一行（只有下载状态）
   - 5秒后`pollTaskStatus`轮询 → `updateStatusWithMultiple`显示两行（下载状态+处理状态）
   - `downloadFile`又调用`updateStatus` → 又显示一行
   - 导致状态在单行和双行之间跳转

---

## 解决方案

### 核心思路

**统一状态显示**：
- 如果`pollTaskStatus`正在运行，所有状态更新都通过它来统一显示
- `downloadFile`函数只更新`downloadingStatusMessage`变量，不直接调用`updateStatus`
- 避免状态更新冲突

---

### 修改1：添加全局标志

**添加全局变量**：
```javascript
let isPolling = false; // 标记pollTaskStatus是否正在运行
```

---

### 修改2：`pollTaskStatus`函数

**在轮询开始和结束时更新标志**：
```javascript
async function pollTaskStatus(taskId) {
    // 标记轮询开始
    isPolling = true;
    
    // ... 轮询逻辑 ...
    
    // 在轮询结束时标记
    if (result.status === 'success' || result.status === 'failed' || allDone || attempts >= maxAttempts) {
        isPolling = false;
    }
}
```

---

### 修改3：`downloadFile`函数

**修改前**：
```javascript
downloadingStatusMessage = `正在下载${versionName}结果...`;
updateStatus(downloadingStatusMessage, 'processing'); // 总是更新状态
```

**修改后**：
```javascript
downloadingStatusMessage = `正在下载${versionName}结果...`;
// 如果pollTaskStatus正在运行，它会统一显示状态
// 否则直接更新状态（处理已完成的情况）
if (!isPolling) {
    updateStatus(downloadingStatusMessage, 'processing');
}
```

---

## 修改后的行为

### 状态更新流程

1. **处理中 + 下载中**：
   - `pollTaskStatus`正在运行（`isPolling = true`）
   - `downloadFile`只更新`downloadingStatusMessage`变量
   - `pollTaskStatus`每5秒轮询一次，使用`updateStatusWithMultiple`同时显示两行：
     - "正在下载Modular版本结果... 10%"
     - "modular版本已完成, V2版本处理中 (已等待70秒)"

2. **处理完成后下载**：
   - `pollTaskStatus`已停止（`isPolling = false`）
   - `downloadFile`直接调用`updateStatus`更新状态
   - 显示一行："正在下载Modular版本结果..."

---

## 预期效果

### 修复前

- ❌ 状态在单行和双行之间跳转
- ❌ `downloadFile`和`pollTaskStatus`的状态更新互相覆盖

### 修复后

- ✅ 如果处理中，状态始终显示两行（下载状态+处理状态）
- ✅ 如果处理已完成，状态显示一行（只有下载状态）
- ✅ 状态显示稳定，不会跳转

---

## 测试建议

### 测试场景1：处理中下载

**步骤**：
1. 上传视频并开始处理
2. 在Modular版本处理完成但V2版本仍在处理时，点击下载Modular版本
3. 观察状态显示

**预期结果**：
- ✅ 状态始终显示两行：
  - "正在下载Modular版本结果... X%"
  - "modular版本已完成, V2版本处理中 (已等待X秒)"
- ✅ 不会跳转到单行显示

---

### 测试场景2：处理完成后下载

**步骤**：
1. 等待所有处理完成
2. 点击下载按钮
3. 观察状态显示

**预期结果**：
- ✅ 状态显示一行："正在下载Modular版本结果..."
- ✅ 不会显示处理状态（因为处理已完成）

---

## 相关文档

- `docs/development/FIX_DOWNLOAD_PROGRESS_CONFLICT.md` - 下载进度显示冲突修复
- `docs/development/STATUS_DISPLAY_OPTIMIZATION_PLAN.md` - 状态显示优化计划

---

**最后更新**：2025-12-05

