import os
import struct

IndexKey = b"1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-@:^[]"

class CRuntimeRandomGenerator:
    def __init__(self):
        self.m_seed = 0

    def srand(self, seed):
        self.m_seed = seed

    def rand(self):
        self.m_seed = (self.m_seed * 214013 + 2531011) & 0xFFFFFFFF
        return (self.m_seed >> 16) & 0x7FFF
    

folder = r"old_dat_de"

idx = bytearray()
pack = bytearray()
name_size = 0x18

offset = 0x174b

for filename in os.listdir(folder):
    print(filename)
    with open(os.path.join(folder, filename), "rb") as f:
        data = f.read()
    
    tmp = filename.encode('cp932')
    idx += tmp
    idx += b'\0' * (name_size - len(tmp))
    idx += struct.pack('<Q', len(pack) + offset)
    idx += struct.pack('<I', len(data))
    idx += struct.pack('<I', 0)
    pack += data

with open("SCPACK.pak", "wb") as f:
    f.write(pack)

idx += b'\0' * (0x61a84 - len(idx))

idx[-4:-3] = b'\x60'

rng = CRuntimeRandomGenerator()
rng.srand(struct.unpack('I', idx[-4:])[0])

len_IndexKey = len(IndexKey)

en_idx = bytearray()
for i in range(len(idx) - 4):
    en_idx.append(idx[i] ^ IndexKey[rng.rand() % len_IndexKey])
    # en_idx.append(idx[i])
en_idx.extend(idx[-4:])

with open("SCPACK.idx", "wb") as f:
    f.write(en_idx)