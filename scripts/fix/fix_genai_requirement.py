filename = "requirements.txt"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

if "google-genai" not in content:
    content += "\ngoogle-genai\n"

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่ม google-genai ลงใน requirements.txt สำเร็จ ===")
