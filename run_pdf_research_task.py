import time
from google import genai

try:
    client = genai.Client()

    # 1. เริ่มงานวิเคราะห์ PDF Document จาก URL แบบ Background
    interaction = client.interactions.create(
        agent="deep-research-preview-04-2026",
        input=[
            {"type": "text", "text": "What is this document about?"},
            {
                "type": "document",
                "uri": "https://arxiv.org/pdf/1706.03762",
                "mime_type": "application/pdf",
            },
        ],
        background=True,
    )

    print(f"=== เริ่มต้น Document Analysis Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 2. ลูปติดตามสถานะจนกว่าจะอ่านและสรุปเอกสาร PDF เสร็จสมบูรณ์
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังอ่านและวิเคราะห์เอกสาร PDF... (รอ 10 วินาที)")
        time.sleep(10)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลการสรุปเอกสาร
    if interaction.status == "completed":
        print("\n=== ผลการวิเคราะห์เอกสาร PDF ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
