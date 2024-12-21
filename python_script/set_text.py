import os
import re
import base64


def get_filelist(dir, Filelist):
    newDir = dir
    if os.path.isfile(dir):
        Filelist.append(dir)
        # # 若只是要返回文件文，使用这个
        # Filelist.append(os.path.basename(dir))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            # 如果需要忽略某些文件夹，使用以下代码
            # if s == "xxx":
            # continue
            newDir = os.path.join(dir, s)
            get_filelist(newDir, Filelist)
    return Filelist


def find_str(data, i):
    j = i
    while j > 0 and not data[j] == ord('"'):
        j -= 1
    k = i + 1
    while k < len(data) and not data[k] == ord('"'):
        k += 1
    return j, k + 1

def check(s):
    # 正则表达式匹配由字母、数字和下划线组成的字符串
    pattern = r'^[a-zA-Z0-9_\.%@(),:=\\]+$'
    return bool(re.match(pattern, s))

files = []

get_filelist(r"old_dat", files)

# for fn in files:
#     with open(fn, "rb") as f:
#         data = f.read()
#         a = chardet.detect(data)["encoding"]
#         print(fn, a)

# exit()
# res_dict = {}
for fn in files:
    # fn = r"D:\touchfish\HSHINTAI2_proj\1.02_\sch13.txt"
    # fn = r"text\75SelectH.txt"
    # res_dict[fn[5:-4]] = []
    file_name = fn.split("\\")[-1].split(".")[0]
    text = ""
    print(fn)

    with open(fn, "rb") as f:
        data = f.read()

    if not os.path.exists("new_text2/" + file_name + ".txt"):
        with open("res_dat/" + fn.split("\\")[-1], "wb") as f:
            f.write(data)
        continue

    with open("new_text2/" + file_name + ".txt", "r", encoding="utf-8") as f:
        res_text = f.readlines()
        res_text = [i[:-1] for i in res_text]
    res_id = 0

    new_data = bytearray()
    last_i = 0
    len_data = len(data)
    i = 0
    while i < len_data:
        # if data[i] == ord('"'):
        #     j = i + 1
        #     while j < len(data) and not data[j] == ord('"'):
        #         j += 1
        #     if j - i > 1000:
        #         i += 1
        #         continue
        #     if j < len(data):
        #         txt = data[i + 1 : j].decode("shift-jis", errors="backslashreplace")
        #         test = txt.strip()
        #         if test != "" and not check(test) and res_id < len(res_text):
        #             # txt = base64.b64encode(data[i + 1 : j]).decode("utf-8")
        #             if txt == res_text[res_id]:
        #                 if res_text[res_id] != res_text[res_id + 1]:
        #                     new_data += data[last_i:i + 1]
        #                     new_data += res_text[res_id + 1].encode("gbk")
        #                     # new_data += data[i + 1:j]
        #                     last_i = j
        #                 res_id += 3
        #     i = j
        # i += 1
        j = -1
        if data[i] == ord('"'):
            j = i + 1
            while j < len_data and not data[j] == ord('"'):
                j += 1
        elif data[i] == ord("#"):
            j = i + 1
            while j + 2 < len_data and not (data[j:j+1] == b"\n" or data[j:j+2] == b"\r\n"):
                j += 1
        if j == -1 or j - i > 1000:
            i += 1
            continue
        if j < len_data:
            txt = data[i + 1 : j].decode("shift-jis", errors="backslashreplace")
            test = txt.strip()
            if test != "" and not check(test) and res_id < len(res_text):
                # txt = base64.b64encode(data[i + 1 : j]).decode("utf-8")
                if txt == res_text[res_id]:
                    # if res_text[res_id] != res_text[res_id + 1]:
                    if data[i] != ord("#"):
                        new_data += data[last_i:i + 1]
                        new_data += res_text[res_id + 1].encode("gbk", errors = "ignore")
                        # new_data += data[i + 1:j]
                        last_i = j
                    res_id += 3
        i = j + 1
    new_data += data[last_i:]
    assert res_id == len(res_text)

    for i in range(100):
        offset = i * 0x24
        if new_data[offset] == 0x00:
            break
        j = offset
        while not new_data[j] == 0x00:
            j += 1
        se_name = new_data[offset:j]
        section = int.from_bytes(new_data[offset + 0x20 : offset + 0x24], "little")
        se_offset = new_data.find(b"\x24" + se_name, 0xE10) - 0xE10
        # print(hex(section), hex(se_offset))
        new_data[offset + 0x20:offset + 0x24] = se_offset.to_bytes(4, byteorder="little")

    with open("res_dat2/" + fn.split("\\")[-1], "wb") as f:
        f.write(new_data)