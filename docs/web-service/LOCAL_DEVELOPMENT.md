# 本地开发指南

## 一、本地开发 vs 线上部署

✅ **可以同时进行**：本地开发和线上部署是**完全独立**的，互不影响。

- **本地开发**：在您的电脑上运行，用于测试和开发
- **线上部署**：在Render服务器上运行，供用户访问

## 二、本地开发环境设置

### 2.1 前置要求

- Python 3.11+
- pip（Python包管理器）
- 已安装项目依赖（librosa, numpy, soundfile, opencv-python等）

### 2.2 安装后端依赖

```bash
cd web_service/backend
pip install -r requirements.txt
```

### 2.3 启动后端服务

#### 方法1：使用uvicorn直接启动（推荐）

```bash
cd web_service/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**参数说明**：
- `--host 0.0.0.0`：允许从任何IP访问（包括localhost）
- `--port 8000`：后端服务端口
- `--reload`：自动重载（代码修改后自动重启，开发时很有用）

#### 方法2：使用Python启动

```bash
cd web_service/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方法3：使用启动脚本

```bash
cd web_service/backend
chmod +x start_server.sh  # 如果还没有执行权限
./start_server.sh
```

### 2.4 启动前端服务

#### 方法1：使用Python HTTP服务器（推荐）

```bash
cd web_service/frontend
python3 -m http.server 8080
```

然后在浏览器中访问：`http://localhost:8080`

#### 方法2：直接在浏览器中打开

直接双击 `web_service/frontend/index.html` 文件，在浏览器中打开。

**注意**：方法2可能会有CORS问题，建议使用方法1。

#### 方法3：使用其他HTTP服务器

```bash
# 使用Node.js的http-server（如果已安装）
cd web_service/frontend
npx http-server -p 8080

# 或使用PHP内置服务器
cd web_service/frontend
php -S localhost:8080
```

## 三、本地开发配置

### 3.1 前端自动检测本地环境

前端代码已经自动检测本地环境：

```javascript
// 在 script.js 中
const API_BASE_URL = (() => {
    // 如果是本地开发环境
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';  // 本地后端
    }
    // 生产环境：使用Render后端URL
    return 'https://beatsync-backend-asha.onrender.com';
})();
```

**这意味着**：
- 在 `localhost:8080` 访问前端 → 自动连接 `localhost:8000` 后端
- 在线上域名访问前端 → 自动连接Render后端

### 3.2 后端CORS配置

后端已配置允许本地开发：

```python
# 在 main.py 中
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
```

**本地开发时**：默认允许所有来源（`*`），包括 `http://localhost:8080`

**生产环境**：通过环境变量 `ALLOWED_ORIGINS` 限制允许的域名

## 四、本地开发流程

### 4.1 启动服务

**终端1 - 启动后端**：
```bash
cd web_service/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**终端2 - 启动前端**：
```bash
cd web_service/frontend
python3 -m http.server 8080
```

### 4.2 访问应用

在浏览器中打开：`http://localhost:8080`

### 4.3 测试功能

1. 上传两个测试视频（dance和bgm）
2. 点击"开始处理"
3. 观察处理进度和日志
4. 下载处理结果

### 4.4 查看日志

**后端日志**：在启动后端的终端中查看

**性能日志**：查看 `outputs/logs/performance_YYYYMMDD.log` 文件

**API文档**：访问 `http://localhost:8000/docs` 查看Swagger文档

## 五、本地开发的优势

### 5.1 快速迭代

- ✅ 代码修改后立即生效（使用 `--reload` 参数）
- ✅ 不需要等待部署
- ✅ 可以快速测试新功能

### 5.2 调试方便

- ✅ 可以直接查看控制台输出
- ✅ 可以使用调试器（如pdb）
- ✅ 可以查看详细的错误堆栈

### 5.3 性能测试

- ✅ 本地性能通常比Render免费层更好
- ✅ 可以测试处理速度
- ✅ 可以验证性能优化效果

### 5.4 成本节约

- ✅ 本地开发不消耗Render资源
- ✅ 可以无限次测试
- ✅ 不影响线上服务

## 六、常见问题

### 6.1 端口被占用

**问题**：`Address already in use`

**解决**：
```bash
# 查找占用端口的进程
lsof -i :8000  # 查找占用8000端口的进程
lsof -i :8080  # 查找占用8080端口的进程

# 杀死进程
kill -9 <PID>  # 替换<PID>为实际进程ID

# 或使用其他端口
uvicorn main:app --host 0.0.0.0 --port 8001  # 使用8001端口
```

### 6.2 CORS错误

**问题**：`Access to fetch at 'http://localhost:8000' from origin 'http://localhost:8080' has been blocked by CORS policy`

**解决**：
- 确保后端已启动
- 检查后端CORS配置（应该允许localhost）
- 确保前端通过HTTP服务器访问（不是直接打开HTML文件）

### 6.3 依赖缺失

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决**：
```bash
cd web_service/backend
pip install -r requirements.txt
```

### 6.4 处理失败

**问题**：本地处理失败，但线上正常

**可能原因**：
- 本地缺少ffmpeg（视频处理需要）
- 本地Python环境不同
- 本地文件路径问题

**解决**：
- 确保已安装ffmpeg：`ffmpeg -version`
- 确保Python版本一致：`python --version`
- 检查文件路径是否正确

## 七、本地开发最佳实践

### 7.1 使用虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r web_service/backend/requirements.txt
```

### 7.2 使用环境变量

创建 `.env` 文件（不要提交到Git）：

```bash
# .env
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
DEBUG=True
```

### 7.3 代码热重载

使用 `--reload` 参数，代码修改后自动重启：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 7.4 日志调试

在代码中添加日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

## 八、总结

✅ **可以同时进行本地开发和线上部署**

**本地开发流程**：
1. 启动后端：`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
2. 启动前端：`python3 -m http.server 8080`
3. 访问：`http://localhost:8080`
4. 测试功能，查看日志

**优势**：
- 快速迭代，立即生效
- 调试方便，查看详细日志
- 成本节约，不消耗线上资源
- 性能测试，验证优化效果

**注意事项**：
- 确保已安装所有依赖
- 确保已安装ffmpeg
- 使用HTTP服务器访问前端（不要直接打开HTML文件）

