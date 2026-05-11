from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
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
    confidence: str = ""  # "High" | "Medium" | "Low"
    delta_pct: float = 0.0
    impact: str = ""         # short action badge, e.g. "↑ €2.24" / "+ 42 units" / "↓ €1.91"
    action_detail: str = ""  # full sentence shown inside Details expander


def _compute_action(rec_type: str, delta_pct: float, baseline: float, sell_price: float, horizon: int = 7) -> tuple[str, str]:
    """Return (impact badge, action detail sentence) for a recommendation."""
    extra_units = baseline * (abs(delta_pct) / 100.0) * horizon
    if rec_type == "promote":
        if sell_price > 0:
            revenue = extra_units * sell_price
            badge = f"+€{revenue:.0f} rev"
            detail = (
                f"Suggested action: Move to end-cap or high-traffic display. "
                f"Keep price at €{sell_price:.2f}/unit - demand is already strong. "
                f"Expected revenue uplift: ~€{revenue:.0f} over {horizon} days."
            )
        else:
            badge = f"+{extra_units:.0f} units"
            detail = (
                f"Suggested action: Move to end-cap or high-traffic display. "
                f"Demand is already strong - amplify with visibility. "
                f"Expected volume uplift: ~{extra_units:.0f} units over {horizon} days."
            )
    elif rec_type == "restock":
        badge = f"+{extra_units:.0f} units"
        detail = (
            f"Suggested action: Order ~{extra_units:.0f} units to cover projected demand "
            f"over the next {horizon} days."
        )
    else:  # markdown
        discount_pct = min(30.0, max(15.0, abs(delta_pct) * 0.05))
        if sell_price > 0:
            new_price = sell_price * (1 - discount_pct / 100.0)
            badge = f"↓ €{new_price:.2f}"
            detail = (
                f"Suggested action: Reduce price to €{new_price:.2f}/unit (-{discount_pct:.0f}%) "
                f"to clear declining inventory before it ages."
            )
        else:
            badge = f"-{discount_pct:.0f}% price"
            detail = (
                f"Suggested action: Apply a -{discount_pct:.0f}% markdown "
                f"to clear declining inventory before it ages."
            )
    return badge, detail


def _compute_confidence(delta_pct: float) -> str:
    """Derive confidence from forecast signal strength.

    Thresholds reflect retail merchandising intuition:
    - High (>100%): very strong momentum, act with confidence
    - Medium (30-100%): solid signal, reasonable to act
    - Low (<30%): weak signal, manager should verify before acting
    """
    abs_delta = abs(delta_pct)
    if abs_delta > 100:
        return "High"
    elif abs_delta > 30:
        return "Medium"
    return "Low"


def _process_seed(seed: dict, store_id: str, summary_text: str, vector_store_dir: Path) -> Rec:
    """Process one seed: RAG retrieve -> LLM reason -> guard check -> Rec."""
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

    impact, action_detail = _compute_action(
        rec_type, seed["delta_pct"], seed.get("baseline", 1.0), seed.get("sell_price", 0.0)
    )
    return Rec(
        rec_type=rec_type,
        text=rec_text,
        flagged=guard_out["flagged"],
        flag_reason=guard_out["reason"],
        intent_check=guard_out["intent_check"],
        numeric_check=guard_out["numeric_check"],
        confidence=_compute_confidence(seed["delta_pct"]),
        delta_pct=seed["delta_pct"],
        impact=impact,
        action_detail=action_detail,
    )


def run_pipeline(
    store_id: str,
    date: str,
    data_dir: Path,
    vector_store_dir: Path,
) -> list[Rec]:
    """Orchestrate forecast -> summarize -> RAG -> LLM -> guard -> Rec list.

    Selects up to 3 candidates per bucket (PROMOTE / RESTOCK / MARKDOWN),
    runs each through RAG + LLM + guard in parallel, and returns the full Rec list.
    """
    forecast_df = forecast_with_names(store_id, date, data_dir)
    summary_text, rec_seeds = summarize_forecast(forecast_df)

    if not rec_seeds:
        return []

    process = partial(_process_seed, store_id=store_id, summary_text=summary_text, vector_store_dir=vector_store_dir)
    with ThreadPoolExecutor(max_workers=len(rec_seeds)) as executor:
        recs = list(executor.map(process, rec_seeds))

    return recs
