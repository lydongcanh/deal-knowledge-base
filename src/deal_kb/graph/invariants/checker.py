"""Checks the non-negotiable invariants of the graph knowledge base.

LadybugDB enforces primary keys and the node types a relationship may connect,
but it cannot express cardinality ("exactly one object") or the presence rules
the schema depends on. Those are checked here.

This runs after ingest and after reconciliation. It is a verification pass, not
a write-time guard: a violation means the data is already wrong.
"""

from deal_kb.graph.invariants.violation import Violation
from deal_kb.graph.store import DOMAIN_GRAPH, MAIN_GRAPH, GraphStore

# Each entry: invariant name -> (query returning `id`, message).
_CORE_CHECKS: tuple[tuple[str, str, str], ...] = (
    (
        "room_scoped",
        """
        MATCH (n) WHERE label(n) IN ['Entity', 'Claim', 'CanonicalStatement', 'Finding']
        OPTIONAL MATCH (n)-[:IN_DATA_ROOM]->(r:DataRoom)
        WITH n, count(r) AS rooms WHERE rooms <> 1
        RETURN coalesce(n.entity_id, n.claim_id, n.canonical_statement_id,
                        n.finding_id) AS id, rooms AS n
        """,
        "must belong to exactly one DataRoom, found {n}",
    ),
    (
        "evidence_has_file",
        """
        MATCH (e:Evidence)
        OPTIONAL MATCH (e)-[:FROM_FILE]->(f:DocumentFile)
        WITH e, count(f) AS files WHERE files <> 1
        RETURN e.evidence_id AS id, files AS n
        """,
        "must point to exactly one DocumentFile, found {n}",
    ),
    (
        "claim_has_one_subject",
        """
        MATCH (c:Claim)
        OPTIONAL MATCH (c)-[:HAS_SUBJECT]->(s:Entity)
        WITH c, count(s) AS subjects WHERE subjects <> 1
        RETURN c.claim_id AS id, subjects AS n
        """,
        "must have exactly one subject, found {n}",
    ),
    (
        "claim_has_one_predicate",
        """
        MATCH (c:Claim)
        OPTIONAL MATCH (c)-[:USES_PREDICATE]->(p:Predicate)
        WITH c, count(p) AS predicates WHERE predicates <> 1
        RETURN c.claim_id AS id, predicates AS n
        """,
        "must have exactly one Predicate, found {n}",
    ),
    (
        "claim_has_one_object",
        """
        MATCH (c:Claim)
        OPTIONAL MATCH (c)-[:HAS_OBJECT_ENTITY]->(oe:Entity)
        OPTIONAL MATCH (c)-[:HAS_OBJECT_VALUE]->(ov:Value)
        WITH c, count(oe) + count(ov) AS objects WHERE objects <> 1
        RETURN c.claim_id AS id, objects AS n
        """,
        "must have exactly one object, entity or value, found {n}",
    ),
    (
        "claim_records_modality",
        """
        MATCH (c:Claim)
        WHERE c.polarity IS NULL OR c.assertion_mode IS NULL
        RETURN c.claim_id AS id, 0 AS n
        """,
        "must record both polarity and assertion_mode",
    ),
    (
        "claim_has_evidence",
        """
        MATCH (c:Claim)
        OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(e:Evidence)
        WITH c, count(e) AS evidence WHERE evidence = 0
        RETURN c.claim_id AS id, evidence AS n
        """,
        "must have at least one Evidence record",
    ),
    (
        "claim_has_extraction_run",
        """
        MATCH (c:Claim)
        OPTIONAL MATCH (c)-[:GENERATED_BY]->(r:ExtractionRun)
        WITH c, count(r) AS runs WHERE runs <> 1
        RETURN c.claim_id AS id, runs AS n
        """,
        "must be attributable to exactly one ExtractionRun, found {n}",
    ),
    (
        "entity_has_concept",
        """
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[:INSTANCE_OF]->(c:Concept)
        WITH e, count(c) AS concepts WHERE concepts = 0
        RETURN e.entity_id AS id, concepts AS n
        """,
        "must be an instance of at least one Concept",
    ),
    (
        "canonical_has_support",
        """
        MATCH (s:CanonicalStatement)
        OPTIONAL MATCH (s)-[:SUPPORTED_BY_CLAIM]->(c:Claim)
        WITH s, count(c) AS claims WHERE claims = 0
        RETURN s.canonical_statement_id AS id, claims AS n
        """,
        "must have at least one supporting Claim",
    ),
)


class InvariantChecker:
    """Runs every machine-checkable invariant and reports what failed."""

    def __init__(self, store: GraphStore) -> None:
        self._store = store

    def check(self) -> list[Violation]:
        """Return every violation found. An empty list means the graph is sound."""
        self._store.use_graph(MAIN_GRAPH)
        violations = [v for name, query, message in _CORE_CHECKS
                      for v in self._run(name, query, message)]
        violations.extend(self._check_projection())
        return violations

    def _run(self, name: str, query: str, message: str) -> list[Violation]:
        return [
            Violation(name, str(row.get("id")), message.format(n=row.get("n")))
            for row in self._store.execute(query)
        ]

    def _check_projection(self) -> list[Violation]:
        """Every materialized domain edge must name the statement it came from.

        The projection is a derived view; an edge that cannot be traced back to a
        CanonicalStatement is unexplainable and must not be trusted.
        """
        self._store.use_graph(DOMAIN_GRAPH)
        try:
            # In an open-typed graph a property that was never written matches
            # neither IS NULL nor IS NOT NULL, so orphans are counted by
            # difference rather than filtered directly.
            total = self._store.scalar("MATCH ()-[r]->() RETURN count(r)") or 0
            traceable = self._store.scalar(
                """
                MATCH ()-[r]->()
                WHERE r.canonical_statement_id IS NOT NULL
                RETURN count(r)
                """
            ) or 0
        except RuntimeError:
            return []  # nothing projected yet
        finally:
            self._store.use_graph(MAIN_GRAPH)
        orphans = total - traceable
        if not orphans:
            return []
        return [Violation("projection_traceable", "domain",
                          f"{orphans} domain edge(s) have no canonical_statement_id")]
