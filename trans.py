from PIL import Image

def convert_favicon_export_all(ico_file='favicon.ico'):
    """
    将 favicon.ico 的透明背景转为白色，然后导出：
    1. 一个新的带白色背景的 .ico 文件。
    2. 一个带白色背景的 .png 文件（原始尺寸）。
    3. 三个指定尺寸的 .png 文件。

    Args:
        ico_file (str, optional): 输入的 .ico 文件名. 默认为 'favicon.ico'.
    """
    try:
        # 1. 打开 ICO 文件并确保为 RGBA 模式
        original_img = Image.open(ico_file)
        img_rgba = original_img.convert("RGBA")

        # 2. 创建白色背景并粘贴原始图像
        white_bg = Image.new("RGBA", img_rgba.size, "WHITE")
        white_bg.paste(img_rgba, mask=img_rgba)

        # 将最终要用于导出的图像转换为 RGB 模式
        final_source_img = white_bg.convert("RGB")

        print("背景处理完成，开始导出文件...")
        print("-" * 30)

        # 3. [新增] 导出为新的ICO文件 (favicon_white_bg.ico)
        # Pillow的ICO保存器可以指定多种尺寸嵌入到同一个ico文件中
        ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)]
        new_ico_filename = 'favicon_white_bg.ico'
        final_source_img.save(new_ico_filename, format='ICO', sizes=ico_sizes)
        print(f"✅ 成功导出新的ICO文件: {new_ico_filename}")

        # 4. 保存一个带有白色背景的PNG文件 (原始尺寸)
        png_bg_filename = 'favicon_with_white_bg.png'
        final_source_img.save(png_bg_filename, "PNG")
        print(f"✅ 成功导出PNG（白底）: {png_bg_filename}")

        # 5. 定义需要转换的PNG尺寸和文件名
        png_exports = {
            (16, 16): "favicon-16x16.png",
            (32, 32): "favicon-32x32.png",
            (180, 180): "apple-touch-icon.png"
        }

        # 6. 基于带有白色背景的图像进行缩放和保存
        for size, filename in png_exports.items():
            resized_img = final_source_img.resize(size, Image.Resampling.LANCZOS)
            resized_img.save(filename, "PNG")
            print(f"✅ 成功导出指定尺寸PNG: {filename} ({size[0]}x{size[1]})")

    except FileNotFoundError:
        print(f"❌ 错误：未在当前目录下找到 {ico_file} 文件。")
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")

if __name__ == "__main__":
    convert_favicon_export_all()
