# Git 快速参考

## 重要改动存档（推荐方式）

### 使用脚本（最简单）

```bash
# 基本用法
./git_commit_important.sh "类型: 简短描述"

# 带详细说明
./git_commit_important.sh "类型: 简短描述" "详细说明..."
```

**示例**：
```bash
./git_commit_important.sh "perf: 优化内存使用" "实现了新的内存管理策略，峰值内存从4GB降至2GB"
```

### 手动提交

```bash
# 1. 查看改动
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "类型: 简短描述" -m "详细说明..."

# 4. 创建标签（可选）
git tag -a v1.4.0 -m "版本说明"
```

## 常用操作

### 查看历史

```bash
# 简洁格式
git log --oneline

# 查看最近5次提交
git log --oneline -5

# 查看特定文件的改动历史
git log --oneline -- beatsync_fine_cut_modular.py
```

### 回退操作

```bash
# 查看提交ID
git log --oneline

# 回退到指定提交（保留改动）
git reset --soft <commit-id>

# 回退到指定提交（丢弃改动，谨慎使用）
git reset --hard <commit-id>

# 恢复特定文件到指定版本
git checkout <commit-id> -- <文件路径>
```

### 查看改动

```bash
# 查看未提交的改动
git diff

# 查看已暂存的改动
git diff --staged

# 查看与上次提交的差异
git diff HEAD

# 查看特定文件的改动
git diff -- <文件路径>
```

## 提交信息模板

### 性能优化
```
perf: 优化描述

- 优化点1
- 优化点2
- 性能提升：X倍
```

### 新功能
```
feat: 功能描述

- 功能点1
- 功能点2
- 影响范围
```

### Bug修复
```
fix: 修复描述

- 问题描述
- 修复方案
- 影响范围
```

## 版本标签

### 创建标签
```bash
git tag -a v1.4.0 -m "版本说明"
```

### 查看标签
```bash
git tag
git show v1.4.0
```

### 回退到标签
```bash
git checkout v1.4.0
```

## 重要提醒

1. **提交前检查**：使用 `git status` 和 `git diff` 确认改动
2. **提交信息清晰**：使用类型前缀和详细说明
3. **重要改动立即提交**：不要积累太多改动
4. **测试后提交**：确保代码可以正常运行
5. **定期创建标签**：标记重要版本节点

## 当前版本

- **当前标签**: v1.3.0
- **当前提交**: `git log -1 --oneline`

查看完整指南：`GIT_COMMIT_GUIDE.md`

