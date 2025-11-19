# 本地开发问题排查指南

## 一、处理失败常见原因

### 1.1 后端服务未启动

**症状**：点击"开始处理"后立即显示"处理失败"或"提交失败"

**检查方法**：
```bash
# 检查端口8000是否被占用
lsof -i :8000

# 或使用诊断脚本
cd web_service
./check_local_setup.sh
```

**解决方法**：
```bash
cd web_service/backend
./start_server.sh
```

### 1.2 依赖缺失

**症状**：后端启动失败，或处理时出现 `ModuleNotFoundError`

**检查方法**：
```bash
cd web_service/backend
pip list | grep -E "fastapi|uvicorn|numpy|librosa|opencv"
```

**解决方法**：
```bash
cd web_service/backend
pip install -r requirements.txt
```

### 1.3 ffmpeg未安装

**症状**：处理失败，后端日志显示 `ffmpeg: command not found`

**检查方法**：
```bash
ffmpeg -version
```

**解决方法**：
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 下载并安装：https://ffmpeg.org/download.html
# 确保ffmpeg在PATH环境变量中
```

### 1.4 CORS错误

**症状**：浏览器控制台显示 `CORS policy` 错误

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 查看Console标签
3. 查找CORS相关错误

**解决方法**：
- 确保前端通过HTTP服务器访问（不是直接打开HTML文件）
- 确保后端CORS配置正确（默认允许localhost）

### 1.5 文件路径问题

**症状**：处理失败，后端日志显示文件不存在

**检查方法**：
```bash
# 检查输出目录
ls -la outputs/

# 检查上传目录
ls -la outputs/web_uploads/
```

**解决方法**：
```bash
# 确保输出目录存在且可写
mkdir -p outputs/web_uploads outputs/web_outputs outputs/logs
chmod -R 755 outputs/
```

### 1.6 导入错误

**症状**：处理失败，后端日志显示 `ImportError` 或 `ModuleNotFoundError`

**检查方法**：
查看后端日志中的错误信息

**解决方法**：
```bash
# 确保在项目根目录运行
cd /Users/scarlett/Projects/BeatSync

# 确保Python路径正确
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 重新安装依赖
cd web_service/backend
pip install -r requirements.txt
```

## 二、诊断步骤

### 步骤1：运行诊断脚本

```bash
cd web_service
./check_local_setup.sh
```

这会检查：
- Python环境
- 依赖包
- ffmpeg
- 服务状态
- 目录权限

### 步骤2：检查后端日志

**查看后端启动终端的输出**，查找：
- `ERROR` 开头的错误信息
- `ImportError` 或 `ModuleNotFoundError`
- `ffmpeg: command not found`
- 文件路径错误

### 步骤3：检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到 **Console** 标签
3. 查找红色错误信息
4. 常见错误：
   - `Failed to fetch` → 后端未启动或CORS问题
   - `404 Not Found` → API路径错误
   - `500 Internal Server Error` → 后端处理错误

### 步骤4：检查网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 点击"开始处理"
4. 查看请求：
   - `/api/process` → 提交任务
   - `/api/status/{task_id}` → 查询状态
5. 点击失败的请求，查看：
   - **Status Code**：HTTP状态码
   - **Response**：错误详情

### 步骤5：查看性能日志

```bash
# 查看最新的性能日志
ls -lt outputs/logs/ | head -5

# 查看日志内容
tail -f outputs/logs/performance_$(date +%Y%m%d).log
```

## 三、常见错误及解决方案

### 错误1：`Failed to fetch`

**原因**：后端服务未启动或无法连接

**解决**：
1. 检查后端是否启动：`lsof -i :8000`
2. 如果未启动，运行：`cd web_service/backend && ./start_server.sh`
3. 确保前端通过HTTP服务器访问（不是直接打开HTML文件）

### 错误2：`处理失败`（无详细错误信息）

**原因**：后端处理过程中出错，但错误信息未传递到前端

**解决**：
1. 查看后端日志，查找 `ERROR` 信息
2. 检查浏览器Network标签，查看 `/api/status/{task_id}` 的响应
3. 查看性能日志：`outputs/logs/performance_*.log`

### 错误3：`ModuleNotFoundError: No module named 'xxx'`

**原因**：Python依赖缺失

**解决**：
```bash
cd web_service/backend
pip install -r requirements.txt
```

### 错误4：`ffmpeg: command not found`

**原因**：ffmpeg未安装或不在PATH中

**解决**：
```bash
# 安装ffmpeg
brew install ffmpeg  # macOS

# 验证安装
ffmpeg -version
```

### 错误5：`导入并行处理器失败`

**原因**：Python路径问题或模块找不到

**解决**：
1. 确保在项目根目录运行后端
2. 检查 `beatsync_parallel_processor.py` 是否存在
3. 检查 `sys.path` 是否包含项目根目录

### 错误6：`处理超时`

**原因**：处理时间过长（超过20分钟）

**解决**：
1. 使用较小的测试视频
2. 检查本地性能（本地通常比Render免费层快）
3. 查看性能日志，找出耗时最长的步骤

## 四、调试技巧

### 4.1 启用详细日志

后端已集成性能日志系统，会自动记录：
- 各步骤耗时
- 资源使用情况
- 错误信息

查看日志：
```bash
tail -f outputs/logs/performance_$(date +%Y%m%d).log
```

### 4.2 使用API文档测试

访问 `http://localhost:8000/docs`，可以：
- 查看所有API接口
- 直接测试API（无需前端）
- 查看请求/响应格式

### 4.3 检查任务状态

如果任务已提交但处理失败，可以：
1. 查看 `/api/status/{task_id}` 的响应
2. 检查 `outputs/task_status.json` 文件
3. 查看后端日志中的错误信息

### 4.4 测试单个组件

**测试后端API**：
```bash
# 测试健康检查
curl http://localhost:8000/

# 测试API文档
open http://localhost:8000/docs
```

**测试文件上传**：
使用API文档页面（`/docs`）直接测试上传接口

## 五、快速排查清单

- [ ] 后端服务是否启动？（`lsof -i :8000`）
- [ ] 前端服务是否启动？（`lsof -i :8080`）
- [ ] 是否通过HTTP服务器访问前端？（不是直接打开HTML）
- [ ] Python依赖是否安装？（`pip list | grep fastapi`）
- [ ] ffmpeg是否安装？（`ffmpeg -version`）
- [ ] 输出目录是否存在且可写？（`ls -la outputs/`）
- [ ] 浏览器控制台是否有错误？（F12 -> Console）
- [ ] 网络请求是否成功？（F12 -> Network）
- [ ] 后端日志是否有错误？（查看启动后端的终端）

## 六、获取帮助

如果以上方法都无法解决问题，请提供：

1. **后端日志**：启动后端的终端输出
2. **浏览器控制台错误**：F12 -> Console中的错误信息
3. **网络请求详情**：F12 -> Network -> 失败的请求
4. **性能日志**：`outputs/logs/performance_*.log` 的相关部分
5. **诊断脚本输出**：`./check_local_setup.sh` 的输出

