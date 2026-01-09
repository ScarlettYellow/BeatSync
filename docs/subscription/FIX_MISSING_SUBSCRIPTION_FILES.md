# 修复：缺少订阅系统文件

## 问题

服务器上缺少订阅系统模块文件（这些文件在本地但未被 Git 跟踪）：
- `subscription_service.py` (1075 行)
- `subscription_db.py` (188 行)
- `subscription_receipt_verification.py` (295 行)
- `payment_service.py` (414 行)

## 解决方案

### 方案 1：使用 scp 从本地复制到服务器（推荐）

在**本地**执行：

```bash
# 替换 user@your-server 为你的服务器 SSH 地址
SERVER="user@your-server"  # 例如：root@beatsync.site 或 ubuntu@123.456.789.0

# 复制文件
scp web_service/backend/subscription_service.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_db.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_receipt_verification.py $SERVER:/opt/beatsync/web_service/backend/
scp web_service/backend/payment_service.py $SERVER:/opt/beatsync/web_service/backend/
```

### 方案 2：先添加到 Git，然后推送（如果网络问题已解决）

在**本地**执行：

```bash
# 添加文件到 Git
git add web_service/backend/subscription_*.py web_service/backend/payment_service.py

# 提交
git commit -m "feat: 添加订阅系统模块文件"

# 推送到远程
git push origin main
```

然后在**服务器**上执行：

```bash
cd /opt/beatsync && \
sudo git fetch origin main && \
sudo git reset --hard origin/main
```

### 方案 3：手动创建文件（如果无法使用 scp 或 Git）

由于文件较大，建议使用方案 1 或 2。

---

## 验证

复制文件后，在**服务器**上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查文件是否存在 ===" && \
ls -la web_service/backend/subscription_*.py payment_service.py && \
echo "" && \
echo "=== 2. 检查语法 ===" && \
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
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 3. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && \
echo "" && \
echo "=== 4. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请先使用方案 1（scp）将文件复制到服务器，然后执行验证命令！** 📁
