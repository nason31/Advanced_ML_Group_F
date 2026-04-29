from pathlib import Path

from src.forecast.serve import forecast_with_names
from src.llm.prompts import QA_SYSTEM_PROMPT, build_qa_prompt
from src.llm.reasoner import _get_client
from src.rag.retriever import retrieve
from src.recommendations.summarize import summarize_forecast


def answer_question(
    question: str,
    store_id: str,
    date: str,
    data_dir: Path,
    vector_store_dir: Path,
) -> str:
    """Answer a natural language question about store performance.

    Loads the current forecast, retrieves relevant RAG context for the
    question, then calls Claude with both as grounding context.
    """
    forecast_df = forecast_with_names(store_id, date, data_dir)
    summary_text, _ = summarize_forecast(forecast_df, top_k=5)

    context_docs = retrieve(question, vector_store_dir, k=4)

    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=QA_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": build_qa_prompt(question, summary_text, context_docs),
        }],
    )
    return response.content[0].text
