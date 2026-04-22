from pathlib import Path
import pandas as pd


def load_m5(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load M5 CSVs from data_dir. Returns dict keyed by table name."""
    data_dir = Path(data_dir)
    sales = pd.read_csv(data_dir / "sales_train_evaluation.csv")
    return {"sales": sales}
