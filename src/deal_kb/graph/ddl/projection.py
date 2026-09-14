"""DDL for the open-typed graph holding the materialized domain projection.

The domain projection carries ontology-driven labels and relationship types
(`Company`, `Agreement`, `PARTY_TO`, `REQUIRES_CONSENT_FROM`) that are not known
when the database is created. An open-typed graph accepts them without DDL, so
promoting a new Concept never requires a schema migration.

`CREATE GRAPH <name> ANY` is what makes the graph open-typed. A graph created
without `ANY` is strictly typed like the default `main` graph, and undeclared
labels there fail to bind. There is no `IF NOT EXISTS` form, so the installer
checks `show_graphs()` before creating it.
"""

OPEN_TYPED = "ANY"


def create_graph_statement(name: str) -> str:
    """DDL creating `name` as an open-typed graph."""
    return f"CREATE GRAPH {name} {OPEN_TYPED}"
