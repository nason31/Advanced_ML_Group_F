"""Turn a per-SKU forecast dataframe into the two inputs the LLM pipeline needs.

Called by src.recommendations.engine.run_pipeline(). Produces:

    summary_text: str        - the ``forecast_summary`` argument to llm.reason()
    rec_seeds: list[dict]    - one seed per candidate recommendation, ordered as
                               PROMOTE -> RESTOCK -> MARKDOWN, up to 3 per bucket.

Buckets:
    PROMOTE  : delta > +50%   - strong upward momentum, amplify immediately
    RESTOCK  : +15% to +50%   - moderate upward trend, replenish to avoid stockout
    MARKDOWN : delta < -15%   - declining demand, discount to clear ageing stock
"""
from __future__ import annotations

import pandas as pd

PROMOTE_THRESHOLD  =  50.0   # delta_pct %
RESTOCK_LOWER      =  15.0
MARKDOWN_THRESHOLD = -15.0
BUCKET_SIZE        =   3     # max recommendations per bucket
MIN_BASELINE       =   1.0   # units/day - filter out low-volume noise


def _build_seed(row: pd.Series, promote_candidate: bool) -> dict:
    item = row.get("item_id_str", row["item_id"])
    dept = row.get("dept_id_str", row["dept_id"])
    cat  = row.get("cat_id_str",  row["cat_id"])
    pct  = float(row["delta_pct"]) * 100

    tag = ""
    if promote_candidate:
        tag = " This SKU is a PROMOTE THIS candidate - strong upward momentum."
    elif row["direction"] == "down":
        tag = " This SKU is a MARKDOWN candidate - demand is falling."

    return {
        "item_id":          item,
        "dept_id":          dept,
        "cat_id":           cat,
        "direction":        row["direction"],
        "delta_pct":        pct,
        "promote_candidate": promote_candidate,
        "focus_line": (
            f"Focus this recommendation on SKU {item} in category {cat}: "
            f"predicted {row['predicted']:.2f} units vs baseline {row['baseline']:.2f} "
            f"({pct:+.1f}%). Trend direction: {row['direction']}." + tag
        ),
    }


def summarize_forecast(
    forecast_df: pd.DataFrame,
    bucket_size: int = BUCKET_SIZE,
    min_baseline: float = MIN_BASELINE,
) -> tuple[str, list[dict]]:
    """Select up to ``bucket_size`` candidates from each of three buckets
    (PROMOTE / RESTOCK / MARKDOWN) and build LLM prompt inputs.

    Expects ``forecast_df`` from src.forecast.serve.forecast_with_names.
    """
    df = forecast_df.copy()
    df = df[df["baseline"].fillna(0) >= min_baseline].dropna(subset=["delta_pct"])

    if df.empty:
        return "No SKUs met the minimum baseline threshold for forecasting.", []

    # delta_pct from serve.py is a fraction; convert to % for thresholds
    df["delta_pct_pct"] = df["delta_pct"] * 100

    promote  = (df[df["delta_pct_pct"] >  PROMOTE_THRESHOLD]
                .sort_values("delta_pct_pct", ascending=False)
                .head(bucket_size))

    restock  = (df[(df["delta_pct_pct"] >= RESTOCK_LOWER) &
                   (df["delta_pct_pct"] <= PROMOTE_THRESHOLD)]
                .sort_values("delta_pct_pct", ascending=False)
                .head(bucket_size))

    markdown = (df[df["delta_pct_pct"] < MARKDOWN_THRESHOLD]
                .sort_values("delta_pct_pct", ascending=True)   # most negative first
                .head(bucket_size))

    seeds: list[dict] = []
    for _, row in promote.iterrows():
        seeds.append(_build_seed(row, promote_candidate=True))
    for _, row in restock.iterrows():
        seeds.append(_build_seed(row, promote_candidate=False))
    for _, row in markdown.iterrows():
        seeds.append(_build_seed(row, promote_candidate=False))

    total = len(seeds)
    summary_lines = [f"Top {total} SKUs selected across PROMOTE / RESTOCK / MARKDOWN buckets:"]
    for s in seeds:
        summary_lines.append(
            f"- {s['item_id']} ({s['cat_id']}, dept {s['dept_id']}): "
            f"delta {s['delta_pct']:+.1f}%, direction: {s['direction']}"
        )

    return "\n".join(summary_lines), seeds
