import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from app.components.audit_trail import render_audit
from app.components.briefing_card import render_table
from src.llm.qa import answer_question
from src.recommendations.engine import run_pipeline

DATA_DIR = Path("data/processed")
VECTOR_DIR = Path("data/vector_store")

st.set_page_config(page_title="MerchAI Daily Briefing", layout="wide")

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
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
                with st.spinner("Running pipeline..."):
                    recs = run_pipeline(
                        store_id=store_id,
                        date=str(date),
                        data_dir=DATA_DIR,
                        vector_store_dir=VECTOR_DIR,
                    )
                st.session_state.recs = recs
                st.session_state.chat_history = []
            except Exception as exc:  # noqa: BLE001
                st.error(f"Pipeline failed: {exc}")
                st.session_state.recs = []

    st.divider()

    # ── Chat assistant ─────────────────────────────────────────────────────────
    st.markdown("#### Ask Your Data")
    st.caption("Grounded in forecast data and historical context.")

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])

    question = st.chat_input("e.g. Why is FOODS_3 spiking?")
    if question:
        model_path = DATA_DIR / f"model_{store_id}.pkl"
        if not model_path.exists():
            st.warning("Generate a briefing first.")
        else:
            try:
                with st.spinner("Thinking..."):
                    answer = answer_question(
                        question=question.strip(),
                        store_id=store_id,
                        date=str(date),
                        data_dir=DATA_DIR,
                        vector_store_dir=VECTOR_DIR,
                    )
                st.session_state.chat_history.append({"question": question, "answer": answer})
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Q&A failed: {exc}")

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("MerchAI - Daily Merchandising Briefing")

recs = st.session_state.get("recs", [])
if not recs:
    st.info("Select a store and date, then click Generate Briefing.")
else:
    st.subheader(f"{store_label.split(' - ')[1]}  |  {datetime.today().strftime('%A, %B %d %Y')}")
    actions = render_table(recs)
    for idx, action in actions:
        rec = recs[idx]
        st.session_state.audit_log.append({
            "action": action,
            "text": rec.text[:80],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })

render_audit(st.session_state.audit_log)
