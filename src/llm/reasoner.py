import os
import time
import threading
import anthropic
from src.llm.prompts import SYSTEM_PROMPT, build_user_prompt

_client: anthropic.Anthropic | None = None
_client_lock = threading.Lock()


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def reason(forecast_summary: str, context_docs: list[str]) -> str:
    """Call Claude to produce merchandising recommendations with citations."""
    client = get_client()
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": build_user_prompt(forecast_summary, context_docs)}],
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
        except anthropic.APIStatusError as exc:
            if attempt == 2 or exc.status_code < 500:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("reason() retry loop exited without returning")
