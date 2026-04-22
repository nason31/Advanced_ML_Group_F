from src.recommendations.engine import Rec, run_pipeline
from pathlib import Path


def test_rec_dataclass_fields():
    rec = Rec(rec_type="markdown", text="Mark down item #3.", flagged=False, flag_reason="")
    assert rec.rec_type == "markdown"
    assert rec.flagged is False


def test_run_pipeline_returns_list(tmp_path):
    result = run_pipeline("CA_1", "2024-01-01", tmp_path, tmp_path)
    assert isinstance(result, list)
