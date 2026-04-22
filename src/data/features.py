import pandas as pd


def build_features(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Transform raw M5 tables into a flat feature matrix for LightGBM.

    Placeholder — returns sales DataFrame unchanged until feature
    engineering is implemented.
    """
    return dfs["sales"]
