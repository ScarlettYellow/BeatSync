#!/usr/bin/env python3
"""
从 favicon.svg 生成 favicon.ico
需要先通过其他工具（如浏览器、在线工具）将 SVG 转换为 256x256 PNG
然后此脚本会将 PNG 转换为包含多尺寸的 ico 文件
"""

import sys
from pathlib import Path
from PIL import Image

# 获取项目根目录（向上两级：scripts -> BeatSync）
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SVG_PATH = PROJECT_ROOT / "web_service/frontend/favicon.svg"
ICO_PATH = PROJECT_ROOT / "web_service/frontend/favicon.ico"

# ico 文件通常包含的尺寸
ICO_SIZES = [16, 32, 48, 64, 128, 256]

def generate_ico_from_png(png_path: Path, ico_path: Path):
    """从 PNG 文件生成包含多尺寸的 ico 文件"""
    print(f"正在从 {png_path} 生成 {ico_path}...")
    
    # 加载原始图片
    img = Image.open(png_path)
    
    # 确保是 RGBA 模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 创建多尺寸的图标列表
    icons = []
    for size in ICO_SIZES:
        # 缩放图片
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        icons.append(resized)
        print(f"  ✅ 已生成 {size}x{size} 图标")
    
    # 保存为 ico 文件
    icons[0].save(ico_path, format='ICO', sizes=[(s, s) for s in ICO_SIZES])
    print(f"✅ 已生成 favicon.ico: {ico_path}")
    return True

def generate_png_from_svg_via_browser():
    """提示用户使用浏览器将 SVG 转换为 PNG"""
    print("\n" + "="*60)
    print("步骤 1: 将 SVG 转换为 256x256 PNG")
    print("="*60)
    print(f"\nSVG 文件路径: {SVG_PATH}")
    print("\n方法 1（推荐）: 使用浏览器")
    print("  1. 在浏览器中打开: file://" + str(SVG_PATH.absolute()))
    print("  2. 右键点击图片 -> '另存为' 或使用截图工具")
    print("  3. 保存为 PNG 格式，尺寸至少 256x256")
    print("\n方法 2: 使用在线工具")
    print("  1. 访问 https://cloudconvert.com/svg-to-png")
    print("  2. 上传 favicon.svg")
    print("  3. 设置尺寸为 256x256，下载 PNG")
    print("\n方法 3: 使用 macOS Preview")
    print("  1. 打开 favicon.svg")
    print("  2. 文件 -> 导出 -> 格式选择 PNG")
    print("  3. 设置尺寸为 256x256")
    print("\n" + "="*60)
    print("步骤 2: 运行此脚本生成 ico")
    print("="*60)
    print(f"\npython3 {__file__} <png_file_path>")
    print(f"\n示例:")
    print(f"python3 {__file__} /path/to/favicon-256x256.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 如果提供了 SVG 路径，尝试直接生成
        # 否则提示用户先转换为 PNG
        generate_png_from_svg_via_browser()
        sys.exit(1)
    
    png_path = Path(sys.argv[1])
    if not png_path.exists():
        print(f"错误: 找不到文件 {png_path}")
        sys.exit(1)
    
    generate_ico_from_png(png_path, ICO_PATH)
    print(f"\n✅ 完成！favicon.ico 已生成: {ICO_PATH}")

