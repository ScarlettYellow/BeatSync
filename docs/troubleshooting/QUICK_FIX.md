# 快速修复指南

## 如果看到"处理失败"，请按以下步骤排查：

### 1. 运行诊断脚本（最快）

```bash
cd web_service
./check_local_setup.sh
```

这会自动检查所有常见问题。

### 2. 检查后端是否启动

```bash
# 检查端口8000
lsof -i :8000

# 如果未启动，启动后端
cd web_service/backend
./start_server.sh
```

### 3. 查看浏览器控制台

1. 按 **F12** 打开开发者工具
2. 切换到 **Console** 标签
3. 查找红色错误信息
4. 截图或复制错误信息

### 4. 查看网络请求

1. 按 **F12** 打开开发者工具
2. 切换到 **Network** 标签
3. 点击"开始处理"
4. 查看失败的请求（红色）
5. 点击请求，查看 **Response** 标签中的错误信息

### 5. 查看后端日志

查看启动后端的终端窗口，查找：
- `ERROR` 开头的错误
- `ImportError` 或 `ModuleNotFoundError`
- `ffmpeg: command not found`

### 6. 常见问题快速修复

**问题：后端未启动**
```bash
cd web_service/backend
./start_server.sh
```

**问题：依赖缺失**
```bash
cd web_service/backend
pip install -r requirements.txt
```

**问题：ffmpeg未安装**
```bash
brew install ffmpeg  # macOS
```

**问题：CORS错误**
- 确保前端通过HTTP服务器访问（`python3 -m http.server 8080`）
- 不要直接打开HTML文件

## 需要帮助？

请提供：
1. 诊断脚本输出：`./check_local_setup.sh`
2. 浏览器控制台错误（F12 -> Console）
3. 后端日志（启动后端的终端）
4. 网络请求详情（F12 -> Network -> 失败的请求）
