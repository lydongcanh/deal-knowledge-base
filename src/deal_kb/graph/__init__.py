"""LadybugDB-backed graph knowledge base.

Implements docs/graph-knowledge-base-schema.md: a governed core schema in the
strictly-typed `main` graph, and an open-typed `domain` graph for the
materialized domain projection.

The graph does not replace the existing application databases. DataRoom,
Document and DocumentFile are reference nodes holding only the stable Ansarada
identifier; those systems remain authoritative for their metadata.
"""

from deal_kb.config import settings
from deal_kb.graph.invariants import InvariantChecker, Violation
from deal_kb.graph.schema_installer import SchemaInstaller
from deal_kb.graph.store import DOMAIN_GRAPH, MAIN_GRAPH, GraphStore

__all__ = [
    "DOMAIN_GRAPH",
    "MAIN_GRAPH",
    "GraphStore",
    "InvariantChecker",
    "SchemaInstaller",
    "Violation",
    "get_graph_store",
]

_store: GraphStore | None = None


def get_graph_store() -> GraphStore:
    """Return a process-wide GraphStore, installing the schema on first use."""
    global _store
    if _store is None:
        _store = GraphStore(settings.graph_db_path)
        SchemaInstaller(_store).install()
    return _store
