# 检查订阅系统状态

## 当前状态

✅ 端点已正常工作，返回 JSON 响应
⚠️ 但返回空列表，提示"订阅系统未启用"

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 是否定义 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    # 只导入到定义 SUBSCRIPTION_AVAILABLE 的位置
    with open('/opt/beatsync/web_service/backend/main.py', 'r') as f:
        code = f.read()
        # 执行到 SUBSCRIPTION_AVAILABLE 定义
        exec(compile(code.split('app = FastAPI')[0], '<string>', 'exec'))
        print(f'✅ SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}')
    except NameError as e:
        print(f'❌ SUBSCRIPTION_AVAILABLE 未定义: {e}')
    except Exception as e:
        print(f'❌ 其他错误: {e}')
        import traceback
        traceback.print_exc()
" && \
echo "" && \
echo "=== 2. 检查订阅系统模块是否存在 ===" && \
ls -la web_service/backend/subscription_*.py 2>/dev/null | head -5 && \
echo "" && \
echo "=== 3. 测试 is_subscription_enabled() ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from subscription_service import is_subscription_enabled
    result = is_subscription_enabled()
    print(f'✅ is_subscription_enabled() = {result}')
except ImportError as e:
    print(f'❌ 无法导入 subscription_service: {e}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 4. 检查 payment_service 模块 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
    print(f'✅ PRODUCT_PRICES: {list(PRODUCT_PRICES.keys())[:5]}')
    print(f'✅ PRODUCT_CREDITS: {list(PRODUCT_CREDITS.keys())[:5]}')
except ImportError as e:
    print(f'❌ 无法导入 payment_service: {e}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
"
```

---

**请执行上述命令，并告诉我输出结果！** 🔍



# 检查订阅系统状态

## 当前状态

✅ 端点已正常工作，返回 JSON 响应
⚠️ 但返回空列表，提示"订阅系统未启用"

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 是否定义 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    # 只导入到定义 SUBSCRIPTION_AVAILABLE 的位置
    with open('/opt/beatsync/web_service/backend/main.py', 'r') as f:
        code = f.read()
        # 执行到 SUBSCRIPTION_AVAILABLE 定义
        exec(compile(code.split('app = FastAPI')[0], '<string>', 'exec'))
        print(f'✅ SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}')
    except NameError as e:
        print(f'❌ SUBSCRIPTION_AVAILABLE 未定义: {e}')
    except Exception as e:
        print(f'❌ 其他错误: {e}')
        import traceback
        traceback.print_exc()
" && \
echo "" && \
echo "=== 2. 检查订阅系统模块是否存在 ===" && \
ls -la web_service/backend/subscription_*.py 2>/dev/null | head -5 && \
echo "" && \
echo "=== 3. 测试 is_subscription_enabled() ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from subscription_service import is_subscription_enabled
    result = is_subscription_enabled()
    print(f'✅ is_subscription_enabled() = {result}')
except ImportError as e:
    print(f'❌ 无法导入 subscription_service: {e}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 4. 检查 payment_service 模块 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
    print(f'✅ PRODUCT_PRICES: {list(PRODUCT_PRICES.keys())[:5]}')
    print(f'✅ PRODUCT_CREDITS: {list(PRODUCT_CREDITS.keys())[:5]}')
except ImportError as e:
    print(f'❌ 无法导入 payment_service: {e}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
"
```

---

**请执行上述命令，并告诉我输出结果！** 🔍



# 检查订阅系统状态

## 当前状态

✅ 端点已正常工作，返回 JSON 响应
⚠️ 但返回空列表，提示"订阅系统未启用"

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 是否定义 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    # 只导入到定义 SUBSCRIPTION_AVAILABLE 的位置
    with open('/opt/beatsync/web_service/backend/main.py', 'r') as f:
        code = f.read()
        # 执行到 SUBSCRIPTION_AVAILABLE 定义
        exec(compile(code.split('app = FastAPI')[0], '<string>', 'exec'))
        print(f'✅ SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}')
    except NameError as e:
        print(f'❌ SUBSCRIPTION_AVAILABLE 未定义: {e}')
    except Exception as e:
        print(f'❌ 其他错误: {e}')
        import traceback
        traceback.print_exc()
" && \
echo "" && \
echo "=== 2. 检查订阅系统模块是否存在 ===" && \
ls -la web_service/backend/subscription_*.py 2>/dev/null | head -5 && \
echo "" && \
echo "=== 3. 测试 is_subscription_enabled() ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from subscription_service import is_subscription_enabled
    result = is_subscription_enabled()
    print(f'✅ is_subscription_enabled() = {result}')
except ImportError as e:
    print(f'❌ 无法导入 subscription_service: {e}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 4. 检查 payment_service 模块 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
    print(f'✅ PRODUCT_PRICES: {list(PRODUCT_PRICES.keys())[:5]}')
    print(f'✅ PRODUCT_CREDITS: {list(PRODUCT_CREDITS.keys())[:5]}')
except ImportError as e:
    print(f'❌ 无法导入 payment_service: {e}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
"
```

---

**请执行上述命令，并告诉我输出结果！** 🔍














