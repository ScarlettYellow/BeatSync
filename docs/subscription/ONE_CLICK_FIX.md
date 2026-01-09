# 一键修复订阅产品端点

## 问题

端点 `/api/subscription/products` 返回 404，经过多次尝试仍未解决。

## 解决方案

使用一键修复脚本，自动完成所有修复步骤。

## 使用方法

### 步骤 1：上传脚本到服务器

在**本地**执行（将脚本内容复制到服务器）：

```bash
# 方法 1: 使用 scp（推荐）
scp scripts/deployment/fix_subscription_endpoint_complete.sh user@your-server:/tmp/

# 方法 2: 在服务器上直接创建
# 见下面的命令
```

### 步骤 2：在服务器上执行修复

在**服务器**上执行：

```bash
# 如果使用 scp，脚本已在 /tmp/
# 如果直接在服务器创建，先创建脚本文件

# 给脚本执行权限
chmod +x /tmp/fix_subscription_endpoint_complete.sh

# 执行修复
sudo /tmp/fix_subscription_endpoint_complete.sh
```

### 或者：直接在服务器上创建并执行

在**服务器**上执行以下完整命令：

```bash
cd /opt/beatsync && \
cat > /tmp/fix_endpoint.sh << 'SCRIPT_END'
#!/bin/bash
# 一键修复脚本（简化版）

MAIN_PY="/opt/beatsync/web_service/backend/main.py"

# 检查并添加端点
python3 << 'PYTHON_FIX'
import re

file_path = "/opt/beatsync/web_service/backend/main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 如果端点已存在，先删除
if '@app.get("/api/subscription/products")' in content:
    pattern = r'@app\.get\("/api/subscription/products"\).*?(?=\n@app\.|\nif SUBSCRIPTION_AVAILABLE:|\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    print("✅ 删除旧端点定义")

# 找到插入点
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if line.strip() == "if SUBSCRIPTION_AVAILABLE:":
        insert_idx = i
        break

if insert_idx is None:
    insert_idx = len(lines)

# 向前查找合适的插入位置
for i in range(insert_idx - 1, max(0, insert_idx - 20), -1):
    if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
        for j in range(i + 1, insert_idx):
            if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                insert_idx = j
                break
        break

# 端点定义
endpoint = '''

# ==================== 订阅系统 API ====================

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
        
        subscription_products = [
            {"id": "basic_monthly", "type": "subscription", "displayName": "基础版（月付）", "description": "公测期特价：4.8元/月，每月20次下载", "price": PRODUCT_PRICES.get("basic_monthly", 4.80), "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月", "credits": PRODUCT_CREDITS.get("basic_monthly", 20), "period": "monthly"},
            {"id": "premium_monthly", "type": "subscription", "displayName": "高级版（月付）", "description": "公测期特价：19.9元/月，每月100次下载", "price": PRODUCT_PRICES.get("premium_monthly", 19.90), "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月", "credits": PRODUCT_CREDITS.get("premium_monthly", 100), "period": "monthly"}
        ]
        
        purchase_products = [
            {"id": "pack_10", "type": "purchase", "displayName": "10次下载包", "description": "一次性购买10次下载，永久有效", "price": PRODUCT_PRICES.get("pack_10", 5.00), "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}", "credits": PRODUCT_CREDITS.get("pack_10", 10), "period": None},
            {"id": "pack_20", "type": "purchase", "displayName": "20次下载包", "description": "一次性购买20次下载，永久有效", "price": PRODUCT_PRICES.get("pack_20", 9.00), "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}", "credits": PRODUCT_CREDITS.get("pack_20", 20), "period": None}
        ]
        
        products = subscription_products + purchase_products
        return {"products": products, "count": len(products)}
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {"products": [], "count": 0, "error": str(e)}

'''

# 插入端点
lines.insert(insert_idx, endpoint)
new_content = '\n'.join(lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 端点定义已添加到第 {insert_idx} 行之后")
PYTHON_FIX

# 检查语法
python3 -m py_compile "$MAIN_PY" && echo "✅ 语法正确" || (echo "❌ 语法错误"; exit 1)

# 测试路由
cd /opt/beatsync/web_service/backend && python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app
routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
if routes:
    print(f'✅ 路由已注册: {routes[0].path}')
else:
    print('❌ 路由未注册')
    exit(1)
PYTHON_TEST

# 重启服务
sudo systemctl restart beatsync && sleep 3 && echo "✅ 服务已重启"

# 测试端点
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -30
SCRIPT_END

chmod +x /tmp/fix_endpoint.sh
sudo /tmp/fix_endpoint.sh
```

---

**请执行上述命令，脚本会自动完成所有修复步骤！** 🚀


# 一键修复订阅产品端点

## 问题

端点 `/api/subscription/products` 返回 404，经过多次尝试仍未解决。

## 解决方案

使用一键修复脚本，自动完成所有修复步骤。

## 使用方法

### 步骤 1：上传脚本到服务器

在**本地**执行（将脚本内容复制到服务器）：

```bash
# 方法 1: 使用 scp（推荐）
scp scripts/deployment/fix_subscription_endpoint_complete.sh user@your-server:/tmp/

# 方法 2: 在服务器上直接创建
# 见下面的命令
```

### 步骤 2：在服务器上执行修复

在**服务器**上执行：

```bash
# 如果使用 scp，脚本已在 /tmp/
# 如果直接在服务器创建，先创建脚本文件

# 给脚本执行权限
chmod +x /tmp/fix_subscription_endpoint_complete.sh

# 执行修复
sudo /tmp/fix_subscription_endpoint_complete.sh
```

### 或者：直接在服务器上创建并执行

在**服务器**上执行以下完整命令：

```bash
cd /opt/beatsync && \
cat > /tmp/fix_endpoint.sh << 'SCRIPT_END'
#!/bin/bash
# 一键修复脚本（简化版）

MAIN_PY="/opt/beatsync/web_service/backend/main.py"

# 检查并添加端点
python3 << 'PYTHON_FIX'
import re

file_path = "/opt/beatsync/web_service/backend/main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 如果端点已存在，先删除
if '@app.get("/api/subscription/products")' in content:
    pattern = r'@app\.get\("/api/subscription/products"\).*?(?=\n@app\.|\nif SUBSCRIPTION_AVAILABLE:|\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    print("✅ 删除旧端点定义")

# 找到插入点
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if line.strip() == "if SUBSCRIPTION_AVAILABLE:":
        insert_idx = i
        break

if insert_idx is None:
    insert_idx = len(lines)

# 向前查找合适的插入位置
for i in range(insert_idx - 1, max(0, insert_idx - 20), -1):
    if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
        for j in range(i + 1, insert_idx):
            if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                insert_idx = j
                break
        break

# 端点定义
endpoint = '''

# ==================== 订阅系统 API ====================

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
        
        subscription_products = [
            {"id": "basic_monthly", "type": "subscription", "displayName": "基础版（月付）", "description": "公测期特价：4.8元/月，每月20次下载", "price": PRODUCT_PRICES.get("basic_monthly", 4.80), "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月", "credits": PRODUCT_CREDITS.get("basic_monthly", 20), "period": "monthly"},
            {"id": "premium_monthly", "type": "subscription", "displayName": "高级版（月付）", "description": "公测期特价：19.9元/月，每月100次下载", "price": PRODUCT_PRICES.get("premium_monthly", 19.90), "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月", "credits": PRODUCT_CREDITS.get("premium_monthly", 100), "period": "monthly"}
        ]
        
        purchase_products = [
            {"id": "pack_10", "type": "purchase", "displayName": "10次下载包", "description": "一次性购买10次下载，永久有效", "price": PRODUCT_PRICES.get("pack_10", 5.00), "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}", "credits": PRODUCT_CREDITS.get("pack_10", 10), "period": None},
            {"id": "pack_20", "type": "purchase", "displayName": "20次下载包", "description": "一次性购买20次下载，永久有效", "price": PRODUCT_PRICES.get("pack_20", 9.00), "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}", "credits": PRODUCT_CREDITS.get("pack_20", 20), "period": None}
        ]
        
        products = subscription_products + purchase_products
        return {"products": products, "count": len(products)}
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {"products": [], "count": 0, "error": str(e)}

'''

# 插入端点
lines.insert(insert_idx, endpoint)
new_content = '\n'.join(lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 端点定义已添加到第 {insert_idx} 行之后")
PYTHON_FIX

# 检查语法
python3 -m py_compile "$MAIN_PY" && echo "✅ 语法正确" || (echo "❌ 语法错误"; exit 1)

# 测试路由
cd /opt/beatsync/web_service/backend && python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app
routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
if routes:
    print(f'✅ 路由已注册: {routes[0].path}')
else:
    print('❌ 路由未注册')
    exit(1)
PYTHON_TEST

# 重启服务
sudo systemctl restart beatsync && sleep 3 && echo "✅ 服务已重启"

# 测试端点
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -30
SCRIPT_END

chmod +x /tmp/fix_endpoint.sh
sudo /tmp/fix_endpoint.sh
```

---

**请执行上述命令，脚本会自动完成所有修复步骤！** 🚀


# 一键修复订阅产品端点

## 问题

端点 `/api/subscription/products` 返回 404，经过多次尝试仍未解决。

## 解决方案

使用一键修复脚本，自动完成所有修复步骤。

## 使用方法

### 步骤 1：上传脚本到服务器

在**本地**执行（将脚本内容复制到服务器）：

```bash
# 方法 1: 使用 scp（推荐）
scp scripts/deployment/fix_subscription_endpoint_complete.sh user@your-server:/tmp/

# 方法 2: 在服务器上直接创建
# 见下面的命令
```

### 步骤 2：在服务器上执行修复

在**服务器**上执行：

```bash
# 如果使用 scp，脚本已在 /tmp/
# 如果直接在服务器创建，先创建脚本文件

# 给脚本执行权限
chmod +x /tmp/fix_subscription_endpoint_complete.sh

# 执行修复
sudo /tmp/fix_subscription_endpoint_complete.sh
```

### 或者：直接在服务器上创建并执行

在**服务器**上执行以下完整命令：

```bash
cd /opt/beatsync && \
cat > /tmp/fix_endpoint.sh << 'SCRIPT_END'
#!/bin/bash
# 一键修复脚本（简化版）

MAIN_PY="/opt/beatsync/web_service/backend/main.py"

# 检查并添加端点
python3 << 'PYTHON_FIX'
import re

file_path = "/opt/beatsync/web_service/backend/main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 如果端点已存在，先删除
if '@app.get("/api/subscription/products")' in content:
    pattern = r'@app\.get\("/api/subscription/products"\).*?(?=\n@app\.|\nif SUBSCRIPTION_AVAILABLE:|\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    print("✅ 删除旧端点定义")

# 找到插入点
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if line.strip() == "if SUBSCRIPTION_AVAILABLE:":
        insert_idx = i
        break

if insert_idx is None:
    insert_idx = len(lines)

# 向前查找合适的插入位置
for i in range(insert_idx - 1, max(0, insert_idx - 20), -1):
    if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
        for j in range(i + 1, insert_idx):
            if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                insert_idx = j
                break
        break

# 端点定义
endpoint = '''

# ==================== 订阅系统 API ====================

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
        
        subscription_products = [
            {"id": "basic_monthly", "type": "subscription", "displayName": "基础版（月付）", "description": "公测期特价：4.8元/月，每月20次下载", "price": PRODUCT_PRICES.get("basic_monthly", 4.80), "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月", "credits": PRODUCT_CREDITS.get("basic_monthly", 20), "period": "monthly"},
            {"id": "premium_monthly", "type": "subscription", "displayName": "高级版（月付）", "description": "公测期特价：19.9元/月，每月100次下载", "price": PRODUCT_PRICES.get("premium_monthly", 19.90), "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月", "credits": PRODUCT_CREDITS.get("premium_monthly", 100), "period": "monthly"}
        ]
        
        purchase_products = [
            {"id": "pack_10", "type": "purchase", "displayName": "10次下载包", "description": "一次性购买10次下载，永久有效", "price": PRODUCT_PRICES.get("pack_10", 5.00), "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}", "credits": PRODUCT_CREDITS.get("pack_10", 10), "period": None},
            {"id": "pack_20", "type": "purchase", "displayName": "20次下载包", "description": "一次性购买20次下载，永久有效", "price": PRODUCT_PRICES.get("pack_20", 9.00), "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}", "credits": PRODUCT_CREDITS.get("pack_20", 20), "period": None}
        ]
        
        products = subscription_products + purchase_products
        return {"products": products, "count": len(products)}
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {"products": [], "count": 0, "error": str(e)}

'''

# 插入端点
lines.insert(insert_idx, endpoint)
new_content = '\n'.join(lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ 端点定义已添加到第 {insert_idx} 行之后")
PYTHON_FIX

# 检查语法
python3 -m py_compile "$MAIN_PY" && echo "✅ 语法正确" || (echo "❌ 语法错误"; exit 1)

# 测试路由
cd /opt/beatsync/web_service/backend && python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app
routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
if routes:
    print(f'✅ 路由已注册: {routes[0].path}')
else:
    print('❌ 路由未注册')
    exit(1)
PYTHON_TEST

# 重启服务
sudo systemctl restart beatsync && sleep 3 && echo "✅ 服务已重启"

# 测试端点
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -30
SCRIPT_END

chmod +x /tmp/fix_endpoint.sh
sudo /tmp/fix_endpoint.sh
```

---

**请执行上述命令，脚本会自动完成所有修复步骤！** 🚀













