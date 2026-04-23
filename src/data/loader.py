from pathlib import Path
import pandas as pd


def load_m5(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    data_dir = Path(data_dir)
    return {
        "sales":      pd.read_csv(data_dir / "sales_train_evaluation.csv"),
        "calendar":   pd.read_csv(data_dir / "calendar.csv"),
        "sell_prices": pd.read_csv(data_dir / "sell_prices.csv"),
    }
