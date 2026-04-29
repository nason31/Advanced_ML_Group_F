import os
import anthropic
from src.llm.prompts import SYSTEM_PROMPT, build_user_prompt

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def reason(forecast_summary: str, context_docs: list[str]) -> str:
    """Call Claude to produce merchandising recommendations with citations."""
    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(forecast_summary, context_docs)}],
    )
    return response.content[0].text
