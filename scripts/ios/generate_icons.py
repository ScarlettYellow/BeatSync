#!/usr/bin/env python3
"""
生成 iOS 应用图标和启动画面
从 favicon.svg 生成所需尺寸的图标和启动画面
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# iOS 需要的图标尺寸（App Store 只需要 1024x1024）
ICON_SIZES = [1024]

# 启动画面尺寸（使用 3x 尺寸，即 2732x2732）
SPLASH_SIZE = 2732

def check_dependencies():
    """检查必要的工具是否可用"""
    # 检查 sips（macOS 自带）
    if not os.path.exists('/usr/bin/sips'):
        print("错误: 未找到 sips 工具（macOS 自带，应该存在）")
        return False
    
    # 检查是否有 SVG 转换工具
    # 尝试使用 qlmanage 或 rsvg-convert
    has_rsvg = subprocess.run(['which', 'rsvg-convert'], 
                            capture_output=True).returncode == 0
    has_qlmanage = os.path.exists('/usr/bin/qlmanage')
    
    if not has_rsvg and not has_qlmanage:
        print("警告: 未找到 SVG 转换工具，将尝试使用其他方法")
    
    return True

def svg_to_png_sips(svg_path, png_path, size):
    """
    使用 Python + cairosvg 将 SVG 转换为 PNG
    """
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, 
                        output_width=size, output_height=size)
        return True
    except ImportError:
        print(f"错误: cairosvg 未安装，请运行: pip3 install cairosvg --user")
        return False
    except Exception as e:
        print(f"错误: 转换 SVG 失败: {e}")
        return False

def create_splash_screen(icon_path, output_path, size, bg_color='#FFFFFF'):
    """
    创建启动画面：白底 + 图标居中
    使用 sips 和 Python PIL 来合成
    """
    try:
        from PIL import Image, ImageDraw
        
        # 创建白色背景
        bg = Image.new('RGB', (size, size), bg_color)
        
        # 加载图标
        icon = Image.open(icon_path)
        icon_size = min(size // 3, 512)  # 图标大小为画布的 1/3，最大 512px
        
        # 调整图标大小（保持宽高比）
        icon.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
        
        # 计算居中位置
        x = (size - icon.width) // 2
        y = (size - icon.height) // 2
        
        # 如果是 PNG 且有透明通道，需要处理
        if icon.mode == 'RGBA':
            bg.paste(icon, (x, y), icon)
        else:
            bg.paste(icon, (x, y))
        
        # 保存
        bg.save(output_path, 'PNG')
        return True
        
    except ImportError:
        print("错误: PIL/Pillow 未安装，请运行: pip3 install Pillow --user")
        return False
    except Exception as e:
        print(f"错误: 创建启动画面失败: {e}")
        return False

def main():
    project_root = Path(__file__).parent.parent.parent
    svg_path = project_root / 'web_service' / 'frontend' / 'favicon.svg'
    ios_assets = project_root / 'ios' / 'App' / 'App' / 'Assets.xcassets'
    app_icon_dir = ios_assets / 'AppIcon.appiconset'
    splash_dir = ios_assets / 'Splash.imageset'
    
    if not svg_path.exists():
        print(f"错误: 未找到 {svg_path}")
        sys.exit(1)
    
    if not check_dependencies():
        print("请安装必要的工具后重试")
        sys.exit(1)
    
    print("正在生成 iOS 图标和启动画面...")
    
    # 1. 生成主图标（1024x1024）
    print("\n1. 生成应用图标 (1024x1024)...")
    icon_1024 = app_icon_dir / 'AppIcon-1024.png'
    if svg_to_png_sips(str(svg_path), str(icon_1024), 1024):
        print(f"   ✅ 已生成: {icon_1024}")
    else:
        print(f"   ❌ 生成失败，请手动转换")
        sys.exit(1)
    
    # 2. 更新 AppIcon Contents.json
    print("\n2. 更新 AppIcon 配置...")
    contents_json = {
        "images": [
            {
                "filename": "AppIcon-1024.png",
                "idiom": "universal",
                "platform": "ios",
                "size": "1024x1024"
            }
        ],
        "info": {
            "author": "xcode",
            "version": 1
        }
    }
    
    import json
    with open(app_icon_dir / 'Contents.json', 'w') as f:
        json.dump(contents_json, f, indent=2)
    print(f"   ✅ 已更新: {app_icon_dir / 'Contents.json'}")
    
    # 3. 生成启动画面
    print("\n3. 生成启动画面 (白底+图标居中)...")
    splash_files = [
        (splash_dir / 'splash-2732x2732.png', 2732, '3x'),
        (splash_dir / 'splash-2732x2732-1.png', 1366, '2x'),
        (splash_dir / 'splash-2732x2732-2.png', 683, '1x'),
    ]
    
    for splash_path, size, scale in splash_files:
        if create_splash_screen(str(icon_1024), str(splash_path), size):
            print(f"   ✅ 已生成 {scale}: {splash_path}")
        else:
            print(f"   ⚠️  {scale} 生成失败，需要手动处理")
    
    # 4. 更新 Splash Contents.json
    print("\n4. 更新启动画面配置...")
    splash_contents = {
        "images": [
            {
                "idiom": "universal",
                "filename": "splash-2732x2732-2.png",
                "scale": "1x"
            },
            {
                "idiom": "universal",
                "filename": "splash-2732x2732-1.png",
                "scale": "2x"
            },
            {
                "idiom": "universal",
                "filename": "splash-2732x2732.png",
                "scale": "3x"
            }
        ],
        "info": {
            "version": 1,
            "author": "xcode"
        }
    }
    
    with open(splash_dir / 'Contents.json', 'w') as f:
        json.dump(splash_contents, f, indent=2)
    print(f"   ✅ 已更新: {splash_dir / 'Contents.json'}")
    
    print("\n✅ iOS 图标和启动画面生成完成！")
    print("\n下一步:")
    print("  1. 在 Xcode 中打开项目: npx cap open ios")
    print("  2. 检查 Assets.xcassets 中的图标和启动画面")
    print("  3. 如果图标显示不正确，可能需要手动调整")

if __name__ == '__main__':
    main()

