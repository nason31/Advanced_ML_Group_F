import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.components.audit_trail import render_audit
from app.components.briefing_card import render_card
from src.llm.qa import answer_question
from src.recommendations.engine import run_pipeline

DATA_DIR = Path("data/processed")
VECTOR_DIR = Path("data/vector_store")

st.set_page_config(page_title="MerchAI Daily Briefing", layout="wide")
st.title("MerchAI - Daily Merchandising Briefing")

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

store_id = st.sidebar.selectbox("Store", ["CA_1", "CA_2", "TX_1"])
date = st.sidebar.date_input("Date", value=datetime.today())

if st.sidebar.button("Generate Briefing"):
    model_path = DATA_DIR / f"model_{store_id}.pkl"
    if not model_path.exists():
        st.error(
            f"No trained model found at {model_path}. "
            "Run `python scripts/train_forecast.py` first."
        )
    elif not any(VECTOR_DIR.glob("*")):
        st.error(
            f"Vector store at {VECTOR_DIR} is empty. "
            "Run `python scripts/build_rag_corpus.py` first."
        )
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
        except Exception as exc:  # noqa: BLE001 - surface any pipeline error inline
            st.error(f"Pipeline failed: {exc}")
            st.session_state.recs = []

recs = st.session_state.get("recs", [])
if not recs:
    st.info("Select a store and date, then click Generate Briefing.")
else:
    st.subheader(f"{store_id} - {date}")
    for i, rec in enumerate(recs):
        action = render_card(rec, i)
        if action:
            st.session_state.audit_log.append({
                "action": action,
                "text": rec.text,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            })

render_audit(st.session_state.audit_log)

st.divider()
st.subheader("Ask Your Data")
st.caption("Ask a natural language question about this store's performance. Answers are grounded in forecast data and historical context.")

question = st.text_input(
    "Your question",
    placeholder='e.g. "Why is FOODS_3 spiking this week?" or "Which category has the most downward pressure?"',
    key="qa_input",
)
if st.button("Ask", key="qa_submit") and question.strip():
    model_path = DATA_DIR / f"model_{store_id}.pkl"
    if not model_path.exists():
        st.error("Generate a briefing first so the model is loaded.")
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
            st.markdown(f"**Answer:** {answer}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Q&A failed: {exc}")
