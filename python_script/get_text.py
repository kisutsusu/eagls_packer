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

get_filelist(r"new_data2", files)

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
    text = ""
    print(fn)
    last_commend = b""
    with open(fn, "rb") as f:
        data = f.read()
    i = 0
    len_data = len(data)
    while i < len_data:
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
            if test != "" and not check(test):
                txt = base64.b64encode(data[i + 1 : j]).decode("utf-8")
                # txt = data[i + 1 : j].decode("gbk", errors="backslashreplace")
                text += txt + "\n" + txt + "\n" + "\n"
        i = j + 1
    file_name = fn.split("\\")[-1].split(".")[0]
    if text != "":
        with open(f"old_textv2\\{file_name}.txt", "w", encoding="utf-8") as f:
            f.write(text)