"""Turn a per-SKU forecast dataframe into the two inputs the LLM pipeline needs.

Called by src.recommendations.engine.run_pipeline(). Produces:

    summary_text: str        - the ``forecast_summary`` argument to llm.reason()
    rec_seeds: list[dict]    - one seed per candidate recommendation, containing
                               the fields llm.guard.check() expects (direction)
                               plus a focus_line the orchestrator appends to the
                               prompt so each call produces a SKU-specific rec.

Forecast rows with a weak baseline (below ``min_baseline`` units/day) are
filtered out before ranking so low-volume noise does not crowd out commercially
meaningful movement.
"""
from __future__ import annotations

import pandas as pd


def summarize_forecast(
    forecast_df: pd.DataFrame,
    top_k: int = 3,
    min_baseline: float = 1.0,
) -> tuple[str, list[dict]]:
    """Rank SKUs by absolute forecast-vs-baseline delta and build prompt inputs.

    Expects ``forecast_df`` to come from src.forecast.serve.forecast_with_names,
    so it carries both the numeric codes (item_id, dept_id, cat_id) and the
    human-readable strings (item_id_str, dept_id_str, cat_id_str).
    """
    df = forecast_df.copy()
    df = df[df["baseline"].fillna(0) >= min_baseline]
    df = df.dropna(subset=["delta_pct"])

    if df.empty:
        return "No SKUs met the minimum baseline threshold for forecasting.", []

    df["abs_delta"] = df["delta_pct"].abs()
    top = df.sort_values("abs_delta", ascending=False).head(top_k)

    summary_lines = [
        f"Top {len(top)} SKUs by absolute forecast-vs-28-day-baseline delta:",
    ]
    seeds: list[dict] = []
    for _, row in top.iterrows():
        item = row.get("item_id_str", row["item_id"])
        dept = row.get("dept_id_str", row["dept_id"])
        cat = row.get("cat_id_str", row["cat_id"])
        pct = float(row["delta_pct"]) * 100  # delta_pct is a fraction in serve.py
        summary_lines.append(
            f"- {item} ({cat}, dept {dept}): predicted {row['predicted']:.2f} units, "
            f"28-day baseline {row['baseline']:.2f}, delta {pct:+.1f}%"
        )
        seeds.append({
            "item_id": item,
            "dept_id": dept,
            "cat_id": cat,
            "direction": row["direction"],
            "delta_pct": pct,
            "focus_line": (
                f"Focus this recommendation on SKU {item} in category {cat}: "
                f"predicted {row['predicted']:.2f} units vs baseline {row['baseline']:.2f} "
                f"({pct:+.1f}%). Trend direction: {row['direction']}."
            ),
        })

    summary_text = "\n".join(summary_lines)
    return summary_text, seeds
