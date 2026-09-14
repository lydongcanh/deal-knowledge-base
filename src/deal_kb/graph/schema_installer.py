"""Creates the knowledge-base schema in an empty or existing database."""

from deal_kb.graph.ddl.node_tables import NODE_TABLES
from deal_kb.graph.ddl.projection import create_graph_statement
from deal_kb.graph.ddl.rel_tables import REL_TABLES
from deal_kb.graph.store import DOMAIN_GRAPH, MAIN_GRAPH, GraphStore


class SchemaInstaller:
    """Installs the governed core tables and the domain projection graph.

    Installing over an existing database is safe and is how the schema is
    applied on startup. Table DDL is idempotent via `IF NOT EXISTS`;
    `CREATE GRAPH` has no such form, so the projection graph is created only
    when `show_graphs()` says it is absent.
    """

    def __init__(self, store: GraphStore) -> None:
        self._store = store

    def install(self) -> None:
        """Create the core schema and the open-typed projection graph."""
        self._store.use_graph(MAIN_GRAPH)
        for statement in (*NODE_TABLES, *REL_TABLES):
            self._store.execute(statement)
        self._install_projection_graph()

    def is_installed(self) -> bool:
        """Whether the core tables and the projection graph are both present."""
        tables = {row["name"] for row in self._store.execute("CALL show_tables() RETURN *")}
        return {"Claim", "Evidence"} <= tables and self._projection_graph_exists()

    def _install_projection_graph(self) -> None:
        if self._projection_graph_exists():
            return
        self._store.execute(create_graph_statement(DOMAIN_GRAPH))

    def _projection_graph_exists(self) -> bool:
        return any(row["name"] == DOMAIN_GRAPH for row in self._store.graphs())
