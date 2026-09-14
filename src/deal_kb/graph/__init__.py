"""LadybugDB-backed deal graph store: schema, seeding, and query access."""

from deal_kb.config import settings
from deal_kb.graph.client import GraphStore
from deal_kb.graph.retrieval import build_context
from deal_kb.graph.seed_data import seed

__all__ = ["GraphStore", "build_context", "get_graph_store"]

_store: GraphStore | None = None


def get_graph_store() -> GraphStore:
    """Return a process-wide GraphStore, initializing schema/seed data on first use."""
    global _store
    if _store is None:
        _store = GraphStore(settings.graph_db_path)
        _store.ensure_schema()
        if _store.is_empty():
            seed(_store)
    return _store
