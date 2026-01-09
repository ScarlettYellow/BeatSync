#!/usr/bin/env python3
"""
在服务器上添加 /api/auth/register 端点
适用于服务器代码版本较旧的情况
"""

import re
from pathlib import Path

MAIN_PY = Path("/opt/beatsync/web_service/backend/main.py")

if not MAIN_PY.exists():
    print(f"❌ 文件不存在: {MAIN_PY}")
    exit(1)

print(f"📝 正在读取文件: {MAIN_PY}")

# 读取文件
with open(MAIN_PY, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# 检查是否已存在
if '@app.post("/api/auth/register")' in content:
    print("✅ 端点已存在，无需添加")
    exit(0)

print(f"📊 文件总行数: {len(lines)}")

# 查找合适的位置插入端点
# 优先在 /api/subscription/products 之后插入
insert_position = None
subscription_products_line = None

for i, line in enumerate(lines):
    if '@app.get("/api/subscription/products")' in line:
        subscription_products_line = i
        # 找到这个函数的结束位置
        for j in range(i + 1, len(lines)):
            if lines[j].strip() and not lines[j].strip().startswith(' ') and not lines[j].strip().startswith('\t'):
                if not lines[j].strip().startswith('#'):
                    insert_position = j
                    break
        break

# 如果没找到 /api/subscription/products，在文件末尾之前插入
if insert_position is None:
    # 查找最后一个 @app 端点
    last_app_line = None
    for i in range(len(lines) - 1, -1, -1):
        if '@app.' in lines[i]:
            last_app_line = i
            # 找到这个函数的结束位置
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].strip().startswith(' ') and not lines[j].strip().startswith('\t'):
                    if not lines[j].strip().startswith('#'):
                        insert_position = j
                        break
            break

# 如果还是没找到，在文件末尾之前插入（在 if __name__ == "__main__": 之前）
if insert_position is None:
    for i in range(len(lines) - 1, -1, -1):
        if 'if __name__' in lines[i]:
            insert_position = i
            break

if insert_position is None:
    insert_position = len(lines) - 10  # 在文件末尾前10行

print(f"📍 将在第 {insert_position + 1} 行插入端点")

# 准备要插入的代码
new_endpoint_code = '''# 用户认证端点（移到条件块外，确保始终可用）
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
backup_file = MAIN_PY.with_suffix('.py.backup')
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"💾 已创建备份: {backup_file}")

# 插入代码
new_lines = lines[:insert_position] + [new_endpoint_code] + lines[insert_position:]
new_content = '\n'.join(new_lines)

# 写入文件
with open(MAIN_PY, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 端点已添加到第 {insert_position + 1} 行")

# 验证语法
print("🔍 验证 Python 语法...")
import py_compile
try:
    py_compile.compile(str(MAIN_PY), doraise=True)
    print("✅ Python 语法检查通过")
except py_compile.PyCompileError as e:
    print(f"❌ Python 语法错误: {e}")
    print("正在恢复备份...")
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_content = f.read()
    with open(MAIN_PY, 'w', encoding='utf-8') as f:
        f.write(backup_content)
    print("✅ 已恢复备份文件")
    exit(1)

print("\n✅ 修复完成！")
print("📋 下一步：重启服务")
print("   sudo systemctl restart beatsync")



