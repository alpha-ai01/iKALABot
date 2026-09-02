import logging
import config

class SearchRouter:
    def __init__(self):
        pass

    def search_web(self, query, max_results=3):
        """Unified interface with zero-hallucination constraint."""
        # Try DuckDuckGo
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(f"📌 {r.get('title')}\n{r.get('body')}\n🔗 {r.get('href')}\n")
            if results:
                return self._format_response(query, results)
        except Exception as e:
            logging.error(f"DDG Search failed: {e}")

        return "ไม่พบข้อมูลจากการค้นหา (หรือระบบค้นหาไม่สามารถใช้งานได้)"

    def _format_response(self, query, results):
        return (
            f"🔍 ผลการค้นหาสำหรับ: '{query}'\n\n"
            f"{chr(10).join(results)}\n"
            f"--- \nคำสั่ง: ให้สรุปข้อมูลจากแหล่งอ้างอิงที่ให้ไว้เท่านั้น ห้ามเดาข้อมูลเพิ่มเอง"
        )
