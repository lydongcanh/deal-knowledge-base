"""Risk Analysis: aggregated view of risk flags across deals."""

import pandas as pd
import plotly.express as px
import streamlit as st

from deal_kb.graph import get_graph_store

st.set_page_config(page_title="Risk Analysis", page_icon="⚠️", layout="wide")
st.title("⚠️ Risk Analysis")


@st.cache_resource
def _load_store():
    return get_graph_store()


store = _load_store()

rows = store.execute(
    """
    MATCH (deal:Deal)-[:HasDocument]->(doc:Document)-[:ContainsClause]->(c:Clause)-[:FlaggedAs]->(r:RiskFlag)
    RETURN deal.name AS deal, doc.title AS document, c.clause_type AS clause_type,
           r.category AS category, r.severity AS severity, r.description AS risk_description
    """
)
df = pd.DataFrame(rows)

if df.empty:
    st.info("No risk flags found in the graph.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        px.bar(df.groupby("severity").size().reset_index(name="count"), x="severity", y="count", title="Risk flags by severity"),
        width="stretch",
    )
with col2:
    st.plotly_chart(
        px.bar(df.groupby("category").size().reset_index(name="count"), x="category", y="count", title="Risk flags by category"),
        width="stretch",
    )

st.subheader("All flagged risks")
deal_filter = st.multiselect("Filter by deal", sorted(df["deal"].unique()))
filtered = df[df["deal"].isin(deal_filter)] if deal_filter else df
st.dataframe(filtered, width="stretch", hide_index=True)
