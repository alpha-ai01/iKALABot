filename = "requirements.txt"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

if "beautifulsoup4" not in content:
    content += "\nbeautifulsoup4\n"

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่ม beautifulsoup4 ลงใน requirements.txt สำเร็จ ===")
