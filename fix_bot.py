import re

# ระบุชื่อไฟล์หลักของบอท (ปรับเปลี่ยนได้ตามชื่อไฟล์จริงของคุณ เช่น main.py หรือ bot.py)
filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

# 1. แก้ไขชื่อโมเดล Gemini ให้เป็น gemini-3.6-flash
# แทนที่โมเดลเก่าทุกรูปแบบ เช่น gemini-2.5-flash หรืออื่นๆ ที่ผิดพลาด
content = re.sub(r'gemini-[\d\.]+(-flash)?', 'gemini-3.6-flash', content)

# 2. แก้ไขชื่อโมเดล OpenRouter ให้เป็น gemma-2-9b-it:free
content = re.sub(r'gemma-[\w\-\:]+', 'gemma-2-9b-it:free', content)

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== อัปเดตชื่อโมเดลในโค้ดเรียบร้อยแล้ว ===")
