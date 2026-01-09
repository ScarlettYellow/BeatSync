# 手动修复：添加订阅产品端点

## 问题

服务器上的 `main.py` 只有 1041 行（本地有 1800 行），缺少端点定义。由于 Git 网络问题，无法通过拉取更新，需要手动添加。

## 解决方案

### 步骤 1：上传修复脚本到服务器

在**本地**执行（将脚本内容复制到服务器）：

```bash
# 在服务器上创建脚本文件
cat > /tmp/add_subscription_endpoint.py << 'SCRIPT_END'
#!/usr/bin/env python3
"""
在服务器上的 main.py 中添加订阅产品端点定义
"""

import sys
import os

# 端点定义代码
ENDPOINT_CODE = '''


# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    # 如果订阅系统未启用，返回空列表
    if not SUBSCRIPTION_AVAILABLE:
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    if not is_subscription_enabled():
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        products = []
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版（月付）",
                "description": "公测期特价：4.8元/月，每月20次下载",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版（月付）",
                "description": "公测期特价：19.9元/月，每月100次下载",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月",
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
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}",
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

'''

def find_insertion_point(file_path):
    """找到插入点：在最后一个函数定义之后，if SUBSCRIPTION_AVAILABLE 之前"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找 "if SUBSCRIPTION_AVAILABLE:" 的位置
    insertion_line = None
    for i, line in enumerate(lines):
        if line.strip() == "if SUBSCRIPTION_AVAILABLE:":
            insertion_line = i
            break
    
    if insertion_line is None:
        # 如果找不到，尝试在文件末尾插入
        print("⚠️  未找到 'if SUBSCRIPTION_AVAILABLE:'，将在文件末尾插入")
        return len(lines)
    
    # 向前查找，找到合适的位置（在函数定义之后）
    # 通常应该在最后一个 return FileResponse 之后
    for i in range(insertion_line - 1, max(0, insertion_line - 20), -1):
        if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
            # 找到这个函数的结束位置（下一个空行或 if 语句）
            for j in range(i + 1, insertion_line):
                if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                    return j
    
    # 如果找不到，就在 if SUBSCRIPTION_AVAILABLE 之前插入
    return insertion_line

def add_endpoint(file_path):
    """在文件中添加端点定义"""
    # 检查是否已经存在
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if '@app.get("/api/subscription/products")' in content:
            print("✅ 端点定义已存在，无需添加")
            return False
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到插入点
    insertion_line = find_insertion_point(file_path)
    
    # 插入代码
    new_lines = lines[:insertion_line] + [ENDPOINT_CODE] + lines[insertion_line:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ 端点定义已添加到第 {insertion_line} 行之后")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 add_subscription_endpoint.py <main.py路径>")
        print("示例: python3 add_subscription_endpoint.py /opt/beatsync/web_service/backend/main.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"📝 处理文件: {file_path}")
    
    try:
        if add_endpoint(file_path):
            print("✅ 端点定义添加成功！")
        else:
            print("ℹ️  端点定义已存在，无需修改")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
SCRIPT_END
```

### 步骤 2：在服务器上执行修复脚本

在**服务器**上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查文件当前状态 ===" && \
wc -l web_service/backend/main.py && \
grep -n "if SUBSCRIPTION_AVAILABLE:" web_service/backend/main.py | head -1 && \
echo "" && \
echo "=== 2. 运行修复脚本 ===" && \
python3 /tmp/add_subscription_endpoint.py /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 3. 验证端点已添加 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 4. 检查语法 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: 行 {e.lineno}, {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 5. 测试路由注册 ===" && \
cd web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 6. 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "" && \
echo "=== 7. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

## 如果脚本方法失败

如果脚本执行失败，可以手动编辑文件：

1. 在服务器上找到 `if SUBSCRIPTION_AVAILABLE:` 的位置
2. 在这行之前插入端点定义代码
3. 确保缩进正确（4个空格）

---

**请先在服务器上创建脚本文件（步骤1），然后执行修复命令（步骤2），并告诉我输出结果！** 🔧



# 手动修复：添加订阅产品端点

## 问题

服务器上的 `main.py` 只有 1041 行（本地有 1800 行），缺少端点定义。由于 Git 网络问题，无法通过拉取更新，需要手动添加。

## 解决方案

### 步骤 1：上传修复脚本到服务器

在**本地**执行（将脚本内容复制到服务器）：

```bash
# 在服务器上创建脚本文件
cat > /tmp/add_subscription_endpoint.py << 'SCRIPT_END'
#!/usr/bin/env python3
"""
在服务器上的 main.py 中添加订阅产品端点定义
"""

import sys
import os

# 端点定义代码
ENDPOINT_CODE = '''


# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    # 如果订阅系统未启用，返回空列表
    if not SUBSCRIPTION_AVAILABLE:
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    if not is_subscription_enabled():
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        products = []
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版（月付）",
                "description": "公测期特价：4.8元/月，每月20次下载",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版（月付）",
                "description": "公测期特价：19.9元/月，每月100次下载",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月",
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
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}",
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

'''

def find_insertion_point(file_path):
    """找到插入点：在最后一个函数定义之后，if SUBSCRIPTION_AVAILABLE 之前"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找 "if SUBSCRIPTION_AVAILABLE:" 的位置
    insertion_line = None
    for i, line in enumerate(lines):
        if line.strip() == "if SUBSCRIPTION_AVAILABLE:":
            insertion_line = i
            break
    
    if insertion_line is None:
        # 如果找不到，尝试在文件末尾插入
        print("⚠️  未找到 'if SUBSCRIPTION_AVAILABLE:'，将在文件末尾插入")
        return len(lines)
    
    # 向前查找，找到合适的位置（在函数定义之后）
    # 通常应该在最后一个 return FileResponse 之后
    for i in range(insertion_line - 1, max(0, insertion_line - 20), -1):
        if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
            # 找到这个函数的结束位置（下一个空行或 if 语句）
            for j in range(i + 1, insertion_line):
                if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                    return j
    
    # 如果找不到，就在 if SUBSCRIPTION_AVAILABLE 之前插入
    return insertion_line

def add_endpoint(file_path):
    """在文件中添加端点定义"""
    # 检查是否已经存在
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if '@app.get("/api/subscription/products")' in content:
            print("✅ 端点定义已存在，无需添加")
            return False
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到插入点
    insertion_line = find_insertion_point(file_path)
    
    # 插入代码
    new_lines = lines[:insertion_line] + [ENDPOINT_CODE] + lines[insertion_line:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ 端点定义已添加到第 {insertion_line} 行之后")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 add_subscription_endpoint.py <main.py路径>")
        print("示例: python3 add_subscription_endpoint.py /opt/beatsync/web_service/backend/main.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"📝 处理文件: {file_path}")
    
    try:
        if add_endpoint(file_path):
            print("✅ 端点定义添加成功！")
        else:
            print("ℹ️  端点定义已存在，无需修改")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
SCRIPT_END
```

### 步骤 2：在服务器上执行修复脚本

在**服务器**上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查文件当前状态 ===" && \
wc -l web_service/backend/main.py && \
grep -n "if SUBSCRIPTION_AVAILABLE:" web_service/backend/main.py | head -1 && \
echo "" && \
echo "=== 2. 运行修复脚本 ===" && \
python3 /tmp/add_subscription_endpoint.py /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 3. 验证端点已添加 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 4. 检查语法 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: 行 {e.lineno}, {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 5. 测试路由注册 ===" && \
cd web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 6. 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "" && \
echo "=== 7. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

## 如果脚本方法失败

如果脚本执行失败，可以手动编辑文件：

1. 在服务器上找到 `if SUBSCRIPTION_AVAILABLE:` 的位置
2. 在这行之前插入端点定义代码
3. 确保缩进正确（4个空格）

---

**请先在服务器上创建脚本文件（步骤1），然后执行修复命令（步骤2），并告诉我输出结果！** 🔧



# 手动修复：添加订阅产品端点

## 问题

服务器上的 `main.py` 只有 1041 行（本地有 1800 行），缺少端点定义。由于 Git 网络问题，无法通过拉取更新，需要手动添加。

## 解决方案

### 步骤 1：上传修复脚本到服务器

在**本地**执行（将脚本内容复制到服务器）：

```bash
# 在服务器上创建脚本文件
cat > /tmp/add_subscription_endpoint.py << 'SCRIPT_END'
#!/usr/bin/env python3
"""
在服务器上的 main.py 中添加订阅产品端点定义
"""

import sys
import os

# 端点定义代码
ENDPOINT_CODE = '''


# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    # 如果订阅系统未启用，返回空列表
    if not SUBSCRIPTION_AVAILABLE:
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    if not is_subscription_enabled():
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        products = []
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版（月付）",
                "description": "公测期特价：4.8元/月，每月20次下载",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版（月付）",
                "description": "公测期特价：19.9元/月，每月100次下载",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月",
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
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，永久有效",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}",
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

'''

def find_insertion_point(file_path):
    """找到插入点：在最后一个函数定义之后，if SUBSCRIPTION_AVAILABLE 之前"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找 "if SUBSCRIPTION_AVAILABLE:" 的位置
    insertion_line = None
    for i, line in enumerate(lines):
        if line.strip() == "if SUBSCRIPTION_AVAILABLE:":
            insertion_line = i
            break
    
    if insertion_line is None:
        # 如果找不到，尝试在文件末尾插入
        print("⚠️  未找到 'if SUBSCRIPTION_AVAILABLE:'，将在文件末尾插入")
        return len(lines)
    
    # 向前查找，找到合适的位置（在函数定义之后）
    # 通常应该在最后一个 return FileResponse 之后
    for i in range(insertion_line - 1, max(0, insertion_line - 20), -1):
        if 'return FileResponse' in lines[i] or 'return JSONResponse' in lines[i]:
            # 找到这个函数的结束位置（下一个空行或 if 语句）
            for j in range(i + 1, insertion_line):
                if lines[j].strip() == '' or lines[j].strip().startswith('if '):
                    return j
    
    # 如果找不到，就在 if SUBSCRIPTION_AVAILABLE 之前插入
    return insertion_line

def add_endpoint(file_path):
    """在文件中添加端点定义"""
    # 检查是否已经存在
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if '@app.get("/api/subscription/products")' in content:
            print("✅ 端点定义已存在，无需添加")
            return False
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到插入点
    insertion_line = find_insertion_point(file_path)
    
    # 插入代码
    new_lines = lines[:insertion_line] + [ENDPOINT_CODE] + lines[insertion_line:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ 端点定义已添加到第 {insertion_line} 行之后")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 add_subscription_endpoint.py <main.py路径>")
        print("示例: python3 add_subscription_endpoint.py /opt/beatsync/web_service/backend/main.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"📝 处理文件: {file_path}")
    
    try:
        if add_endpoint(file_path):
            print("✅ 端点定义添加成功！")
        else:
            print("ℹ️  端点定义已存在，无需修改")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
SCRIPT_END
```

### 步骤 2：在服务器上执行修复脚本

在**服务器**上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查文件当前状态 ===" && \
wc -l web_service/backend/main.py && \
grep -n "if SUBSCRIPTION_AVAILABLE:" web_service/backend/main.py | head -1 && \
echo "" && \
echo "=== 2. 运行修复脚本 ===" && \
python3 /tmp/add_subscription_endpoint.py /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 3. 验证端点已添加 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 4. 检查语法 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: 行 {e.lineno}, {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 5. 测试路由注册 ===" && \
cd web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 6. 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "" && \
echo "=== 7. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

## 如果脚本方法失败

如果脚本执行失败，可以手动编辑文件：

1. 在服务器上找到 `if SUBSCRIPTION_AVAILABLE:` 的位置
2. 在这行之前插入端点定义代码
3. 确保缩进正确（4个空格）

---

**请先在服务器上创建脚本文件（步骤1），然后执行修复命令（步骤2），并告诉我输出结果！** 🔧














