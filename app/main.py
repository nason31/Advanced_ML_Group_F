import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from app.components.audit_trail import render_audit
from app.components.briefing_card import render_table, _extract_sku
from src.data.product_names import get_dept_name, get_product_name
from src.llm.qa import answer_question
from src.recommendations.engine import run_pipeline

DATA_DIR = Path("data/processed")
VECTOR_DIR = Path("data/vector_store")
AUDIT_FILE = Path("data/audit_trail.csv")

st.set_page_config(page_title="MerchAI Daily Briefing", layout="wide")


def _load_audit() -> list[dict]:
    if not AUDIT_FILE.exists():
        return []
    with AUDIT_FILE.open(newline="") as f:
        return list(csv.DictReader(f))


def _append_audit(entry: dict) -> None:
    write_header = not AUDIT_FILE.exists()
    with AUDIT_FILE.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["action", "text", "timestamp", "guard_flagged"])
        if write_header:
            writer.writeheader()
        writer.writerow(entry)


_PIPELINE_VERSION = "v5"  # bump when engine/guard/badge logic changes to force fresh recs

if st.session_state.get("_pipeline_version") != _PIPELINE_VERSION:
    st.session_state.pop("recs", None)
    st.session_state["_pipeline_version"] = _PIPELINE_VERSION

if "audit_log" not in st.session_state:
    st.session_state.audit_log = _load_audit()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## MerchAI")
    st.markdown(
        "<p style='color:#6b7280;font-size:0.9em;margin-top:-8px;'>"
        "Forecast-backed merchandising decisions, ready for your review. "
        "Act on what matters, skip what doesn't."
        "</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    _STORE_OPTIONS = {
        "CA_1 - California (Store 1)": "CA_1",
        "CA_2 - California (Store 2)": "CA_2",
        "TX_1 - Texas (Store 1)":      "TX_1",
    }
    store_label = st.selectbox("Store", list(_STORE_OPTIONS.keys()))
    store_id = _STORE_OPTIONS[store_label]
    date = datetime.today().strftime("%Y-%m-%d")

    if st.button("Generate Today's Briefing", use_container_width=True, type="primary"):
        model_path = DATA_DIR / f"model_{store_id}.pkl"
        if not model_path.exists():
            st.error("No trained model found. Run `python scripts/train_forecast.py` first.")
        elif not any(VECTOR_DIR.glob("*")):
            st.error("Vector store is empty. Run `python scripts/build_rag_corpus.py` first.")
        else:
            try:
                with st.status("Analysing products...", expanded=True) as status:
                    st.write("Running forecast, retrieving context, and reasoning with Claude...")
                    recs = run_pipeline(
                        store_id=store_id,
                        date=str(date),
                        data_dir=DATA_DIR,
                        vector_store_dir=VECTOR_DIR,
                    )
                    status.update(
                        label=f"Briefing ready - {len(recs)} recommendation{'s' if len(recs) != 1 else ''}",
                        state="complete",
                        expanded=False,
                    )
                st.session_state.recs = recs
                st.session_state.chat_history = []
            except Exception as exc:  # noqa: BLE001
                st.error(f"Pipeline failed: {exc}")
                st.session_state.recs = []

    st.divider()

    # ── Chat assistant ─────────────────────────────────────────────────────────
    st.markdown("#### Ask Your Data")
    st.caption("Ask about any product above - why it's moving, whether to act, what's driving it.")

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])

    question = st.chat_input("e.g. Why is Maple Syrup selling so much?")
    if question:
        model_path = DATA_DIR / f"model_{store_id}.pkl"
        if not model_path.exists():
            st.warning("Generate a briefing first.")
        else:
            try:
                with st.spinner("Thinking..."):
                    current_recs = st.session_state.get("recs", [])
                    active_products = {}
                    for rec in current_recs:
                        sku = rec.sku or _extract_sku(rec.text)
                        if sku and sku != "-":
                            active_products[f"{get_product_name(sku)} ({get_dept_name(sku)})"] = sku
                    answer = answer_question(
                        question=question.strip(),
                        store_id=store_id,
                        date=str(date),
                        data_dir=DATA_DIR,
                        vector_store_dir=VECTOR_DIR,
                        active_products=active_products or None,
                    )
                st.session_state.chat_history.append({"question": question, "answer": answer})
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Q&A failed: {exc}")

    st.divider()
    st.caption(
        "All recommendations are AI-generated. The manager retains final authority on every action. "
        "Decisions are logged to the audit trail."
    )

# ── Main area ──────────────────────────────────────────────────────────────────
st.info("Demo mode: running on historical Walmart (M5) benchmark data.")

st.markdown(
    "<span style='font-size:0.85em;font-weight:600;color:#6b7280;text-transform:uppercase;"
    "letter-spacing:0.08em;'>MerchAI</span>",
    unsafe_allow_html=True,
)

recs = st.session_state.get("recs", [])
if not recs:
    st.markdown("## Daily Merchandising Briefing")
    st.info("Select a store and click Generate Today's Briefing.")
else:
    st.markdown(
        f"## {store_label.split(' - ')[1]}"
        f"<span style='color:#9ca3af;font-weight:400;'>"
        f"  &nbsp;|&nbsp;  {datetime.today().strftime('%A, %B %d %Y')}</span>",
        unsafe_allow_html=True,
    )
    actions = render_table(recs)
    for idx, action in actions:
        rec = recs[idx]
        entry = {
            "action": action,
            "text": rec.text[:80],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "guard_flagged": rec.flagged,
        }
        st.session_state.audit_log.append(entry)
        _append_audit(entry)

render_audit(st.session_state.audit_log)
