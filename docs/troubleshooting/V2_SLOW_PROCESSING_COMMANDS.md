# V2版本处理速度变慢 - 诊断命令（无中文）

> **目的**：提供不含中文的命令，用于在VNC终端中执行

---

## 查看V2版本详细处理日志

### 命令1：查看最近的V2处理日志

```bash
sudo journalctl -u beatsync -n 1000 --no-pager | grep -A30 "V2" | tail -200
```

**说明**：
- 查看最近1000条日志
- 过滤包含"V2"的行及其后30行
- 显示最后200行

---

### 命令2：查看特定时间段的V2处理日志

```bash
sudo journalctl -u beatsync --since="2025-12-02 17:00:00" --until="2025-12-02 18:00:00" --no-pager | grep -A30 "V2"
```

**说明**：
- 查看12月2日17:00-18:00的日志
- 过滤包含"V2"的行及其后30行

---

### 命令3：查看今天的V2处理日志

```bash
sudo journalctl -u beatsync --since="today" --no-pager | grep -A30 "V2" | tail -200
```

**说明**：
- 查看今天的日志
- 过滤包含"V2"的行及其后30行
- 显示最后200行

---

### 命令4：查看V2处理时间信息

```bash
sudo journalctl -u beatsync -n 1000 --no-pager | grep -E "V2.*time|V2.*complete|V2.*elapsed" | tail -50
```

**说明**：
- 查看包含V2和时间相关的日志
- 显示最后50行

---

### 命令5：查看V2处理的所有步骤

```bash
sudo journalctl -u beatsync -n 2000 --no-pager | grep -B5 -A25 "V2 version" | tail -300
```

**说明**：
- 查看最近2000条日志
- 查找"V2 version"及其前后内容
- 显示最后300行

---

## 对比不同日期的处理日志

### 命令6：对比12月2日和12月3日的处理时间

```bash
echo "=== Dec 2 ===" && sudo journalctl -u beatsync --since="2025-12-02 17:00:00" --until="2025-12-02 18:00:00" --no-pager | grep -E "elapsed|time|complete" | head -20 && echo "=== Dec 3 ===" && sudo journalctl -u beatsync --since="2025-12-03 14:00:00" --until="2025-12-03 15:00:00" --no-pager | grep -E "elapsed|time|complete" | head -20
```

**说明**：
- 对比12月2日和12月3日的处理时间
- 显示包含"elapsed"、"time"、"complete"的日志

---

## 查看性能日志文件

### 命令7：查看性能日志

```bash
tail -200 /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2"
```

**说明**：
- 查看性能日志文件的最后200行
- 过滤包含"V2"的行及其后10行

---

### 命令8：查看特定任务的处理日志

```bash
tail -500 /opt/beatsync/outputs/logs/performance_*.log | grep -B5 -A20 "36d7e5c7-cf1c-4a18-9578-fa8a72767486"
```

**说明**：
- 查看特定任务ID的处理日志
- 替换任务ID为实际的任务ID

---

## 检查代码版本

### 命令9：检查当前代码版本

```bash
cd /opt/beatsync && git log --oneline -10
```

**说明**：
- 查看最近的10个commit

---

### 命令10：检查V2版本的FFmpeg参数

```bash
cd /opt/beatsync && grep -n "preset\|crf\|faststart\|movflags" beatsync_badcase_fix_trim_v2.py | head -20
```

**说明**：
- 查看V2版本的FFmpeg参数设置

---

## 检查系统资源

### 命令11：检查CPU和内存使用

```bash
top -bn1 | head -20
```

**说明**：
- 查看CPU和内存使用情况

---

### 命令12：检查磁盘空间

```bash
df -h
```

**说明**：
- 查看磁盘空间使用情况

---

## 检查处理进程

### 命令13：查看正在运行的FFmpeg进程

```bash
ps aux | grep ffmpeg
```

**说明**：
- 查看是否有FFmpeg进程正在运行

---

### 命令14：查看Python处理进程

```bash
ps aux | grep python | grep beatsync
```

**说明**：
- 查看BeatSync相关的Python进程

---

## 总结

**最常用的命令**：

1. **查看最近的V2处理日志**：
```bash
sudo journalctl -u beatsync -n 1000 --no-pager | grep -A30 "V2" | tail -200
```

2. **查看性能日志**：
```bash
tail -200 /opt/beatsync/outputs/logs/performance_*.log | grep -A10 "V2"
```

3. **检查代码版本**：
```bash
cd /opt/beatsync && git log --oneline -10
```

---

**最后更新**：2025-12-03

