import os

for file in os.listdir("script"):
    if not file.endswith(".dat"):
        continue
    with open(f"script\\{file}", "rb") as f:
        data = f.read()
    with open(f"descript\\{file}", "w", encoding="gbk") as f:
        f.write(data.decode("gbk", errors="ignore").replace("\x00", ""))

