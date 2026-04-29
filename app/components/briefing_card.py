import streamlit as st
from src.recommendations.engine import Rec


def render_card(rec: Rec, index: int) -> str | None:
    """Render a single recommendation card. Returns 'accept', 'reject', or None."""
    if rec.flagged:
        color = "#ffe4e4"  # red tint - guard triggered
    elif rec.rec_type == "promote":
        color = "#e6f4ea"  # green tint - strong momentum
    else:
        color = "#f0f4ff"  # blue tint - markdown / restock
    with st.container():
        st.markdown(
            f"<div style='background:{color};padding:12px;border-radius:8px;margin-bottom:8px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**[{rec.rec_type.upper()}]** {rec.text}")
        if rec.flagged:
            st.warning(f"Guard flagged: {rec.flag_reason}")
        col1, col2 = st.columns(2)
        accepted = col1.button("Accept", key=f"accept_{index}")
        rejected = col2.button("Reject", key=f"reject_{index}")
        st.markdown("</div>", unsafe_allow_html=True)
    if accepted:
        return "accept"
    if rejected:
        return "reject"
    return None
