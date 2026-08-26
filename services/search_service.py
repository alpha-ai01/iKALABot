import logging
import requests
import config

class SearchRouter:
    def __init__(self):
        self.google_api_key = config.GOOGLE_SEARCH_API_KEY
        self.google_cx = config.GOOGLE_SEARCH_CX

    def search_web(self, query, max_results=3):
        """Unified interface with zero-hallucination constraint."""
        # 1. Try DuckDuckGo
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

        # 2. Try Google Search
        try:
            if not self.google_api_key or not self.google_cx:
                raise ValueError("Google Search API not configured.")
            
            url = f"https://www.googleapis.com/customsearch/v1?key={self.google_api_key}&cx={self.google_cx}&q={query}&num={max_results}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append(f"📌 {item.get('title')}\n{item.get('snippet')}\n🔗 {item.get('link')}\n")
            
            if results:
                return self._format_response(query, results)
        except Exception as e:
            logging.error(f"Google Search failed: {e}")

        return "ไม่พบข้อมูลจากการค้นหา (หรือระบบค้นหาไม่สามารถใช้งานได้)"

    def _format_response(self, query, results):
        return (
            f"🔍 ผลการค้นหาสำหรับ: '{query}'\n\n"
            f"{chr(10).join(results)}\n"
            f"--- \nคำสั่ง: ให้สรุปข้อมูลจากแหล่งอ้างอิงที่ให้ไว้เท่านั้น ห้ามเดาข้อมูลเพิ่มเอง"
        )
