import re

import streamlit as st
from src.data.product_names import get_dept_name, get_product_name
from src.recommendations.engine import Rec

_CONFIDENCE_STYLE = {
    "Strong":   ("#dcfce7", "#166534"),
    "Moderate": ("#fef9c3", "#854d0e"),
    "Weak":     ("#fee2e2", "#9b1c1c"),
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
    h = st.columns([0.6, 1.05, 1.1, 0.85, 0.92, 0.76, 0.9, 0.8, 0.8])
    for col, label in zip(h, ["Type", "SKU", "Product", "Department", "Signal", "Delta", "Action", "", ""]):
        col.markdown(f"<span style='font-size:0.8em;font-weight:600;color:#666;text-transform:uppercase;letter-spacing:0.05em;'>{label}</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:4px 0 8px 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)

    for i, rec in enumerate(recs):
        sku = rec.sku or _extract_sku(rec.text)
        product_name = get_product_name(sku)
        dept_name = get_dept_name(sku)
        conf_bg, conf_fg = _CONFIDENCE_STYLE.get(rec.confidence, ("#f3f4f6", "#374151"))
        bg, fg, label = _TYPE_STYLE.get(rec.rec_type, ("#f3f4f6", "#374151", rec.rec_type.upper()))
        arrow = "↑" if rec.delta_pct > 0 else "↓"
        delta_color = "#166534" if rec.delta_pct > 0 else "#9b1c1c"
        delta_bg = "#dcfce7" if rec.delta_pct > 0 else "#fee2e2"

        cols = st.columns([0.6, 1.05, 1.1, 0.85, 0.92, 0.76, 0.9, 0.8, 0.8])

        cols[0].markdown(
            f"<span style='background:{bg};color:{fg};padding:2px 8px;border-radius:4px;"
            f"font-size:0.78em;font-weight:700;white-space:nowrap;'>{label}</span>",
            unsafe_allow_html=True,
        )
        cols[1].markdown(f"`{sku}`")
        cols[2].markdown(f"{product_name}")
        cols[3].markdown(f"<span style='color:#6b7280;font-size:0.9em;'>{dept_name}</span>", unsafe_allow_html=True)
        cols[4].markdown(
            f"<span style='background:{conf_bg};color:{conf_fg};padding:2px 8px;border-radius:4px;"
            f"font-size:0.78em;font-weight:700;white-space:nowrap;'>{rec.confidence}</span>",
            unsafe_allow_html=True,
        )
        cols[5].markdown(
            f"<span style='background:{delta_bg};color:{delta_color};padding:2px 7px;"
            f"border-radius:4px;font-size:0.85em;font-weight:700;white-space:nowrap;'>"
            f"{arrow} {rec.delta_pct:+.1f}%</span>",
            unsafe_allow_html=True,
        )
        cols[6].markdown(
            f"<span style='color:#374151;font-size:0.85em;font-weight:600;'>{rec.impact or '-'}</span>",
            unsafe_allow_html=True,
        )

        # Accept: Weak Signal requires a confirmation step before logging
        if rec.confidence == "Weak":
            pending_key = f"confirm_pending_{i}"
            if pending_key not in st.session_state:
                st.session_state[pending_key] = False
            if cols[7].button("Accept", key=f"accept_{i}", use_container_width=True):
                st.session_state[pending_key] = True
            if st.session_state.get(pending_key):
                wcols = st.columns([2, 1, 1, 3])
                wcols[0].warning("Weak signal - confirm?")
                if wcols[1].button("Confirm", key=f"confirm_{i}", type="primary"):
                    actions.append((i, "accept"))
                    st.session_state[pending_key] = False
                if wcols[2].button("Cancel", key=f"cancel_{i}"):
                    st.session_state[pending_key] = False
        else:
            if cols[7].button("Accept", key=f"accept_{i}", use_container_width=True):
                actions.append((i, "accept"))

        if cols[8].button("Reject", key=f"reject_{i}", use_container_width=True):
            actions.append((i, "reject"))

        if rec.flagged:
            st.markdown(
                f"<div style='background:#fef9c3;border:1px solid #f59e0b;border-radius:4px;"
                f"padding:5px 12px;margin:2px 0 4px 0;font-size:0.82em;color:#854d0e;'>"
                f"⚠ Guard flagged: {rec.flag_reason}</div>",
                unsafe_allow_html=True,
            )

        with st.expander(f"Details - {product_name}", expanded=False):
            if rec.action_detail:
                st.info(rec.action_detail)
            if rec.flagged:
                st.warning(f"Guard flagged: {rec.flag_reason}")
            st.markdown(_clean_text(rec.text))
            st.divider()
            dcol1, dcol2 = st.columns(2)
            dcol1.caption(f"**Intent check:** {rec.intent_check or 'n/a'}")
            dcol2.caption(f"**Numeric check:** {rec.numeric_check or 'n/a'}")
            if rec.context_docs:
                with st.expander("Context Sources", expanded=False):
                    for j, doc in enumerate(rec.context_docs, 1):
                        st.caption(f"**Source {j}:** {doc}")

        st.markdown("<hr style='margin:6px 0;border-color:#f3f4f6;'>", unsafe_allow_html=True)

    return actions
