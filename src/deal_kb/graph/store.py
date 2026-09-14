"""Owns the embedded LadybugDB database behind the knowledge base."""

from pathlib import Path
from typing import Any, Self

import ladybug as lb

MAIN_GRAPH = "main"
DOMAIN_GRAPH = "domain"


class GraphStore:
    """A connection to the knowledge base, across both of its graphs.

    The database holds two graphs with deliberately different typing:

    `main` is strictly typed and holds the governed core — Claims, Evidence,
    the ontology, reconciled knowledge. Its tables are declared up front and
    changed only by engineering migration.

    `domain` is an open-typed graph (`CREATE GRAPH ... ANY`) holding the
    materialized domain projection, where labels and relationship types come
    from the ontology at runtime. Nothing there is a source of truth: it is
    rebuilt from CanonicalStatements.

    Properties in an open-typed graph are stored as JSON, so they compare and
    filter correctly but need a CAST before aggregation. Anything requiring
    aggregation belongs on typed `Value` in the main graph.
    """

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._database = lb.Database(str(db_path))
        self._connection = lb.Connection(self._database)
        self._current_graph = MAIN_GRAPH

    @property
    def current_graph(self) -> str:
        """Which graph subsequent statements run against."""
        return self._current_graph

    def use_graph(self, name: str) -> None:
        """Switch the connection to `name`, for the rest of the session."""
        self._connection.execute(f"USE GRAPH {name}")
        self._current_graph = name

    def execute(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run one Cypher statement and return its rows as dicts."""
        result = self._connection.execute(query, parameters=parameters or {})
        return list(result.rows_as_dict())

    def scalar(self, query: str, parameters: dict[str, Any] | None = None) -> Any:
        """Run a statement expected to return a single value."""
        rows = self.execute(query, parameters)
        if not rows:
            return None
        return next(iter(rows[0].values()))

    def graphs(self) -> list[dict[str, Any]]:
        """Every graph in the database, with its typing mode."""
        return self.execute("CALL show_graphs() RETURN *")

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
