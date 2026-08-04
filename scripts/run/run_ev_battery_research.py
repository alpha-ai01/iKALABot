import time
from google import genai

try:
    client = genai.Client()

    # 1. กำหนด Prompt สำหรับโครงสร้าง รายงานเชิงเทคนิค
    prompt = """Research the competitive landscape of EV batteries. Format the output as a technical report with the following structure:
1. Executive Summary
2. Key Players (Must include a data table comparing capacity and chemistry)
3. Supply Chain Risks"""

    # 2. เริ่มงานวิจัยเชิงลึกแบบ Background Task
    interaction = client.interactions.create(
        input=prompt,
        agent="deep-research-preview-04-2026",
        background=True
    )

    print(f"=== เริ่มต้น EV Battery Research Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 3. ติดตามสถานะการค้นคว้าเชิงลึก
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังรวบรวมข้อมูลและเขียนรายงานเชิงเทคนิค... (รอ 15 วินาที)")
        time.sleep(15)
        interaction = client.interactions.get(interaction.id)

    # 4. แสดงผลลัพธ์รายงานเชิงเทคนิคเมื่อเสร็จสมบูรณ์
    if interaction.status == "completed":
        print("\n=== รายงานเชิงเทคนิค: EV Battery Competitive Landscape ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
