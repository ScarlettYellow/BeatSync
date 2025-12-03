# V2性能日志为空 - 检查命令

> **问题**：性能日志下载后为空文件

---

## 检查步骤

### 步骤1：检查性能日志文件是否存在

**在服务器上执行**：
```bash
ls -lh /opt/beatsync/outputs/logs/performance_*.log
```

**预期结果**：
- 应该看到类似 `performance_20251203.log` 的文件
- 文件大小应该 > 0

---

### 步骤2：检查文件权限

**在服务器上执行**：
```bash
ls -l /opt/beatsync/outputs/logs/
```

**预期结果**：
- 文件应该可读（`-rw-r--r--` 或类似）

---

### 步骤3：查看性能日志文件内容

**在服务器上执行**：
```bash
# 查看最后50行
tail -50 /opt/beatsync/outputs/logs/performance_*.log

# 或者查看所有内容
cat /opt/beatsync/outputs/logs/performance_*.log | head -100
```

**如果文件为空或不存在**：
- 说明性能日志记录功能可能没有正常工作
- 或者日志文件路径配置错误

---

### 步骤4：检查性能日志记录代码

**在服务器上执行**：
```bash
# 查看性能日志模块
cat /opt/beatsync/web_service/backend/performance_logger.py | grep -A10 "V2"
```

**或者查看是否有V2相关的日志记录**：
```bash
# 查看所有日志文件
find /opt/beatsync/outputs/logs/ -name "*.log" -type f -exec ls -lh {} \;
```

---

### 步骤5：检查systemd日志中的性能信息

**在服务器上执行**：
```bash
# 查看最近的性能相关日志
sudo journalctl -u beatsync -n 500 --no-pager | grep -i "performance\|资源使用\|CPU\|内存"
```

---

## 如果性能日志确实为空

### 可能原因

1. **性能日志记录功能未启用**
   - `performance_logger.py` 可能没有在V2处理时记录日志

2. **日志文件路径错误**
   - 日志文件可能写到了其他位置

3. **权限问题**
   - 服务可能没有写入日志文件的权限

4. **日志记录代码问题**
   - 可能只记录了总体性能，没有记录V2单独的性能

---

## 替代诊断方法

### 方法1：使用systemd日志

**在服务器上执行**：
```bash
# 查看V2处理相关的所有日志
sudo journalctl -u beatsync --since="2025-12-03 14:00:00" --until="2025-12-03 15:00:00" --no-pager | grep -A20 "V2版本处理"
```

---

### 方法2：实时监控CPU使用率

**在服务器上执行**（在处理任务时）：
```bash
# 监控所有进程的CPU使用率
top -b -n 60 -d 1 | grep -E "PID|python|ffmpeg" > /tmp/cpu_usage.log

# 然后下载
scp ubuntu@124.221.58.149:/tmp/cpu_usage.log ~/Downloads/
```

---

### 方法3：检查FFmpeg实际使用的线程数

**在服务器上执行**（在处理任务时）：
```bash
# 查看FFmpeg进程的线程数
ps aux | grep ffmpeg | grep -v grep | awk '{print $2}' | xargs -I {} sh -c 'echo "PID: {}"; ps -T -p {} | wc -l'
```

---

## 导出替代诊断信息

### 导出systemd日志中的性能信息

**在服务器上执行**：
```bash
# 导出包含性能信息的日志
sudo journalctl -u beatsync --since="2025-12-03 14:00:00" --no-pager | grep -E "资源使用|CPU|内存|V2版本处理" > /tmp/v2_performance_from_journal.txt && ls -lh /tmp/v2_performance_from_journal.txt
```

**在本地下载**：
```bash
scp ubuntu@124.221.58.149:/tmp/v2_performance_from_journal.txt ~/Downloads/
```

---

**最后更新**：2025-12-03

