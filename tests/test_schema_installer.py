"""The schema installs, is idempotent, and creates both graphs."""

from pathlib import Path

from deal_kb.graph import DOMAIN_GRAPH, MAIN_GRAPH, GraphStore, SchemaInstaller


def test_install_creates_core_tables(store: GraphStore) -> None:
    tables = {row["name"] for row in store.execute("CALL show_tables() RETURN *")}
    assert {"DataRoom", "Document", "DocumentFile", "Evidence", "Mention",
            "ExtractionRun", "Entity", "Value", "Claim", "OntologyRelease",
            "Concept", "Predicate", "TermLabel", "OntologyConstraint",
            "OntologyProposal", "ResolutionDecision", "ReconciliationRun",
            "CanonicalStatement", "Finding"} <= tables


def test_domain_projection_graph_is_open_typed(store: GraphStore) -> None:
    graphs = {row["name"]: row["type"] for row in store.graphs()}
    assert graphs[DOMAIN_GRAPH] == "ANY"


def test_install_is_idempotent(tmp_path: Path) -> None:
    with GraphStore(tmp_path / "twice.lbdb") as store:
        installer = SchemaInstaller(store)
        installer.install()
        installer.install()
        assert installer.is_installed()
        domain_graphs = [g for g in store.graphs() if g["name"] == DOMAIN_GRAPH]
        assert len(domain_graphs) == 1


def test_store_tracks_current_graph(store: GraphStore) -> None:
    assert store.current_graph == MAIN_GRAPH
    store.use_graph(DOMAIN_GRAPH)
    assert store.current_graph == DOMAIN_GRAPH
