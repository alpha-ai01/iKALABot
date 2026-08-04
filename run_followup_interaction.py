import time
import sys
from google import genai

try:
    client = genai.Client()

    # ระบุ Interaction ID จาก Task ก่อนหน้าที่ทำเสร็จสมบูรณ์แล้ว
    # (เปลี่ยนค่าตรงนี้หรือรับผ่าน Argument)
    previous_id = "COMPLETED_INTERACTION_ID"

    if len(sys.argv) > 1:
        previous_id = sys.argv[1]

    print(f"=== เริ่มต้นถามคำถามต่อเนื่องจาก Interaction ID: {previous_id} ===")

    # 1. ส่งคำถามต่อยอดโดยอ้างอิงบริบทเดิมผ่าน previous_interaction_id
    interaction = client.interactions.create(
        input="Can you elaborate on the second point in the report?",
        model="gemini-3.1-pro-preview",
        previous_interaction_id=previous_id
    )

    # 2. ตรวจสอบสถานะการประมวลผล
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังประมวลผลคำตอบเพิ่มเติม... (รอ 5 วินาที)")
        time.sleep(5)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลลัพธ์คำตอบล่าสุด
    if interaction.status == "completed":
        print("\n=== รายละเอียดเพิ่มเติม (Follow-up Result) ===")
        print(interaction.steps[-1].content[0].text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
