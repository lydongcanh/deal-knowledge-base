"""Node table DDL for the governed core schema.

Source-reference nodes (DataRoom, Document, DocumentFile) hold only the stable
Ansarada identifier. The existing application databases remain authoritative for
their metadata; duplicating it here would create a second source of truth.
"""

NODE_TABLES: tuple[str, ...] = (
    # ---- Source references -------------------------------------------------
    "CREATE NODE TABLE IF NOT EXISTS DataRoom(data_room_id STRING PRIMARY KEY)",
    "CREATE NODE TABLE IF NOT EXISTS Document(document_id STRING PRIMARY KEY)",
    "CREATE NODE TABLE IF NOT EXISTS DocumentFile(document_file_id STRING PRIMARY KEY)",
    # ---- Evidence and extraction lineage -----------------------------------
    """CREATE NODE TABLE IF NOT EXISTS Evidence(
        evidence_id STRING PRIMARY KEY,
        locator_type STRING,
        locator STRING,
        excerpt STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS Mention(
        mention_id STRING PRIMARY KEY,
        surface_form STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS ExtractionRun(
        extraction_run_id STRING PRIMARY KEY,
        extractor_version STRING,
        model_id STRING,
        prompt_version STRING,
        extraction_schema_version STRING,
        ontology_release_id STRING,
        completed_at TIMESTAMP
    )""",
    # ---- Knowledge objects -------------------------------------------------
    """CREATE NODE TABLE IF NOT EXISTS Entity(
        entity_id STRING PRIMARY KEY,
        canonical_name STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS Value(
        value_id STRING PRIMARY KEY,
        datatype STRING,
        canonical_value STRING,
        number_value DOUBLE,
        date_value DATE,
        datetime_value TIMESTAMP,
        boolean_value BOOL,
        text_value STRING,
        unit_code STRING,
        currency_code STRING,
        calendar_basis STRING,
        precision STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS Claim(
        claim_id STRING PRIMARY KEY,
        polarity STRING,
        assertion_mode STRING,
        extraction_confidence DOUBLE,
        claim_status STRING,
        valid_from DATE,
        valid_to DATE,
        as_of_date DATE
    )""",
    # ---- Ontology ----------------------------------------------------------
    """CREATE NODE TABLE IF NOT EXISTS OntologyRelease(
        ontology_release_id STRING PRIMARY KEY,
        version STRING,
        released_at TIMESTAMP
    )""",
    """CREATE NODE TABLE IF NOT EXISTS Concept(
        concept_id STRING PRIMARY KEY,
        preferred_label STRING,
        definition STRING,
        concept_kind STRING,
        lifecycle_status STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS Predicate(
        predicate_id STRING PRIMARY KEY,
        preferred_label STRING,
        definition STRING,
        object_kind STRING,
        lifecycle_status STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS TermLabel(
        term_label_id STRING PRIMARY KEY,
        text STRING,
        language STRING,
        label_type STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS OntologyConstraint(
        ontology_constraint_id STRING PRIMARY KEY,
        constraint_type STRING,
        severity STRING,
        parameters STRING
    )""",
    """CREATE NODE TABLE IF NOT EXISTS OntologyProposal(
        ontology_proposal_id STRING PRIMARY KEY,
        proposal_type STRING,
        proposed_label STRING,
        proposed_definition STRING,
        proposal_status STRING,
        proposal_confidence DOUBLE
    )""",
    # ---- Resolution --------------------------------------------------------
    """CREATE NODE TABLE IF NOT EXISTS ResolutionDecision(
        resolution_decision_id STRING PRIMARY KEY,
        resolution_type STRING,
        resolver_version STRING,
        resolution_confidence DOUBLE,
        resolution_status STRING
    )""",
    # ---- Reconciled knowledge ----------------------------------------------
    """CREATE NODE TABLE IF NOT EXISTS ReconciliationRun(
        reconciliation_run_id STRING PRIMARY KEY,
        reconciliation_ruleset_version STRING,
        ontology_release_id STRING,
        completed_at TIMESTAMP
    )""",
    """CREATE NODE TABLE IF NOT EXISTS CanonicalStatement(
        canonical_statement_id STRING PRIMARY KEY,
        canonical_status STRING,
        canonical_confidence DOUBLE,
        valid_from DATE,
        valid_to DATE,
        as_of_date DATE
    )""",
    # ---- Derived application output ----------------------------------------
    """CREATE NODE TABLE IF NOT EXISTS Finding(
        finding_id STRING PRIMARY KEY,
        finding_type STRING,
        finding_status STRING,
        finding_confidence DOUBLE,
        ruleset_version STRING,
        created_at TIMESTAMP
    )""",
)
