"""Mock deal-graph dataset used to populate the POC on first run."""

from deal_kb.graph.client import GraphStore

_DEALS = [
    {"id": "deal-1", "name": "Project Falcon", "stage": "Due Diligence", "sector": "FinTech", "value_usd": 250_000_000},
    {"id": "deal-2", "name": "Project Horizon", "stage": "Negotiation", "sector": "Healthcare", "value_usd": 90_000_000},
]

_DOCUMENTS = [
    {"id": "doc-1", "deal_id": "deal-1", "title": "Share Purchase Agreement", "doc_type": "Contract", "uploaded_at": "2026-06-01"},
    {"id": "doc-2", "deal_id": "deal-1", "title": "Financial Statements FY25", "doc_type": "Financial", "uploaded_at": "2026-06-02"},
    {"id": "doc-3", "deal_id": "deal-1", "title": "Non-Compete Addendum", "doc_type": "Contract", "uploaded_at": "2026-06-05"},
    {"id": "doc-4", "deal_id": "deal-2", "title": "Merger Agreement Draft", "doc_type": "Contract", "uploaded_at": "2026-07-11"},
    {"id": "doc-5", "deal_id": "deal-2", "title": "Regulatory Compliance Report", "doc_type": "Compliance", "uploaded_at": "2026-07-14"},
]

_ENTITIES = [
    {"id": "ent-1", "name": "Acme Capital Partners", "entity_type": "Organization"},
    {"id": "ent-2", "name": "Northwind Health Group", "entity_type": "Organization"},
    {"id": "ent-3", "name": "Jane Whitfield", "entity_type": "Person"},
    {"id": "ent-4", "name": "Marcus Lee", "entity_type": "Person"},
    {"id": "ent-5", "name": "Falcon Holdings Ltd", "entity_type": "Organization"},
]

_CLAUSES = [
    {"id": "cl-1", "document_id": "doc-1", "clause_type": "Indemnification", "text": "Seller shall indemnify Buyer for breaches of representations up to 20% of deal value."},
    {"id": "cl-2", "document_id": "doc-1", "clause_type": "Change of Control", "text": "A change of control triggers immediate repayment of outstanding loan facilities."},
    {"id": "cl-3", "document_id": "doc-3", "clause_type": "Non-Compete", "text": "Key executives are barred from competing in the FinTech sector for 24 months."},
    {"id": "cl-4", "document_id": "doc-4", "clause_type": "Termination", "text": "Either party may terminate the agreement if regulatory approval is not obtained within 180 days."},
    {"id": "cl-5", "document_id": "doc-5", "clause_type": "Compliance", "text": "Target has an open HIPAA compliance remediation item flagged by internal audit."},
]

_RISK_FLAGS = [
    {"id": "risk-1", "category": "Legal", "severity": "High", "description": "Uncapped indemnification exposure beyond typical market terms."},
    {"id": "risk-2", "category": "Financial", "severity": "Medium", "description": "Change-of-control clause may accelerate debt obligations post-close."},
    {"id": "risk-3", "category": "Regulatory", "severity": "High", "description": "Unresolved HIPAA compliance remediation could delay or block approval."},
]

_TOPICS = [
    {"id": "topic-1", "name": "Indemnification"},
    {"id": "topic-2", "name": "Regulatory Approval"},
    {"id": "topic-3", "name": "Compliance Risk"},
]


def seed(store: GraphStore) -> None:
    """Populate an empty GraphStore with the demo deal graph dataset."""
    for deal in _DEALS:
        store.execute(
            "CREATE (:Deal {id: $id, name: $name, stage: $stage, sector: $sector, value_usd: $value_usd})",
            deal,
        )
    for doc in _DOCUMENTS:
        store.execute(
            "CREATE (:Document {id: $id, deal_id: $deal_id, title: $title, doc_type: $doc_type, uploaded_at: $uploaded_at})",
            doc,
        )
        store.execute(
            "MATCH (d:Deal {id: $deal_id}), (doc:Document {id: $id}) CREATE (d)-[:HasDocument]->(doc)",
            doc,
        )
    for entity in _ENTITIES:
        store.execute(
            "CREATE (:Entity {id: $id, name: $name, entity_type: $entity_type})",
            entity,
        )
    for clause in _CLAUSES:
        store.execute(
            "CREATE (:Clause {id: $id, document_id: $document_id, clause_type: $clause_type, text: $text})",
            clause,
        )
        store.execute(
            "MATCH (doc:Document {id: $document_id}), (c:Clause {id: $id}) CREATE (doc)-[:ContainsClause]->(c)",
            clause,
        )
    for risk in _RISK_FLAGS:
        store.execute(
            "CREATE (:RiskFlag {id: $id, category: $category, severity: $severity, description: $description})",
            risk,
        )
    for topic in _TOPICS:
        store.execute("CREATE (:Topic {id: $id, name: $name})", topic)

    _seed_relationships(store)


def _seed_relationships(store: GraphStore) -> None:
    involvements = [
        ("deal-1", "ent-1", "Buyer"),
        ("deal-1", "ent-5", "Seller"),
        ("deal-1", "ent-3", "Lead Counsel"),
        ("deal-2", "ent-1", "Buyer"),
        ("deal-2", "ent-2", "Target"),
        ("deal-2", "ent-4", "Deal Lead"),
    ]
    for deal_id, entity_id, role in involvements:
        store.execute(
            "MATCH (d:Deal {id: $deal_id}), (e:Entity {id: $entity_id}) CREATE (d)-[:InvolvesEntity {role: $role}]->(e)",
            {"deal_id": deal_id, "entity_id": entity_id, "role": role},
        )

    mentions = [
        ("doc-1", "ent-1", 5), ("doc-1", "ent-5", 8), ("doc-1", "ent-3", 3),
        ("doc-2", "ent-5", 4), ("doc-3", "ent-3", 6), ("doc-3", "ent-5", 2),
        ("doc-4", "ent-1", 4), ("doc-4", "ent-2", 7), ("doc-5", "ent-2", 5), ("doc-5", "ent-4", 2),
    ]
    for doc_id, entity_id, count in mentions:
        store.execute(
            "MATCH (doc:Document {id: $doc_id}), (e:Entity {id: $entity_id}) "
            "CREATE (doc)-[:MentionsEntity {mentions: $count}]->(e)",
            {"doc_id": doc_id, "entity_id": entity_id, "count": count},
        )

    flags = [("cl-1", "risk-1"), ("cl-2", "risk-2"), ("cl-5", "risk-3")]
    for clause_id, risk_id in flags:
        store.execute(
            "MATCH (c:Clause {id: $clause_id}), (r:RiskFlag {id: $risk_id}) CREATE (c)-[:FlaggedAs]->(r)",
            {"clause_id": clause_id, "risk_id": risk_id},
        )

    references = [("doc-3", "doc-1", "amends"), ("doc-5", "doc-4", "supports")]
    for src, dst, relation in references:
        store.execute(
            "MATCH (a:Document {id: $src}), (b:Document {id: $dst}) "
            "CREATE (a)-[:DocReferences {relation: $relation}]->(b)",
            {"src": src, "dst": dst, "relation": relation},
        )

    topics = [
        ("doc-1", "topic-1"), ("doc-4", "topic-2"), ("doc-5", "topic-2"), ("doc-5", "topic-3"),
    ]
    for doc_id, topic_id in topics:
        store.execute(
            "MATCH (doc:Document {id: $doc_id}), (t:Topic {id: $topic_id}) CREATE (doc)-[:AboutTopic]->(t)",
            {"doc_id": doc_id, "topic_id": topic_id},
        )

    related_entities = [("ent-1", "ent-3", "represented_by"), ("ent-2", "ent-4", "represented_by")]
    for a, b, relation in related_entities:
        store.execute(
            "MATCH (x:Entity {id: $a}), (y:Entity {id: $b}) CREATE (x)-[:RelatedEntity {relation: $relation}]->(y)",
            {"a": a, "b": b, "relation": relation},
        )
