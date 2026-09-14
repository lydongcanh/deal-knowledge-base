"""Cross-Document Intelligence: shared entities and references between documents."""

import pandas as pd
import streamlit as st

from deal_kb.graph import get_graph_store

st.set_page_config(page_title="Cross-Document Intelligence", page_icon="🧩", layout="wide")
st.title("🧩 Cross-Document Intelligence")


@st.cache_resource
def _load_store():
    return get_graph_store()


store = _load_store()

st.subheader("Documents linked by explicit references")
references = store.execute(
    """
    MATCH (a:Document)-[rel:DocReferences]->(b:Document)
    RETURN a.title AS source_document, rel.relation AS relation, b.title AS target_document
    """
)
if references:
    st.dataframe(pd.DataFrame(references), width="stretch", hide_index=True)
else:
    st.info("No explicit document references found.")

st.subheader("Documents that share entities")
shared = store.execute(
    """
    MATCH (d1:Document)-[:MentionsEntity]->(e:Entity)<-[:MentionsEntity]-(d2:Document)
    WHERE d1.id < d2.id
    RETURN d1.title AS document_a, d2.title AS document_b, e.name AS shared_entity
    """
)
if shared:
    st.dataframe(pd.DataFrame(shared), width="stretch", hide_index=True)
else:
    st.info("No documents share common entities yet.")

st.subheader("Documents grouped by topic")
topics = store.execute(
    """
    MATCH (doc:Document)-[:AboutTopic]->(t:Topic)
    RETURN t.name AS topic, doc.title AS document
    ORDER BY t.name
    """
)
if topics:
    df = pd.DataFrame(topics)
    for topic_name, group in df.groupby("topic"):
        st.markdown(f"**{topic_name}**: " + ", ".join(group["document"]))
else:
    st.info("No topic links found.")
