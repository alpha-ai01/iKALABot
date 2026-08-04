import time
from google import genai

try:
    client = genai.Client()

    # 1. เริ่มงานค้นคว้าเชิงลึกแบบ Background Task
    interaction = client.interactions.create(
        agent="deep-research-preview-04-2026",
        input="What are the latest developments in quantum computing?",
        tools=[{"type": "google_search"}],
        background=True,
    )

    print(f"=== เริ่มต้น Research Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 2. รอจนกว่าระบบจะประมวลผลเสร็จ (Polling status)
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังค้นคว้าข้อมูลเชิงลึก... (รอ 10 วินาที)")
        time.sleep(10)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลลัพธ์เมื่อทำงานเสร็จสมบูรณ์
    if interaction.status == "completed":
        print("\n=== ผลการวิจัยเชิงลึก ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
