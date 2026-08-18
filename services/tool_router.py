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
            return f"ปัจจุบันเวลา: {now.strftime('%H:%M:%S')} (เขตเวลา: {timezone_str})"
        except pytz.UnknownTimeZoneError:
            return f"ไม่รู้จักเขตเวลา: {timezone_str}"
