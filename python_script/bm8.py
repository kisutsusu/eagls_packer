import struct
from PIL import Image
import numpy as np

# class GrMetaData:
#     def __init__(self, width, height, bpp, unpacked_size):
#         self.width = width
#         self.height = height
#         self.bpp = bpp
#         self.unpacked_size = unpacked_size

# def read_metadata(file):
with open(r"HISTMAINP.bmp", 'rb') as f:
    data = f.read()

assert data[:2] == b'BM'
assert data[4] == 0x24

file_size = struct.unpack('<I', data[0x2:0x6])[0]
width = struct.unpack('<I', data[0x12:0x16])[0]
height = struct.unpack('<I', data[0x16:0x1a])[0]
bpp = struct.unpack('<H', data[0x1c:0x1e])[0]
image_size = struct.unpack('<I', data[0x22:0x26])[0]
lines = data[0x36:]

assert len(lines) == image_size

bpp = bpp // 8

image = np.full(shape=(height, width, bpp), fill_value=[0, 0, 0, 0], dtype=np.uint8)
idx = 0
for y in range(height):
    for x in range(width):
        # image[y, x] = [image[y, x][2], image[y, x][1], image[y, x][0], image[y, x][3]]
        # idx = y * width * bpp + x * bpp
        if bpp == 3:
            image[height - y - 1, x] = [lines[idx + i] for i in range(bpp)]
        elif bpp == 4:
            image[height - y - 1, x] = [lines[idx + 2], lines[idx + 1], lines[idx], lines[idx + 3]]
        idx += bpp

img = Image.fromarray(image)
img.save(r"HISTMAINP_.png")