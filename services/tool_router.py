import datetime
import pytz
from utils import tools
from services import document_service

class ToolRouter:
    def route(self, task, text=None, **kwargs):
        if task == "time":
            return self._handle_time(kwargs.get("timezone", "Asia/Bangkok"))
        elif task == "search":
            return tools.search_web(text)
        elif task == "document":
            return document_service.process_document(kwargs.get("file_path"))
        # ... other tasks
        return None

    def _handle_time(self, timezone_str):
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.datetime.now(tz)
            
            day_map = {
                0: "วันจันทร์", 1: "วันอังคาร", 2: "วันพุธ", 3: "วันพฤหัสบดี",
                4: "วันศุกร์", 5: "วันเสาร์", 6: "วันอาทิตย์"
            }
            day_name = day_map[now.weekday()]
            
            # Use Thai locale months manually for now since locale setup might be tricky
            month_map = {
                1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
                5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
                9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
            }
            month_name = month_map[now.month]
            
            return f"ปัจจุบันเวลา: {now.strftime('%H:%M:%S')} น.\n{day_name}ที่ {now.strftime('%d')} {month_name} {now.year + 543} (เขตเวลา: {timezone_str})"
        except Exception:
            return f"ไม่รู้จักเขตเวลา: {timezone_str}"
