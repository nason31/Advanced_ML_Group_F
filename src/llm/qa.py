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
    active_products: dict[str, str] | None = None,
) -> str:
    """Answer a natural language question grounded in forecast data and RAG context.

    active_products: {product_name: sku} for the recs currently on screen.
    Used to resolve product names in the question and build a targeted RAG query.
    """
    forecast_df = forecast_with_names(store_id, date, data_dir)
    summary_text, _ = summarize_forecast(forecast_df, bucket_size=5)

    # Match question against active product names, then SKU codes
    rag_query = question
    q_upper = question.upper()

    if active_products:
        for name, sku in active_products.items():
            if name.upper() in q_upper or q_upper in name.upper():
                # Look up this SKU's category/dept for a targeted RAG query
                match = forecast_df[
                    forecast_df["item_id_str"].apply(lambda x: str(x).upper() == sku.upper())
                ]
                if not match.empty:
                    row = match.iloc[0]
                    rag_query = f"{store_id} {row['cat_id_str']} {row['dept_id_str']} trend"
                break
        else:
            # Fall back to SKU code match
            sku_match = forecast_df[
                forecast_df["item_id_str"].apply(lambda x: str(x).upper() in q_upper)
            ]
            if not sku_match.empty:
                row = sku_match.iloc[0]
                rag_query = f"{store_id} {row['cat_id_str']} {row['dept_id_str']} trend"

    context_docs = retrieve(rag_query, vector_store_dir, k=6)

    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=QA_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": build_qa_prompt(question, summary_text, context_docs, active_products),
        }],
    )
    return response.content[0].text
