import pytz
from datetime import datetime
import logging

def get_current_time():
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    return now.strftime("ขณะนี้เวลา %H:%M น. ของวันที่ %d/%m/%Y")

def search_web(query, max_results=3):
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(query, max_results=max_results)
    except ImportError:
        logging.error("DuckDuckGo search dependency is missing.")
        return "ฟังก์ชันการค้นหาไม่สามารถใช้งานได้ในขณะนี้ (ขาดไลบรารี)"
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return f"เกิดข้อผิดพลาดในการค้นหา: {e}"

    if not results:
        return "ไม่พบข้อมูลจากการค้นหา"

    response = f"🔍 ผลการค้นหาสำหรับ: '{query}'\n\n"
    for res in results:
        response += f"📌 {res['title']}\n{res['body']}\n🔗 {res['href']}\n\n"
    return response

