# 端口8000被占用问题解决指南

## 问题现象
启动后端服务时出现错误：
```
ERROR: [Errno 48] Address already in use
```

## 原因
端口8000已被其他进程占用，通常是：
1. 后端服务已经在运行（最常见）
2. 其他程序占用了8000端口

## 解决方案

### 方案1：使用已运行的服务（推荐）

如果后端服务已经在运行，**无需重启**，直接使用即可：
1. 打开浏览器访问 `http://localhost:8000/docs` 查看API文档
2. 如果API文档能打开，说明服务正常运行
3. 直接测试上传功能

### 方案2：停止并重启服务

如果需要重启服务：

```bash
# 方法1：使用停止脚本（推荐）
cd web_service/backend
./stop_server.sh
./start_server.sh

# 方法2：使用重启脚本
cd web_service/backend
./restart_server.sh

# 方法3：手动停止
# 找到占用端口的进程
lsof -i :8000
# 停止进程（替换PID为实际进程ID）
kill <PID>
```

### 方案3：使用其他端口

如果必须使用8000端口，但无法停止现有服务：

修改 `web_service/backend/start_server.sh`：
```bash
# 将端口改为8001
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

同时修改前端 `web_service/frontend/script.js` 中的 `API_BASE_URL`：
```javascript
const backendUrl = 'http://localhost:8001';
```

## 快速诊断

```bash
# 检查端口占用
lsof -i :8000

# 测试服务是否正常
curl http://localhost:8000/api/health

# 查看API文档
open http://localhost:8000/docs
```

## 常见问题

**Q: 服务显示已启动，但无法访问？**
A: 可能是服务崩溃了但端口仍被占用，使用 `stop_server.sh` 强制停止后重启。

**Q: 如何确认服务正常运行？**
A: 访问 `http://localhost:8000/docs`，如果能看到API文档页面，说明服务正常。

