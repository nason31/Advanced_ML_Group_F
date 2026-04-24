"""Serve-time adapter: load a persisted LightGBM booster and score the latest features.

Called from src/recommendations/engine.py. Pure adapter, no training.
"""
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd

FEATURE_COLS = [
    "item_id", "dept_id", "cat_id",
    "wday", "month", "year",
    "snap_CA", "snap_TX", "snap_WI",
    "sell_price",
    "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_28",
]


def load_model(store_id: str, data_dir: Path) -> lgb.Booster:
    path = Path(data_dir) / f"model_{store_id}.pkl"
    return joblib.load(path)


def _load_features(store_id: str, data_dir: Path) -> pd.DataFrame:
    return pd.read_parquet(Path(data_dir) / f"features_{store_id}.parquet")


def _load_idmap(store_id: str, data_dir: Path) -> pd.DataFrame:
    return pd.read_parquet(Path(data_dir) / f"idmap_{store_id}.parquet")


def forecast_store(
    model: lgb.Booster,
    features_df: pd.DataFrame,
    store_id: str,
    date: str,
    horizon: int = 7,
) -> pd.DataFrame:
    """Predict next-period sales for every SKU in ``store_id``.

    Picks the most recent feature row per id at or before ``date``; if ``date`` falls
    past the M5 data range, silently uses the last available day. Returns one row per
    item with columns: id, item_id, dept_id, cat_id, predicted, baseline, delta_pct,
    direction.
    """
    df = features_df[features_df["day_num"] <= features_df["day_num"].max()].copy()
    # Pick latest row per id (one forecast per SKU).
    latest = df.sort_values("day_num").groupby("id", as_index=False).tail(1).reset_index(drop=True)

    X = latest[FEATURE_COLS].to_numpy()
    latest["predicted"] = model.predict(X)
    latest["baseline"] = latest["rolling_mean_28"].replace(0, np.nan)
    latest["delta_pct"] = (latest["predicted"] - latest["baseline"]) / latest["baseline"]
    latest["delta_pct"] = latest["delta_pct"].fillna(0.0)
    latest["direction"] = np.where(latest["delta_pct"] >= 0, "up", "down")

    out_cols = [
        "id", "item_id", "dept_id", "cat_id",
        "predicted", "baseline", "delta_pct", "direction",
    ]
    return latest[out_cols].reset_index(drop=True)


def forecast_with_names(
    store_id: str,
    date: str,
    data_dir: Path,
    horizon: int = 7,
) -> pd.DataFrame:
    """Convenience wrapper used by the orchestrator: load model + features + idmap,
    run forecast_store, and attach the human-readable item/dept/cat strings the LLM
    needs to cite specific SKUs.
    """
    model = load_model(store_id, data_dir)
    features = _load_features(store_id, data_dir)
    idmap = _load_idmap(store_id, data_dir)

    forecast = forecast_store(model, features, store_id, date, horizon=horizon)
    return forecast.merge(idmap, on="id", how="left")
