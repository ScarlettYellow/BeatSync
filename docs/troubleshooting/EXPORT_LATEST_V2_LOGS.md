# 导出最新V2版本处理日志

> **目的**：导出最新测试的V2版本相关日志，用于分析处理速度问题

---

## 导出命令

### 方法1：导出最近的V2处理日志（推荐）

**在服务器上执行**：
```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt && ls -lh /tmp/v2_latest_processing_log.txt
```

**说明**：
- 导出最近30分钟内的V2处理日志
- 包含V2版本处理的详细步骤
- 保存到 `/tmp/v2_latest_processing_log.txt`

---

### 方法2：导出今天的V2处理日志

**在服务器上执行**：
```bash
sudo journalctl -u beatsync --since="today" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_today_processing_log.txt && ls -lh /tmp/v2_today_processing_log.txt
```

---

### 方法3：导出最近的完整处理日志（包含modular和V2对比）

**在服务器上执行**：
```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A30 -E "V2版本处理|modular版本处理|并行处理完成|资源使用" > /tmp/latest_comparison_log.txt && ls -lh /tmp/latest_comparison_log.txt
```

**说明**：
- 导出modular和V2版本的对比日志
- 包含处理完成时间和资源使用情况
- 便于对比两个版本的性能差异

---

### 方法4：导出性能日志中的V2信息

**在服务器上执行**：
```bash
tail -200 /opt/beatsync/outputs/logs/performance_*.log | grep -A20 -E "V2|v2" > /tmp/v2_performance_log_latest.txt && ls -lh /tmp/v2_performance_log_latest.txt
```

**说明**：
- 导出性能日志中的V2相关信息
- 包含CPU、内存、I/O等资源使用情况

---

## 下载日志到本地

### 下载V2处理日志

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_latest_processing_log.txt ~/Downloads/
```

---

### 下载对比日志

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/tmp/latest_comparison_log.txt ~/Downloads/
```

---

### 下载性能日志

**在本地终端执行**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_performance_log_latest.txt ~/Downloads/
```

---

## 一键导出和下载

### 在服务器上执行（导出所有相关日志）

```bash
sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt && sudo journalctl -u beatsync --since="30 minutes ago" --no-pager | grep -A30 -E "V2版本处理|modular版本处理|并行处理完成|资源使用" > /tmp/latest_comparison_log.txt && tail -200 /opt/beatsync/outputs/logs/performance_*.log | grep -A20 -E "V2|v2" > /tmp/v2_performance_log_latest.txt && ls -lh /tmp/v2_*.txt /tmp/latest_*.txt
```

---

### 在本地执行（下载所有日志）

```bash
scp ubuntu@124.221.58.149:/tmp/v2_latest_processing_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/latest_comparison_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/v2_performance_log_latest.txt ~/Downloads/ && ls -lh ~/Downloads/v2_*.txt ~/Downloads/latest_*.txt
```

---

## 如果文件太大，可以压缩

### 在服务器上压缩

```bash
cd /tmp && tar -czf v2_logs_latest.tar.gz v2_latest_processing_log.txt latest_comparison_log.txt v2_performance_log_latest.txt && ls -lh /tmp/v2_logs_latest.tar.gz
```

### 在本地下载压缩文件

```bash
scp ubuntu@124.221.58.149:/tmp/v2_logs_latest.tar.gz ~/Downloads/ && cd ~/Downloads && tar -xzf v2_logs_latest.tar.gz && ls -lh v2_*.txt latest_*.txt
```

---

## 注意事项

### 时间范围调整

如果最近30分钟没有日志，可以调整时间范围：
```bash
# 最近1小时
sudo journalctl -u beatsync --since="1 hour ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt

# 最近2小时
sudo journalctl -u beatsync --since="2 hours ago" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_latest_processing_log.txt

# 今天的所有日志
sudo journalctl -u beatsync --since="today" --no-pager | grep -A50 "V2版本处理" > /tmp/v2_today_processing_log.txt
```

---

### 检查文件大小

**在服务器上**：
```bash
ls -lh /tmp/v2_*.txt /tmp/latest_*.txt
```

**在本地**：
```bash
ls -lh ~/Downloads/v2_*.txt ~/Downloads/latest_*.txt
```

---

**最后更新**：2025-12-03

