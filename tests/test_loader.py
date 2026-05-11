from pathlib import Path
from src.data.loader import load_m5


def test_load_m5_returns_expected_keys(tmp_path):
    (tmp_path / "sales_train_evaluation.csv").write_text(
        "id,item_id\nFOODS_1_001_CA_1_evaluation,FOODS_1_001\n"
    )
    (tmp_path / "calendar.csv").write_text("d,wm_yr_wk\nd_1,11101\n")
    (tmp_path / "sell_prices.csv").write_text("store_id,item_id,wm_yr_wk,sell_price\nCA_1,FOODS_1_001,11101,1.99\n")
    result = load_m5(tmp_path)
    assert set(result.keys()) == {"sales", "calendar", "sell_prices"}
