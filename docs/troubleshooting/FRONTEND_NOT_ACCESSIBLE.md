# 前端服务无法访问问题解决

## 问题现象
- 浏览器访问 `http://localhost:8080/` 显示 "ERR_CONNECTION_REFUSED"
- 后端服务（8000端口）正常运行，但前端（8080端口）无法访问

## 原因
前端服务没有启动。前端和后端是分开的服务，需要分别启动。

## 解决方案

### 方案1：使用前端启动脚本（推荐）

```bash
cd web_service/frontend
./start_frontend.sh
```

### 方案2：使用一键启动脚本（同时启动前后端）

```bash
cd web_service
./start_local.sh
```

### 方案3：手动启动前端

在**新终端窗口**中：

```bash
cd web_service/frontend
python3 -m http.server 8080
```

## 验证服务已启动

启动后应该看到：
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

然后访问：`http://localhost:8080/`

## 完整启动流程

**终端1 - 启动后端：**
```bash
cd web_service/backend
./start_and_wait.sh
```

**终端2 - 启动前端：**
```bash
cd web_service/frontend
./start_frontend.sh
```

**浏览器：**
访问 `http://localhost:8080/`

## 常见问题

**Q: 为什么需要两个服务？**
A: 前端是静态文件服务器（HTML/CSS/JS），后端是API服务器（FastAPI）。它们需要分别运行。

**Q: 可以只启动一个吗？**
A: 可以，但功能不完整：
- 只有后端：可以访问API文档（`http://localhost:8000/docs`），但没有网页界面
- 只有前端：可以打开页面，但无法上传和处理视频（后端未运行）

**Q: 端口冲突怎么办？**
A: 如果8080端口被占用，可以修改端口：
```bash
python3 -m http.server 8081
```
然后访问 `http://localhost:8081/`

