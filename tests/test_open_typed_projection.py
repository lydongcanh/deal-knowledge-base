"""The domain projection accepts ontology-driven labels without DDL.

This is what lets a newly promoted Concept be projected without a migration.
"""

from deal_kb.graph import DOMAIN_GRAPH, MAIN_GRAPH, GraphStore


def test_undeclared_labels_and_relationships_are_accepted(store: GraphStore) -> None:
    store.use_graph(DOMAIN_GRAPH)
    store.execute("CREATE (:Company {name:'TargetCo', canonical_statement_id:'cs1'})")
    store.execute("CREATE (:Organization {name:'BigBank', canonical_statement_id:'cs2'})")
    store.execute(
        """MATCH (a:Company {name:'TargetCo'}), (b:Organization {name:'BigBank'})
           CREATE (a)-[:REQUIRES_CONSENT_FROM {canonical_statement_id:'cs3',
                                               canonical_confidence:0.91}]->(b)"""
    )
    rows = store.execute(
        """MATCH (a:Company)-[r:REQUIRES_CONSENT_FROM]->(b:Organization)
           RETURN a.name AS subject, b.name AS object,
                  r.canonical_statement_id AS traces_to"""
    )
    assert rows == [{"subject": "TargetCo", "object": "BigBank", "traces_to": "cs3"}]


def test_undeclared_labels_are_rejected_in_the_typed_main_graph(store: GraphStore) -> None:
    """The governed core stays strictly typed; only the projection is open."""
    store.use_graph(MAIN_GRAPH)
    try:
        store.execute("CREATE (:Company {name:'TargetCo'})")
    except RuntimeError as error:
        assert "does not exist" in str(error)
    else:
        raise AssertionError("main graph should reject an undeclared label")
