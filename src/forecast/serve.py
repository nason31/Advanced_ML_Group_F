"""Serve-time adapter: load a persisted LightGBM booster and score the latest features.

Called from src/recommendations/engine.py. Pure adapter, no training.
"""
from functools import lru_cache
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


@lru_cache(maxsize=8)
def load_model(store_id: str, data_dir: Path) -> lgb.Booster:
    path = Path(data_dir) / f"model_{store_id}.pkl"
    return joblib.load(path)


@lru_cache(maxsize=8)
def _load_features(store_id: str, data_dir: Path) -> pd.DataFrame:
    return pd.read_parquet(Path(data_dir) / f"features_{store_id}.parquet")


@lru_cache(maxsize=8)
def _load_idmap(store_id: str, data_dir: Path) -> pd.DataFrame:
    return pd.read_parquet(Path(data_dir) / f"idmap_{store_id}.parquet")


def _date_to_day_num(date_str: str, min_day: int, max_day: int) -> int:
    """Map any calendar date into the available M5 day_num window.

    M5 data covers a fixed historical range; any user-selected date is mapped
    cyclically into that window so different dates produce different forecasts.
    """
    from datetime import date as _date
    try:
        d = _date.fromisoformat(str(date_str))
    except ValueError:
        return max_day
    span = max_day - min_day + 1
    return min_day + (d.toordinal() % span)


def forecast_store(
    model: lgb.Booster,
    features_df: pd.DataFrame,
    store_id: str,
    date: str,
    horizon: int = 7,
) -> pd.DataFrame:
    """Predict next-period sales for every SKU in ``store_id``.

    Maps the requested date into the available M5 day_num window, then picks
    the most recent feature row per item at or before that day. Returns one row
    per item with columns: id, item_id, dept_id, cat_id, predicted, baseline,
    delta_pct, direction.
    """
    df = features_df.copy()
    min_day = int(df["day_num"].min())
    max_day = int(df["day_num"].max())
    target_day = _date_to_day_num(date, min_day, max_day)

    df_window = df[df["day_num"] <= target_day]
    if df_window.empty:
        df_window = df
    latest = df_window.sort_values("day_num").groupby("id", as_index=False).tail(1).reset_index(drop=True)

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
