import logging

class SearchRouter:
    def __init__(self):
        # Primary: duckduckgo, Fallback: google
        self.primary = "duckduckgo"
        self.fallback = "google"

    def search_web(self, query, max_results=5):
        """Unified interface for web search. Always tries DuckDuckGo first."""
        
        logging.info("[Search] Query: %s", query)
        
        # 1. Try DuckDuckGo
        try:
            results = self._duckduckgo_search(query, max_results)
            if results:
                logging.info("[Search] DuckDuckGo success")
                return results
            logging.warning("[Search] DuckDuckGo returned no results")
        except Exception as e:
            logging.error("[Search] DuckDuckGo error: %s", str(e))
        
        # 2. Fallback to Google
        logging.info("[Search] Trying Google fallback")
        try:
            return self._google_search(query, max_results)
        except Exception as e:
            logging.error("[Search] Google error: %s", str(e))
            return "Search failed: No providers available."

    def _duckduckgo_search(self, query, max_results):
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            # ddgs.text returns a generator
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "duckduckgo"
                })
        return results

    def _google_search(self, query, max_results):
        # Placeholder: Implement actual Google Search API call
        return [
            {"title": "Sample Result (Google)", "url": "https://example.com", "snippet": "This is a search result for " + query, "source": "google"}
        ]
