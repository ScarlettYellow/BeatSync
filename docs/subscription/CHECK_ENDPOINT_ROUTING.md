# 检查端点路由注册

## 问题

文件已存在，模块导入成功，但端点返回 404。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查端点定义是否存在 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查端点函数是否完整 ===" && \
sed -n '1048,1100p' web_service/backend/main.py && \
echo "" && \
echo "=== 3. 测试路由注册（直接导入）===" && \
cd web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    print('✅ 应用导入成功')
    # 查找所有路由
    all_routes = [r for r in app.routes if hasattr(r, 'path')]
    print(f'✅ 总路由数: {len(all_routes)}')
    # 查找订阅相关路由
    subscription_routes = [r for r in all_routes if 'subscription' in r.path]
    print(f'✅ 订阅相关路由数: {len(subscription_routes)}')
    for r in subscription_routes:
        methods = getattr(r, 'methods', set())
        print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
    # 查找 products 端点
    products_routes = [r for r in all_routes if 'products' in r.path]
    print(f'✅ products 相关路由: {len(products_routes)}')
    for r in products_routes:
        methods = getattr(r, 'methods', set())
        print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 4. 检查服务日志（最近错误）===" && \
sudo journalctl -u beatsync -n 20 --no-pager | tail -20
```

---

**请执行上述命令，并告诉我输出结果！** 🔍


# 检查端点路由注册

## 问题

文件已存在，模块导入成功，但端点返回 404。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查端点定义是否存在 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查端点函数是否完整 ===" && \
sed -n '1048,1100p' web_service/backend/main.py && \
echo "" && \
echo "=== 3. 测试路由注册（直接导入）===" && \
cd web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    print('✅ 应用导入成功')
    # 查找所有路由
    all_routes = [r for r in app.routes if hasattr(r, 'path')]
    print(f'✅ 总路由数: {len(all_routes)}')
    # 查找订阅相关路由
    subscription_routes = [r for r in all_routes if 'subscription' in r.path]
    print(f'✅ 订阅相关路由数: {len(subscription_routes)}')
    for r in subscription_routes:
        methods = getattr(r, 'methods', set())
        print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
    # 查找 products 端点
    products_routes = [r for r in all_routes if 'products' in r.path]
    print(f'✅ products 相关路由: {len(products_routes)}')
    for r in products_routes:
        methods = getattr(r, 'methods', set())
        print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 4. 检查服务日志（最近错误）===" && \
sudo journalctl -u beatsync -n 20 --no-pager | tail -20
```

---

**请执行上述命令，并告诉我输出结果！** 🔍


# 检查端点路由注册

## 问题

文件已存在，模块导入成功，但端点返回 404。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查端点定义是否存在 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查端点函数是否完整 ===" && \
sed -n '1048,1100p' web_service/backend/main.py && \
echo "" && \
echo "=== 3. 测试路由注册（直接导入）===" && \
cd web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    print('✅ 应用导入成功')
    # 查找所有路由
    all_routes = [r for r in app.routes if hasattr(r, 'path')]
    print(f'✅ 总路由数: {len(all_routes)}')
    # 查找订阅相关路由
    subscription_routes = [r for r in all_routes if 'subscription' in r.path]
    print(f'✅ 订阅相关路由数: {len(subscription_routes)}')
    for r in subscription_routes:
        methods = getattr(r, 'methods', set())
        print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
    # 查找 products 端点
    products_routes = [r for r in all_routes if 'products' in r.path]
    print(f'✅ products 相关路由: {len(products_routes)}')
    for r in products_routes:
        methods = getattr(r, 'methods', set())
        print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 4. 检查服务日志（最近错误）===" && \
sudo journalctl -u beatsync -n 20 --no-pager | tail -20
```

---

**请执行上述命令，并告诉我输出结果！** 🔍













