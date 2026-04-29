from dataclasses import dataclass
from pathlib import Path

from src.forecast.serve import forecast_with_names
from src.llm.guard import check
from src.llm.reasoner import reason
from src.rag.retriever import retrieve
from src.recommendations.summarize import summarize_forecast


@dataclass
class Rec:
    rec_type: str        # "markdown" | "restock" | "promote"
    text: str
    flagged: bool
    flag_reason: str
    intent_check: str = ""
    numeric_check: str = ""


def run_pipeline(
    store_id: str,
    date: str,
    data_dir: Path,
    vector_store_dir: Path,
    top_k: int = 3,
) -> list[Rec]:
    """Orchestrate forecast -> summarize -> RAG -> LLM -> guard -> Rec list.

    Layers are already implemented independently; this function simply wires
    them together in sequence and emits one Rec per top-K SKU.
    """
    forecast_df = forecast_with_names(store_id, date, data_dir)
    summary_text, rec_seeds = summarize_forecast(forecast_df, top_k=top_k)

    recs: list[Rec] = []
    for seed in rec_seeds:
        query = f"{store_id} {seed['cat_id']} {seed['direction']} trend"
        context_docs = retrieve(query, vector_store_dir, k=3)

        rec_text = reason(
            forecast_summary=summary_text + "\n\n" + seed["focus_line"],
            context_docs=context_docs,
        )

        guard_out = check(
            {"text": rec_text},
            {"direction": seed["direction"], "delta_pct": seed["delta_pct"]},
        )

        if seed["direction"] == "down":
            rec_type = "markdown"
        elif seed.get("promote_candidate"):
            rec_type = "promote"
        else:
            rec_type = "restock"
        recs.append(Rec(
            rec_type=rec_type,
            text=rec_text,
            flagged=guard_out["flagged"],
            flag_reason=guard_out["reason"],
            intent_check=guard_out["intent_check"],
            numeric_check=guard_out["numeric_check"],
        ))

    return recs
