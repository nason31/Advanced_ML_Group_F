from pathlib import Path

from src.forecast.serve import forecast_with_names
from src.llm.guard import check as guard_check
from src.llm.prompts import QA_SYSTEM_PROMPT, build_qa_prompt
from src.llm.reasoner import get_client
from src.rag.retriever import retrieve
from src.recommendations.summarize import summarize_forecast


def answer_question(
    question: str,
    store_id: str,
    date: str,
    data_dir: Path,
    vector_store_dir: Path,
    active_products: dict[str, str] | None = None,
    chat_history: list[dict] | None = None,
) -> dict:
    """Answer a natural language question grounded in forecast data and RAG context.

    active_products: {product_name: sku} for the recs currently on screen.
    Used to resolve product names in the question and build a targeted RAG query.

    Returns {"answer": str, "flagged": bool, "flag_reason": str}.
    """
    forecast_df = forecast_with_names(store_id, date, data_dir)
    summary_text, _ = summarize_forecast(forecast_df, bucket_size=5)

    # Match question against active product names, then SKU codes
    rag_query = question
    q_upper = question.upper()
    matched_direction: str | None = None

    if active_products:
        matched = False
        for name, sku in active_products.items():
            if name.upper() in q_upper:
                match = forecast_df[
                    forecast_df["item_id_str"].apply(lambda x: str(x).upper() == sku.upper())
                ]
                if not match.empty:
                    row = match.iloc[0]
                    matched_direction = row["direction"]
                    rag_query = f"{store_id} {row['cat_id_str']} {row['dept_id_str']} trend"
                matched = True
                break

        if not matched:
            sku_match = forecast_df[
                forecast_df["item_id_str"].apply(lambda x: str(x).upper() in q_upper)
            ]
            if not sku_match.empty:
                row = sku_match.iloc[0]
                matched_direction = row["direction"]
                rag_query = f"{store_id} {row['cat_id_str']} {row['dept_id_str']} trend"

    context_docs = retrieve(rag_query, vector_store_dir, k=6)

    client = get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=QA_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": build_qa_prompt(question, summary_text, context_docs, active_products, chat_history),
        }],
    )
    answer_text = response.content[0].text

    # Guard: intent check only - Q&A intentionally translates numbers to plain language,
    # so the numeric % check would always false-positive. Intent contradiction is the real risk.
    guard_result = {"flagged": False, "reason": ""}
    if matched_direction:
        guard_result = guard_check(
            {"text": answer_text},
            {"direction": matched_direction, "delta_pct": None},
        )

    return {
        "answer": answer_text,
        "flagged": guard_result["flagged"],
        "flag_reason": guard_result["reason"],
    }
