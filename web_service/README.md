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

### 1. 安装后端依赖

```bash
cd web_service/backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd web_service/backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 打开前端页面

在浏览器中打开 `web_service/frontend/index.html`

或者使用Python简单HTTP服务器：

```bash
cd web_service/frontend
python3 -m http.server 8080
```

然后在浏览器中访问 `http://localhost:8080`

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

