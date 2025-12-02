# 修复手机端视频预览加载失败

> **问题**：手机端在线预览视频加载失败，显示"视频加载失败，请检查网络连接或稍后重试"

---

## 问题分析

### 可能原因

1. **Range请求支持不完整**
   - 手机浏览器通常需要Range请求来支持视频流式播放
   - 后端虽然设置了`Accept-Ranges: bytes`，但可能没有正确处理Range请求

2. **CORS问题**
   - 视频URL是跨域的（GitHub Pages -> 腾讯云）
   - 可能被CORS策略阻止

3. **HTTPS/HTTP混合内容**
   - GitHub Pages是HTTPS，但视频URL可能是HTTP
   - 浏览器会阻止混合内容

4. **视频格式/编码问题**
   - 某些手机浏览器可能不支持特定的视频编码
   - 需要确保视频编码兼容

5. **网络超时**
   - 视频文件太大，加载超时
   - 手机网络可能较慢

---

## 解决方案

### 方案1：优化预览页面错误处理（立即实施）

**问题**：当前错误处理太简单，无法诊断具体问题

**改进**：
- 添加详细的错误信息显示
- 添加重试机制
- 添加备用下载链接

---

### 方案2：确保后端支持Range请求（重要）

**问题**：FastAPI的`FileResponse`默认支持Range请求，但需要确保正确配置

**检查**：
- 后端已设置`Accept-Ranges: bytes`
- FastAPI自动处理Range请求

**如果需要手动处理**：
```python
from fastapi.responses import StreamingResponse
from fastapi import Request

@app.get("/api/preview/{task_id}")
async def preview_result(task_id: str, version: Optional[str] = None, request: Request):
    # ... 文件查找逻辑 ...
    
    # 检查Range请求
    range_header = request.headers.get('Range')
    if range_header:
        # 处理Range请求
        # FastAPI的FileResponse会自动处理，但可以手动优化
        pass
    
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "public, max-age=3600"  # 添加缓存
        }
    )
```

---

### 方案3：优化预览页面（推荐）

**改进预览页面**：
- 添加加载状态
- 添加详细错误信息
- 添加重试按钮
- 添加备用下载链接
- 优化视频标签属性

---

## 实施修复

### 1. 优化预览页面

**添加功能**：
- 加载状态显示
- 详细错误信息
- 重试机制
- 备用下载链接
- 视频预加载优化

---

### 2. 检查后端配置

**确保**：
- CORS正确配置
- Range请求支持
- HTTPS正确配置

---

## 测试建议

### 测试场景

1. **不同网络环境**：
   - WiFi
   - 4G
   - 5G

2. **不同设备**：
   - iOS Safari
   - Android Chrome
   - 其他浏览器

3. **不同视频大小**：
   - 小文件（<50MB）
   - 大文件（>100MB）

---

## 临时解决方案

**如果预览失败，用户可以**：
1. 使用"下载视频"功能
2. 下载后在本地播放器打开
3. 刷新页面重试

---

**最后更新**：2025-12-02

