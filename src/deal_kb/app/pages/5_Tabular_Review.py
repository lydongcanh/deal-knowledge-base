"""Tabular Review: reviewable table of clauses and their linked risk flags."""

import pandas as pd
import streamlit as st

from deal_kb.graph import get_graph_store

st.set_page_config(page_title="Tabular Review", page_icon="📋", layout="wide")
st.title("📋 Tabular Review")
st.caption("Review clauses and mark them as reviewed. (In-memory only for this POC.)")


@st.cache_resource
def _load_store():
    return get_graph_store()


store = _load_store()

rows = store.execute(
    """
    MATCH (deal:Deal)-[:HasDocument]->(doc:Document)-[:ContainsClause]->(c:Clause)
    OPTIONAL MATCH (c)-[:FlaggedAs]->(r:RiskFlag)
    RETURN deal.name AS deal_name, doc.title AS document_title, c.clause_type AS clause_type,
           c.text AS clause_text, r.severity AS risk_severity
    ORDER BY deal_name, document_title
    """
)
df = pd.DataFrame(rows)
df["reviewed"] = False

edited = st.data_editor(
    df,
    width="stretch",
    hide_index=True,
    disabled=["deal_name", "document_title", "clause_type", "clause_text", "risk_severity"],
    column_config={"reviewed": st.column_config.CheckboxColumn("Reviewed")},
)

reviewed_count = int(edited["reviewed"].sum())
st.metric("Clauses reviewed", f"{reviewed_count} / {len(edited)}")
