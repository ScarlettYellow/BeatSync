#!/bin/bash
# 简单的图标生成脚本
# 使用 macOS 自带工具或提供手动步骤

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SVG_PATH="$PROJECT_ROOT/web_service/frontend/favicon.svg"
IOS_ASSETS="$PROJECT_ROOT/ios/App/App/Assets.xcassets"
APP_ICON_DIR="$IOS_ASSETS/AppIcon.appiconset"
SPLASH_DIR="$IOS_ASSETS/Splash.imageset"

echo "正在生成 iOS 图标和启动画面..."
echo ""

# 检查 SVG 文件
if [ ! -f "$SVG_PATH" ]; then
    echo "错误: 未找到 $SVG_PATH"
    exit 1
fi

# 方法1: 尝试使用 rsvg-convert（如果已安装）
if command -v rsvg-convert &> /dev/null; then
    echo "✅ 使用 rsvg-convert 转换图标..."
    
    # 生成 1024x1024 图标
    rsvg-convert -w 1024 -h 1024 "$SVG_PATH" -o "$APP_ICON_DIR/AppIcon-1024.png"
    echo "   ✅ 已生成: AppIcon-1024.png"
    
    # 生成启动画面（使用图标作为基础）
    rsvg-convert -w 2732 -h 2732 "$SVG_PATH" -o "$SPLASH_DIR/icon-2732.png"
    rsvg-convert -w 1366 -h 1366 "$SVG_PATH" -o "$SPLASH_DIR/icon-1366.png"
    rsvg-convert -w 683 -h 683 "$SVG_PATH" -o "$SPLASH_DIR/icon-683.png"
    
    echo "   ✅ 已生成启动画面图标"
    
elif command -v qlmanage &> /dev/null; then
    echo "⚠️  rsvg-convert 未安装，使用替代方法..."
    echo ""
    echo "请手动完成以下步骤："
    echo ""
    echo "方法1（推荐）: 使用在线工具"
    echo "  1. 访问 https://cloudconvert.com/svg-to-png"
    echo "  2. 上传 $SVG_PATH"
    echo "  3. 设置尺寸为 1024x1024，下载为 AppIcon-1024.png"
    echo "  4. 保存到: $APP_ICON_DIR/AppIcon-1024.png"
    echo ""
    echo "方法2: 使用 macOS Preview"
    echo "  1. 打开 $SVG_PATH"
    echo "  2. 文件 -> 导出 -> 格式选择 PNG"
    echo "  3. 设置尺寸为 1024x1024"
    echo "  4. 保存到: $APP_ICON_DIR/AppIcon-1024.png"
    echo ""
    exit 1
else
    echo "错误: 未找到可用的转换工具"
    exit 1
fi

# 创建启动画面（白底+图标居中）
echo ""
echo "正在创建启动画面（白底+图标居中）..."

# 检查是否有 Python 和 PIL
if python3 -c "from PIL import Image" 2>/dev/null; then
    python3 << 'PYTHON_SCRIPT'
import sys
from pathlib import Path
from PIL import Image, ImageDraw

project_root = Path("$PROJECT_ROOT")
icon_1024 = project_root / "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"
splash_dir = project_root / "ios/App/App/Assets.xcassets/Splash.imageset"

# 加载图标
icon = Image.open(str(icon_1024))
icon_size = 512  # 启动画面中的图标大小
icon.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)

# 创建不同尺寸的启动画面
sizes = [
    (2732, "splash-2732x2732.png"),
    (1366, "splash-2732x2732-1.png"),
    (683, "splash-2732x2732-2.png"),
]

for size, filename in sizes:
    # 创建白色背景
    bg = Image.new('RGB', (size, size), '#FFFFFF')
    
    # 计算居中位置
    x = (size - icon.width) // 2
    y = (size - icon.height) // 2
    
    # 粘贴图标
    if icon.mode == 'RGBA':
        bg.paste(icon, (x, y), icon)
    else:
        bg.paste(icon, (x, y))
    
    # 保存
    bg.save(splash_dir / filename, 'PNG')
    print(f"   ✅ 已生成: {filename}")

PYTHON_SCRIPT
else
    echo "⚠️  PIL/Pillow 未安装，启动画面需要手动创建"
    echo "   请使用图像编辑软件创建白底+图标居中的启动画面"
fi

echo ""
echo "✅ 图标和启动画面生成完成！"
echo ""
echo "下一步:"
echo "  1. 在 Xcode 中打开项目: npx cap open ios"
echo "  2. 检查 Assets.xcassets 中的图标和启动画面"

