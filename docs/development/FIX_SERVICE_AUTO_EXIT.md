# 修复服务自动终止问题

> **问题**：启动脚本执行后立即退出，服务虽然启动但脚本终止

---

## 问题原因

**原脚本使用 `wait` 命令**：
```bash
wait
```

**问题**：
- `wait` 命令只等待**子进程**（通过 `&` 启动的后台进程）
- 但是当后台进程启动后，它们不再是脚本的直接子进程
- `wait` 立即返回，导致脚本退出

---

## 解决方案

**使用循环检查进程状态**：

```bash
# 保持脚本运行，定期检查服务状态
echo "服务正在运行中，按 Ctrl+C 停止..."
while true; do
    # 检查后端进程是否还在运行
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  后端服务已停止 (PID: $BACKEND_PID)"
        break
    fi
    # 检查前端进程是否还在运行
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  前端服务已停止 (PID: $FRONTEND_PID)"
        break
    fi
    # 等待1秒后再次检查
    sleep 1
done
```

**工作原理**：
- 使用 `while true` 无限循环
- 使用 `kill -0 $PID` 检查进程是否存在
- 每秒检查一次进程状态
- 如果进程停止，自动退出循环
- 按 `Ctrl+C` 触发 `trap`，停止服务并退出

---

## 使用方法

### 启动服务

```bash
cd web_service
./start_local_mobile.sh
```

**或**：

```bash
./start_local.sh
```

### 停止服务

**方法1**：按 `Ctrl+C`
- 脚本会停止所有服务并退出

**方法2**：手动停止
```bash
# 查找进程ID
ps aux | grep -E "(uvicorn|http.server)" | grep -v grep

# 停止服务
kill <BACKEND_PID> <FRONTEND_PID>
```

---

## 验证修复

### 检查脚本是否持续运行

**启动服务后**：
- 脚本应该显示："服务正在运行中，按 Ctrl+C 停止..."
- 脚本不会立即退出
- 终端会保持运行状态

### 检查服务是否正常运行

**在另一个终端**：
```bash
# 检查后端服务
curl http://localhost:8000/api/health

# 检查前端服务
curl http://localhost:8080
```

**在手机浏览器**：
- 访问：`http://<电脑IP>:8080`
- 应该能正常访问前端页面

---

## 常见问题

### 问题1：脚本仍然立即退出

**可能原因**：
- 服务启动失败
- 进程ID获取失败

**解决方法**：
```bash
# 检查服务是否启动
ps aux | grep -E "(uvicorn|http.server)" | grep -v grep

# 查看日志
tail -f backend.log
tail -f frontend.log
```

---

### 问题2：服务启动但无法访问

**可能原因**：
- 端口被占用
- 防火墙阻止

**解决方法**：

**检查端口占用**：
```bash
# macOS
lsof -i :8000
lsof -i :8080

# 如果端口被占用，停止占用进程
kill <PID>
```

**检查防火墙**：
- macOS：系统设置 → 安全性与隐私 → 防火墙
- 确保允许Python和Python3

---

### 问题3：按 Ctrl+C 无法停止服务

**解决方法**：
```bash
# 手动查找并停止进程
ps aux | grep -E "(uvicorn|http.server)" | grep -v grep
kill <PID1> <PID2>
```

---

## 技术细节

### `kill -0` 命令

**作用**：
- 检查进程是否存在
- 不发送任何信号，只检查进程状态
- 如果进程存在，返回0（成功）
- 如果进程不存在，返回非0（失败）

**使用场景**：
- 检查后台进程是否还在运行
- 监控服务状态

---

### `trap` 命令

**作用**：
- 捕获信号（如 `SIGINT`、`SIGTERM`）
- 执行清理操作（如停止服务）

**使用场景**：
- 优雅地停止服务
- 清理临时文件
- 保存状态

---

## 总结

**修复内容**：
- ✅ 替换 `wait` 为 `while true` 循环
- ✅ 添加进程状态检查
- ✅ 保持脚本持续运行
- ✅ 支持优雅停止（Ctrl+C）

**效果**：
- ✅ 脚本不会立即退出
- ✅ 服务持续运行
- ✅ 可以正常访问
- ✅ 可以优雅停止

---

**最后更新**：2025-12-02

