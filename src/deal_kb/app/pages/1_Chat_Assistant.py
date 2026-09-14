"""Chat Assistant: Bedrock LLM answers grounded in retrieved deal graph facts."""

import streamlit as st

from deal_kb.graph import build_context, get_graph_store
from deal_kb.llm import BedrockChatClient

st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")
st.title("💬 Chat Assistant")
st.caption("Ask questions about deals, clauses, and risks. Answers are grounded in the graph.")

SYSTEM_PROMPT = (
    "You are a due-diligence assistant for M&A deal teams. Answer ONLY using the "
    "provided graph context. If the context doesn't contain the answer, say so "
    "explicitly rather than guessing."
)


@st.cache_resource
def _load_store():
    return get_graph_store()


@st.cache_resource
def _load_llm():
    return BedrockChatClient()


store = _load_store()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

question = st.chat_input("Ask about a deal, clause, entity, or risk...")
if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    context = build_context(store, question)
    with st.chat_message("assistant"):
        with st.spinner("Querying graph and Bedrock..."):
            try:
                llm = _load_llm()
                answer = llm.ask(question=question, context=context, system_prompt=SYSTEM_PROMPT)
            except Exception as exc:  # noqa: BLE001 - surface Bedrock/auth errors directly to the user
                answer = f"⚠️ Could not reach Bedrock: {exc}"
        st.markdown(answer)
        with st.expander("Graph context used"):
            st.code(context)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
