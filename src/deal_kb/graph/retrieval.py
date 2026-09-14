"""Naive keyword-based retrieval over the graph, used to ground chat answers."""

from deal_kb.graph.client import GraphStore

_SUMMARY_QUERY = """
MATCH (d:Deal)
OPTIONAL MATCH (d)-[:HasDocument]->(doc:Document)
OPTIONAL MATCH (doc)-[:ContainsClause]->(c:Clause)-[:FlaggedAs]->(r:RiskFlag)
RETURN d.name AS deal, d.stage AS stage, doc.title AS document,
       c.clause_type AS clause_type, r.severity AS risk_severity, r.description AS risk_description
"""


def build_context(store: GraphStore, question: str) -> str:
    """Return a text block of graph facts relevant to the question for LLM grounding."""
    keywords = [w.strip(".,?!").lower() for w in question.split() if len(w) > 3]

    rows = store.execute(
        """
        MATCH (c:Clause)
        OPTIONAL MATCH (c)-[:FlaggedAs]->(r:RiskFlag)
        OPTIONAL MATCH (doc:Document)-[:ContainsClause]->(c)
        RETURN doc.title AS document, c.clause_type AS clause_type, c.text AS clause_text,
               r.severity AS risk_severity, r.description AS risk_description
        """
    )
    matched = [
        row
        for row in rows
        if any(k in (row.get("clause_text") or "").lower() or k in (row.get("clause_type") or "").lower() for k in keywords)
    ]

    if not matched:
        matched = store.execute(_SUMMARY_QUERY)

    lines = []
    for row in matched:
        lines.append(
            f"- Document '{row.get('document')}': clause '{row.get('clause_type')}' "
            f"(risk: {row.get('risk_severity') or 'none'} - {row.get('risk_description') or 'n/a'})"
        )
    return "\n".join(lines) if lines else "No relevant graph data found."
