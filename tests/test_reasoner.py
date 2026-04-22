import os
from unittest.mock import patch, MagicMock
from src.llm.reasoner import reason
from src.llm.guard import check


def test_reason_returns_string():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Markdown item #5 by 20%.")]
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("src.llm.reasoner.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            result = reason("Sales down 5% WoW.", ["Campaign A drove +10% in Q3."])
    assert isinstance(result, str)
    assert len(result) > 0


def test_guard_no_flag_when_consistent():
    rec = {"text": "Sales trending up", "rec_type": "markdown"}
    data = {"direction": "up", "change_pct": 5.0}
    result = check(rec, data)
    assert "flagged" in result


def test_guard_flags_markdown_on_uptrend():
    rec = {"text": "Apply markdown to clear inventory", "rec_type": "markdown"}
    data = {"direction": "up", "change_pct": 8.0}
    result = check(rec, data)
    assert result["flagged"] is True


def test_guard_flags_restock_on_downtrend():
    rec = {"text": "Restock item #7", "rec_type": "restock"}
    data = {"direction": "down", "change_pct": -3.0}
    result = check(rec, data)
    assert result["flagged"] is True
