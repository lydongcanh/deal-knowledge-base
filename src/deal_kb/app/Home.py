"""Streamlit entry point: landing page + shared graph store bootstrap."""

import streamlit as st

from deal_kb.graph import get_graph_store

st.set_page_config(page_title="Deal Knowledge Base", page_icon="🕸️", layout="wide")


@st.cache_resource
def _load_store():
    return get_graph_store()


store = _load_store()

st.title("🕸️ Ansarada Deal Graph Knowledge Base")
st.caption("End-to-end POC: graph-grounded chat, risk analysis, and cross-document intelligence.")

deal_count = store.execute("MATCH (d:Deal) RETURN count(d) AS n")[0]["n"]
doc_count = store.execute("MATCH (d:Document) RETURN count(d) AS n")[0]["n"]
entity_count = store.execute("MATCH (e:Entity) RETURN count(e) AS n")[0]["n"]
risk_count = store.execute("MATCH (r:RiskFlag) RETURN count(r) AS n")[0]["n"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Deals", deal_count)
col2.metric("Documents", doc_count)
col3.metric("Entities", entity_count)
col4.metric("Risk Flags", risk_count)

st.markdown(
    """
    Use the pages in the sidebar to explore the demo:

    - **Chat Assistant** — ask questions answered by Bedrock, grounded in graph facts.
    - **Graph Explorer** — interactively visualize the deal graph.
    - **Risk Analysis** — risk flags by category and severity.
    - **Cross-Document Intelligence** — shared entities and references across documents.
    - **Tabular Review** — review clauses and their linked risks in a table.
    """
)
