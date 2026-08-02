import pytz
from datetime import datetime
from duckduckgo_search import DDGS

def get_current_time():
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    return now.strftime("ขณะนี้เวลา %H:%M น. ของวันที่ %d/%m/%Y")

def search_web(query, max_results=3):
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "ไม่พบข้อมูลจากการค้นหา"
        
        response = f"🔍 ผลการค้นหาสำหรับ: '{query}'\n\n"
        for res in results:
            response += f"📌 {res['title']}\n{res['body']}\n🔗 {res['href']}\n\n"
        return response
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการค้นหา: {e}"
