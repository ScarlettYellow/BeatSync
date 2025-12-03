# V2版本处理速度变慢 - 导出日志到本地

> **目的**：将V2处理日志和性能日志导出到文件，并下载到本地分析

---

## 步骤1：在服务器上导出日志到文件

### 导出V2处理日志

**命令1：导出最近的V2处理日志**

```bash
sudo journalctl -u beatsync -n 2000 --no-pager | grep -A30 "V2" > /tmp/v2_processing_log.txt && echo "V2 log exported to /tmp/v2_processing_log.txt"
```

**说明**：
- 查看最近2000条日志
- 过滤包含"V2"的行及其后30行
- 保存到 `/tmp/v2_processing_log.txt`

---

**命令2：导出特定时间段的V2处理日志**

```bash
sudo journalctl -u beatsync --since="2025-12-02 17:00:00" --until="2025-12-03 15:00:00" --no-pager | grep -A30 "V2" > /tmp/v2_processing_log_dec2_3.txt && echo "V2 log exported to /tmp/v2_processing_log_dec2_3.txt"
```

**说明**：
- 导出12月2日17:00到12月3日15:00的日志
- 保存到 `/tmp/v2_processing_log_dec2_3.txt`

---

**命令3：导出今天的V2处理日志**

```bash
sudo journalctl -u beatsync --since="today" --no-pager | grep -A30 "V2" > /tmp/v2_processing_log_today.txt && echo "V2 log exported to /tmp/v2_processing_log_today.txt"
```

**说明**：
- 导出今天的日志
- 保存到 `/tmp/v2_processing_log_today.txt`

---

### 导出性能日志

**命令4：导出性能日志**

```bash
tail -500 /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2" > /tmp/v2_performance_log.txt && echo "Performance log exported to /tmp/v2_performance_log.txt"
```

**说明**：
- 查看性能日志文件的最后500行
- 过滤包含"V2"的行及其后10行
- 保存到 `/tmp/v2_performance_log.txt`

---

**命令5：导出所有性能日志（包含V2）**

```bash
cat /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2" > /tmp/v2_performance_log_all.txt && echo "All performance log exported to /tmp/v2_performance_log_all.txt"
```

**说明**：
- 导出所有性能日志文件
- 过滤包含"V2"的行及其后10行
- 保存到 `/tmp/v2_performance_log_all.txt`

---

## 步骤2：从服务器下载日志到本地

### 使用SCP下载（推荐）

**命令6：下载V2处理日志**

```bash
scp ubuntu@124.221.58.149:/tmp/v2_processing_log.txt ~/Downloads/
```

**说明**：
- 从服务器下载V2处理日志
- 保存到本地的 `~/Downloads/` 目录

---

**命令7：下载性能日志**

```bash
scp ubuntu@124.221.58.149:/tmp/v2_performance_log.txt ~/Downloads/
```

**说明**：
- 从服务器下载性能日志
- 保存到本地的 `~/Downloads/` 目录

---

**命令8：下载所有导出的日志**

```bash
scp ubuntu@124.221.58.149:/tmp/v2_*.txt ~/Downloads/
```

**说明**：
- 下载所有以 `v2_` 开头的日志文件
- 保存到本地的 `~/Downloads/` 目录

---

### 使用SFTP下载

**命令9：使用SFTP下载**

```bash
sftp ubuntu@124.221.58.149
```

**进入SFTP后执行**：
```
cd /tmp
get v2_processing_log.txt ~/Downloads/
get v2_performance_log.txt ~/Downloads/
exit
```

---

## 一键导出和下载脚本

### 在服务器上执行（导出日志）

```bash
sudo journalctl -u beatsync -n 2000 --no-pager | grep -A30 "V2" > /tmp/v2_processing_log.txt && tail -500 /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2" > /tmp/v2_performance_log.txt && echo "Logs exported: /tmp/v2_processing_log.txt and /tmp/v2_performance_log.txt"
```

---

### 在本地执行（下载日志）

```bash
scp ubuntu@124.221.58.149:/tmp/v2_processing_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/v2_performance_log.txt ~/Downloads/ && echo "Logs downloaded to ~/Downloads/"
```

---

## 完整流程

### 步骤1：在服务器上导出日志

```bash
sudo journalctl -u beatsync -n 2000 --no-pager | grep -A30 "V2" > /tmp/v2_processing_log.txt && tail -500 /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2" > /tmp/v2_performance_log.txt && ls -lh /tmp/v2_*.txt
```

**说明**：
- 导出V2处理日志和性能日志
- 显示文件大小，确认导出成功

---

### 步骤2：在本地下载日志

```bash
scp ubuntu@124.221.58.149:/tmp/v2_processing_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/v2_performance_log.txt ~/Downloads/ && ls -lh ~/Downloads/v2_*.txt
```

**说明**：
- 下载两个日志文件
- 显示文件大小，确认下载成功

---

## 注意事项

### 文件权限

**如果遇到权限问题**：

```bash
# 在服务器上修改文件权限
sudo chmod 644 /tmp/v2_*.txt
```

---

### 文件大小

**检查文件大小**：

```bash
# 在服务器上检查
ls -lh /tmp/v2_*.txt

# 在本地检查
ls -lh ~/Downloads/v2_*.txt
```

---

### 如果文件太大

**如果日志文件太大，可以压缩**：

```bash
# 在服务器上压缩
cd /tmp && tar -czf v2_logs.tar.gz v2_*.txt && echo "Logs compressed to /tmp/v2_logs.tar.gz"

# 在本地下载压缩文件
scp ubuntu@124.221.58.149:/tmp/v2_logs.tar.gz ~/Downloads/

# 在本地解压
cd ~/Downloads && tar -xzf v2_logs.tar.gz
```

---

## 总结

### 最常用的命令组合

**在服务器上（导出）**：
```bash
sudo journalctl -u beatsync -n 2000 --no-pager | grep -A30 "V2" > /tmp/v2_processing_log.txt && tail -500 /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2" > /tmp/v2_performance_log.txt && ls -lh /tmp/v2_*.txt
```

**在本地（下载）**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_processing_log.txt ~/Downloads/ && scp ubuntu@124.221.58.149:/tmp/v2_performance_log.txt ~/Downloads/ && ls -lh ~/Downloads/v2_*.txt
```

---

**最后更新**：2025-12-03

