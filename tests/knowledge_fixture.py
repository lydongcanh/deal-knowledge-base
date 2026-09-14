"""Builds a minimal, fully valid slice of the knowledge base.

Mirrors the worked example in the schema doc: a Credit Agreement whose
clause 14.2 requires the consent of BigBank on a change of control.
"""

from deal_kb.graph import GraphStore
from deal_kb.graph.vocabulary import (
    AssertionMode,
    ClaimStatus,
    ConceptKind,
    LifecycleStatus,
    LocatorType,
    ObjectKind,
    Polarity,
)


def build_valid_claim(store: GraphStore) -> None:
    """Create one Claim satisfying every non-negotiable invariant."""
    store.execute("CREATE (:DataRoom {data_room_id:'room-1'})")
    store.execute("CREATE (:Document {document_id:'doc-1'})")
    store.execute("CREATE (:DocumentFile {document_file_id:'file-1'})")
    store.execute("""MATCH (r:DataRoom {data_room_id:'room-1'}),
                           (d:Document {document_id:'doc-1'})
                     CREATE (r)-[:CONTAINS_DOCUMENT]->(d)""")
    store.execute("""MATCH (d:Document {document_id:'doc-1'}),
                           (f:DocumentFile {document_file_id:'file-1'})
                     CREATE (d)-[:HAS_FILE]->(f)""")

    store.execute(
        f"""CREATE (:Evidence {{evidence_id:'ev-1',
            locator_type:'{LocatorType.PDF_REGION}',
            locator:'{{"page": 48, "start_offset": 1052, "end_offset": 1244}}',
            excerpt:'...requires the prior written consent of the Lender...'}})"""
    )
    store.execute("""MATCH (e:Evidence {evidence_id:'ev-1'}),
                           (f:DocumentFile {document_file_id:'file-1'})
                     CREATE (e)-[:FROM_FILE]->(f)""")

    store.execute("""CREATE (:ExtractionRun {extraction_run_id:'run-1',
        extractor_version:'0.1.0', model_id:'claude-opus-5', prompt_version:'p1',
        extraction_schema_version:'1', ontology_release_id:'onto-1'})""")
    store.execute("""MATCH (r:ExtractionRun {extraction_run_id:'run-1'}),
                           (f:DocumentFile {document_file_id:'file-1'})
                     CREATE (r)-[:PROCESSED]->(f)""")

    store.execute("CREATE (:OntologyRelease {ontology_release_id:'onto-1', version:'0.1'})")
    for concept_id, label, kind in (
        ("cpt-clause", "ChangeOfControlClause", ConceptKind.CLAUSE_TYPE),
        ("cpt-org", "Organization", ConceptKind.ENTITY_TYPE),
    ):
        store.execute(
            f"""CREATE (:Concept {{concept_id:'{concept_id}', preferred_label:'{label}',
                definition:'', concept_kind:'{kind}',
                lifecycle_status:'{LifecycleStatus.CANONICAL}'}})"""
        )
        store.execute(f"""MATCH (c:Concept {{concept_id:'{concept_id}'}}),
                               (o:OntologyRelease {{ontology_release_id:'onto-1'}})
                         CREATE (c)-[:DEFINED_IN]->(o)""")

    store.execute(
        f"""CREATE (:Predicate {{predicate_id:'prd-consent',
            preferred_label:'requiresConsentFrom', definition:'',
            object_kind:'{ObjectKind.ENTITY}',
            lifecycle_status:'{LifecycleStatus.CANONICAL}'}})"""
    )

    for entity_id, name, concept_id in (
        ("ent-clause", "Clause 14.2", "cpt-clause"),
        ("ent-bank", "BigBank", "cpt-org"),
    ):
        store.execute(f"CREATE (:Entity {{entity_id:'{entity_id}', canonical_name:'{name}'}})")
        store.execute(f"""MATCH (e:Entity {{entity_id:'{entity_id}'}}),
                               (r:DataRoom {{data_room_id:'room-1'}})
                         CREATE (e)-[:IN_DATA_ROOM]->(r)""")
        store.execute(f"""MATCH (e:Entity {{entity_id:'{entity_id}'}}),
                               (c:Concept {{concept_id:'{concept_id}'}})
                         CREATE (e)-[:INSTANCE_OF]->(c)""")

    store.execute(
        f"""CREATE (:Claim {{claim_id:'claim-1', polarity:'{Polarity.POSITIVE}',
            assertion_mode:'{AssertionMode.ASSERTED}', extraction_confidence:0.92,
            claim_status:'{ClaimStatus.ACTIVE}'}})"""
    )
    for target, rel in (
        ("DataRoom {data_room_id:'room-1'}", "IN_DATA_ROOM"),
        ("Entity {entity_id:'ent-clause'}", "HAS_SUBJECT"),
        ("Predicate {predicate_id:'prd-consent'}", "USES_PREDICATE"),
        ("Entity {entity_id:'ent-bank'}", "HAS_OBJECT_ENTITY"),
        ("Evidence {evidence_id:'ev-1'}", "SUPPORTED_BY"),
        ("ExtractionRun {extraction_run_id:'run-1'}", "GENERATED_BY"),
    ):
        store.execute(
            f"MATCH (c:Claim {{claim_id:'claim-1'}}), (t:{target}) CREATE (c)-[:{rel}]->(t)"
        )
