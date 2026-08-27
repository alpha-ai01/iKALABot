import pytz
from datetime import datetime
import logging
import os
import abc
from typing import List, Dict

from utils.file_handler import read_file_range, targeted_edit, get_file_type

# Project Root for sandboxing
PROJECT_ROOT = os.getcwd()

# --- Search Architecture ---

class SearchProvider(abc.ABC):
    @abc.abstractmethod
    def search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        pass

class DDGProvider(SearchProvider):
    def search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return [{'title': r['title'], 'body': r['body'], 'href': r['href']} for r in results]
        except ImportError:
            logging.error("ddgs library not installed, skipping DDG search.")
            return []
        except Exception as e:
            logging.error(f"DDG Search failed: {e}")
            return []

class GoogleSearchProvider(SearchProvider):
    def __init__(self, api_key: str, engine_id: str):
        self.api_key = api_key
        self.engine_id = engine_id

    def search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        # TODO: Implement actual Google Search API call with quota check
        logging.info("Google Search API called.")
        return []

class SearchRouter:
    def __init__(self):
        self.providers = []
        # Register providers
        if os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_SEARCH_ENGINE_ID"):
             self.providers.append(GoogleSearchProvider(os.getenv("GOOGLE_SEARCH_API_KEY"), os.getenv("GOOGLE_SEARCH_ENGINE_ID")))
        self.providers.append(DDGProvider())

    def search(self, query: str, max_results: int = 3) -> str:
        for provider in self.providers:
            results = provider.search(query, max_results)
            if results:
                response = f"🔍 ผลการค้นหาจาก {provider.__class__.__name__} สำหรับ: '{query}'\n\n"
                for res in results:
                    response += f"📌 {res['title']}\n{res['body']}\n🔗 {res['href']}\n\n"
                return response
        return "ไม่พบข้อมูลจากการค้นหา"

# --- Existing Functions ---

def validate_path(file_path):
    """Ensure path is within project root and not sensitive."""
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(PROJECT_ROOT):
        raise ValueError("Access Denied: Path is outside project directory.")
    
    # Deny access to sensitive files
    sensitive_files = [".env", ".git", ".db", "config.py"]
    for s in sensitive_files:
        if s in abs_path:
            raise ValueError(f"Access Denied: Cannot access sensitive file {s}")
    return abs_path

def get_current_time():
    # TODO: Implement Thai format as per requirements
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    return now.strftime("ขณะนี้เวลา %H:%M น. ของวันที่ %d/%m/%Y")

def read_file_tool(file_path, start_line=1, end_line=None):
    try:
        validated_path = validate_path(file_path)
        return read_file_range(validated_path, start_line, end_line)
    except Exception as e:
        return str(e)

def edit_file_tool(file_path, search_pattern, new_content):
    try:
        validated_path = validate_path(file_path)
        return targeted_edit(validated_path, search_pattern, new_content)
    except Exception as e:
        return str(e)

def search_web(query, max_results=3):
    router = SearchRouter()
    return router.search(query, max_results)
