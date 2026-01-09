# 修复 SUBSCRIPTION_AVAILABLE 未定义错误

## 问题

端点函数中使用了 `SUBSCRIPTION_AVAILABLE` 变量，但该变量未定义，导致 `NameError`。

## 解决方案

需要修复端点函数，使其能够安全处理 `SUBSCRIPTION_AVAILABLE` 未定义的情况。

## 修复命令

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 2. 修复端点函数 ===" && \
python3 << 'FIX_SCRIPT'
import re

file_path = '/opt/beatsync/web_service/backend/main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找端点函数
pattern = r'(async def get_subscription_products\(\):.*?)(if not SUBSCRIPTION_AVAILABLE:)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # 替换为安全版本
    old_code = match.group(0)
    new_code = old_code.replace(
        'if not SUBSCRIPTION_AVAILABLE:',
        'if not globals().get("SUBSCRIPTION_AVAILABLE", False):'
    )
    content = content.replace(old_code, new_code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 端点函数已修复")
else:
    print("⚠️  未找到端点函数，使用备用方案")
    # 备用方案：直接替换字符串
    if 'if not SUBSCRIPTION_AVAILABLE:' in content:
        content = content.replace(
            'if not SUBSCRIPTION_AVAILABLE:',
            'if not globals().get("SUBSCRIPTION_AVAILABLE", False):'
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 端点函数已修复（备用方案）")
    else:
        print("❌ 未找到需要修复的代码")
FIX_SCRIPT
echo "" && \
echo "=== 3. 验证修复 ===" && \
grep -A 2 "get_subscription_products" web_service/backend/main.py | grep -A 2 "SUBSCRIPTION_AVAILABLE" | head -5 && \
echo "" && \
echo "=== 4. 检查语法 ===" && \
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "" && \
echo "=== 5. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，并告诉我输出结果！** 🔧



# 修复 SUBSCRIPTION_AVAILABLE 未定义错误

## 问题

端点函数中使用了 `SUBSCRIPTION_AVAILABLE` 变量，但该变量未定义，导致 `NameError`。

## 解决方案

需要修复端点函数，使其能够安全处理 `SUBSCRIPTION_AVAILABLE` 未定义的情况。

## 修复命令

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 2. 修复端点函数 ===" && \
python3 << 'FIX_SCRIPT'
import re

file_path = '/opt/beatsync/web_service/backend/main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找端点函数
pattern = r'(async def get_subscription_products\(\):.*?)(if not SUBSCRIPTION_AVAILABLE:)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # 替换为安全版本
    old_code = match.group(0)
    new_code = old_code.replace(
        'if not SUBSCRIPTION_AVAILABLE:',
        'if not globals().get("SUBSCRIPTION_AVAILABLE", False):'
    )
    content = content.replace(old_code, new_code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 端点函数已修复")
else:
    print("⚠️  未找到端点函数，使用备用方案")
    # 备用方案：直接替换字符串
    if 'if not SUBSCRIPTION_AVAILABLE:' in content:
        content = content.replace(
            'if not SUBSCRIPTION_AVAILABLE:',
            'if not globals().get("SUBSCRIPTION_AVAILABLE", False):'
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 端点函数已修复（备用方案）")
    else:
        print("❌ 未找到需要修复的代码")
FIX_SCRIPT
echo "" && \
echo "=== 3. 验证修复 ===" && \
grep -A 2 "get_subscription_products" web_service/backend/main.py | grep -A 2 "SUBSCRIPTION_AVAILABLE" | head -5 && \
echo "" && \
echo "=== 4. 检查语法 ===" && \
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "" && \
echo "=== 5. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，并告诉我输出结果！** 🔧



# 修复 SUBSCRIPTION_AVAILABLE 未定义错误

## 问题

端点函数中使用了 `SUBSCRIPTION_AVAILABLE` 变量，但该变量未定义，导致 `NameError`。

## 解决方案

需要修复端点函数，使其能够安全处理 `SUBSCRIPTION_AVAILABLE` 未定义的情况。

## 修复命令

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 2. 修复端点函数 ===" && \
python3 << 'FIX_SCRIPT'
import re

file_path = '/opt/beatsync/web_service/backend/main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找端点函数
pattern = r'(async def get_subscription_products\(\):.*?)(if not SUBSCRIPTION_AVAILABLE:)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # 替换为安全版本
    old_code = match.group(0)
    new_code = old_code.replace(
        'if not SUBSCRIPTION_AVAILABLE:',
        'if not globals().get("SUBSCRIPTION_AVAILABLE", False):'
    )
    content = content.replace(old_code, new_code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 端点函数已修复")
else:
    print("⚠️  未找到端点函数，使用备用方案")
    # 备用方案：直接替换字符串
    if 'if not SUBSCRIPTION_AVAILABLE:' in content:
        content = content.replace(
            'if not SUBSCRIPTION_AVAILABLE:',
            'if not globals().get("SUBSCRIPTION_AVAILABLE", False):'
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 端点函数已修复（备用方案）")
    else:
        print("❌ 未找到需要修复的代码")
FIX_SCRIPT
echo "" && \
echo "=== 3. 验证修复 ===" && \
grep -A 2 "get_subscription_products" web_service/backend/main.py | grep -A 2 "SUBSCRIPTION_AVAILABLE" | head -5 && \
echo "" && \
echo "=== 4. 检查语法 ===" && \
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "" && \
echo "=== 5. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，并告诉我输出结果！** 🔧














