"""Thin wrapper around LadybugDB for the deal graph store."""

from pathlib import Path
from typing import Any

import ladybug as lb

from deal_kb.graph.schema import NODE_TABLES, REL_TABLES


class GraphStore:
    """Owns a single embedded LadybugDB database connection."""

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._database = lb.Database(str(db_path))
        self._connection = lb.Connection(self._database)

    def ensure_schema(self) -> None:
        """Create node/relationship tables if they don't already exist."""
        for statement in [*NODE_TABLES, *REL_TABLES]:
            self._connection.execute(statement)

    def is_empty(self) -> bool:
        result = self._connection.execute("MATCH (d:Deal) RETURN count(d) AS n")
        rows = list(result.rows_as_dict())
        return not rows or rows[0]["n"] == 0

    def execute(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run a Cypher query and return rows as a list of dicts."""
        result = self._connection.execute(query, parameters=parameters or {})
        return list(result.rows_as_dict())

    def close(self) -> None:
        self._connection.close()
