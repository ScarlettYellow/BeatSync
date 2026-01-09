# 添加订阅系统文件到 Git

## 当前状态

✅ 文件已添加到 Git 暂存区
📝 需要提交并推送到远程仓库

## 下一步操作

### 在本地执行：

```bash
# 1. 提交文件
git commit -m "feat: 添加订阅系统模块文件

- subscription_service.py: 订阅系统服务层
- subscription_db.py: 数据库初始化和管理
- subscription_receipt_verification.py: 收据验证
- payment_service.py: 支付服务模块"

# 2. 推送到远程
git push origin main
```

### 在服务器上执行（如果 Git 拉取成功）：

```bash
cd /opt/beatsync && \
sudo git fetch origin main && \
sudo git reset --hard origin/main && \
echo "=== 验证文件已同步 ===" && \
ls -la web_service/backend/subscription_*.py payment_service.py && \
echo "" && \
echo "=== 测试模块导入 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from subscription_service import is_subscription_enabled
    from payment_service import PRODUCT_PRICES
    print('✅ 模块导入成功')
    print(f'✅ PRODUCT_PRICES: {list(PRODUCT_PRICES.keys())[:5]}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
" && \
echo "" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

### 如果 Git 拉取仍然失败（网络问题）

使用 scp 从本地复制文件到服务器：

```bash
# 在本地执行（替换为你的服务器地址）
SERVER="user@your-server"  # 例如：root@beatsync.site

scp web_service/backend/subscription_service.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_db.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_receipt_verification.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/payment_service.py $SERVER:/opt/beatsync/web_service/backend/
```

---

**请先在本地提交并推送文件，然后在服务器上拉取（或使用 scp 复制）！** 🚀


# 添加订阅系统文件到 Git

## 当前状态

✅ 文件已添加到 Git 暂存区
📝 需要提交并推送到远程仓库

## 下一步操作

### 在本地执行：

```bash
# 1. 提交文件
git commit -m "feat: 添加订阅系统模块文件

- subscription_service.py: 订阅系统服务层
- subscription_db.py: 数据库初始化和管理
- subscription_receipt_verification.py: 收据验证
- payment_service.py: 支付服务模块"

# 2. 推送到远程
git push origin main
```

### 在服务器上执行（如果 Git 拉取成功）：

```bash
cd /opt/beatsync && \
sudo git fetch origin main && \
sudo git reset --hard origin/main && \
echo "=== 验证文件已同步 ===" && \
ls -la web_service/backend/subscription_*.py payment_service.py && \
echo "" && \
echo "=== 测试模块导入 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from subscription_service import is_subscription_enabled
    from payment_service import PRODUCT_PRICES
    print('✅ 模块导入成功')
    print(f'✅ PRODUCT_PRICES: {list(PRODUCT_PRICES.keys())[:5]}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
" && \
echo "" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

### 如果 Git 拉取仍然失败（网络问题）

使用 scp 从本地复制文件到服务器：

```bash
# 在本地执行（替换为你的服务器地址）
SERVER="user@your-server"  # 例如：root@beatsync.site

scp web_service/backend/subscription_service.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_db.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_receipt_verification.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/payment_service.py $SERVER:/opt/beatsync/web_service/backend/
```

---

**请先在本地提交并推送文件，然后在服务器上拉取（或使用 scp 复制）！** 🚀


# 添加订阅系统文件到 Git

## 当前状态

✅ 文件已添加到 Git 暂存区
📝 需要提交并推送到远程仓库

## 下一步操作

### 在本地执行：

```bash
# 1. 提交文件
git commit -m "feat: 添加订阅系统模块文件

- subscription_service.py: 订阅系统服务层
- subscription_db.py: 数据库初始化和管理
- subscription_receipt_verification.py: 收据验证
- payment_service.py: 支付服务模块"

# 2. 推送到远程
git push origin main
```

### 在服务器上执行（如果 Git 拉取成功）：

```bash
cd /opt/beatsync && \
sudo git fetch origin main && \
sudo git reset --hard origin/main && \
echo "=== 验证文件已同步 ===" && \
ls -la web_service/backend/subscription_*.py payment_service.py && \
echo "" && \
echo "=== 测试模块导入 ===" && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from subscription_service import is_subscription_enabled
    from payment_service import PRODUCT_PRICES
    print('✅ 模块导入成功')
    print(f'✅ PRODUCT_PRICES: {list(PRODUCT_PRICES.keys())[:5]}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
" && \
echo "" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

### 如果 Git 拉取仍然失败（网络问题）

使用 scp 从本地复制文件到服务器：

```bash
# 在本地执行（替换为你的服务器地址）
SERVER="user@your-server"  # 例如：root@beatsync.site

scp web_service/backend/subscription_service.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_db.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_receipt_verification.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/payment_service.py $SERVER:/opt/beatsync/web_service/backend/
```

---

**请先在本地提交并推送文件，然后在服务器上拉取（或使用 scp 复制）！** 🚀













