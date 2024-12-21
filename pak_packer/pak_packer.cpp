#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstring>
#include <cstdint>
#include <filesystem>

const char* IndexKey = "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-@:^[]";
const char* EaglsKey = "EAGLS_SYSTEM";

class CRuntimeRandomGenerator {
public:
    void srand(int32_t seed) {
        m_seed = seed;
    }

    int16_t rand() {
        m_seed = m_seed * 214013 + 2531011;
        return (int16_t)(m_seed >> 16) & 0x7FFF;
    }

private:
    uint32_t m_seed = 0;
};

class LehmerRandomGenerator {
public:
    LehmerRandomGenerator() : m_seed(0) {}

    void srand(int32_t seed) {
        m_seed = seed ^ 123459876;
    }

    int32_t rand() {
        m_seed = (48271 * (m_seed % 44488) - 3399 * (m_seed / 44488));
        if (m_seed < 0) {
            m_seed += 2147483647;
        }
        return m_seed * 4.656612875245797e-10 * 256;
    }

private:
    int32_t m_seed;
};

void DecryptIndex(std::vector<uint8_t>& data) {
    CRuntimeRandomGenerator rng;
    rng.srand(*reinterpret_cast<const uint32_t*>(data.data() + data.size() - 4));
    size_t len_IndexKey = strlen(IndexKey);
    for (size_t i = 0; i < data.size() - 4; ++i) {
        data[i] ^= IndexKey[rng.rand() % len_IndexKey];
    }
}

void DecryptCg(std::vector<unsigned char>& data) {
    LehmerRandomGenerator rng;
    rng.srand(data.back());
    size_t limit = data.size() - 1;
    if (limit > 0x174b)
        limit = 0x174b;
    for (size_t i = 0; i < limit; ++i) {
        data[i] ^= EaglsKey[rng.rand() % 12];
    }
}

void DecryptDat(std::vector<uint8_t>& data) {
    CRuntimeRandomGenerator rng;
    int text_offset = 3600;
    int text_length = data.size() - text_offset - 2;
    rng.srand((int8_t)data[data.size() - 1]);  // 使用数据的最后一个字节作为随机数生成器的种子
    for (int i = 0; i < text_length; i += 2) {
        data[text_offset + i] ^= EaglsKey[rng.rand() % 12];
    }
}

int main(int argc, char* argv[]) {
    std::string folder = argv[1];
    std::vector<uint8_t> pack;
    std::vector<uint8_t> idx;
    uint32_t offset = 0x174b;
    bool decrypt = false;
    if (argc > 1 && argv[2] == "1")
        decrypt = false;
    for (const auto& entry : std::filesystem::directory_iterator(folder)) {
        std::ifstream file(entry.path(), std::ios::binary);
        if (file.is_open()) {
            std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(file), {});
            auto path = entry.path();
            if (decrypt)
            {
                if (path.extension() == ".dat")
                    DecryptDat(buffer);
                else if (path.extension() == ".gr")
                    DecryptCg(buffer);
            }
            std::string filename = path.filename().string();
            std::vector<uint8_t> tmp(filename.begin(), filename.end());
            tmp.resize(0x18);
            idx.insert(idx.end(), tmp.begin(), tmp.end());
            uint64_t data1 = pack.size() + offset;
            idx.insert(idx.end(), reinterpret_cast<const uint8_t*>(&data1), reinterpret_cast<const uint8_t*>(&data1) + sizeof(data1));
            uint32_t data2 = buffer.size();
            idx.insert(idx.end(), reinterpret_cast<const uint8_t*>(&data2), reinterpret_cast<const uint8_t*>(&data2) + sizeof(data2));
            uint32_t data3 = 0;
            idx.insert(idx.end(), reinterpret_cast<const uint8_t*>(&data3), reinterpret_cast<const uint8_t*>(&data3) + sizeof(data3));
            file.seekg(0, 0);
            pack.insert(pack.end(), buffer.begin(), buffer.end());
        }
        file.close();
    }

    std::string pak_path = argv[2];
    std::ofstream pak_file(pak_path, std::ios::binary);
    pak_file.write(reinterpret_cast<const char*>(pack.data()), pack.size());
    pak_file.close();

    // idx.insert(idx.end(), 0, 0x61a84 - idx.size());
    idx.resize(0x61a84);
    idx[idx.size() - 4] = 0x00;
    DecryptIndex(idx);

    std::string idx_path = pak_path.substr(0, pak_path.length() - 3) + "idx";
    std::ofstream idx_file(idx_path, std::ios::binary);
    idx_file.write(reinterpret_cast<const char*>(idx.data()), idx.size());
    idx_file.close();

    return 0;
}
