# BeatSync Web服务

## 目录结构

```
web_service/
├── backend/          # 后端API
│   ├── main.py      # FastAPI主程序
│   └── requirements.txt  # Python依赖
└── frontend/         # 前端页面
    ├── index.html   # 主页面
    ├── style.css    # 样式文件
    └── script.js    # JavaScript逻辑
```

## 快速开始

### 方法1：一键启动（推荐）

```bash
cd web_service
./start_local.sh
```

这会同时启动后端和前端服务。

### 方法2：手动启动

#### 1. 安装后端依赖

```bash
cd web_service/backend
pip install -r requirements.txt
```

#### 2. 启动后端服务

```bash
cd web_service/backend
./start_server.sh
# 或
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 `http://localhost:8000` 启动

#### 3. 启动前端服务

在另一个终端中：

```bash
cd web_service/frontend
python3 -m http.server 8080
```

然后在浏览器中访问 `http://localhost:8080`

## 本地开发 vs 线上部署

✅ **可以同时进行**：本地开发和线上部署完全独立，互不影响。

- **本地开发**：在您的电脑上运行，用于测试和开发
- **线上部署**：在Render服务器上运行，供用户访问

前端会自动检测环境：
- 在 `localhost:8080` 访问 → 自动连接 `localhost:8000` 后端
- 在线上域名访问 → 自动连接Render后端

详细说明请查看 [本地开发指南](LOCAL_DEVELOPMENT.md)

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看自动生成的API文档

## 使用说明

1. 上传原始视频（Dance Video）
2. 上传音源视频（BGM Video）
3. 点击"开始处理"按钮
4. 等待处理完成
5. 点击"下载结果"下载处理后的视频

## 注意事项

- 处理时间可能较长（几分钟到十几分钟），请耐心等待
- 文件会在24小时后自动清理
- 目前是同步处理，处理期间页面会等待响应

