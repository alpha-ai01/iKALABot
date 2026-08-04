import time
from google import genai

try:
    client = genai.Client()

    # 1. เริ่มงานวิเคราะห์เปรียบเทียบข้อมูลไฟล์ภายในกับข่าวบนเว็บแบบ Background
    interaction = client.interactions.create(
        input="Compare our 2025 fiscal year report against current public web news.",
        agent="deep-research-preview-04-2026",
        background=True,
        tools=[
            {
                "type": "file_search",
                "file_search_store_names": ['fileSearchStores/my-store-name']
            }
        ]
    )

    print(f"=== เริ่มต้น File Search Comparison Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 2. ติดตามสถานะจนกว่าการค้นหาไฟล์และเปรียบเทียบข้อมูลจะเสร็จสิ้น
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังค้นหาข้อมูลในคลังเอกสารและเปรียบเทียบกับข่าว... (รอ 10 วินาที)")
        time.sleep(10)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลลัพธ์เมื่อประมวลผลเสร็จสมบูรณ์
    if interaction.status == "completed":
        print("\n=== ผลการวิเคราะห์เปรียบเทียบ ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
