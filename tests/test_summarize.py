"""Unit tests for src/recommendations/summarize.py."""
import pandas as pd

from src.recommendations.summarize import summarize_forecast


def _toy_forecast_df() -> pd.DataFrame:
    """Five SKUs: two below min_baseline, three valid with mixed directions."""
    return pd.DataFrame([
        # below baseline floor, should be filtered out
        {"id": "a1", "item_id": 1, "dept_id": 1, "cat_id": 1,
         "item_id_str": "FOODS_3_low", "dept_id_str": "FOODS_3", "cat_id_str": "FOODS",
         "predicted": 0.05, "baseline": 0.1, "delta_pct": -0.50, "direction": "down"},
        {"id": "a2", "item_id": 2, "dept_id": 1, "cat_id": 1,
         "item_id_str": "HOBBIES_1_low", "dept_id_str": "HOBBIES_1", "cat_id_str": "HOBBIES",
         "predicted": 0.2, "baseline": 0.5, "delta_pct": -0.60, "direction": "down"},
        # above baseline, biggest absolute delta (up)
        {"id": "a3", "item_id": 3, "dept_id": 2, "cat_id": 1,
         "item_id_str": "FOODS_3_827", "dept_id_str": "FOODS_3", "cat_id_str": "FOODS",
         "predicted": 4.2, "baseline": 3.0, "delta_pct": 0.40, "direction": "up"},
        # above baseline, second biggest (down)
        {"id": "a4", "item_id": 4, "dept_id": 3, "cat_id": 2,
         "item_id_str": "HOBBIES_1_234", "dept_id_str": "HOBBIES_1", "cat_id_str": "HOBBIES",
         "predicted": 1.4, "baseline": 2.0, "delta_pct": -0.30, "direction": "down"},
        # above baseline, smallest delta (up)
        {"id": "a5", "item_id": 5, "dept_id": 4, "cat_id": 3,
         "item_id_str": "HOUSEHOLD_2_145", "dept_id_str": "HOUSEHOLD_2", "cat_id_str": "HOUSEHOLD",
         "predicted": 7.7, "baseline": 7.0, "delta_pct": 0.10, "direction": "up"},
    ])


def test_summarize_returns_tuple_of_text_and_seeds():
    summary, seeds = summarize_forecast(_toy_forecast_df(), top_k=3)
    assert isinstance(summary, str)
    assert isinstance(seeds, list)


def test_summarize_filters_below_min_baseline():
    """SKUs with baseline < 1.0 should not appear in seeds regardless of delta."""
    _, seeds = summarize_forecast(_toy_forecast_df(), top_k=3, min_baseline=1.0)
    seed_items = {s["item_id"] for s in seeds}
    assert "FOODS_3_low" not in seed_items
    assert "HOBBIES_1_low" not in seed_items


def test_summarize_ranks_by_absolute_delta():
    """Top-3 order should be 40%, -30%, 10% by absolute magnitude."""
    _, seeds = summarize_forecast(_toy_forecast_df(), top_k=3)
    assert [s["item_id"] for s in seeds] == ["FOODS_3_827", "HOBBIES_1_234", "HOUSEHOLD_2_145"]
    assert [s["direction"] for s in seeds] == ["up", "down", "up"]


def test_summarize_top_k_limits_output():
    _, seeds = summarize_forecast(_toy_forecast_df(), top_k=2)
    assert len(seeds) == 2


def test_summary_text_cites_human_readable_skus():
    summary, _ = summarize_forecast(_toy_forecast_df(), top_k=3)
    assert "FOODS_3_827" in summary
    assert "HOBBIES_1_234" in summary


def test_seed_contains_guard_check_fields():
    """Each seed must carry the 'direction' key that src.llm.guard.check() reads."""
    _, seeds = summarize_forecast(_toy_forecast_df(), top_k=3)
    for seed in seeds:
        assert "direction" in seed
        assert seed["direction"] in {"up", "down"}
        assert "focus_line" in seed
        assert seed["item_id"] in seed["focus_line"]


def test_summarize_empty_when_all_below_baseline():
    df = _toy_forecast_df().head(2)  # only the two low-baseline rows
    summary, seeds = summarize_forecast(df, top_k=3, min_baseline=1.0)
    assert seeds == []
    assert "No SKUs" in summary
