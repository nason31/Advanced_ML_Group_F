import html as _html
import re

import streamlit as st


def _is_flagged(val) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() == "true"


def _plain(raw: str) -> str:
    """Strip markdown syntax and collapse to a single plain-text line.

    LLM output contains ## headers and ** bold markers. html.escape() alone
    does not neutralise these because Streamlit parses markdown before HTML,
    so # and * must be removed first.
    """
    text = re.sub(r"^#+\s*", "", raw, flags=re.MULTILINE)
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"__?", "", text)
    text = text.replace("\n", " ").replace("\r", "").strip()
    return _html.escape(text[:80])


def render_audit(log: list[dict]) -> None:
    """Render the accept/reject audit trail."""
    st.subheader("Audit Trail")
    if not log:
        st.info("No decisions recorded yet.")
        return
    for entry in reversed(log):
        flagged = _is_flagged(entry.get("guard_flagged", False))
        flag_badge = (
            "<span style='background:#fef9c3;color:#854d0e;padding:1px 6px;"
            "border-radius:3px;font-size:0.75em;font-weight:600;margin-left:6px;'>⚠ flagged</span>"
            if flagged else
            "<span style='background:#dcfce7;color:#166534;padding:1px 6px;"
            "border-radius:3px;font-size:0.75em;font-weight:600;margin-left:6px;'>✓ clean</span>"
        )
        action = entry["action"].upper()
        action_color = "#166534" if action == "ACCEPT" else "#9b1c1c"
        st.markdown(
            f"<div style='padding:3px 0;'>"
            f"<strong style='color:{action_color};'>{action}</strong>"
            f"{flag_badge}"
            f" &mdash; <span style='color:#374151;'>{_plain(entry['text'])}</span>"
            f" <span style='color:#9ca3af;font-size:0.85em;'>({entry['timestamp']})</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
