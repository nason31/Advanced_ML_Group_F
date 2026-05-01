import re

import streamlit as st
from src.data.product_names import get_product_name
from src.recommendations.engine import Rec

_CONFIDENCE_STYLE = {
    "High":   ("🟢", "#1a7f3c"),
    "Medium": ("🟡", "#b45309"),
    "Low":    ("🔴", "#9b1c1c"),
}

_TYPE_STYLE = {
    "promote":  ("#dcfce7", "#166534", "PROMOTE"),
    "restock":  ("#dbeafe", "#1e40af", "RESTOCK"),
    "markdown": ("#fef9c3", "#854d0e", "MARKDOWN"),
}


def _extract_sku(text: str) -> str:
    match = re.search(r"[A-Z]+_\d+_\d+", text)
    return match.group(0) if match else "-"


def _clean_text(text: str) -> str:
    """Strip leading markdown headers and type-prefix boilerplate from LLM output."""
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        line = re.sub(r"^#+\s*", "", line)
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def render_table(recs: list[Rec]) -> list[tuple[int, str]]:
    """Render all recs as a compact scannable table. Returns list of (index, action) tuples."""
    actions: list[tuple[int, str]] = []

    # Table header
    h = st.columns([0.8, 1.2, 1.6, 1.0, 0.7, 0.6, 0.6])
    for col, label in zip(h, ["Type", "SKU", "Product", "Confidence", "Delta", "", ""]):
        col.markdown(f"<span style='font-size:0.8em;font-weight:600;color:#666;text-transform:uppercase;letter-spacing:0.05em;'>{label}</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:4px 0 8px 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)

    for i, rec in enumerate(recs):
        sku = _extract_sku(rec.text)
        product_name = get_product_name(sku)
        icon, _ = _CONFIDENCE_STYLE.get(rec.confidence, ("⚪", "#666"))
        bg, fg, label = _TYPE_STYLE.get(rec.rec_type, ("#f3f4f6", "#374151", rec.rec_type.upper()))

        cols = st.columns([0.8, 1.2, 1.6, 1.0, 0.7, 0.6, 0.6])

        cols[0].markdown(
            f"<span style='background:{bg};color:{fg};padding:2px 8px;border-radius:4px;"
            f"font-size:0.78em;font-weight:700;white-space:nowrap;'>{label}</span>",
            unsafe_allow_html=True,
        )
        cols[1].markdown(f"`{sku}`")
        cols[2].markdown(f"{product_name}")
        cols[3].markdown(f"{icon} **{rec.confidence}**")
        cols[4].markdown(
            f"<span style='font-weight:700;color:{'#166534' if rec.delta_pct > 0 else '#9b1c1c'};'>"
            f"{rec.delta_pct:+.1f}%</span>",
            unsafe_allow_html=True,
        )
        if cols[5].button("Accept", key=f"accept_{i}", type="primary", use_container_width=True):
            actions.append((i, "accept"))
        if cols[6].button("Reject", key=f"reject_{i}", use_container_width=True):
            actions.append((i, "reject"))

        with st.expander(f"Details - {product_name} ({sku})", expanded=False):
            if rec.flagged:
                st.warning(f"Guard flagged: {rec.flag_reason}")
            st.markdown(_clean_text(rec.text))
            st.divider()
            dcol1, dcol2 = st.columns(2)
            dcol1.caption(f"**Intent check:** {rec.intent_check or 'n/a'}")
            dcol2.caption(f"**Numeric check:** {rec.numeric_check or 'n/a'}")

        st.markdown("<hr style='margin:6px 0;border-color:#f3f4f6;'>", unsafe_allow_html=True)

    return actions
