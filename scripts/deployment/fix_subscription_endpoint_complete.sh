#!/bin/bash
# 一键修复订阅产品端点 - 完整版本

set -e

MAIN_PY="/opt/beatsync/web_service/backend/main.py"
BACKUP_PY="${MAIN_PY}.backup.$(date +%Y%m%d_%H%M%S)"

echo "=== 一键修复订阅产品端点 ==="
echo ""

# 1. 备份原文件
echo "1. 备份原文件..."
cp "$MAIN_PY" "$BACKUP_PY"
echo "✅ 备份完成: $BACKUP_PY"
echo ""

# 2. 检查端点是否已存在
if grep -q '@app.get("/api/subscription/products")' "$MAIN_PY"; then
    echo "2. 端点定义已存在，检查是否需要修复..."
    # 检查端点函数是否完整
    if grep -A 50 '@app.get("/api/subscription/products")' "$MAIN_PY" | grep -q 'async def get_subscription_products'; then
        echo "✅ 端点函数完整"
    else
        echo "⚠️  端点函数不完整，需要修复"
        NEED_FIX=1
    fi
else
    echo "2. 端点定义不存在，需要添加"
    NEED_FIX=1
fi
echo ""

# 3. 如果需要修复，添加端点定义
if [ "$NEED_FIX" = "1" ]; then
    echo "3. 添加/修复端点定义..."
    
    # 查找插入点：在 "if SUBSCRIPTION_AVAILABLE:" 之前
    INSERT_LINE=$(grep -n "^if SUBSCRIPTION_AVAILABLE:" "$MAIN_PY" | head -1 | cut -d: -f1)
    
    if [ -z "$INSERT_LINE" ]; then
        # 如果找不到，在文件末尾添加
        INSERT_LINE=$(wc -l < "$MAIN_PY")
        echo "⚠️  未找到 'if SUBSCRIPTION_AVAILABLE:'，将在文件末尾添加"
    else
        echo "✅ 找到插入点: 第 $INSERT_LINE 行"
    fi
    
    # 创建临时文件
    TEMP_FILE=$(mktemp)
    
    # 端点定义代码
    ENDPOINT_CODE='
# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    try:
        subscription_available = SUBSCRIPTION_AVAILABLE
    except NameError:
        subscription_available = False
    
    if not subscription_available:
        return {"products": [], "count": 0, "message": "订阅系统未启用"}
    
    try:
        subscription_enabled = is_subscription_enabled()
    except NameError:
        subscription_enabled = False
    
    if not subscription_enabled:
        return {"products": [], "count": 0, "message": "订阅系统未启用"}
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版（月付）",
                "description": "公测期特价：4.8元/月，每月20次下载",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"basic_monthly\", 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版（月付）",
                "description": "公测期特价：19.9元/月，每月100次下载",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"premium_monthly\", 19.90)}/月",
                "credits": PRODUCT_CREDITS.get("premium_monthly", 100),
                "period": "monthly"
            }
        ]
        
        # 一次性购买产品
        purchase_products = [
            {
                "id": "pack_10",
                "type": "purchase",
                "displayName": "10次下载包",
                "description": "一次性购买10次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_10", 5.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"pack_10\", 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"pack_20\", 9.00)}",
                "credits": PRODUCT_CREDITS.get("pack_20", 20),
                "period": None
            }
        ]
        
        products = subscription_products + purchase_products
        
        return {
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "products": [],
            "count": 0,
            "error": str(e)
        }

'
    
    # 如果端点已存在，先删除旧的定义
    if grep -q '@app.get("/api/subscription/products")' "$MAIN_PY"; then
        echo "   删除旧的端点定义..."
        python3 << PYTHON_SCRIPT
import re

with open("$MAIN_PY", 'r', encoding='utf-8') as f:
    content = f.read()

# 删除旧的端点定义（从 @app.get 到下一个 @app 或 if 语句）
pattern = r'@app\.get\("/api/subscription/products"\).*?(?=\n@app\.|\nif |\Z)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

with open("$MAIN_PY", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 旧端点定义已删除")
PYTHON_SCRIPT
    fi
    
    # 插入新端点
    python3 << PYTHON_SCRIPT
with open("$MAIN_PY", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到插入点
insert_line = $INSERT_LINE
for i in range(insert_line - 1, max(0, insert_line - 20), -1):
    if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
        for j in range(i + 1, insert_line):
            if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                insert_line = j
                break
        break

# 插入端点定义
endpoint_code = '''$ENDPOINT_CODE'''
new_lines = lines[:insert_line] + [endpoint_code] + lines[insert_line:]

with open("$MAIN_PY", 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ 端点定义已添加到第 {insert_line} 行之后")
PYTHON_SCRIPT
    
    echo "✅ 端点定义添加完成"
else
    echo "3. 端点定义已存在，跳过"
fi
echo ""

# 4. 检查语法
echo "4. 检查语法..."
if python3 -m py_compile "$MAIN_PY" 2>/dev/null; then
    echo "✅ 语法正确"
else
    echo "❌ 语法错误，恢复备份..."
    cp "$BACKUP_PY" "$MAIN_PY"
    exit 1
fi
echo ""

# 5. 测试路由注册
echo "5. 测试路由注册..."
cd /opt/beatsync/web_service/backend
python3 << PYTHON_SCRIPT
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 路由已注册: {routes[0].path}')
    else:
        print('❌ 路由未注册')
        print('所有路由（前20个）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            methods = getattr(r, 'methods', set())
            print(f'  {list(methods)[0] if methods else "N/A"}: {r.path}')
        sys.exit(1)
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ 路由注册失败，恢复备份..."
    cp "$BACKUP_PY" "$MAIN_PY"
    exit 1
fi
echo ""

# 6. 重启服务
echo "6. 重启服务..."
sudo systemctl restart beatsync
sleep 3
echo "✅ 服务已重启"
echo ""

# 7. 测试端点
echo "7. 测试端点..."
RESPONSE=$(curl -s http://127.0.0.1:8000/api/subscription/products)
if echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ 端点响应正常:"
    echo "$RESPONSE" | python3 -m json.tool | head -30
else
    echo "⚠️  端点响应异常:"
    echo "$RESPONSE"
fi

echo ""
echo "=== 修复完成 ==="


#!/bin/bash
# 一键修复订阅产品端点 - 完整版本

set -e

MAIN_PY="/opt/beatsync/web_service/backend/main.py"
BACKUP_PY="${MAIN_PY}.backup.$(date +%Y%m%d_%H%M%S)"

echo "=== 一键修复订阅产品端点 ==="
echo ""

# 1. 备份原文件
echo "1. 备份原文件..."
cp "$MAIN_PY" "$BACKUP_PY"
echo "✅ 备份完成: $BACKUP_PY"
echo ""

# 2. 检查端点是否已存在
if grep -q '@app.get("/api/subscription/products")' "$MAIN_PY"; then
    echo "2. 端点定义已存在，检查是否需要修复..."
    # 检查端点函数是否完整
    if grep -A 50 '@app.get("/api/subscription/products")' "$MAIN_PY" | grep -q 'async def get_subscription_products'; then
        echo "✅ 端点函数完整"
    else
        echo "⚠️  端点函数不完整，需要修复"
        NEED_FIX=1
    fi
else
    echo "2. 端点定义不存在，需要添加"
    NEED_FIX=1
fi
echo ""

# 3. 如果需要修复，添加端点定义
if [ "$NEED_FIX" = "1" ]; then
    echo "3. 添加/修复端点定义..."
    
    # 查找插入点：在 "if SUBSCRIPTION_AVAILABLE:" 之前
    INSERT_LINE=$(grep -n "^if SUBSCRIPTION_AVAILABLE:" "$MAIN_PY" | head -1 | cut -d: -f1)
    
    if [ -z "$INSERT_LINE" ]; then
        # 如果找不到，在文件末尾添加
        INSERT_LINE=$(wc -l < "$MAIN_PY")
        echo "⚠️  未找到 'if SUBSCRIPTION_AVAILABLE:'，将在文件末尾添加"
    else
        echo "✅ 找到插入点: 第 $INSERT_LINE 行"
    fi
    
    # 创建临时文件
    TEMP_FILE=$(mktemp)
    
    # 端点定义代码
    ENDPOINT_CODE='
# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    try:
        subscription_available = SUBSCRIPTION_AVAILABLE
    except NameError:
        subscription_available = False
    
    if not subscription_available:
        return {"products": [], "count": 0, "message": "订阅系统未启用"}
    
    try:
        subscription_enabled = is_subscription_enabled()
    except NameError:
        subscription_enabled = False
    
    if not subscription_enabled:
        return {"products": [], "count": 0, "message": "订阅系统未启用"}
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版（月付）",
                "description": "公测期特价：4.8元/月，每月20次下载",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"basic_monthly\", 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版（月付）",
                "description": "公测期特价：19.9元/月，每月100次下载",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"premium_monthly\", 19.90)}/月",
                "credits": PRODUCT_CREDITS.get("premium_monthly", 100),
                "period": "monthly"
            }
        ]
        
        # 一次性购买产品
        purchase_products = [
            {
                "id": "pack_10",
                "type": "purchase",
                "displayName": "10次下载包",
                "description": "一次性购买10次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_10", 5.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"pack_10\", 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"pack_20\", 9.00)}",
                "credits": PRODUCT_CREDITS.get("pack_20", 20),
                "period": None
            }
        ]
        
        products = subscription_products + purchase_products
        
        return {
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "products": [],
            "count": 0,
            "error": str(e)
        }

'
    
    # 如果端点已存在，先删除旧的定义
    if grep -q '@app.get("/api/subscription/products")' "$MAIN_PY"; then
        echo "   删除旧的端点定义..."
        python3 << PYTHON_SCRIPT
import re

with open("$MAIN_PY", 'r', encoding='utf-8') as f:
    content = f.read()

# 删除旧的端点定义（从 @app.get 到下一个 @app 或 if 语句）
pattern = r'@app\.get\("/api/subscription/products"\).*?(?=\n@app\.|\nif |\Z)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

with open("$MAIN_PY", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 旧端点定义已删除")
PYTHON_SCRIPT
    fi
    
    # 插入新端点
    python3 << PYTHON_SCRIPT
with open("$MAIN_PY", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到插入点
insert_line = $INSERT_LINE
for i in range(insert_line - 1, max(0, insert_line - 20), -1):
    if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
        for j in range(i + 1, insert_line):
            if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                insert_line = j
                break
        break

# 插入端点定义
endpoint_code = '''$ENDPOINT_CODE'''
new_lines = lines[:insert_line] + [endpoint_code] + lines[insert_line:]

with open("$MAIN_PY", 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ 端点定义已添加到第 {insert_line} 行之后")
PYTHON_SCRIPT
    
    echo "✅ 端点定义添加完成"
else
    echo "3. 端点定义已存在，跳过"
fi
echo ""

# 4. 检查语法
echo "4. 检查语法..."
if python3 -m py_compile "$MAIN_PY" 2>/dev/null; then
    echo "✅ 语法正确"
else
    echo "❌ 语法错误，恢复备份..."
    cp "$BACKUP_PY" "$MAIN_PY"
    exit 1
fi
echo ""

# 5. 测试路由注册
echo "5. 测试路由注册..."
cd /opt/beatsync/web_service/backend
python3 << PYTHON_SCRIPT
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 路由已注册: {routes[0].path}')
    else:
        print('❌ 路由未注册')
        print('所有路由（前20个）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            methods = getattr(r, 'methods', set())
            print(f'  {list(methods)[0] if methods else "N/A"}: {r.path}')
        sys.exit(1)
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ 路由注册失败，恢复备份..."
    cp "$BACKUP_PY" "$MAIN_PY"
    exit 1
fi
echo ""

# 6. 重启服务
echo "6. 重启服务..."
sudo systemctl restart beatsync
sleep 3
echo "✅ 服务已重启"
echo ""

# 7. 测试端点
echo "7. 测试端点..."
RESPONSE=$(curl -s http://127.0.0.1:8000/api/subscription/products)
if echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ 端点响应正常:"
    echo "$RESPONSE" | python3 -m json.tool | head -30
else
    echo "⚠️  端点响应异常:"
    echo "$RESPONSE"
fi

echo ""
echo "=== 修复完成 ==="


#!/bin/bash
# 一键修复订阅产品端点 - 完整版本

set -e

MAIN_PY="/opt/beatsync/web_service/backend/main.py"
BACKUP_PY="${MAIN_PY}.backup.$(date +%Y%m%d_%H%M%S)"

echo "=== 一键修复订阅产品端点 ==="
echo ""

# 1. 备份原文件
echo "1. 备份原文件..."
cp "$MAIN_PY" "$BACKUP_PY"
echo "✅ 备份完成: $BACKUP_PY"
echo ""

# 2. 检查端点是否已存在
if grep -q '@app.get("/api/subscription/products")' "$MAIN_PY"; then
    echo "2. 端点定义已存在，检查是否需要修复..."
    # 检查端点函数是否完整
    if grep -A 50 '@app.get("/api/subscription/products")' "$MAIN_PY" | grep -q 'async def get_subscription_products'; then
        echo "✅ 端点函数完整"
    else
        echo "⚠️  端点函数不完整，需要修复"
        NEED_FIX=1
    fi
else
    echo "2. 端点定义不存在，需要添加"
    NEED_FIX=1
fi
echo ""

# 3. 如果需要修复，添加端点定义
if [ "$NEED_FIX" = "1" ]; then
    echo "3. 添加/修复端点定义..."
    
    # 查找插入点：在 "if SUBSCRIPTION_AVAILABLE:" 之前
    INSERT_LINE=$(grep -n "^if SUBSCRIPTION_AVAILABLE:" "$MAIN_PY" | head -1 | cut -d: -f1)
    
    if [ -z "$INSERT_LINE" ]; then
        # 如果找不到，在文件末尾添加
        INSERT_LINE=$(wc -l < "$MAIN_PY")
        echo "⚠️  未找到 'if SUBSCRIPTION_AVAILABLE:'，将在文件末尾添加"
    else
        echo "✅ 找到插入点: 第 $INSERT_LINE 行"
    fi
    
    # 创建临时文件
    TEMP_FILE=$(mktemp)
    
    # 端点定义代码
    ENDPOINT_CODE='
# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    try:
        subscription_available = SUBSCRIPTION_AVAILABLE
    except NameError:
        subscription_available = False
    
    if not subscription_available:
        return {"products": [], "count": 0, "message": "订阅系统未启用"}
    
    try:
        subscription_enabled = is_subscription_enabled()
    except NameError:
        subscription_enabled = False
    
    if not subscription_enabled:
        return {"products": [], "count": 0, "message": "订阅系统未启用"}
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版（月付）",
                "description": "公测期特价：4.8元/月，每月20次下载",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"basic_monthly\", 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版（月付）",
                "description": "公测期特价：19.9元/月，每月100次下载",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"premium_monthly\", 19.90)}/月",
                "credits": PRODUCT_CREDITS.get("premium_monthly", 100),
                "period": "monthly"
            }
        ]
        
        # 一次性购买产品
        purchase_products = [
            {
                "id": "pack_10",
                "type": "purchase",
                "displayName": "10次下载包",
                "description": "一次性购买10次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_10", 5.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"pack_10\", 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get(\"pack_20\", 9.00)}",
                "credits": PRODUCT_CREDITS.get("pack_20", 20),
                "period": None
            }
        ]
        
        products = subscription_products + purchase_products
        
        return {
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "products": [],
            "count": 0,
            "error": str(e)
        }

'
    
    # 如果端点已存在，先删除旧的定义
    if grep -q '@app.get("/api/subscription/products")' "$MAIN_PY"; then
        echo "   删除旧的端点定义..."
        python3 << PYTHON_SCRIPT
import re

with open("$MAIN_PY", 'r', encoding='utf-8') as f:
    content = f.read()

# 删除旧的端点定义（从 @app.get 到下一个 @app 或 if 语句）
pattern = r'@app\.get\("/api/subscription/products"\).*?(?=\n@app\.|\nif |\Z)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

with open("$MAIN_PY", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 旧端点定义已删除")
PYTHON_SCRIPT
    fi
    
    # 插入新端点
    python3 << PYTHON_SCRIPT
with open("$MAIN_PY", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到插入点
insert_line = $INSERT_LINE
for i in range(insert_line - 1, max(0, insert_line - 20), -1):
    if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
        for j in range(i + 1, insert_line):
            if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                insert_line = j
                break
        break

# 插入端点定义
endpoint_code = '''$ENDPOINT_CODE'''
new_lines = lines[:insert_line] + [endpoint_code] + lines[insert_line:]

with open("$MAIN_PY", 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ 端点定义已添加到第 {insert_line} 行之后")
PYTHON_SCRIPT
    
    echo "✅ 端点定义添加完成"
else
    echo "3. 端点定义已存在，跳过"
fi
echo ""

# 4. 检查语法
echo "4. 检查语法..."
if python3 -m py_compile "$MAIN_PY" 2>/dev/null; then
    echo "✅ 语法正确"
else
    echo "❌ 语法错误，恢复备份..."
    cp "$BACKUP_PY" "$MAIN_PY"
    exit 1
fi
echo ""

# 5. 测试路由注册
echo "5. 测试路由注册..."
cd /opt/beatsync/web_service/backend
python3 << PYTHON_SCRIPT
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 路由已注册: {routes[0].path}')
    else:
        print('❌ 路由未注册')
        print('所有路由（前20个）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            methods = getattr(r, 'methods', set())
            print(f'  {list(methods)[0] if methods else "N/A"}: {r.path}')
        sys.exit(1)
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ 路由注册失败，恢复备份..."
    cp "$BACKUP_PY" "$MAIN_PY"
    exit 1
fi
echo ""

# 6. 重启服务
echo "6. 重启服务..."
sudo systemctl restart beatsync
sleep 3
echo "✅ 服务已重启"
echo ""

# 7. 测试端点
echo "7. 测试端点..."
RESPONSE=$(curl -s http://127.0.0.1:8000/api/subscription/products)
if echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ 端点响应正常:"
    echo "$RESPONSE" | python3 -m json.tool | head -30
else
    echo "⚠️  端点响应异常:"
    echo "$RESPONSE"
fi

echo ""
echo "=== 修复完成 ==="













