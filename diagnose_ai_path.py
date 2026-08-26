import logging
from ai.gateway import AIGateway
from ai.model_registry import get_best_free_model
import config

# Configure logging to capture details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagnostics")

def run_diagnosis():
    prompt = "ทดสอบบอท"
    
    logger.info("--- Starting Forensic AI Diagnosis ---")
    
    # 1. Check Configuration
    api_key = config.OPENROUTER_API_KEY
    logger.info(f"API_KEY Status: {'SET' if api_key else 'NOT SET'}")
    
    # 2. Check Model Selection
    capability = "text"
    model_id = get_best_free_model(capability)
    logger.info(f"Model Selected: {model_id}")
    
    if not model_id:
        logger.error("Root Cause: No free model returned by registry.")
        return

    # 3. Simulate Gateway Call
    logger.info("Attempting Gateway Call...")
    try:
        response = AIGateway.call_ai(prompt, capability=capability)
        logger.info(f"Response: {response}")
    except Exception as e:
        logger.error(f"Gateway Exception: {e}")

    logger.info("--- Diagnosis Complete ---")

if __name__ == "__main__":
    run_diagnosis()
