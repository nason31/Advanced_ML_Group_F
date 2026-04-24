"""Train per-store LightGBM baselines and persist artifacts for serve-time use.

Run: python scripts/train_forecast.py

Produces, for each store in STORES:
    data/processed/model_{store}.pkl        - trained LightGBM booster
    data/processed/features_{store}.parquet - tail of feature matrix for inference
    data/processed/idmap_{store}.parquet    - id -> human-readable item/dept/cat strings

Also prints validation WRMSSE per store (last 28 days held out).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np

from src.data.loader import load_m5
from src.data.features import build_features
from src.forecast.model import train, predict
from src.forecast.evaluate import wrmsse

STORES = ["CA_1", "CA_2", "TX_1"]

FEATURE_COLS = [
    "item_id", "dept_id", "cat_id",
    "wday", "month", "year",
    "snap_CA", "snap_TX", "snap_WI",
    "sell_price",
    "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_28",
]

TAIL_DAYS = 60  # keeps enough history for 28-day lags plus a serving window


def _build_idmap(raw_sales, store: str):
    """id -> item_id_str/dept_id_str/cat_id_str lookup, recovered from raw sales."""
    cols = ["id", "item_id", "dept_id", "cat_id"]
    return (
        raw_sales.loc[raw_sales["store_id"] == store, cols]
        .drop_duplicates()
        .rename(columns={"item_id": "item_id_str", "dept_id": "dept_id_str", "cat_id": "cat_id_str"})
        .reset_index(drop=True)
    )


def main() -> None:
    data_raw = Path("data/raw")
    data_out = Path("data/processed")
    data_out.mkdir(parents=True, exist_ok=True)

    dfs = load_m5(data_raw)
    print(
        f"Loaded M5: sales={dfs['sales'].shape}, "
        f"calendar={dfs['calendar'].shape}, sell_prices={dfs['sell_prices'].shape}"
    )

    for store in STORES:
        print(f"\n=== Training {store} ===")
        feat = build_features(dfs, store=store)
        feat = feat.dropna(subset=["sell_price"]).reset_index(drop=True)

        max_day = int(feat["day_num"].max())
        val_cutoff = max_day - 28
        train_df = feat[feat["day_num"] <= val_cutoff]
        val_df = feat[feat["day_num"] > val_cutoff]
        print(f"train rows={len(train_df)}, val rows={len(val_df)}, max day_num={max_day}")

        X_train = train_df[FEATURE_COLS].to_numpy()
        y_train = train_df["sales"].to_numpy()
        X_val = val_df[FEATURE_COLS].to_numpy()
        y_val = val_df["sales"].to_numpy()

        model = train(X_train, y_train)
        preds = predict(model, X_val)
        score = wrmsse(y_val, preds, np.ones_like(y_val, dtype=float))
        print(f"{store} val WRMSSE: {score:.4f}")

        tail = feat[feat["day_num"] > (max_day - TAIL_DAYS)].reset_index(drop=True)
        idmap = _build_idmap(dfs["sales"], store)

        joblib.dump(model, data_out / f"model_{store}.pkl")
        tail.to_parquet(data_out / f"features_{store}.parquet")
        idmap.to_parquet(data_out / f"idmap_{store}.parquet")
        print(
            f"Saved model_{store}.pkl, features_{store}.parquet ({len(tail)} rows), "
            f"idmap_{store}.parquet ({len(idmap)} ids)"
        )


if __name__ == "__main__":
    main()
