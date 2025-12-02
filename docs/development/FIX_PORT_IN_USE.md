# 修复端口占用问题

> **问题**：启动脚本报错 "Address already in use"，服务无法启动

---

## 问题原因

**错误信息**：
```
ERROR:    [Errno 48] Address already in use
```

**原因**：
- 端口8000或8080已被之前的服务占用
- 之前的服务进程没有正确停止
- 多次启动脚本导致多个进程占用同一端口

---

## 解决方案

### 方案1：使用停止脚本（推荐）

**创建了专门的停止脚本**：

```bash
cd web_service
./stop_local.sh
```

**功能**：
- 自动查找并停止所有后端和前端服务
- 检查端口占用情况
- 显示详细的停止信息

---

### 方案2：启动脚本自动检查（已修复）

**启动脚本现在会自动检查端口占用**：

```bash
cd web_service
./start_local_mobile.sh
# 或
./start_local.sh
```

**功能**：
- 启动前自动检查端口8000和8080
- 如果被占用，自动停止旧服务
- 等待2秒后重新启动

---

### 方案3：手动停止（临时）

**如果脚本无法自动停止，可以手动停止**：

```bash
# 停止后端服务
ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}' | xargs kill

# 停止前端服务
ps aux | grep "http.server 8080" | grep -v grep | awk '{print $2}' | xargs kill

# 检查端口占用
lsof -i :8000
lsof -i :8080
```

---

## 使用方法

### 正常启动流程

1. **停止旧服务**（如果存在）：
   ```bash
   cd web_service
   ./stop_local.sh
   ```

2. **启动新服务**：
   ```bash
   ./start_local_mobile.sh
   ```

3. **验证服务运行**：
   - 后端：`http://localhost:8000/api/health`
   - 前端：`http://localhost:8080`
   - 手机：`http://<电脑IP>:8080`

---

### 如果服务仍然无法启动

**检查步骤**：

1. **查看后端日志**：
   ```bash
   tail -50 web_service/backend.log
   ```

2. **检查端口占用**：
   ```bash
   lsof -i :8000
   lsof -i :8080
   ```

3. **强制停止所有相关进程**：
   ```bash
   # 强制停止
   ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}' | xargs kill -9
   ps aux | grep "http.server 8080" | grep -v grep | awk '{print $2}' | xargs kill -9
   ```

4. **重新启动**：
   ```bash
   ./start_local_mobile.sh
   ```

---

## 预防措施

### 1. 使用停止脚本

**每次停止服务时使用停止脚本**：
```bash
./stop_local.sh
```

**而不是直接关闭终端**，这样可以：
- 确保服务正确停止
- 释放端口
- 避免僵尸进程

---

### 2. 检查服务状态

**启动前检查**：
```bash
# 检查是否有服务在运行
ps aux | grep -E "(uvicorn|http.server)" | grep -v grep

# 检查端口占用
lsof -i :8000
lsof -i :8080
```

---

### 3. 使用Ctrl+C停止

**在运行脚本的终端按 `Ctrl+C`**：
- 脚本会优雅地停止所有服务
- 释放端口
- 清理进程

---

## 常见问题

### 问题1：停止脚本无法停止服务

**解决方法**：
```bash
# 查找进程ID
ps aux | grep "uvicorn main:app" | grep -v grep

# 强制停止（替换<PID>为实际进程ID）
kill -9 <PID>
```

---

### 问题2：端口仍然被占用

**可能原因**：
- 进程没有完全停止
- 有其他程序占用端口

**解决方法**：
```bash
# 查看占用端口的进程
lsof -i :8000
lsof -i :8080

# 停止占用进程（替换<PID>为实际进程ID）
kill -9 <PID>
```

---

### 问题3：服务启动后立即停止

**可能原因**：
- 代码错误
- 依赖缺失
- 配置错误

**解决方法**：
```bash
# 查看详细日志
tail -100 web_service/backend.log
tail -100 web_service/frontend.log

# 检查Python依赖
pip list | grep -E "(uvicorn|fastapi)"

# 手动启动后端查看错误
cd web_service/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 总结

**已修复的问题**：
- ✅ 启动脚本自动检查端口占用
- ✅ 自动停止旧服务
- ✅ 创建了专门的停止脚本

**推荐流程**：
1. 停止旧服务：`./stop_local.sh`
2. 启动新服务：`./start_local_mobile.sh`
3. 使用完毕后按 `Ctrl+C` 停止

**如果仍有问题**：
- 查看日志文件
- 检查端口占用
- 手动停止进程

---

**最后更新**：2025-12-02

