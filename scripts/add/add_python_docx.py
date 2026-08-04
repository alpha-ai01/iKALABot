import re

filename = "requirements.txt"

try:
    with open(filename, "r", encoding="utf-8") as f:
        requirements = f.read()
except FileNotFoundError:
    requirements = ""

if "python-docx" not in requirements:
    with open(filename, "a", encoding="utf-8") as f:
        f.write("\npython-docx\n")
    print("=== เพิ่ม python-docx ลงใน requirements.txt สำเร็จ ===")
else:
    print("=== python-docx มีอยู่ใน requirements.txt อยู่แล้ว ===")
