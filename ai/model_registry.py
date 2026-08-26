import requests
import logging
import time
from typing import List, Dict, Optional

# Cache for models to avoid excessive API calls
_model_cache = {
    "data": [],
    "last_updated": 0,
    "ttl": 3600  # 1 hour
}

logger = logging.getLogger(__name__)

def fetch_and_cache_models():
    """Fetch models from OpenRouter and cache them."""
    global _model_cache
    
    if time.time() - _model_cache["last_updated"] < _model_cache["ttl"]:
        return _model_cache["data"]
    
    url = "https://openrouter.ai/api/v1/models"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        models = data.get("data", [])
        
        # Sort by quality/reliability (simplified: prioritize models with 'instruct' in name)
        models.sort(key=lambda x: 'instruct' in x.get('id', '').lower(), reverse=True)
        
        _model_cache["data"] = models
        _model_cache["last_updated"] = time.time()
        
        logger.info(f"[ModelRegistry] Fetched and sorted {len(models)} models.")
        return models
    except Exception as e:
        logger.error(f"[ModelRegistry] Failed to fetch models: {e}")
        return []

def get_free_models() -> List[Dict]:
    """Return only models that are free."""
    all_models = fetch_and_cache_models()
    if not all_models:
        return []
    # Pricing is 0 if prompt and completion are both '0'
    return [
        m for m in all_models 
        if m.get("pricing", {}).get("prompt") == "0" and 
           m.get("pricing", {}).get("completion") == "0"
    ]

def is_model_free(model_id: str) -> bool:
    """Check if a specific model is free."""
    all_models = fetch_and_cache_models()
    for m in all_models:
        if m.get("id") == model_id:
            return m.get("pricing", {}).get("prompt") == "0" and \
                   m.get("pricing", {}).get("completion") == "0"
    return False

def get_best_free_model(capability: str) -> Optional[str]:
    """Return a suitable free model ID based on capability."""
    free_models = get_free_models()
    
    for m in free_models:
        model_id = m.get("id", "").lower()
        if capability == "vision" and any(tag in model_id for tag in ["vision", "flash"]):
            return m.get("id")
    
    return free_models[0].get("id") if free_models else None
