from PIL import Image

def convert_favicon(ico_file='favicon.ico'):
    """
    将 favicon.ico 文件转换为指定尺寸的 PNG 图像。

    Args:
        ico_file (str, optional): 输入的 .ico 文件名. 默认为 'favicon.ico'.
    """
    try:
        # 打开ICO文件
        img = Image.open(ico_file)

        # 定义需要转换的尺寸和对应的文件名
        sizes = {
            (16, 16): "favicon-16x16.png",
            (32, 32): "favicon-32x32.png",
            (180, 180): "apple-touch-icon.png"
        }

        for size, filename in sizes.items():
            # 调整图像大小
            # 使用 Image.Resampling.LANCZOS 以获得高质量的缩放效果
            resized_img = img.resize(size, Image.Resampling.LANCZOS)

            # 保存为PNG格式
            resized_img.save(filename, "PNG")
            print(f"成功将图像转换为 {size} 并保存为 {filename}")

    except FileNotFoundError:
        print(f"错误：未在当前目录下找到 {ico_file} 文件。")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    convert_favicon()