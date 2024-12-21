import os

class CRuntimeRandomGenerator:
    def __init__(self):
        self.m_seed = 0

    def SRand(self, seed):
        self.m_seed = seed

    def Rand(self):
        self.m_seed = (self.m_seed * 214013 + 2531011) & 0xFFFFFFFF
        return (self.m_seed >> 16) & 0x7FFF

class EaglsEncryption:
    def __init__(self):
        self.m_rng = CRuntimeRandomGenerator()
        self.Key = b'EAGLS_SYSTEM'

    def Decrypt(self, data):
        text_offset = 3600
        text_length = len(data) - text_offset - 2
        self.m_rng.SRand(data[-1])
        for i in range(0, text_length, 2):
            data[text_offset + i] ^= self.Key[self.m_rng.Rand() % len(self.Key)]

for file in os.listdir("old_dat"):
    print(file)
    with open(f"old_dat\\{file}", 'rb') as f:
        data = bytearray(f.read())
    enc = EaglsEncryption()
    enc.Decrypt(data)
    with open(f"old_dat_de\\{file}", 'wb') as f:
        f.write(data)