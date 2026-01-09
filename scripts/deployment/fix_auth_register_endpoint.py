#!/usr/bin/env python3
"""
修复 /api/auth/register 端点：将其移到条件块外
直接在服务器上运行此脚本即可修复
"""

import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
MAIN_PY = PROJECT_ROOT / "web_service" / "backend" / "main.py"

# 如果脚本在服务器上运行，使用绝对路径
if not MAIN_PY.exists():
    MAIN_PY = Path("/opt/beatsync/web_service/backend/main.py")

if not MAIN_PY.exists():
    print(f"❌ 找不到 main.py 文件: {MAIN_PY}")
    sys.exit(1)

print(f"📝 正在修复文件: {MAIN_PY}")

# 读取文件内容
with open(MAIN_PY, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经修复过
if '# 用户认证端点（移到条件块外，确保始终可用）' in content:
    print("✅ 文件已经修复过，无需再次修复")
    sys.exit(0)

# 查找需要移动的端点定义
old_pattern = """if SUBSCRIPTION_AVAILABLE:
    # 用户认证
    @app.post("/api/auth/register")
    async def register_user(
        device_id: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        phone: Optional[str] = Form(None)
    ):
        \"\"\"注册新用户\"\"\"
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        result = create_or_get_user(device_id=device_id, email=email, phone=phone)
        return result"""

new_pattern = """# 用户认证端点（移到条件块外，确保始终可用）
@app.post("/api/auth/register")
async def register_user(
    device_id: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None)
):
    \"\"\"注册新用户\"\"\"
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

if SUBSCRIPTION_AVAILABLE:"""

# 执行替换
if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ 找到并替换端点定义")
else:
    print("⚠️  未找到预期的模式，尝试其他方式...")
    # 尝试更灵活的匹配
    import re
    
    # 查找 if SUBSCRIPTION_AVAILABLE: 后面的 @app.post("/api/auth/register")
    pattern = r'(if SUBSCRIPTION_AVAILABLE:\s*# 用户认证\s*@app\.post\("/api/auth/register"\)\s*async def register_user\([^)]+\):\s*""".*?"""\s*if not is_subscription_enabled\(\):\s*return JSONResponse\(\s*status_code=503,\s*content=\{"error": "订阅系统未启用"\}\s*\)\s*result = create_or_get_user\(device_id=device_id, email=email, phone=phone\)\s*return result)'
    
    replacement = '''# 用户认证端点（移到条件块外，确保始终可用）
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
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✅ 使用正则表达式替换成功")
    else:
        print("❌ 无法找到需要修复的代码模式")
        print("请手动检查文件内容")
        sys.exit(1)

# 备份原文件
backup_file = MAIN_PY.with_suffix('.py.backup')
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(open(MAIN_PY, 'r', encoding='utf-8').read())
print(f"💾 已创建备份: {backup_file}")

# 写入修复后的内容
with open(MAIN_PY, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 文件修复完成: {MAIN_PY}")

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
    sys.exit(1)

print("\n✅ 修复完成！")
print("📋 下一步：重启服务")
print("   sudo systemctl restart beatsync")



