
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdint>
#include <filesystem>
#include <thread>
namespace fs = std::filesystem;

const char* EaglsKey = "EAGLS_SYSTEM";

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

void make_next(const std::vector<char>& pattern, int* next, int size)
{
    next[0] = -1;
    int j = 0;
    int k = -1;
    while (j < size)
    {
        if (k == -1 || pattern[j] == pattern[k])
        {
            j++;
            k++;
            next[j] = k;
        }
        else
            k = next[k];
    }
}

std::vector<char> LZSS_encode_kmp(const std::vector<char>& data) {

    const int max_buflen = 18;

    int i = 0;
    int size = data.size();

    std::vector<char> output;
    output.reserve(size);

    char frame[0x1000] = { 0 };
    int frame_pos = 0xfee;
    int frame_mask = 0x1000 - 1;
    int itemnum = 0;
    char signbits = 0;

    int* kmp_next = new int[size];

    std::vector<char> restorebuff;  // 待写入的数据缓存区，满一组数据写入一次文件
    make_next(data, kmp_next, size);
    while (i < size)
    {

        //find
        int max_length = -1;
        int max_id = -1;
        int j = 1;
        int k = -1;
        while (j <= 0x1000 && k < max_buflen && i + k < size)
        {
            int frame_pos_i = (j + frame_pos) & frame_mask;
            if (k == -1 || frame[frame_pos_i] == data[i + k])
            {
                j++;
                k++;
            }
            else
            {
                if (k > max_length)
                {
                    max_length = k;
                    max_id = (j + frame_pos - k - 1) & frame_mask;
                }
                k = kmp_next[i + k] - i;
                if (k < 0)
                    k = -1;
            }
            /*for (; k < max_buflen && i + k < size; k++)
            {
                int frame_pos_i = (j + frame_pos + k) & frame_mask;
                if (frame[frame_pos_i] != data[i + k])
                {
                    if (j == 0x1000 && k > 0 && data[i] == data[i + k])
                    {
                        int j = 1;
                        for (; k + j < max_buflen && i + k + j < size; j++)
                        {
                            if (data[i + j] != data[i + k + j])
                            {
                                break;
                            }
                        }
                        k += j;
                    }
                    break;
                }
            }
            if (k > 2 && k > max_length)
            {
                max_length = k;
                max_id = (j + frame_pos - 1) & frame_mask;
            }
            if (max_length == max_buflen)
                break;*/
        }
        if (k > max_length)
        {
            max_length = k;
            max_id = (j + frame_pos - k - 1) & frame_mask;
        }

        // match
        if (max_length < 3)
        {
            restorebuff.push_back(data[i]);
            signbits += (1 << itemnum);
        }
        else
        {
            restorebuff.push_back(max_id & 0xff);
            restorebuff.push_back(((max_id >> 4) & 0xf0) + (max_length - 3));
        }
        itemnum += 1;

        // 项目数达到8了，说明做完了一组压缩，将这一组数据写入文件
        if (itemnum >= 8) {
            std::vector<char> writebytes = { signbits };
            writebytes.insert(writebytes.end(), restorebuff.begin(), restorebuff.end());
            output.insert(output.end(), writebytes.begin(), writebytes.end());
            itemnum = 0;
            signbits = 0;
            restorebuff.clear();
        }
        if (false)
        {
            for (int j = 0; j < max_length; j++) {
                frame_pos += 1;
                frame_pos &= frame_mask;
                frame[frame_pos] = data[i + j];
            }
            i += max_length;
        }
        else
        {
            frame_pos += 1;
            frame_pos &= frame_mask;
            frame[frame_pos] = data[i];
            i += 1;
        }
    }
    if (!restorebuff.empty()) {  // 文件最后可能不满一组数据量，直接写到文件里
        std::vector<char> writebytes = { signbits };
        writebytes.insert(writebytes.end(), restorebuff.begin(), restorebuff.end());
        output.insert(output.end(), writebytes.begin(), writebytes.end());
    }
    delete[] kmp_next;
    return output;
}

std::vector<unsigned char> LZSS_encode(const std::vector<unsigned char>& data) {

    const int max_buflen = 18;
    int size = data.size();

    std::vector<unsigned char> output;
    output.reserve(size);

    unsigned char frame[0x1000] = { 0 };
    int frame_pos = 0xfee;
    int frame_mask = 0x1000 - 1;
    int itemnum = 0;
    unsigned char signbits = 0;
    std::vector<unsigned char> restorebuff;  // 待写入的数据缓存区，满一组数据写入一次文件
    int i = 0;
    while (i < size)
    {
        //find
        int max_length = -1;
        int max_id = -1;
        for (int j = 1; j < 0x1000; j++)
        {
            // break;
            if (i < 0x12 && (((j + frame_pos - 1) & frame_mask) >= 0xfee))
                break;
            int k = 0;
            for (; k < max_buflen && i + k < size; k++)
            {
                if (j + k >= 0x1000 && j + k - 0x1000 < k)
                {
                    break;
                    if (data[i + j + k - 0x1000 - 1] != data[i + k])
                    {
                        break;
                    }
                }
                else
                {
                    int frame_pos_i = (j + frame_pos + k) & frame_mask;
                    if (frame[frame_pos_i] != data[i + k])
                    {
                        break;
                    }
                }
            }
            if (k > 2 && k > max_length)
            {
                max_length = k;
                max_id = (j + frame_pos - 1) & frame_mask;
            }
            if (max_length == max_buflen)
                break;
        }

        // match
        if (max_length == -1)
        {
            restorebuff.push_back(data[i]);
            signbits += (1 << itemnum);
        }
        else
        {
            restorebuff.push_back(max_id & 0xff);
            restorebuff.push_back(((max_id >> 4) & 0xf0) + (max_length - 3));
        }
        itemnum += 1;

        // 项目数达到8了，说明做完了一组压缩，将这一组数据写入文件
        if (itemnum >= 8) {
            std::vector<unsigned char> writebytes = { signbits };
            writebytes.insert(writebytes.end(), restorebuff.begin(), restorebuff.end());
            output.insert(output.end(), writebytes.begin(), writebytes.end());
            itemnum = 0;
            signbits = 0;
            restorebuff.clear();
        }
        if (max_length > 0)
        {
            for (int j = 0; j < max_length; j++) {
                frame_pos += 1;
                frame_pos &= frame_mask;
                frame[frame_pos] = data[i + j];
            }
            i += max_length;
        }
        else
        {
            frame_pos += 1;
            frame_pos &= frame_mask;
            frame[frame_pos] = data[i];
            i += 1;
        }
    }
    if (!restorebuff.empty()) {  // 文件最后可能不满一组数据量，直接写到文件里
        std::vector<unsigned char> writebytes = { signbits };
        writebytes.insert(writebytes.end(), restorebuff.begin(), restorebuff.end());
        output.insert(output.end(), writebytes.begin(), writebytes.end());
    }

    return output;
}

void decode(const std::string infile, const std::string outfile, bool decrypt=true)
{
    std::ifstream input(infile, std::ios::binary);
    std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});
    input.close();
    std::vector<unsigned char> compresseddata = LZSS_encode(buffer);
    if (decrypt)
        DecryptCg(compresseddata);

    std::ofstream output(outfile, std::ios::binary);
    auto res = compresseddata.data();
    output.write(reinterpret_cast<char*>(compresseddata.data()), compresseddata.size());
    output.close();
}

int main(int argc, char* argv[]) {
    std::string folder = argv[1];
    std::string outfolder = argv[2];
    bool decrypt = true;
    if (argc > 2 && argv[3] == "1")
        decrypt = false;
    std::filesystem::create_directory(outfolder);
    std::vector<std::thread> threads;
    for (const auto& entry : std::filesystem::directory_iterator(folder)) {
        auto path = entry.path();
        std::string infile = path.string();
        std::string outfile = outfolder + "/" + path.replace_extension(".gr").filename().string();
        threads.push_back(std::thread(decode, infile, outfile, false));
    }
    for (auto& t : threads) {
        t.join();
    }
    //std::ifstream input(argv[1], std::ios::binary);
    //std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});
    //input.close();
    //std::vector<unsigned char> compresseddata = LZSS_encode(buffer);
    //Lehmer_encode(compresseddata);

    //std::ofstream output(fs::path("d:\\galgame\\eagls\\new_bm8_2")/ fs::path(argv[1]).filename(), std::ios::binary);
    //auto res = compresseddata.data();
    //output.write(reinterpret_cast<char*>(compresseddata.data()), compresseddata.size());
    //output.close();

    //for (const auto& entry : fs::directory_iterator("D:\\GalGame\\eagls\\new_bm8")) {
    //    if (fs::is_directory(entry)) {
    //    }
    //    else {
    //        std::cout << "File: " << entry.path() << std::endl;
    //        std::ifstream input(entry.path(), std::ios::binary);
    //        std::vector<char> buffer(std::istreambuf_iterator<char>(input), {});
    //        input.close();
    //        std::vector<char> compressedData = LZSS_encode(buffer);

    //        std::ofstream output(fs::path("D:\\GalGame\\eagls\\new_bm8_2")/ entry.path().filename(), std::ios::binary);
    //        output.write(compressedData.data(), compressedData.size());
    //        output.close();
    //    }
    //}

    //std::ifstream input("D:\\GalGame\\eagls\\test.bmp", std::ios::binary);

    //// copies all data into buffer
    //std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});

    //// std::vector<char> data = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    //// std::vector<unsigned char> data = { 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01};



    //std::vector<unsigned char> compressedData = LZSS_encode(buffer);
    //std::ofstream output("D:\\GalGame\\eagls\\test.gr", std::ios::binary);
    //output.write(reinterpret_cast<char*>(compressedData.data()), compressedData.size());
    return 0;
}