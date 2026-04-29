import streamlit as st
from src.recommendations.engine import Rec

_CONFIDENCE_STYLE = {
    "High":   ("🟢", "#1a7f3c"),
    "Medium": ("🟡", "#b45309"),
    "Low":    ("🔴", "#9b1c1c"),
}


def render_card(rec: Rec, index: int) -> str | None:
    """Render a single recommendation card. Returns 'accept', 'reject', or None."""
    if rec.flagged:
        color = "#ffe4e4"  # red tint - guard triggered
    elif rec.rec_type == "promote":
        color = "#e6f4ea"  # green tint - strong momentum
    else:
        color = "#f0f4ff"  # blue tint - markdown / restock

    icon, conf_color = _CONFIDENCE_STYLE.get(rec.confidence, ("⚪", "#666"))

    with st.container():
        st.markdown(
            f"<div style='background:{color};padding:12px;border-radius:8px;margin-bottom:8px;'>",
            unsafe_allow_html=True,
        )
        col_title, col_conf = st.columns([4, 1])
        col_title.markdown(f"**[{rec.rec_type.upper()}]** {rec.text}")
        col_conf.markdown(
            f"<div style='text-align:right;color:{conf_color};font-weight:600;'>"
            f"{icon} {rec.confidence} confidence<br>"
            f"<span style='font-size:0.8em;font-weight:400;'>delta {rec.delta_pct:+.1f}%</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if rec.flagged:
            st.warning(f"Guard flagged: {rec.flag_reason}")
        with st.expander("Guard checks", expanded=rec.flagged):
            st.caption(f"Intent:   {rec.intent_check or 'SKIP'}")
            st.caption(f"Numerics: {rec.numeric_check or 'SKIP'}")
        col1, col2 = st.columns(2)
        accepted = col1.button("Accept", key=f"accept_{index}")
        rejected = col2.button("Reject", key=f"reject_{index}")
        st.markdown("</div>", unsafe_allow_html=True)
    if accepted:
        return "accept"
    if rejected:
        return "reject"
    return None
