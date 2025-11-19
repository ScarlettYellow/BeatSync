# Web服务问题排查指南

## 处理失败问题排查

### 1. 检查后端服务是否正常运行

```bash
# 启动后端服务
cd web_service/backend
python3 main.py

# 或使用启动脚本
./start_server.sh
```

### 2. 查看后端日志

启动后端服务后，在前端进行操作，观察后端控制台的输出：
- 如果有ERROR日志，会显示详细的错误信息
- 检查文件路径是否正确
- 检查导入是否成功

### 3. 检查浏览器控制台

按F12打开开发者工具：
- **Network标签**：查看API请求
  - 检查`/api/process`请求的状态码
  - 查看响应内容
  - 检查是否有超时（Timeout）
- **Console标签**：查看JavaScript错误

### 4. 可能的原因和解决方案

#### 原因1：超时问题（最可能）

**现象**：
- 浏览器Network标签显示请求超时
- 后端日志显示处理正在进行，但前端已断开连接

**解决方案**：
- 暂时：增加浏览器超时时间（不推荐）
- 长期：改为异步处理方案（推荐）

#### 原因2：文件路径问题

**检查**：
```bash
# 检查上传的文件是否存在
ls -la outputs/web_uploads/

# 检查输出目录
ls -la outputs/web_outputs/
```

#### 原因3：导入错误

**检查后端启动日志**：
- 如果看到"ModuleNotFoundError"，说明依赖未安装
- 运行：`pip install -r requirements.txt`

### 5. 手动测试

如果Web服务失败，可以手动测试：

```bash
# 测试并行处理器
python3 beatsync_parallel_processor.py \
  --dance test_data/input_allcases/fallingout_short/dance.mp4 \
  --bgm test_data/input_allcases/fallingout_short/bgm.mp4 \
  --output-dir outputs/test_manual \
  --sample-name test
```

如果手动测试成功，说明问题在Web服务层。

### 6. 查看详细错误信息

后端现在会输出详细的错误日志，包括：
- 输出目录内容
- 对比报告文件内容（如果存在）
- 完整的异常堆栈

查看后端控制台即可看到这些信息。

