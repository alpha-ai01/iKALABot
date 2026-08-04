import time
from google import genai

try:
    client = genai.Client()

    # 1. เริ่มงานวิเคราะห์และสรุปเนื้อหาจาก URL แบบ Background Task
    interaction = client.interactions.create(
        agent="deep-research-preview-04-2026",
        input="Summarize the content of https://www.wikipedia.org/.",
        tools=[{"type": "url_context"}],
        background=True,
    )

    print(f"=== เริ่มต้น URL Summary Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 2. รอจนกว่าระบบจะประมวลผลเสร็จ (Polling status)
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังอ่านและสรุปเนื้อหาจาก URL... (รอ 10 วินาที)")
        time.sleep(10)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลลัพธ์เมื่อทำงานเสร็จสมบูรณ์
    if interaction.status == "completed":
        print("\n=== ผลการสรุปเนื้อหา ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
