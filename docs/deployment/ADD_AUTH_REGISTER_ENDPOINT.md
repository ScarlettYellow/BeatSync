# 在服务器上添加 /api/auth/register 端点

## 问题

服务器上的代码版本较旧（1041 行），没有 `/api/auth/register` 端点。

## 解决方案：直接在服务器上添加端点

### 方法一：使用 Python 脚本（推荐）

**在服务器上执行：**

```bash
cd /opt/beatsync && \
python3 << 'PYTHON_SCRIPT'
import re
from pathlib import Path

MAIN_PY = Path("/opt/beatsync/web_service/backend/main.py")

# 读取文件
with open(MAIN_PY, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# 检查是否已存在
if '@app.post("/api/auth/register")' in content:
    print("✅ 端点已存在")
    exit(0)

# 查找插入位置（在最后一个 @app 端点之后）
insert_position = len(lines) - 10  # 默认在文件末尾前10行

# 查找最后一个 @app 端点
for i in range(len(lines) - 1, -1, -1):
    if '@app.' in lines[i]:
        # 找到函数结束位置
        for j in range(i + 1, len(lines)):
            if lines[j].strip() and not lines[j].strip().startswith(' ') and not lines[j].strip().startswith('\t'):
                if not lines[j].strip().startswith('#'):
                    insert_position = j
                    break
        break

# 要插入的代码
new_code = '''# 用户认证端点
@app.post("/api/auth/register")
async def register_user(
    device_id: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None)
):
    """注册新用户"""
    # 检查订阅系统是否可用
    try:
        from subscription_service import create_or_get_user, is_subscription_enabled
        SUBSCRIPTION_AVAILABLE = True
    except ImportError:
        SUBSCRIPTION_AVAILABLE = False
    
    if not SUBSCRIPTION_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "订阅系统未启用"}
        )
    
    if not is_subscription_enabled():
        return JSONResponse(
            status_code=503,
            content={"error": "订阅系统未启用"}
        )
    
    result = create_or_get_user(device_id=device_id, email=email, phone=phone)
    return result

'''

# 备份
with open(str(MAIN_PY) + '.backup', 'w') as f:
    f.write(content)

# 插入
new_lines = lines[:insert_position] + [new_code] + lines[insert_position:]
new_content = '\n'.join(new_lines)

# 写入
with open(MAIN_PY, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 端点已添加到第 {insert_position + 1} 行")
PYTHON_SCRIPT

# 验证语法
python3 -m py_compile /opt/beatsync/web_service/backend/main.py && echo "✅ 语法检查通过" || echo "❌ 语法错误"

# 重启服务
sudo systemctl restart beatsync && echo "✅ 服务已重启"
```

### 方法二：使用 scp 传输完整文件（如果方法一失败）

**在本地执行：**

```bash
cd /Users/scarlett/Projects/BeatSync

# 使用 root 用户传输
scp web_service/backend/main.py root@124.221.58.149:/opt/beatsync/web_service/backend/main.py
```

**然后在服务器上：**

```bash
# 验证文件已更新
grep -n "api/auth/register" /opt/beatsync/web_service/backend/main.py

# 重启服务
sudo systemctl restart beatsync
```

## 验证修复

```bash
# 1. 检查端点是否存在
grep -n "api/auth/register" /opt/beatsync/web_service/backend/main.py

# 2. 测试端点（应该返回 503 而不是 404）
curl -X POST https://beatsync.site/api/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_123"
```

## 注意事项

- 如果订阅系统模块不存在，端点会返回 503 错误（这是正常的）
- 确保服务器上已安装订阅系统相关模块
- 如果服务无法启动，检查日志：`sudo journalctl -u beatsync -n 50`



