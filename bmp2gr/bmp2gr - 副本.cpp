
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdint>
//#include <filesystem>

void make_next(const std::vector<char>& pattern, int* next, int i, int size)
{
    next[0] = -1;
    int j = 0;
    int k = -1;
    while (j < 18 - 1 && j + i < size - 1)
    {
        if (k == -1 || pattern[i + j] == pattern[i + k])
        {
            j++;
            k++;
            next[j] = k;
        }
        else
            k = next[k];
    }
}

std::vector<char> LZSS_encode(const std::vector<char>& data) {

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

    int kmp_next[18];

    std::vector<char> restorebuff;  // 待写入的数据缓存区，满一组数据写入一次文件
    while (i < size)
    {

        //find
        int max_length = -1;
        int max_id = -1;

        make_next(data, kmp_next, i, size);
        int j = 1;
        int k = 0;
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
                k = kmp_next[k];
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
        if (max_length > 2)
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

    return output;
}

int main() {
    std::ifstream input("D:\\GalGame\\eagls\\a01.bmp", std::ios::binary);

    // copies all data into buffer
    std::vector<char> buffer(std::istreambuf_iterator<char>(input), {});

    // std::vector<char> data = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    // std::vector<char> data = { 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01};
    std::vector<char> data = { 0x42, 0x4D, 0x38, 0x00, 0x24, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, 0x00, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x01, 0x00 };
    std::vector<char> compressedData = LZSS_encode(buffer);
    std::ofstream output("D:\\GalGame\\eagls\\a01.gr", std::ios::binary);
    output.write(compressedData.data(), compressedData.size());
    return 0;
}