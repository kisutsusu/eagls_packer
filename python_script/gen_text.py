import os
import base64

for file in os.listdir("old_text"):
    print(file)
    with open("old_text/" + file, "r", encoding="utf-8") as f:
        old_text = f.readlines()
    with open("new_text/" + file, "r", encoding="utf-8") as f:
        new_text = f.readlines()
    assert len(old_text) == len(new_text)

    for i in range(0, len(old_text), 3):
        tmp = base64.b64decode(new_text[i]).decode("shift-jis", errors="backslashreplace")
        if tmp == old_text[i][:-1]:
            pass
        else:
            old_text[i + 1] = base64.b64decode(new_text[i]).decode("gbk", errors="backslashreplace") + "\n"

    with open("new_text2/" + file, "w", encoding="utf-8") as f:
        f.writelines(old_text)