"""Relationship table DDL for the governed core schema.

Several relationships are shared by more than one source type — a Claim and an
OntologyProposal are both `SUPPORTED_BY` Evidence. LadybugDB rel tables accept
multiple FROM-TO pairs, so each stays one relationship type rather than
fragmenting into per-source variants.
"""

REL_TABLES: tuple[str, ...] = (
    # ---- Source structure --------------------------------------------------
    "CREATE REL TABLE IF NOT EXISTS CONTAINS_DOCUMENT(FROM DataRoom TO Document)",
    "CREATE REL TABLE IF NOT EXISTS HAS_FILE(FROM Document TO DocumentFile)",
    "CREATE REL TABLE IF NOT EXISTS FROM_FILE(FROM Evidence TO DocumentFile)",
    "CREATE REL TABLE IF NOT EXISTS APPEARS_IN(FROM Mention TO Evidence)",
    "CREATE REL TABLE IF NOT EXISTS PROCESSED(FROM ExtractionRun TO DocumentFile)",
    # ---- Data Room isolation -----------------------------------------------
    """CREATE REL TABLE IF NOT EXISTS IN_DATA_ROOM(
        FROM Entity TO DataRoom,
        FROM Claim TO DataRoom,
        FROM CanonicalStatement TO DataRoom,
        FROM Finding TO DataRoom
    )""",
    # ---- Claim structure ---------------------------------------------------
    "CREATE REL TABLE IF NOT EXISTS INSTANCE_OF(FROM Entity TO Concept)",
    """CREATE REL TABLE IF NOT EXISTS HAS_SUBJECT(
        FROM Claim TO Entity,
        FROM CanonicalStatement TO Entity
    )""",
    """CREATE REL TABLE IF NOT EXISTS USES_PREDICATE(
        FROM Claim TO Predicate,
        FROM CanonicalStatement TO Predicate
    )""",
    """CREATE REL TABLE IF NOT EXISTS HAS_OBJECT_ENTITY(
        FROM Claim TO Entity,
        FROM CanonicalStatement TO Entity
    )""",
    """CREATE REL TABLE IF NOT EXISTS HAS_OBJECT_VALUE(
        FROM Claim TO Value,
        FROM CanonicalStatement TO Value
    )""",
    """CREATE REL TABLE IF NOT EXISTS SUPPORTED_BY(
        FROM Claim TO Evidence,
        FROM OntologyProposal TO Evidence
    )""",
    """CREATE REL TABLE IF NOT EXISTS GENERATED_BY(
        FROM Claim TO ExtractionRun,
        FROM ResolutionDecision TO ExtractionRun,
        FROM OntologyProposal TO ExtractionRun
    )""",
    # ---- Resolution --------------------------------------------------------
    "CREATE REL TABLE IF NOT EXISTS RESOLVES_INPUT(FROM ResolutionDecision TO Mention)",
    "CREATE REL TABLE IF NOT EXISTS SELECTED_ENTITY(FROM ResolutionDecision TO Entity)",
    "CREATE REL TABLE IF NOT EXISTS SELECTED_CONCEPT(FROM ResolutionDecision TO Concept)",
    "CREATE REL TABLE IF NOT EXISTS SELECTED_PREDICATE(FROM ResolutionDecision TO Predicate)",
    "CREATE REL TABLE IF NOT EXISTS SELECTED_VALUE(FROM ResolutionDecision TO Value)",
    # Alternatives the resolver considered but did not select.
    """CREATE REL TABLE IF NOT EXISTS CANDIDATE_TARGET(
        FROM ResolutionDecision TO Entity,
        FROM ResolutionDecision TO Concept,
        FROM ResolutionDecision TO Predicate,
        FROM ResolutionDecision TO Value,
        rank INT64,
        score DOUBLE
    )""",
    # ---- Ontology ----------------------------------------------------------
    """CREATE REL TABLE IF NOT EXISTS DEFINED_IN(
        FROM Concept TO OntologyRelease,
        FROM Predicate TO OntologyRelease
    )""",
    """CREATE REL TABLE IF NOT EXISTS NARROWER_THAN(
        FROM Concept TO Concept,
        FROM Predicate TO Predicate
    )""",
    "CREATE REL TABLE IF NOT EXISTS INVERSE_OF(FROM Predicate TO Predicate)",
    "CREATE REL TABLE IF NOT EXISTS RELATED_TO(FROM Predicate TO Predicate)",
    "CREATE REL TABLE IF NOT EXISTS DEPRECATED_IN_FAVOR_OF(FROM Predicate TO Predicate)",
    """CREATE REL TABLE IF NOT EXISTS LABEL_FOR(
        FROM TermLabel TO Concept,
        FROM TermLabel TO Predicate
    )""",
    """CREATE REL TABLE IF NOT EXISTS CONSTRAINS(
        FROM OntologyConstraint TO Concept,
        FROM OntologyConstraint TO Predicate
    )""",
    """CREATE REL TABLE IF NOT EXISTS CANDIDATE_MATCH(
        FROM OntologyProposal TO Concept,
        FROM OntologyProposal TO Predicate
    )""",
    """CREATE REL TABLE IF NOT EXISTS RESOLVED_TO(
        FROM OntologyProposal TO Concept,
        FROM OntologyProposal TO Predicate
    )""",
    # ---- Reconciled knowledge ----------------------------------------------
    "CREATE REL TABLE IF NOT EXISTS PRODUCED_BY(FROM CanonicalStatement TO ReconciliationRun)",
    "CREATE REL TABLE IF NOT EXISTS SUPPORTED_BY_CLAIM(FROM CanonicalStatement TO Claim)",
    "CREATE REL TABLE IF NOT EXISTS CONTRADICTED_BY_CLAIM(FROM CanonicalStatement TO Claim)",
    # ---- Derived findings --------------------------------------------------
    """CREATE REL TABLE IF NOT EXISTS DERIVED_FROM(
        FROM Finding TO CanonicalStatement,
        FROM Finding TO Claim
    )""",
)
