# 导出最新V2版本处理日志（修复版）

> **问题**：`tail: option used in invalid context -- 2`  
> **原因**：`tail -200` 无法直接处理通配符匹配的多个文件  
> **解决方案**：先合并文件，再使用tail

---

## 修复后的导出命令

### 方法1：分步执行（推荐，更稳定）

**步骤1：导出V2处理日志**

```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt
```

**步骤2：导出对比日志**

```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A30 -E "V2版本处理|modular版本处理|并行处理完成|资源使用" > /tmp/latest_comparison_log.txt
```

**步骤3：导出性能日志**

```bash
cat /opt/beatsync/outputs/logs/performance_*.log | tail -200 | grep -A20 -E "V2|v2" > /tmp/v2_performance_log_latest.txt
```

**步骤4：检查文件**

```bash
ls -lh /tmp/v2_*.txt /tmp/latest_*.txt
```

---

### 方法2：一键执行（修复版）

**在服务器上执行**：
```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt && sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A30 -E "V2版本处理|modular版本处理|并行处理完成|资源使用" > /tmp/latest_comparison_log.txt && cat /opt/beatsync/outputs/logs/performance_*.log | tail -200 | grep -A20 -E "V2|v2" > /tmp/v2_performance_log_latest.txt && ls -lh /tmp/v2_*.txt /tmp/latest_*.txt
```

**关键修复**：
- 将 `tail -200 /opt/beatsync/outputs/logs/performance_*.log` 
- 改为 `cat /opt/beatsync/outputs/logs/performance_*.log | tail -200`
- 先合并所有文件，再使用tail

---

### 方法3：如果最近30分钟没有日志，使用今天的所有日志

**在服务器上执行**：
```bash
sudo journalctl -u beatsync --since="today" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_today_processing_log.txt && sudo journalctl -u beatsync --since="today" --no-pager | grep -A30 -E "V2版本处理|modular版本处理|并行处理完成|资源使用" > /tmp/today_comparison_log.txt && cat /opt/beatsync/outputs/logs/performance_*.log | tail -500 | grep -A20 -E "V2|v2" > /tmp/v2_performance_log_today.txt && ls -lh /tmp/v2_*.txt /tmp/today_*.txt
```

---

## 下载日志到本地

### 下载所有日志

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_latest_processing_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/latest_comparison_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/v2_performance_log_latest.txt ~/Downloads/ && ls -lh ~/Downloads/v2_*.txt ~/Downloads/latest_*.txt
```

---

## 如果性能日志文件不存在

### 检查性能日志文件

**在服务器上执行**：
```bash
ls -lh /opt/beatsync/outputs/logs/performance_*.log
```

**如果文件不存在或为空**，可以跳过性能日志导出，只导出systemd日志：

```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt && sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A30 -E "V2版本处理|modular版本处理|并行处理完成|资源使用" > /tmp/latest_comparison_log.txt && ls -lh /tmp/v2_*.txt /tmp/latest_*.txt
```

---

## 说明

### 为什么会出现错误？

- `tail -200 /opt/beatsync/outputs/logs/performance_*.log` 中的通配符 `*.log` 可能匹配到多个文件
- `tail` 命令在处理多个文件时，需要先合并或分别处理
- 使用 `cat` 先合并所有文件，再通过管道传递给 `tail`，可以避免这个问题

### 修复方法

- **原命令**：`tail -200 /opt/beatsync/outputs/logs/performance_*.log`
- **修复后**：`cat /opt/beatsync/outputs/logs/performance_*.log | tail -200`
- 先合并所有文件，再使用tail提取最后200行

---

**最后更新**：2025-12-03

