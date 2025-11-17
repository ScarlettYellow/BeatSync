#!/bin/bash
# 设置自动化Git版本管理

echo "=========================================="
echo "设置自动化Git版本管理"
echo "=========================================="
echo ""

# 1. 确保hooks可执行
echo "1. 设置Git hooks权限..."
chmod +x .git/hooks/pre-commit 2>/dev/null || true
chmod +x .git/hooks/post-commit 2>/dev/null || true
echo "   ✅ 完成"
echo ""

# 2. 配置自动推送（可选）
echo "2. 配置自动推送选项..."
echo "   选项："
echo "   a) 启用自动推送（每次提交后自动推送到GitHub）"
echo "   b) 禁用自动推送（需要手动推送）"
echo ""
read -p "请选择 (a/b，默认b): " -n 1 -r
echo

if [[ $REPLY =~ ^[Aa]$ ]]; then
    git config beatsync.auto-push true
    echo "   ✅ 已启用自动推送"
else
    git config beatsync.auto-push false
    echo "   ✅ 已禁用自动推送（默认）"
fi
echo ""

# 3. 创建自动提交脚本快捷方式
echo "3. 创建快捷方式..."
if [ ! -f "ac" ]; then
    ln -s auto_commit.sh ac 2>/dev/null || true
    echo "   ✅ 创建快捷方式: ./ac (等同于 ./auto_commit.sh)"
else
    echo "   ℹ️  快捷方式已存在"
fi
echo ""

# 4. 显示配置信息
echo "4. 当前配置："
echo "   自动推送: $(git config --get beatsync.auto-push || echo 'false')"
echo "   远程仓库: $(git remote get-url origin 2>/dev/null || echo '未设置')"
echo ""

echo "=========================================="
echo "设置完成！"
echo "=========================================="
echo ""
echo "使用方法："
echo "  1. 自动提交: ./auto_commit.sh 或 ./ac"
echo "  2. 手动提交: ./git_commit_important.sh \"类型: 描述\""
echo "  3. 手动推送: git push"
echo ""

