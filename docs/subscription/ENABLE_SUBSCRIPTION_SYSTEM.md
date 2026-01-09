# 启用订阅系统

## 当前状态

✅ 端点已成功注册并正常工作
⚠️ 但返回空列表，提示"订阅系统未启用"

## 启用订阅系统

订阅系统需要设置环境变量 `SUBSCRIPTION_ENABLED=true`。

### 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查当前环境变量 ===" && \
grep -E "SUBSCRIPTION_ENABLED|JWT_SECRET_KEY" web_service/backend/.env 2>/dev/null || echo "未找到 .env 文件" && \
echo "" && \
echo "=== 2. 检查 systemd 服务配置 ===" && \
sudo systemctl show beatsync | grep -E "Environment" && \
echo "" && \
echo "=== 3. 启用订阅系统 ===" && \
# 方法 1: 在 .env 文件中设置
if [ -f web_service/backend/.env ]; then
    if grep -q "SUBSCRIPTION_ENABLED" web_service/backend/.env; then
        sudo sed -i 's/SUBSCRIPTION_ENABLED=.*/SUBSCRIPTION_ENABLED=true/' web_service/backend/.env
    else
        echo "SUBSCRIPTION_ENABLED=true" | sudo tee -a web_service/backend/.env
    fi
    echo "✅ 已在 .env 文件中设置"
else
    echo "SUBSCRIPTION_ENABLED=true" | sudo tee web_service/backend/.env
    echo "✅ 已创建 .env 文件"
fi && \
echo "" && \
echo "=== 4. 检查 systemd 服务配置（需要设置环境变量）===" && \
# 检查服务文件
if sudo grep -q "Environment=" /etc/systemd/system/beatsync.service; then
    echo "服务文件已包含 Environment 配置"
    sudo cat /etc/systemd/system/beatsync.service | grep -A 5 "Environment"
else
    echo "⚠️  服务文件未包含 Environment 配置，需要添加"
    echo "编辑 /etc/systemd/system/beatsync.service，在 [Service] 部分添加："
    echo "Environment=\"SUBSCRIPTION_ENABLED=true\""
fi && \
echo "" && \
echo "=== 5. 重启服务 ===" && \
sudo systemctl daemon-reload && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "✅ 服务已重启" && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，启用订阅系统！** 🚀


# 启用订阅系统

## 当前状态

✅ 端点已成功注册并正常工作
⚠️ 但返回空列表，提示"订阅系统未启用"

## 启用订阅系统

订阅系统需要设置环境变量 `SUBSCRIPTION_ENABLED=true`。

### 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查当前环境变量 ===" && \
grep -E "SUBSCRIPTION_ENABLED|JWT_SECRET_KEY" web_service/backend/.env 2>/dev/null || echo "未找到 .env 文件" && \
echo "" && \
echo "=== 2. 检查 systemd 服务配置 ===" && \
sudo systemctl show beatsync | grep -E "Environment" && \
echo "" && \
echo "=== 3. 启用订阅系统 ===" && \
# 方法 1: 在 .env 文件中设置
if [ -f web_service/backend/.env ]; then
    if grep -q "SUBSCRIPTION_ENABLED" web_service/backend/.env; then
        sudo sed -i 's/SUBSCRIPTION_ENABLED=.*/SUBSCRIPTION_ENABLED=true/' web_service/backend/.env
    else
        echo "SUBSCRIPTION_ENABLED=true" | sudo tee -a web_service/backend/.env
    fi
    echo "✅ 已在 .env 文件中设置"
else
    echo "SUBSCRIPTION_ENABLED=true" | sudo tee web_service/backend/.env
    echo "✅ 已创建 .env 文件"
fi && \
echo "" && \
echo "=== 4. 检查 systemd 服务配置（需要设置环境变量）===" && \
# 检查服务文件
if sudo grep -q "Environment=" /etc/systemd/system/beatsync.service; then
    echo "服务文件已包含 Environment 配置"
    sudo cat /etc/systemd/system/beatsync.service | grep -A 5 "Environment"
else
    echo "⚠️  服务文件未包含 Environment 配置，需要添加"
    echo "编辑 /etc/systemd/system/beatsync.service，在 [Service] 部分添加："
    echo "Environment=\"SUBSCRIPTION_ENABLED=true\""
fi && \
echo "" && \
echo "=== 5. 重启服务 ===" && \
sudo systemctl daemon-reload && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "✅ 服务已重启" && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，启用订阅系统！** 🚀


# 启用订阅系统

## 当前状态

✅ 端点已成功注册并正常工作
⚠️ 但返回空列表，提示"订阅系统未启用"

## 启用订阅系统

订阅系统需要设置环境变量 `SUBSCRIPTION_ENABLED=true`。

### 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查当前环境变量 ===" && \
grep -E "SUBSCRIPTION_ENABLED|JWT_SECRET_KEY" web_service/backend/.env 2>/dev/null || echo "未找到 .env 文件" && \
echo "" && \
echo "=== 2. 检查 systemd 服务配置 ===" && \
sudo systemctl show beatsync | grep -E "Environment" && \
echo "" && \
echo "=== 3. 启用订阅系统 ===" && \
# 方法 1: 在 .env 文件中设置
if [ -f web_service/backend/.env ]; then
    if grep -q "SUBSCRIPTION_ENABLED" web_service/backend/.env; then
        sudo sed -i 's/SUBSCRIPTION_ENABLED=.*/SUBSCRIPTION_ENABLED=true/' web_service/backend/.env
    else
        echo "SUBSCRIPTION_ENABLED=true" | sudo tee -a web_service/backend/.env
    fi
    echo "✅ 已在 .env 文件中设置"
else
    echo "SUBSCRIPTION_ENABLED=true" | sudo tee web_service/backend/.env
    echo "✅ 已创建 .env 文件"
fi && \
echo "" && \
echo "=== 4. 检查 systemd 服务配置（需要设置环境变量）===" && \
# 检查服务文件
if sudo grep -q "Environment=" /etc/systemd/system/beatsync.service; then
    echo "服务文件已包含 Environment 配置"
    sudo cat /etc/systemd/system/beatsync.service | grep -A 5 "Environment"
else
    echo "⚠️  服务文件未包含 Environment 配置，需要添加"
    echo "编辑 /etc/systemd/system/beatsync.service，在 [Service] 部分添加："
    echo "Environment=\"SUBSCRIPTION_ENABLED=true\""
fi && \
echo "" && \
echo "=== 5. 重启服务 ===" && \
sudo systemctl daemon-reload && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "✅ 服务已重启" && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，启用订阅系统！** 🚀













