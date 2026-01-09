# 在服务配置中添加环境变量

## 问题

服务配置文件中没有 `SUBSCRIPTION_ENABLED=true` 环境变量，导致订阅系统未启用。

## 修复步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 备份服务配置文件 ===" && \
sudo cp /etc/systemd/system/beatsync.service /etc/systemd/system/beatsync.service.backup.$(date +%Y%m%d_%H%M%S) && \
echo "✅ 备份完成" && \
echo "" && \
echo "=== 2. 添加 SUBSCRIPTION_ENABLED 环境变量 ===" && \
# 在 Environment 行后添加新的环境变量
sudo sed -i '/Environment="PATH=/a Environment="SUBSCRIPTION_ENABLED=true"' /etc/systemd/system/beatsync.service && \
echo "✅ 环境变量已添加" && \
echo "" && \
echo "=== 3. 验证配置 ===" && \
sudo cat /etc/systemd/system/beatsync.service | grep -A 5 "\[Service\]" && \
echo "" && \
echo "=== 4. 重新加载并重启服务 ===" && \
sudo systemctl daemon-reload && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "✅ 服务已重启" && \
echo "" && \
echo "=== 5. 验证环境变量 ===" && \
sudo systemctl show beatsync | grep -E "SUBSCRIPTION" && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，添加环境变量并重启服务！** 🚀


# 在服务配置中添加环境变量

## 问题

服务配置文件中没有 `SUBSCRIPTION_ENABLED=true` 环境变量，导致订阅系统未启用。

## 修复步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 备份服务配置文件 ===" && \
sudo cp /etc/systemd/system/beatsync.service /etc/systemd/system/beatsync.service.backup.$(date +%Y%m%d_%H%M%S) && \
echo "✅ 备份完成" && \
echo "" && \
echo "=== 2. 添加 SUBSCRIPTION_ENABLED 环境变量 ===" && \
# 在 Environment 行后添加新的环境变量
sudo sed -i '/Environment="PATH=/a Environment="SUBSCRIPTION_ENABLED=true"' /etc/systemd/system/beatsync.service && \
echo "✅ 环境变量已添加" && \
echo "" && \
echo "=== 3. 验证配置 ===" && \
sudo cat /etc/systemd/system/beatsync.service | grep -A 5 "\[Service\]" && \
echo "" && \
echo "=== 4. 重新加载并重启服务 ===" && \
sudo systemctl daemon-reload && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "✅ 服务已重启" && \
echo "" && \
echo "=== 5. 验证环境变量 ===" && \
sudo systemctl show beatsync | grep -E "SUBSCRIPTION" && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，添加环境变量并重启服务！** 🚀


# 在服务配置中添加环境变量

## 问题

服务配置文件中没有 `SUBSCRIPTION_ENABLED=true` 环境变量，导致订阅系统未启用。

## 修复步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 备份服务配置文件 ===" && \
sudo cp /etc/systemd/system/beatsync.service /etc/systemd/system/beatsync.service.backup.$(date +%Y%m%d_%H%M%S) && \
echo "✅ 备份完成" && \
echo "" && \
echo "=== 2. 添加 SUBSCRIPTION_ENABLED 环境变量 ===" && \
# 在 Environment 行后添加新的环境变量
sudo sed -i '/Environment="PATH=/a Environment="SUBSCRIPTION_ENABLED=true"' /etc/systemd/system/beatsync.service && \
echo "✅ 环境变量已添加" && \
echo "" && \
echo "=== 3. 验证配置 ===" && \
sudo cat /etc/systemd/system/beatsync.service | grep -A 5 "\[Service\]" && \
echo "" && \
echo "=== 4. 重新加载并重启服务 ===" && \
sudo systemctl daemon-reload && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "✅ 服务已重启" && \
echo "" && \
echo "=== 5. 验证环境变量 ===" && \
sudo systemctl show beatsync | grep -E "SUBSCRIPTION" && \
echo "" && \
echo "=== 6. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，添加环境变量并重启服务！** 🚀













