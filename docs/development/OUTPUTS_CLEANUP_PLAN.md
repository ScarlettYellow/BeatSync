# Outputs文件夹清理方案

## 当前状态分析

- **总大小**: 11GB
- **MP4文件**: 174个
- **主要目录**:
  - `batch_all_hd_samples/` - 批量处理高清样本输出（35个样本）
  - `batch_hd_samples/` - 批量处理高清样本输出（24个样本，可能是旧版本）
  - `web_uploads/` - Web服务上传的临时文件（49个文件）
  - `web_outputs/` - Web服务处理结果（30个任务）
  - `test_*` - 各种测试目录（多个）
  - `logs/` - 日志文件
  - 单个测试文件（test_modular_debug.mp4等）

## 清理方案

### 方案1：保守清理（推荐）
**删除内容**：
1. ✅ **测试目录**（`test_*`）- 调试和测试用的临时文件
2. ✅ **Web上传文件**（`web_uploads/`）- 用户上传的临时文件，处理完成后不再需要
3. ✅ **旧的Web输出**（`web_outputs/`）- 保留最近7天的，删除更早的
4. ✅ **日志文件**（`*.log`）- 处理日志，可以删除
5. ✅ **单个测试文件**（`test_*.mp4`）- 调试用的单个文件
6. ✅ **旧的批量处理结果**（`batch_hd_samples/`）- 如果有`batch_all_hd_samples/`，删除旧的

**保留内容**：
- ✅ `batch_all_hd_samples/` - 最新的批量处理结果（重要）
- ✅ `task_status.json` - 任务状态文件（运行时需要）
- ✅ `logs/`目录结构（如果需要）

**预计释放空间**: 约2-3GB

### 方案2：激进清理
在方案1基础上，额外删除：
- `web_outputs/` - 所有Web服务输出（如果不需要历史记录）
- `batch_all_hd_samples/` - 批量处理结果（如果不需要保留）

**预计释放空间**: 约8-10GB

### 方案3：仅清理临时文件
只删除明显的临时文件：
- `test_*`目录
- `web_uploads/`目录
- `*.log`文件
- 单个测试文件

**预计释放空间**: 约500MB-1GB

## 推荐方案：方案1（保守清理）

### 执行步骤

1. **删除测试目录**
   ```bash
   rm -rf outputs/test_*
   ```

2. **删除Web上传文件**
   ```bash
   rm -rf outputs/web_uploads
   ```

3. **删除旧的Web输出（保留最近7天）**
   ```bash
   find outputs/web_outputs -type d -mtime +7 -exec rm -rf {} \;
   ```

4. **删除日志文件**
   ```bash
   rm -f outputs/*.log
   rm -rf outputs/logs/*
   ```

5. **删除单个测试文件**
   ```bash
   rm -f outputs/test_*.mp4
   rm -f outputs/dejavu_*.mp4
   ```

6. **删除旧的批量处理结果（如果存在）**
   ```bash
   # 如果batch_all_hd_samples是最新的，删除batch_hd_samples
   rm -rf outputs/batch_hd_samples
   ```

## 清理后建议

1. **更新.gitignore**：确保outputs/目录被正确忽略
2. **定期清理**：建议每月清理一次Web服务的临时文件
3. **保留重要结果**：批量处理的结果可以保留，作为测试基准

