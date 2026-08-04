import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

# ค้นหาจุดที่มีการเรียกใช้งาน client.interactions.create หรือ client.models.generate_content 
# และทำการแทรก tools=[{"type": "google_search"}] เข้าไปหากยังไม่มี
if 'tools=' not in content:
    # ตัวอย่างการแทรกเข้าไปในส่วนคำสั่งเรียกโมเดล
    content = re.sub(
        r'(client\.(?:interactions|models)\.create\([^)]*model="gemini-3.6-flash"[^)]*)',
        r'\1, tools=[{"type": "google_search"}]',
        content,
        flags=re.DOTALL
    )

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่ม Google Search Tool สำเร็จ ===")
