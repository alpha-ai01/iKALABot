import logging
import json
import config
from openai import OpenAI
from ai.model_registry import is_model_free, get_best_free_model

logger = logging.getLogger(__name__)

class AIGateway:
    @staticmethod
    def _get_client():
        if not config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not configured in the environment.")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "https://ikalabot.ai",
                "X-Title": "iKALABot"
            }
        )

    @staticmethod
    def call_ai_stream(prompt: str, capability: str = "text"):
        """Interface for streaming AI requests."""
        model_id = get_best_free_model(capability)
        if not model_id:
            yield "No compatible free model available."
            return

        client = AIGateway._get_client()
        stream = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            stream_options={"include_usage": True}
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            if chunk.usage and chunk.usage.completion_tokens_details:
                reasoning = chunk.usage.completion_tokens_details.reasoning_tokens
                if reasoning:
                    yield f"\n\n(Reasoning tokens: {reasoning})"

