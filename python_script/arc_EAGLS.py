Python




import struct
import random
import os

class CRuntimeRandomGenerator:
    def __init__(self):
        self.m_seed = 0

    def SRand(self, seed):
        self.m_seed = seed

    def Rand(self):
        self.m_seed = self.m_seed * 214013 + 2531011
        return (self.m_seed >> 16) & 0x7FFF

class LehmerRandomGenerator:
    def __init__(self):
        self.m_seed = 0

    def SRand(self, seed):
        self.m_seed = seed ^ 123459876

    def Rand(self):
        self.m_seed = 48271 * (self.m_seed % 44488) - 3399 * (self.m_seed // 44488)
        if self.m_seed < 0:
            self.m_seed += 2147483647
        return int(self.m_seed * 4.656612875245797e-10 * 256)

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

class EaglsArchive:
    def __init__(self, arc, impl, dir, enc):
        self.arc = arc
        self.impl = impl
        self.dir = dir
        self.enc = enc

    def DecryptEntry(self, entry):
        input_data = self.arc.read_bytes(entry.Offset, entry.Size)
        self.enc.Decrypt(input_data)
        return input_data