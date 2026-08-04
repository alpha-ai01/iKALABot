import time
from google import genai

try:
    client = genai.Client()

    # 1. เริ่มงานคำนวณ Fibonacci โดยใช้ Code Execution Tool แบบ Background
    interaction = client.interactions.create(
        agent="deep-research-preview-04-2026",
        input="Calculate the 50th Fibonacci number.",
        tools=[{"type": "code_execution"}],
        background=True,
    )

    print(f"=== เริ่มต้น Fibonacci Calculation Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 2. ติดตามสถานะจนกว่าการประมวลผลโค้ดจะเสร็จสิ้น
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังประมวลผลโค้ดคณิตศาสตร์... (รอ 5 วินาที)")
        time.sleep(5)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลลัพธ์คำนวณเมื่อเสร็จสมบูรณ์
    if interaction.status == "completed":
        print("\n=== ผลการคำนวณ Fibonacci ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
