# 后端服务启动问题排查

## 问题现象
- `curl http://localhost:8000/api/health` 连接超时
- 前端显示 "无法连接到后端服务"

## 快速诊断

### 方法1：直接启动查看错误（推荐）

```bash
cd web_service/backend
./quick_start.sh
```

这个脚本会直接启动服务并显示所有输出，可以立即看到错误信息。

### 方法2：检查端口占用

```bash
# 检查8000端口是否被占用
lsof -i :8000

# 如果被占用，停止它
./stop_server.sh
```

### 方法3：检查Python环境

```bash
# 确认Python版本
python3 --version

# 确认uvicorn已安装
python3 -m pip list | grep uvicorn

# 如果没有，安装它
python3 -m pip install uvicorn fastapi
```

## 常见错误及解决

### 错误1：ModuleNotFoundError
**原因**: 缺少依赖
**解决**: 
```bash
cd web_service/backend
pip3 install -r requirements.txt
```

### 错误2：Address already in use
**原因**: 端口被占用
**解决**: 
```bash
./stop_server.sh
./quick_start.sh
```

### 错误3：导入main模块很慢
**原因**: `main.py` 在导入时执行了耗时操作（如加载大量任务状态）
**解决**: 这是正常的，首次启动可能需要几秒钟加载任务状态

## 验证服务已启动

启动后应该看到：
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

然后在新终端测试：
```bash
curl http://localhost:8000/api/health
```

应该返回：`{"status":"ok"}`

