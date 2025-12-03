# V2版本诊断文件下载命令

> **目的**：下载性能日志和systemd导出的性能信息文件到本地分析

---

## 下载命令

### 步骤1：修改文件权限（如果需要）

**如果 `v2_performance_from_journal.txt` 无法下载（权限问题）**，在服务器上执行：

```bash
sudo chmod 644 /tmp/v2_performance_from_journal.txt && sudo chown ubuntu:ubuntu /tmp/v2_performance_from_journal.txt
```

---

### 步骤2：下载性能日志文件

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/opt/beatsync/outputs/logs/performance_20251202.log ~/Downloads/
```

**说明**：
- 下载性能日志文件到本地 `~/Downloads/` 目录
- 文件大小：73KB

---

### 步骤3：下载systemd导出的性能信息

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_performance_from_journal.txt ~/Downloads/
```

**说明**：
- 下载systemd导出的性能信息到本地 `~/Downloads/` 目录
- 文件大小：5.1KB

---

## 一键下载（如果权限已正确）

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/opt/beatsync/outputs/logs/performance_20251202.log ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/v2_performance_from_journal.txt ~/Downloads/ && ls -lh ~/Downloads/performance_20251202.log ~/Downloads/v2_performance_from_journal.txt
```

**说明**：
- 同时下载两个文件
- 显示文件大小，确认下载成功

---

## 如果遇到权限问题

### 方法1：修改文件权限后下载

**在服务器上执行**：
```bash
sudo chmod 644 /tmp/v2_performance_from_journal.txt && sudo chown ubuntu:ubuntu /tmp/v2_performance_from_journal.txt && ls -lh /tmp/v2_performance_from_journal.txt
```

**然后在本地下载**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_performance_from_journal.txt ~/Downloads/
```

---

### 方法2：使用sudo下载（不推荐，但可行）

**在本地终端执行**：
```bash
# 先复制到ubuntu用户可访问的位置
ssh ubuntu@124.221.58.149 "sudo cp /tmp/v2_performance_from_journal.txt /tmp/v2_perf.txt && sudo chmod 644 /tmp/v2_perf.txt && sudo chown ubuntu:ubuntu /tmp/v2_perf.txt"

# 然后下载
scp ubuntu@124.221.58.149:/tmp/v2_perf.txt ~/Downloads/v2_performance_from_journal.txt
```

---

## 验证下载

**在本地终端执行**：
```bash
# 检查文件是否存在和大小
ls -lh ~/Downloads/performance_20251202.log ~/Downloads/v2_performance_from_journal.txt

# 查看文件内容预览
head -20 ~/Downloads/performance_20251202.log
head -20 ~/Downloads/v2_performance_from_journal.txt
```

---

## 注意事项

1. **性能日志文件日期**：
   - 文件名是 `performance_20251202.log`（12月2日）
   - 但V2变慢是从12月3日开始的
   - 可能需要检查是否有 `performance_20251203.log` 文件

2. **检查是否有12月3日的性能日志**：

**在服务器上执行**：
```bash
ls -lh /opt/beatsync/outputs/logs/performance_*.log
```

**如果有12月3日的日志，也下载它**：
```bash
scp ubuntu@124.221.58.149:/opt/beatsync/outputs/logs/performance_20251203.log ~/Downloads/
```

---

**最后更新**：2025-12-03

