from pathlib import Path
from src.data.loader import load_m5


def test_load_m5_returns_expected_keys(tmp_path):
    (tmp_path / "sales_train_evaluation.csv").write_text(
        "id,item_id\nFOODS_1_001_CA_1_evaluation,FOODS_1_001\n"
    )
    result = load_m5(tmp_path)
    assert "sales" in result
