filename = "requirements.txt"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

if "pyTelegramBotAPI" not in content:
    content += "\npyTelegramBotAPI\n"

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่ม pyTelegramBotAPI ลงใน requirements.txt สำเร็จ ===")
