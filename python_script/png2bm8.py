import os
import PIL.Image as Image
import struct
import numpy as np

png_folder = r"D:\10947\Download\HSHINTAI2_NG_改(不包括无对应翻译文件)\HSHINTAI2_NG"
old_bmp = r"decode"

for file in os.listdir(png_folder):
    if not file.endswith(".png"):
        continue
    print(file)
    image = Image.open(f"{png_folder}/{file}")
    fname = file[:-4]

    with open(f"{old_bmp}\{fname}.bmp", "rb") as f:
        raw_data = f.read()
    assert raw_data[:2] == b'BM'
    # if raw_data[4] != 0x24:
    #     print(file, "is not 24bit")
    #     continue

    file_size = struct.unpack('<I', raw_data[0x2:0x6])[0]
    width = struct.unpack('<I', raw_data[0x12:0x16])[0]
    height = struct.unpack('<I', raw_data[0x16:0x1a])[0]
    bpp = struct.unpack('<H', raw_data[0x1c:0x1e])[0] // 8
    image_size = struct.unpack('<I', raw_data[0x22:0x26])[0]
    lines = raw_data[0x36:]

    # assert len(lines) == image_size
    # assert width * height * bpp == image_size
    assert image.width == width and image.height == height

    image = np.array(image)

    new_lines = bytearray()
    for y in range(height):
        for x in range(width):
            if bpp == 3:
                pixel = image[height - y - 1, x]
                new_lines.extend([pixel[2], pixel[1], pixel[0]])
            elif bpp == 4:
                pixel = image[height - y - 1, x]
                if pixel[3] == 0:
                    new_lines.extend([0, 0, 0, 0])
                else:
                    new_lines.extend([pixel[2], pixel[1], pixel[0], pixel[3]])


    with open(f"new_bm8\{fname}.bmp", "wb") as f:
        f.write(raw_data[:0x36] + new_lines + raw_data[0x36 + len(new_lines):])