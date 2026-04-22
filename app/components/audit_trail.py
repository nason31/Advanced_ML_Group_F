import streamlit as st


def render_audit(log: list[dict]) -> None:
    """Render the accept/reject audit trail."""
    st.subheader("Audit Trail")
    if not log:
        st.info("No decisions recorded yet.")
        return
    for entry in reversed(log):
        st.markdown(
            f"- **{entry['action'].upper()}** — {entry['text']} _(at {entry['timestamp']})_"
        )
