import os

log = ""
for file in os.listdir("new_text2"):
    print(file)
    if not os.path.exists("old_textv22/" + file):
        continue

    with open("new_text2/" + file, "r", encoding="utf-8") as f:
        res_text = f.readlines()
    with open("old_textv22/" + file, "r", encoding="utf-8") as f:
        new_text = f.readlines()

    if len(res_text) != len(new_text):
        print("new_text2/" + file)
        print("old_textv22/" + file)
        print("fail")
        break

    for i in range(0, len(res_text), 3):
        if res_text[i] == res_text[i + 1]:
            log += res_text[i + 1] + "\n" + new_text[i + 1] + "\n\n"
            res_text[i + 1] = new_text[i + 1]

    with open("new_text3/" + file, "w", encoding="utf-8") as f:
        f.writelines(res_text)

with open("log.txt", "w", encoding="utf-8") as f:
    f.write(log)