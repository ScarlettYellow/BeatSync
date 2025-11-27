# 后端连接超时问题解决

## 问题现象
- `curl http://localhost:8000/api/health` 立即失败
- 显示 "Failed to connect to localhost port 8000"
- 前端显示 "无法连接到后端服务"

## 原因
服务正在启动过程中，但清理操作（清理旧文件、旧任务）可能耗时较长，导致服务启动慢。

## 解决方案

### 方案1：使用智能启动脚本（推荐）

```bash
cd web_service/backend
./start_and_wait.sh
```

这个脚本会：
1. 后台启动服务
2. 等待服务完全启动（最多30秒）
3. 确认服务响应后才提示成功
4. 显示实时日志

### 方案2：手动启动并等待

```bash
cd web_service/backend
./quick_start.sh
```

然后**等待看到以下信息**：
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

**重要**：必须等到看到 "Application startup complete" 才能测试！

### 方案3：检查服务状态

如果服务已经启动，在新终端测试：
```bash
# 等待3-5秒后测试
sleep 5
curl http://localhost:8000/api/health
```

## 验证服务已启动

看到以下信息表示服务已就绪：
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

然后测试：
```bash
curl http://localhost:8000/api/health
```

应该返回：`{"status":"ok"}`

## 性能优化

已优化：
- ✅ 清理操作移至后台线程（不阻塞启动）
- ✅ 导入时间从数秒降至0.5秒
- ✅ 服务可以立即开始监听请求

## 常见问题

**Q: 为什么启动需要几秒钟？**
A: 需要加载任务状态和初始化，这是正常的。现在已优化，通常3-5秒内就能启动。

**Q: 如何查看启动日志？**
A: 使用 `start_and_wait.sh` 会自动显示日志，或手动查看：
```bash
tail -f /tmp/beatsync_backend.log
```

