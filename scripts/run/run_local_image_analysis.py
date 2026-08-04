import os
import sys
from PIL import Image
from google import genai

try:
    client = genai.Client()

    # ระบุ Path ของไฟล์ภาพในเครื่อง (สามารถส่ง path ผ่าน argument ได้ เช่น: python run_local_image_analysis.py my_image.png)
    image_path = "organ.png"
    if len(sys.argv) > 1:
        image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"[Error]: ไม่พบไฟล์ภาพที่ Path: {image_path}")
        print("กรุณาเปลี่ยน image_path ในไฟล์ หรือส่ง path ผ่าน command line argument")
        sys.exit(1)

    print(f"=== กำลังโหลดภาพจาก: {image_path} ===")
    image = Image.open(image_path)

    print("=== กำลังส่งภาพไปวิเคราะห์ที่ gemini-3.6-flash ===")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[image, "Tell me about this instrument"]
    )

    print("\n=== ผลการวิเคราะห์ภาพ ===")
    print(response.text)

except Exception as e:
    print(f"[Error]: {e}")
