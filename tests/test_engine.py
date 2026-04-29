"""Tests for src/recommendations/engine.py.

The live pipeline calls out to the Anthropic API, ChromaDB, and a trained
LightGBM model on disk. Unit tests monkeypatch forecast_with_names, retrieve,
and reason so the orchestrator can be validated without those dependencies.
"""
from pathlib import Path

import pandas as pd

from src.recommendations import engine as engine_mod
from src.recommendations.engine import Rec, run_pipeline


def test_rec_dataclass_fields():
    rec = Rec(rec_type="markdown", text="Mark down item #3.", flagged=False, flag_reason="")
    assert rec.rec_type == "markdown"
    assert rec.flagged is False
    assert rec.text == "Mark down item #3."


def _toy_forecast_with_names(store_id: str, date: str, data_dir: Path) -> pd.DataFrame:
    """Three SKUs above min_baseline: one up, one down, one up."""
    return pd.DataFrame([
        {"id": "a3", "item_id": 3, "dept_id": 2, "cat_id": 1,
         "item_id_str": "FOODS_3_827", "dept_id_str": "FOODS_3", "cat_id_str": "FOODS",
         "predicted": 4.2, "baseline": 3.0, "delta_pct": 0.40, "direction": "up"},
        {"id": "a4", "item_id": 4, "dept_id": 3, "cat_id": 2,
         "item_id_str": "HOBBIES_1_234", "dept_id_str": "HOBBIES_1", "cat_id_str": "HOBBIES",
         "predicted": 1.4, "baseline": 2.0, "delta_pct": -0.30, "direction": "down"},
        {"id": "a5", "item_id": 5, "dept_id": 4, "cat_id": 3,
         "item_id_str": "HOUSEHOLD_2_145", "dept_id_str": "HOUSEHOLD_2", "cat_id_str": "HOUSEHOLD",
         "predicted": 7.7, "baseline": 7.0, "delta_pct": 0.10, "direction": "up"},
    ])


def _fake_retrieve(query, store_dir, k=3):
    return [
        f"Context stub for query='{query}'",
        "FOODS peak on Saturday in CA_1 historically.",
    ]


def test_run_pipeline_returns_three_recs_with_expected_shapes(monkeypatch, tmp_path):
    monkeypatch.setattr(engine_mod, "forecast_with_names", _toy_forecast_with_names)
    monkeypatch.setattr(engine_mod, "retrieve", _fake_retrieve)
    monkeypatch.setattr(engine_mod, "reason",
                        lambda forecast_summary, context_docs: "Restock this SKU; evidence: forecast +40%.")

    recs = run_pipeline("CA_1", "2024-01-01", tmp_path, tmp_path)
    assert len(recs) == 3
    assert all(isinstance(r, Rec) for r in recs)

    # Mapping from direction to rec_type: up -> restock, down -> markdown.
    rec_types = [r.rec_type for r in recs]
    assert rec_types == ["restock", "markdown", "restock"]


def test_run_pipeline_guard_flags_contradictory_reasoner_output(monkeypatch, tmp_path):
    """If the LLM returns 'markdown' text for an uptrending SKU, guard must flag it."""
    monkeypatch.setattr(engine_mod, "forecast_with_names", _toy_forecast_with_names)
    monkeypatch.setattr(engine_mod, "retrieve", _fake_retrieve)
    # Always recommend a markdown, regardless of the actual trend.
    monkeypatch.setattr(engine_mod, "reason",
                        lambda forecast_summary, context_docs: "Apply markdown to clear stock.")

    recs = run_pipeline("CA_1", "2024-01-01", tmp_path, tmp_path)
    # Uptrending SKUs (1st and 3rd) should be flagged; downtrending 2nd should not.
    assert recs[0].flagged is True
    assert recs[1].flagged is False
    assert recs[2].flagged is True
    assert "Markdown" in recs[0].flag_reason or "markdown" in recs[0].flag_reason.lower()


def test_run_pipeline_no_seeds_returns_empty(monkeypatch, tmp_path):
    """When no SKUs survive the baseline filter, pipeline returns an empty list."""
    def _empty_forecast(store_id, date, data_dir):
        return pd.DataFrame(columns=[
            "id", "item_id", "dept_id", "cat_id",
            "item_id_str", "dept_id_str", "cat_id_str",
            "predicted", "baseline", "delta_pct", "direction",
        ])

    monkeypatch.setattr(engine_mod, "forecast_with_names", _empty_forecast)
    # retrieve and reason should never be called; stub anyway.
    monkeypatch.setattr(engine_mod, "retrieve", _fake_retrieve)
    monkeypatch.setattr(engine_mod, "reason", lambda **_: "unused")

    recs = run_pipeline("CA_1", "2024-01-01", tmp_path, tmp_path)
    assert recs == []
