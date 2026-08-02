from google import genai
from google.genai import types

# เตรียมเชื่อมต่อด้วย API Key (Generation ของเดือน 8 ปี 2026)
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# กำหนด Config เพื่อใส่ฟังก์ชันค้นหาข้อมูลทาง Google Search
config = types.GenerateContentConfig(
    tools=[types.Tool(google_search=types.GoogleSearch())]
)

# โครงสร้างสำหรับรับข้อความจาก Telegram และส่งให้โมเดล
# response = client.models.generate_content(
#     model="gemini-3.6-flash",
#     contents="คำถามหรือคำสั่งจากผู้ใช้งาน",
#     config=config
# )
