import ctypes
import os
import threading

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

def fake_LZSS_encode(data):
    output = bytearray()

    i = 0
    len_data = len(data)

    while i < len_data:
        output.append(0xff)
        for j in range(8):
            if i+j < len_data:
                output.append(data[i+j])
            else:
                output.append(0)
        i += 8
    return bytes(output)

def LZSS_encode(data):

    restorebuff = b''  # 待写入的数据缓存区，满一组数据写入一次文件
    itemnum = 0  # 8个项目为一组，用来统计当前项目数
    signbits = 0  # 标记字节
    Buflen = 18

    iid = 0
    preBuf = data[iid: iid+Buflen]  # 读取数据填满前向缓冲区
    iid += Buflen
    output = bytearray()

    frame = [0]*0x1000
    frame_pos = 0xfee
    frame_mask = 0x1000-1
    # 前向缓冲区没数据可操作了即为压缩结束
    while preBuf != b'':
        matchString = b''
        matchIndex = -1
        # 在滑动窗口中寻找最长的匹配串
        for i in range(3, len(preBuf)+1):
            index = -1
            for j in range(1, 0x100+i):
                bfind = 1
                for k in range(i):
                    if(i-k-1-j >= 0):
                        if(preBuf[i-j-1-k] != preBuf[i-k-1]):
                            bfind = -1
                            break
                    else:
                        if(frame[(frame_pos-j+i-k) & frame_mask] != preBuf[i-k-1]):
                            bfind = -1
                            break
                if(bfind > 0):
                    index = j
                    break
            # index = frame.find(self.preBuf[0:i])
            if index != -1:
                matchString = preBuf[0:i]
                matchIndex = (frame_pos-index) & frame_mask
            else:
                break
        # 如果没找到匹配串或者匹配长度为1，直接输出原始数据
        if matchIndex == -1:
            matchString = preBuf[0:1]
            restorebuff += matchString
            signbits += (1 << itemnum)
        else:
            restorebuff += (matchIndex & 0xff).to_bytes(1, byteorder='big')
            restorebuff += (((matchIndex >> 4) & 0xf0) +
                            (len(matchString)-3)).to_bytes(1, byteorder='big')
        # 操作完一个项目+1
        itemnum += 1
        # 项目数达到8了，说明做完了一组压缩，将这一组数据写入文件
        if itemnum >= 8:
            writebytes = bytes(ctypes.c_uint8(signbits)) + restorebuff
            output.extend(writebytes)
            itemnum = 0
            signbits = 0
            restorebuff = b''

        # 将刚刚匹配过的数据移出前向缓冲区
        preBuf = preBuf[len(matchString):]
        for i in range(len(matchString)):
            frame_pos += 1
            frame_pos &= frame_mask
            frame[frame_pos] = matchString[i]
        # 读取数据补充前向缓冲区
        lpre = len(preBuf)
        preBuf += data[iid:iid+Buflen - lpre]
        iid += Buflen - lpre

    if restorebuff != b'':  # 文件最后可能不满一组数据量，直接写到文件里
        writebytes = bytes(ctypes.c_uint8(signbits)) + restorebuff
        output.extend(writebytes)

    return bytes(output)

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

exe_path = r"C:\Users\10947\source\repos\bmp2gr\x64\Release\bmp2gr.exe"

def run_command(file):
    os.system(f"{exe_path} D:\\GalGame\\eagls\\new_bm8\\{file}")

# threads = []
# for file in os.listdir(r"new_bm8"):
#     thread = threading.Thread(target=run_command, args=(file,))
#     thread.start()
#     threads.append(thread)
#     break

# for thread in threads:
#     thread.join()

# for file in os.listdir(r"new_bm8"):
#     print(file)
#     os.system(f"{exe_path} D:\\GalGame\\eagls\\new_bm8\\{file}")

# for file in os.listdir(r"new_bm8"):
#     if not file.endswith(".bmp"):
#         continue
#     # file = "cc01n.bmp"
#     print(file)
#     fname = file.split(".")[0]
#     with open(f"new_bm8/{file}", "rb") as f:
#         data = f.read()

#     # with open(r"HISTMAINP.gr", "wb") as f:
#     #     f.write(LZSS_encode(data))
#     # test = LZSS_decode(fake_LZSS_encode(data))

#     with open(f"new_gr/{fname}.gr", "wb") as f:
#         f.write(Lehmer_encode(fake_LZSS_encode(data)))
#     # break

for file in os.listdir(r"new_bm"):
    print(file)
    fname = file.split(".")[0]
    with open(f"new_bm/{file}", "rb") as f:
        data = f.read()

    # with open(r"HISTMAINP.gr", "wb") as f:
    #     f.write(LZSS_encode(data))
    # test = LZSS_decode(fake_LZSS_encode(data))

    with open(f"new_gr4/{fname}.gr", "wb") as f:
        f.write(Lehmer_encode(fake_LZSS_encode(data)))
        # f.write(data)
    # break



# with open(r"D:\GalGame\eagls\test.gr", "rb") as f:
#     data = f.read()
# with open(r"D:\GalGame\eagls\test_2.bmp", "wb") as f:
#     f.write(LZSS_decode(data))