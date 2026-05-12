import html as _html

import streamlit as st


def _is_flagged(val) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() == "true"


def render_audit(log: list[dict]) -> None:
    """Render the accept/reject audit trail."""
    st.subheader("Audit Trail")
    if not log:
        st.info("No decisions recorded yet.")
        return
    for entry in reversed(log):
        flagged = _is_flagged(entry.get("guard_flagged", False))
        flag_html = (
            "<span style='background:#fef9c3;color:#854d0e;padding:1px 6px;"
            "border-radius:3px;font-size:0.75em;font-weight:600;margin-left:6px;'>⚠ flagged</span>"
            if flagged else
            "<span style='background:#dcfce7;color:#166534;padding:1px 6px;"
            "border-radius:3px;font-size:0.75em;font-weight:600;margin-left:6px;'>✓ clean</span>"
        )
        action = entry["action"].upper()
        action_color = "#166534" if action == "ACCEPT" else "#9b1c1c"
        # Escape text so LLM markdown (##, **, newlines) cannot break the HTML layout
        clean_text = _html.escape(entry["text"][:80].replace("\n", " ").replace("\r", ""))
        st.markdown(
            f"<div style='padding:3px 0;'>"
            f"<strong style='color:{action_color};'>{action}</strong>"
            f"{flag_html}"
            f" &mdash; <span style='color:#374151;'>{clean_text}</span>"
            f" <span style='color:#9ca3af;font-size:0.85em;'>({entry['timestamp']})</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
