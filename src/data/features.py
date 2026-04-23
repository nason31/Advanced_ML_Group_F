import pandas as pd


def build_features(dfs: dict[str, pd.DataFrame], store: str = "CA_1") -> pd.DataFrame:
    sales = dfs["sales"][dfs["sales"]["store_id"] == store].copy()
    calendar = dfs["calendar"]
    sell_prices = dfs["sell_prices"]

    # Melt wide -> long (one row per item-day)
    id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    day_cols = [c for c in sales.columns if c.startswith("d_")]
    df = sales.melt(id_vars=id_cols, value_vars=day_cols, var_name="d", value_name="sales")

    # Join calendar features
    cal_keep = ["d", "wm_yr_wk", "wday", "month", "year", "snap_CA", "snap_TX", "snap_WI"]
    df = df.merge(calendar[cal_keep], on="d", how="left")

    # Join price
    df = df.merge(sell_prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")

    # Sort for time-ordered lag computation
    df["day_num"] = df["d"].str[2:].astype(int)
    df = df.sort_values(["id", "day_num"]).reset_index(drop=True)

    # Lag features (strongest M5 predictors)
    g = df.groupby("id")["sales"]
    for lag in [7, 14, 28]:
        df[f"lag_{lag}"] = g.shift(lag)

    # Rolling means shifted by 28 days to prevent leakage
    df["rolling_mean_7"]  = g.transform(lambda x: x.shift(28).rolling(7).mean())
    df["rolling_mean_28"] = g.transform(lambda x: x.shift(28).rolling(28).mean())

    # Drop rows without enough history
    df = df.dropna(subset=["lag_7", "lag_14", "lag_28"]).reset_index(drop=True)

    # Encode categoricals for LightGBM
    for col in ["item_id", "dept_id", "cat_id"]:
        df[col] = df[col].astype("category").cat.codes

    return df
