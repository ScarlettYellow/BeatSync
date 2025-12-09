#!/usr/bin/env python3
"""
创建 iOS 启动画面：白底 + 图标居中
需要先完成步骤 1（生成 AppIcon-1024.png）
"""

import sys
from pathlib import Path
from PIL import Image

def main():
    project_root = Path(__file__).parent.parent.parent
    icon_path = project_root / 'ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png'
    splash_dir = project_root / 'ios/App/App/Assets.xcassets/Splash.imageset'
    
    # 检查图标是否存在
    if not icon_path.exists():
        print(f"❌ 错误: 未找到图标文件 {icon_path}")
        print("   请先完成步骤 1：生成 AppIcon-1024.png")
        print("   参考: scripts/ios/generate_icons_manual.md")
        sys.exit(1)
    
    print("正在创建启动画面（白底+图标居中）...")
    
    # 加载图标
    try:
        icon = Image.open(str(icon_path))
    except Exception as e:
        print(f"❌ 错误: 无法打开图标文件: {e}")
        sys.exit(1)
    
    # 图标在启动画面中的大小（约为画布的 1/3）
    icon_size_ratio = 0.3
    
    # 创建不同尺寸的启动画面
    sizes = [
        (2732, "splash-2732x2732.png"),
        (1366, "splash-2732x2732-1.png"),
        (683, "splash-2732x2732-2.png"),
    ]
    
    for size, filename in sizes:
        # 创建白色背景
        bg = Image.new('RGB', (size, size), '#FFFFFF')
        
        # 计算图标大小
        target_icon_size = int(size * icon_size_ratio)
        
        # 调整图标大小（保持宽高比）
        icon_copy = icon.copy()
        icon_copy.thumbnail((target_icon_size, target_icon_size), Image.Resampling.LANCZOS)
        
        # 计算居中位置
        x = (size - icon_copy.width) // 2
        y = (size - icon_copy.height) // 2
        
        # 粘贴图标
        if icon_copy.mode == 'RGBA':
            bg.paste(icon_copy, (x, y), icon_copy)
        else:
            bg.paste(icon_copy, (x, y))
        
        # 保存
        output_path = splash_dir / filename
        bg.save(str(output_path), 'PNG')
        print(f"   ✅ 已生成: {filename} ({size}x{size})")
    
    print("\n✅ 启动画面创建完成！")
    print("\n下一步:")
    print("  1. 在 Xcode 中打开项目: npx cap open ios")
    print("  2. 检查 Assets.xcassets 中的启动画面")

if __name__ == '__main__':
    main()

