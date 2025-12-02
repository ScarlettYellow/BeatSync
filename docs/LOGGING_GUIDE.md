# 后端日志查看指南

> **目的**：说明如何查看后端处理日志

---

## 日志类型

### 1. systemd服务日志（主要日志）

**位置**：systemd journal

**内容**：
- FastAPI服务启动/停止日志
- API请求日志
- 错误日志
- 标准输出和标准错误

**查看命令**：

```bash
# 查看最近50条日志
sudo journalctl -u beatsync -n 50

# 实时查看日志（跟随模式）
sudo journalctl -u beatsync -f

# 查看今天的日志
sudo journalctl -u beatsync --since today

# 查看最近1小时的日志
sudo journalctl -u beatsync --since "1 hour ago"

# 查看指定时间范围的日志
sudo journalctl -u beatsync --since "2025-12-02 10:00:00" --until "2025-12-02 12:00:00"

# 查看错误日志
sudo journalctl -u beatsync -p err

# 查看警告及以上级别的日志
sudo journalctl -u beatsync -p warning
```

---

### 2. 性能日志（处理过程详细日志）

**位置**：`/opt/beatsync/outputs/logs/`

**文件格式**：`performance_YYYYMMDD.log`

**内容**：
- 处理任务详细步骤
- 每个步骤的耗时
- 资源使用情况（CPU、内存）
- 文件操作记录

**查看命令**：

```bash
# 查看今天的性能日志
cat /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log

# 实时查看性能日志
tail -f /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log

# 查看最近的性能日志
ls -lt /opt/beatsync/outputs/logs/ | head -10

# 查看指定日期的日志
cat /opt/beatsync/outputs/logs/performance_20251202.log

# 搜索特定任务ID的日志
grep "task_id" /opt/beatsync/outputs/logs/performance_*.log
```

---

### 3. Nginx日志

**位置**：
- 访问日志：`/var/log/nginx/access.log`
- 错误日志：`/var/log/nginx/error.log`

**内容**：
- HTTP/HTTPS请求记录
- 错误信息
- 访问统计

**查看命令**：

```bash
# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# 查看最近的错误
sudo tail -n 100 /var/log/nginx/error.log
```

---

## 常用日志查看场景

### 场景1：查看服务是否正常运行

```bash
# 查看服务状态
sudo systemctl status beatsync

# 查看最近10条日志
sudo journalctl -u beatsync -n 10
```

---

### 场景2：查看处理任务的详细过程

```bash
# 实时查看服务日志（可以看到任务提交和处理过程）
sudo journalctl -u beatsync -f

# 在另一个终端查看性能日志
tail -f /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log
```

---

### 场景3：排查错误

```bash
# 查看错误日志
sudo journalctl -u beatsync -p err -n 50

# 查看警告日志
sudo journalctl -u beatsync -p warning -n 50

# 查看Nginx错误日志
sudo tail -n 100 /var/log/nginx/error.log
```

---

### 场景4：查看特定任务的处理日志

```bash
# 假设任务ID是 abc123
# 在systemd日志中搜索
sudo journalctl -u beatsync | grep "abc123"

# 在性能日志中搜索
grep "abc123" /opt/beatsync/outputs/logs/performance_*.log
```

---

### 场景5：查看API请求日志

```bash
# 查看最近的API请求
sudo journalctl -u beatsync -n 100 | grep -E "POST|GET|PUT|DELETE"

# 查看Nginx访问日志（包含所有HTTP请求）
sudo tail -f /var/log/nginx/access.log
```

---

## 日志格式说明

### systemd日志格式

```
时间戳 主机名 服务名[进程ID]: 日志内容
```

**示例**：
```
Dec 02 14:12:27 VM-0-11-ubuntu python3[147832]: INFO: Started server process [147832]
Dec 02 14:12:27 VM-0-11-ubuntu python3[147832]: INFO: Application startup complete.
```

---

### 性能日志格式

```
时间戳 | 级别 | 消息内容
```

**示例**：
```
2025-12-02 14:13:43 | INFO | [task_id] [operation] 开始处理
2025-12-02 14:13:45 | INFO | [task_id] [operation] 步骤: 提取音频 | 耗时: 2.3秒
```

---

## 日志文件位置总结

### 服务器上的日志位置

```
/opt/beatsync/
├── outputs/
│   └── logs/
│       └── performance_YYYYMMDD.log  # 性能日志
├── logs/                              # 其他日志（如果有）
└── web_service/backend/
    └── main.py                        # 主程序（日志输出到systemd）

/var/log/
├── nginx/
│   ├── access.log                    # Nginx访问日志
│   └── error.log                     # Nginx错误日志
└── journal/                          # systemd日志（通过journalctl访问）
```

---

## 快速参考

### 最常用的命令

```bash
# 1. 查看服务状态
sudo systemctl status beatsync

# 2. 实时查看服务日志
sudo journalctl -u beatsync -f

# 3. 查看今天的性能日志
tail -f /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log

# 4. 查看最近的错误
sudo journalctl -u beatsync -p err -n 50
```

---

## 日志清理

### 清理旧日志

**systemd日志**：
```bash
# 查看日志占用空间
sudo journalctl --disk-usage

# 只保留最近7天的日志
sudo journalctl --vacuum-time=7d

# 限制日志最大大小为500MB
sudo journalctl --vacuum-size=500M
```

**性能日志**：
```bash
# 删除7天前的性能日志
find /opt/beatsync/outputs/logs/ -name "performance_*.log" -mtime +7 -delete

# 或手动删除
rm /opt/beatsync/outputs/logs/performance_20251201.log
```

**Nginx日志**：
```bash
# 清理旧的Nginx日志（需要配置logrotate）
sudo logrotate -f /etc/logrotate.d/nginx
```

---

## 故障排查示例

### 示例1：服务无法启动

```bash
# 查看服务状态
sudo systemctl status beatsync

# 查看详细错误
sudo journalctl -u beatsync -n 100
```

---

### 示例2：处理任务失败

```bash
# 查看任务相关的日志
sudo journalctl -u beatsync | grep "task_id"

# 查看性能日志中的错误
grep "ERROR\|失败\|Exception" /opt/beatsync/outputs/logs/performance_*.log
```

---

### 示例3：上传失败

```bash
# 查看上传相关的日志
sudo journalctl -u beatsync | grep -i "upload"

# 查看Nginx错误日志
sudo tail -n 50 /var/log/nginx/error.log
```

---

## 日志级别

### systemd日志级别

- **emerg**：紧急情况
- **alert**：需要立即处理
- **crit**：严重错误
- **err**：错误
- **warning**：警告
- **notice**：通知
- **info**：信息（默认）
- **debug**：调试

### 查看不同级别的日志

```bash
# 只查看错误及以上级别
sudo journalctl -u beatsync -p err

# 查看警告及以上级别
sudo journalctl -u beatsync -p warning

# 查看所有级别（包括debug）
sudo journalctl -u beatsync -p debug
```

---

## 远程查看日志

### 通过SSH查看

```bash
# SSH登录服务器
ssh ubuntu@124.221.58.149

# 然后执行日志查看命令
sudo journalctl -u beatsync -f
```

---

## 总结

**主要日志位置**：
1. **systemd日志**：`sudo journalctl -u beatsync`（最常用）
2. **性能日志**：`/opt/beatsync/outputs/logs/performance_*.log`
3. **Nginx日志**：`/var/log/nginx/error.log` 和 `/var/log/nginx/access.log`

**最常用的命令**：
- `sudo journalctl -u beatsync -f` - 实时查看服务日志
- `tail -f /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log` - 实时查看性能日志

---

**最后更新**：2025-12-02

