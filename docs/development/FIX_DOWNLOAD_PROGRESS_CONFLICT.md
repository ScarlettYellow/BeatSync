# 修复下载进度显示冲突

> **修复日期**：2025-12-05  
> **问题**：下载视频时，状态在"正在下载modular版本结果...60%"和"正在下载modular版本结果...10%"之间跳转  
> **原因**：下载进度更新和状态轮询更新互相覆盖

---

## 问题描述

**用户反馈**：
- 手机网页上下载视频时，状态显示异常
- 一会儿显示"正在下载modular版本结果...60%"
- 一会儿又显示"正在下载modular版本结果...10%"
- 状态在60%和10%之间跳来跳去

---

## 问题分析

### 代码逻辑冲突

**问题根源**：

1. **`downloadFileWithBlob`函数**：
   - 每10%更新一次进度时，直接调用`updateStatus`更新状态
   - 这会覆盖掉当前显示的状态

2. **`pollTaskStatus`函数**：
   - 每5秒轮询一次，如果正在下载，会使用`updateStatusWithMultiple`同时显示下载状态和处理状态
   - 这会恢复多行显示

3. **冲突过程**：
   - 下载进度更新到60% → `updateStatus`显示"60%"
   - 5秒后轮询 → `updateStatusWithMultiple`显示"10%"（因为`downloadingStatusMessage`变量可能被重置或未及时更新）
   - 下载进度更新到70% → `updateStatus`显示"70%"
   - 5秒后轮询 → `updateStatusWithMultiple`又显示"10%"
   - 导致状态在60%和10%之间跳转

---

## 解决方案

### 修改策略

**核心思路**：
- 下载进度更新时，只更新`downloadingStatusMessage`变量，不直接调用`updateStatus`
- 让`pollTaskStatus`中的逻辑来统一显示状态
- 避免下载进度更新和处理状态更新互相覆盖

---

### 修改1：`downloadFileWithBlob`函数

**修改前**：
```javascript
if (percent % 10 === 0) {
    downloadingStatusMessage = `正在下载${versionName}结果... ${percent}%`;
    updateStatus(downloadingStatusMessage, 'processing'); // 直接更新状态
}
```

**修改后**：
```javascript
if (percent % 10 === 0) {
    downloadingStatusMessage = `正在下载${versionName}结果... ${percent}%`;
    // 不直接调用updateStatus，只更新变量，让pollTaskStatus统一显示
}
```

---

### 修改2：`downloadFile`函数

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
if (typeof pollInterval === 'undefined' || pollInterval === null) {
    updateStatus(downloadingStatusMessage, 'processing');
}
```

---

## 修改后的行为

### 状态更新流程

1. **下载开始**：
   - 更新`downloadingStatusMessage`变量
   - 如果`pollTaskStatus`正在运行，它会统一显示状态
   - 如果处理已完成（`pollTaskStatus`已停止），直接更新状态

2. **下载进度更新**：
   - 只更新`downloadingStatusMessage`变量（包含进度百分比）
   - 不直接调用`updateStatus`
   - `pollTaskStatus`会在下次轮询时显示更新后的状态

3. **状态轮询**：
   - 每5秒轮询一次
   - 如果正在下载，使用`updateStatusWithMultiple`同时显示下载状态和处理状态
   - 显示的是最新的`downloadingStatusMessage`（包含最新进度）

---

## 预期效果

### 修复前

- ❌ 状态在"60%"和"10%"之间跳转
- ❌ 下载进度更新和处理状态更新互相覆盖

### 修复后

- ✅ 状态显示稳定，不会跳转
- ✅ 下载进度正确显示（10%, 20%, 30%, ...）
- ✅ 下载状态和处理状态同时显示，互不干扰

---

## 测试建议

### 测试场景

1. **处理中下载**：
   - 上传视频并开始处理
   - 在Modular版本处理完成但V2版本仍在处理时，点击下载Modular版本
   - 观察状态显示

2. **处理完成后下载**：
   - 等待所有处理完成
   - 点击下载按钮
   - 观察状态显示

**预期结果**：
- ✅ 下载进度正确显示（10%, 20%, 30%, ...）
- ✅ 状态不会在60%和10%之间跳转
- ✅ 如果处理仍在进行，会同时显示下载状态和处理状态

---

## 相关文档

- `docs/development/STATUS_DISPLAY_OPTIMIZATION_PLAN.md` - 状态显示优化计划
- `docs/development/FIX_MOBILE_BROWSER_DOWNLOAD.md` - 手机端浏览器下载体验修复

---

**最后更新**：2025-12-05

