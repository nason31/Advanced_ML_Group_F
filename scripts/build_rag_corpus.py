"""Derive RAG context documents from M5 and ingest them into ChromaDB.

Run: python scripts/build_rag_corpus.py

For each store in STORES, extracts a handful of short natural-language context
blurbs covering:
  - SNAP-day sales lift per category
  - Top event-day effects (Super Bowl, Easter, Christmas, etc.)
  - Weekday peak per category
  - Price-drop elasticity per department
  - Year-over-year category movement

Writes each blurb as a .txt file under data/rag_source/ and calls
src.rag.ingest.ingest_docs() to embed them in the existing collection at
data/vector_store/. Re-running clears the source directory first, so the
corpus is deterministic for a given M5 snapshot.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.data.loader import load_m5
from src.rag.ingest import ingest_docs

STORES = ["CA_1", "CA_2", "TX_1"]
SOURCE_DIR = Path("data/rag_source")
VECTOR_DIR = Path("data/vector_store")

STATE_SNAP_COL = {
    "CA_1": "snap_CA", "CA_2": "snap_CA", "CA_3": "snap_CA", "CA_4": "snap_CA",
    "TX_1": "snap_TX", "TX_2": "snap_TX", "TX_3": "snap_TX",
    "WI_1": "snap_WI", "WI_2": "snap_WI", "WI_3": "snap_WI",
}
WDAY_NAMES = {
    1: "Saturday", 2: "Sunday", 3: "Monday", 4: "Tuesday",
    5: "Wednesday", 6: "Thursday", 7: "Friday",
}


def _long_for_store(sales: pd.DataFrame, calendar: pd.DataFrame, store: str) -> pd.DataFrame:
    """One row per (item, day) for a single store, with calendar fields joined."""
    s = sales[sales["store_id"] == store]
    day_cols = [c for c in s.columns if c.startswith("d_")]
    long = s.melt(
        id_vars=["id", "item_id", "dept_id", "cat_id", "store_id"],
        value_vars=day_cols,
        var_name="d",
        value_name="sales",
    )
    cal_keep = [
        "d", "wday", "month", "year", "wm_yr_wk",
        "event_name_1", "snap_CA", "snap_TX", "snap_WI",
    ]
    return long.merge(calendar[cal_keep], on="d", how="left")


def snap_lift_blurbs(long_df: pd.DataFrame, store: str) -> list[tuple[str, str]]:
    snap_col = STATE_SNAP_COL[store]
    grouped = (
        long_df.groupby(["cat_id", snap_col])["sales"]
        .mean()
        .unstack(snap_col)
    )
    if 0 not in grouped.columns or 1 not in grouped.columns:
        return []
    grouped["lift_pct"] = (grouped[1] - grouped[0]) / grouped[0] * 100

    out = []
    for cat, row in grouped.iterrows():
        out.append((
            f"{store}_{cat}_snap",
            f"In {store}, the {cat} category averages {row[1]:.2f} units/day on SNAP days "
            f"versus {row[0]:.2f} units/day on non-SNAP days ({row['lift_pct']:+.1f}%). "
            "SNAP benefit disbursement days concentrate grocery demand and should be "
            "treated as structured demand shocks rather than random variance."
        ))
    return out


def event_lift_blurbs(long_df: pd.DataFrame, store: str, top_n: int = 3) -> list[tuple[str, str]]:
    base_mean = long_df["sales"].mean()
    evt = long_df[long_df["event_name_1"].notna()]
    stats = evt.groupby("event_name_1")["sales"].agg(["mean", "count"])
    stats = stats[stats["count"] >= 5]
    if stats.empty:
        return []
    stats["lift_pct"] = (stats["mean"] - base_mean) / base_mean * 100
    top = stats.reindex(stats["lift_pct"].abs().sort_values(ascending=False).index).head(top_n)

    out = []
    for name, row in top.iterrows():
        safe = str(name).replace(" ", "_").replace("'", "")
        out.append((
            f"{store}_event_{safe}",
            f"In {store}, {name} produces average sales of {row['mean']:.2f} units/day "
            f"({row['lift_pct']:+.1f}% vs the {base_mean:.2f} all-day baseline, "
            f"n={int(row['count'])} item-day observations). Factor this event when it "
            "falls within the forecast horizon."
        ))
    return out


def weekday_blurbs(long_df: pd.DataFrame, store: str) -> list[tuple[str, str]]:
    out = []
    for cat, grp in long_df.groupby("cat_id"):
        by_wday = grp.groupby("wday")["sales"].mean()
        if by_wday.empty or by_wday.min() == 0:
            continue
        peak_day = int(by_wday.idxmax())
        peak_mean = by_wday.max()
        trough_mean = by_wday.min()
        spread = (peak_mean - trough_mean) / trough_mean * 100
        out.append((
            f"{store}_{cat}_wday",
            f"In {store}, {cat} sales peak on {WDAY_NAMES[peak_day]} at {peak_mean:.2f} units/day "
            f"(trough {trough_mean:.2f}, weekly spread +{spread:.1f}%). "
            "Use this to time weekly promotions and replenishment windows."
        ))
    return out


def price_elasticity_blurbs(
    long_df: pd.DataFrame,
    sell_prices: pd.DataFrame,
    store: str,
    threshold_pct: float = 10.0,
) -> list[tuple[str, str]]:
    weekly = (
        long_df.groupby(["item_id", "dept_id", "wm_yr_wk"])["sales"]
        .sum()
        .reset_index()
    )
    prices = sell_prices[sell_prices["store_id"] == store].sort_values(["item_id", "wm_yr_wk"]).copy()
    prices["price_lag"] = prices.groupby("item_id")["sell_price"].shift(1)
    prices["pct_change"] = (prices["sell_price"] - prices["price_lag"]) / prices["price_lag"] * 100
    joined = weekly.merge(
        prices[["item_id", "wm_yr_wk", "pct_change"]],
        on=["item_id", "wm_yr_wk"],
        how="left",
    )
    joined["is_drop"] = joined["pct_change"] <= -threshold_pct

    out = []
    for dept, grp in joined.groupby("dept_id"):
        drop_mean = grp.loc[grp["is_drop"], "sales"].mean()
        normal_mean = grp.loc[~grp["is_drop"], "sales"].mean()
        if pd.isna(drop_mean) or pd.isna(normal_mean) or normal_mean == 0:
            continue
        lift = (drop_mean - normal_mean) / normal_mean * 100
        n_drops = int(grp["is_drop"].sum())
        out.append((
            f"{store}_{dept}_price",
            f"In {store}, {dept} SKUs average {drop_mean:.2f} weekly units in weeks with a "
            f">={threshold_pct:.0f}% price drop vs {normal_mean:.2f} at stable prices "
            f"({lift:+.1f}%, n={n_drops} drop weeks observed). Use this when sizing markdown uplift."
        ))
    return out


def yoy_blurbs(long_df: pd.DataFrame, store: str) -> list[tuple[str, str]]:
    yearly = long_df.groupby(["cat_id", "year"])["sales"].sum().reset_index()
    years = sorted(yearly["year"].dropna().unique())
    if len(years) < 3:
        return []
    # Use the last two complete years (the most recent year in M5 is typically partial).
    y_now, y_prev = int(years[-2]), int(years[-3])
    out = []
    for cat, grp in yearly.groupby("cat_id"):
        now = float(grp.loc[grp["year"] == y_now, "sales"].sum())
        prev = float(grp.loc[grp["year"] == y_prev, "sales"].sum())
        if prev == 0:
            continue
        lift = (now - prev) / prev * 100
        out.append((
            f"{store}_{cat}_yoy",
            f"In {store}, annual {cat} sales moved {lift:+.1f}% from {y_prev} "
            f"({prev:.0f} units) to {y_now} ({now:.0f} units). "
            "Year-on-year trend anchors baseline expectations for this category."
        ))
    return out


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    # Wipe prior blurbs so the corpus reflects only the current M5 snapshot.
    for old in SOURCE_DIR.glob("*.txt"):
        old.unlink()

    dfs = load_m5(Path("data/raw"))
    print(f"Loaded M5: sales={dfs['sales'].shape}, calendar={dfs['calendar'].shape}")

    all_blurbs: list[tuple[str, str]] = []
    for store in STORES:
        print(f"\n=== {store} ===")
        long_df = _long_for_store(dfs["sales"], dfs["calendar"], store)

        store_blurbs: list[tuple[str, str]] = []
        store_blurbs += snap_lift_blurbs(long_df, store)
        store_blurbs += event_lift_blurbs(long_df, store)
        store_blurbs += weekday_blurbs(long_df, store)
        store_blurbs += price_elasticity_blurbs(long_df, dfs["sell_prices"], store)
        store_blurbs += yoy_blurbs(long_df, store)

        print(f"  {store}: {len(store_blurbs)} blurbs")
        all_blurbs.extend(store_blurbs)

    paths: list[Path] = []
    for name, text in all_blurbs:
        path = SOURCE_DIR / f"{name}.txt"
        path.write_text(text)
        paths.append(path)
    print(f"\nWrote {len(paths)} context docs to {SOURCE_DIR}/")

    ingest_docs(paths, VECTOR_DIR)
    print(f"Ingested into ChromaDB at {VECTOR_DIR}/")


if __name__ == "__main__":
    main()
