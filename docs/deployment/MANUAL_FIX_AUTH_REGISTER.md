# 手动修复 /api/auth/register 404 错误（无需 Git）

## 问题

服务器无法连接 GitHub，无法通过 `git pull` 更新代码。

## 解决方案：直接在服务器上修复文件

### 方法一：使用 Python 脚本（推荐）

**在服务器上执行：**

```bash
# 1. 切换到项目目录
cd /opt/beatsync

# 2. 创建修复脚本（复制以下内容到服务器）
cat > /tmp/fix_auth_register.py << 'EOF'
#!/usr/bin/env python3
import re
from pathlib import Path

main_py = Path("/opt/beatsync/web_service/backend/main.py")

# 读取文件
with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已修复
if '# 用户认证端点（移到条件块外，确保始终可用）' in content:
    print("✅ 已经修复过")
    exit(0)

# 查找并替换
old = '''if SUBSCRIPTION_AVAILABLE:
    # 用户认证
    @app.post("/api/auth/register")
    async def register_user(
        device_id: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        phone: Optional[str] = Form(None)
    ):
        """注册新用户"""
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        result = create_or_get_user(device_id=device_id, email=email, phone=phone)
        return result'''

new = '''# 用户认证端点（移到条件块外，确保始终可用）
@app.post("/api/auth/register")
async def register_user(
    device_id: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None)
):
    """注册新用户"""
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

if SUBSCRIPTION_AVAILABLE:'''

if old in content:
    # 备份
    with open(str(main_py) + '.backup', 'w') as f:
        f.write(content)
    # 替换
    content = content.replace(old, new)
    # 写入
    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 修复完成")
else:
    print("❌ 未找到需要修复的代码")
EOF

# 3. 执行修复脚本
python3 /tmp/fix_auth_register.py

# 4. 验证语法
python3 -m py_compile /opt/beatsync/web_service/backend/main.py && echo "✅ 语法检查通过"

# 5. 重启服务
sudo systemctl restart beatsync

# 6. 验证修复
curl -X POST https://beatsync.site/api/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_123"
```

### 方法二：使用 scp 从本地传输文件

**在本地（你的 Mac）执行：**

```bash
# 1. 确保本地代码已修复
cd /Users/scarlett/Projects/BeatSync

# 2. 传输文件到服务器
scp web_service/backend/main.py ubuntu@你的服务器IP:/opt/beatsync/web_service/backend/main.py

# 或者使用 root 用户
scp web_service/backend/main.py root@你的服务器IP:/opt/beatsync/web_service/backend/main.py
```

**然后在服务器上：**

```bash
# 验证文件已更新
grep -n "用户认证端点（移到条件块外" /opt/beatsync/web_service/backend/main.py

# 重启服务
sudo systemctl restart beatsync
```

### 方法三：手动编辑文件（如果上述方法都失败）

**在服务器上执行：**

```bash
# 1. 编辑文件
sudo nano /opt/beatsync/web_service/backend/main.py

# 2. 找到第 1220 行左右，查找：
#    if SUBSCRIPTION_AVAILABLE:
#        # 用户认证
#        @app.post("/api/auth/register")

# 3. 将整个 register_user 函数移到 if SUBSCRIPTION_AVAILABLE: 之前
#    并在函数开头添加 SUBSCRIPTION_AVAILABLE 检查

# 4. 保存并退出（Ctrl+X, Y, Enter）

# 5. 重启服务
sudo systemctl restart beatsync
```

## 验证修复

```bash
# 1. 检查端点是否已移到条件块外
grep -B 5 -A 15 '用户认证端点（移到条件块外' /opt/beatsync/web_service/backend/main.py

# 2. 测试端点（应该返回 503 而不是 404）
curl -X POST https://beatsync.site/api/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_123"

# 预期结果：
# - ✅ 如果订阅系统已启用：返回 {"user_id": "...", "token": "..."}
# - ✅ 如果订阅系统未启用：返回 {"error": "订阅系统未启用"} (503)
# - ❌ 如果返回 404：说明修复未生效
```

## 注意事项

- 修复前建议备份：`sudo cp /opt/beatsync/web_service/backend/main.py /opt/beatsync/web_service/backend/main.py.backup`
- 修复后必须重启服务才能生效
- 如果服务无法启动，检查日志：`sudo journalctl -u beatsync -n 50`



