"""Graph Explorer: interactive visualization of the deal graph."""

import streamlit as st
from streamlit_agraph import Config, agraph

from deal_kb.app.components.graph_view import GraphView
from deal_kb.graph import get_graph_store

st.set_page_config(page_title="Graph Explorer", page_icon="🔎", layout="wide")
st.title("🔎 Graph Explorer")


@st.cache_resource
def _load_store():
    return get_graph_store()


store = _load_store()
deals = store.execute("MATCH (d:Deal) RETURN d.id AS id, d.name AS name ORDER BY d.name")
deal_names = {d["name"]: d["id"] for d in deals}

selected_deal_name = st.selectbox("Focus deal", list(deal_names.keys()))
selected_deal_id = deal_names[selected_deal_name]

rows = store.execute(
    """
    MATCH (d:Deal {id: $deal_id})
    OPTIONAL MATCH (d)-[:InvolvesEntity]->(e:Entity)
    OPTIONAL MATCH (d)-[:HasDocument]->(doc:Document)
    OPTIONAL MATCH (doc)-[:MentionsEntity]->(me:Entity)
    OPTIONAL MATCH (doc)-[:ContainsClause]->(c:Clause)
    OPTIONAL MATCH (c)-[:FlaggedAs]->(r:RiskFlag)
    RETURN d.id AS deal_id, d.name AS deal_name,
           e.id AS entity_id, e.name AS entity_name,
           doc.id AS doc_id, doc.title AS doc_title,
           me.id AS mentioned_entity_id, me.name AS mentioned_entity_name,
           c.id AS clause_id, c.clause_type AS clause_type,
           r.id AS risk_id, r.severity AS risk_severity
    """,
    {"deal_id": selected_deal_id},
)

view = GraphView()
for row in rows:
    view.add_node(row["deal_id"], row["deal_name"], "Deal")
    if row.get("entity_id"):
        view.add_node(row["entity_id"], row["entity_name"], "Entity")
        view.add_edge(row["deal_id"], row["entity_id"], "involves")
    if row.get("doc_id"):
        view.add_node(row["doc_id"], row["doc_title"], "Document")
        view.add_edge(row["deal_id"], row["doc_id"], "has_document")
    if row.get("mentioned_entity_id"):
        view.add_node(row["mentioned_entity_id"], row["mentioned_entity_name"], "Entity")
        view.add_edge(row["doc_id"], row["mentioned_entity_id"], "mentions")
    if row.get("clause_id"):
        view.add_node(row["clause_id"], row["clause_type"], "Clause")
        view.add_edge(row["doc_id"], row["clause_id"], "contains")
    if row.get("risk_id"):
        view.add_node(row["risk_id"], row["risk_severity"], "RiskFlag")
        view.add_edge(row["clause_id"], row["risk_id"], "flagged_as")

config = Config(width=1100, height=650, directed=True, physics=True, hierarchical=False)
agraph(nodes=view.nodes, edges=view.edges, config=config)
