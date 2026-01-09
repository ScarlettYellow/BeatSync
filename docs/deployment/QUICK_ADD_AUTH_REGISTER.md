# 快速添加 /api/auth/register 端点

## 问题

服务器代码版本较旧，没有 `/api/auth/register` 端点。

## 解决方案：在服务器上直接添加端点

### 一键修复命令（在服务器上执行）

```bash
cd /opt/beatsync && \
python3 << 'PYTHON_SCRIPT'
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

# 查找最后一个 @app 端点之后的位置
insert_position = len(lines) - 10  # 默认在文件末尾前10行

for i in range(len(lines) - 1, -1, -1):
    if '@app.' in lines[i]:
        # 找到函数结束位置（下一个非缩进行）
        for j in range(i + 1, len(lines)):
            line = lines[j]
            if line.strip() and not line.strip().startswith(' ') and not line.strip().startswith('\t'):
                if not line.strip().startswith('#'):
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

### 验证修复

```bash
# 1. 检查端点是否存在
grep -n "api/auth/register" /opt/beatsync/web_service/backend/main.py

# 2. 测试端点（应该返回 503 而不是 404）
curl -X POST https://beatsync.site/api/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_123"
```

**预期结果**：
- ✅ 如果订阅系统已启用：返回 `{"user_id": "...", "token": "..."}`
- ✅ 如果订阅系统未启用：返回 `{"error": "订阅系统未启用"}` (503)
- ❌ 如果返回 404：说明端点未添加成功



