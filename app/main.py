from datetime import datetime
from pathlib import Path

import streamlit as st

from app.components.audit_trail import render_audit
from app.components.briefing_card import render_card
from src.recommendations.engine import run_pipeline

st.set_page_config(page_title="MerchAI Daily Briefing", layout="wide")
st.title("MerchAI — Daily Merchandising Briefing")

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

store_id = st.sidebar.selectbox("Store", ["CA_1", "CA_2", "TX_1"])
date = st.sidebar.date_input("Date", value=datetime.today())

if st.sidebar.button("Generate Briefing"):
    with st.spinner("Running pipeline..."):
        recs = run_pipeline(
            store_id=store_id,
            date=str(date),
            data_dir=Path("data/processed"),
            vector_store_dir=Path("data/vector_store"),
        )
    st.session_state.recs = recs

recs = st.session_state.get("recs", [])
if not recs:
    st.info("Select a store and date, then click Generate Briefing.")
else:
    for i, rec in enumerate(recs):
        action = render_card(rec, i)
        if action:
            st.session_state.audit_log.append({
                "action": action,
                "text": rec.text,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            })

render_audit(st.session_state.audit_log)
