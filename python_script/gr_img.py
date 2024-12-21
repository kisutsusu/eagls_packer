import os

def LZSS_decode(data):

    dst = 0
    frame = [0]*0x1000
    frame_pos = 0xfee
    frame_mask = 0x1000-1
    nowi = 0x0

    output = bytearray()
    len_data = len(data)

    while nowi < len_data:
        ctl = data[nowi]
        nowi += 1
        for i in range(8):  # 8个项目为一组进行解压
            if ctl & (1 << i) != 0:
                if(nowi == len_data):
                    break
                output.append(data[nowi])
                dst += 1
                frame[frame_pos] = data[nowi]
                frame_pos = (frame_pos+1) & frame_mask
                nowi += 1
            else:
                if(nowi + 1 >= len_data):
                    break
                lo = data[nowi]
                hi = data[nowi+1]
                nowi += 2
                offset = (hi & 0xf0) << 4 | lo
                count = 3 + (hi & 0xF)
                while(count > 0):
                    v = frame[offset]
                    offset += 1
                    offset &= frame_mask
                    frame[frame_pos] = v
                    frame_pos += 1
                    frame_pos &= frame_mask
                    output.append(v)
                    dst += 1
                    count -= 1
    return bytes(output)

EaglsKey = b"EAGLS_SYSTEM"
len_key = len(EaglsKey)

class LehmerRandomGenerator:
    
    def __init__(self):
        self.m_seed = 0

    def srand(self, seed):
        self.m_seed = seed ^ 123459876

    def rand(self):
        self.m_seed = (48271 * (self.m_seed % 44488) - 3399 * (self.m_seed // 44488))
        if self.m_seed < 0:
            self.m_seed += 2147483647
        self.m_seed = self.m_seed & 0xFFFFFFFF
        return int(self.m_seed * 4.656612875245797e-10 * 256) & 0xFFFFFFFF
    
def Lehmer_encode(data):
    rng = LehmerRandomGenerator()
    encode_data = bytearray(data)
    rng.srand(encode_data[-1])
    limit = min(len(data)-1, 0x174b)
    for i in range(limit):
        encode_data[i] ^= EaglsKey[rng.rand() % len_key]
    return bytes(encode_data)


with open(f"warning.gr", "rb") as f:
    data = f.read()
res = LZSS_decode(Lehmer_encode(data))
with open(f"warning.bmp", "wb") as f:
    f.write(res)

# for gr in os.listdir("out"):
#     if not gr.endswith(".gr"):
#         continue
#     print(gr)
#     with open(f"out/{gr}", "rb") as f:
#         data = f.read()
#     res = LZSS_decode(data)
#     with open(f"decode/{gr.split('.')[0]}.bmp", "wb") as f:
#         f.write(res)