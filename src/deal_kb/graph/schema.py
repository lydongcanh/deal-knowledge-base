"""Cypher DDL statements defining the deal graph schema in LadybugDB."""

NODE_TABLES: list[str] = [
    """
    CREATE NODE TABLE IF NOT EXISTS Deal(
        id STRING PRIMARY KEY,
        name STRING,
        stage STRING,
        sector STRING,
        value_usd INT64
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Document(
        id STRING PRIMARY KEY,
        deal_id STRING,
        title STRING,
        doc_type STRING,
        uploaded_at STRING
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Entity(
        id STRING PRIMARY KEY,
        name STRING,
        entity_type STRING
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Clause(
        id STRING PRIMARY KEY,
        document_id STRING,
        clause_type STRING,
        text STRING
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS RiskFlag(
        id STRING PRIMARY KEY,
        category STRING,
        severity STRING,
        description STRING
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Topic(
        id STRING PRIMARY KEY,
        name STRING
    )
    """,
]

REL_TABLES: list[str] = [
    "CREATE REL TABLE IF NOT EXISTS HasDocument(FROM Deal TO Document)",
    "CREATE REL TABLE IF NOT EXISTS InvolvesEntity(FROM Deal TO Entity, role STRING)",
    "CREATE REL TABLE IF NOT EXISTS MentionsEntity(FROM Document TO Entity, mentions INT64)",
    "CREATE REL TABLE IF NOT EXISTS ContainsClause(FROM Document TO Clause)",
    "CREATE REL TABLE IF NOT EXISTS FlaggedAs(FROM Clause TO RiskFlag)",
    "CREATE REL TABLE IF NOT EXISTS DocReferences(FROM Document TO Document, relation STRING)",
    "CREATE REL TABLE IF NOT EXISTS AboutTopic(FROM Document TO Topic)",
    "CREATE REL TABLE IF NOT EXISTS RelatedEntity(FROM Entity TO Entity, relation STRING)",
]
