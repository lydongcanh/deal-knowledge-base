"""Every answer traces back to source. This is the product promise."""

from deal_kb.graph import GraphStore
from knowledge_fixture import build_valid_claim


def test_claim_traces_to_document_file_and_excerpt(store: GraphStore) -> None:
    build_valid_claim(store)
    rows = store.execute(
        """
        MATCH (c:Claim)-[:HAS_SUBJECT]->(subject:Entity),
              (c)-[:USES_PREDICATE]->(predicate:Predicate),
              (c)-[:HAS_OBJECT_ENTITY]->(object:Entity),
              (c)-[:SUPPORTED_BY]->(e:Evidence)-[:FROM_FILE]->(f:DocumentFile),
              (c)-[:GENERATED_BY]->(run:ExtractionRun)
        MATCH (d:Document)-[:HAS_FILE]->(f), (room:DataRoom)-[:CONTAINS_DOCUMENT]->(d)
        RETURN room.data_room_id AS room, subject.canonical_name AS subject,
               predicate.preferred_label AS predicate, object.canonical_name AS object,
               c.polarity AS polarity, c.assertion_mode AS mode,
               f.document_file_id AS file, e.locator AS locator, e.excerpt AS excerpt,
               run.model_id AS model
        """
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["subject"] == "Clause 14.2"
    assert row["predicate"] == "requiresConsentFrom"
    assert row["object"] == "BigBank"
    assert row["polarity"] == "positive"
    assert row["file"] == "file-1"
    assert "consent of the Lender" in row["excerpt"]
    assert row["model"] == "claude-opus-5"


def test_deleting_a_file_identifies_every_dependent_claim(store: GraphStore) -> None:
    """Deletion must deterministically find what depends on a DocumentFile."""
    build_valid_claim(store)
    dependents = store.execute(
        """
        MATCH (f:DocumentFile {document_file_id:'file-1'})<-[:FROM_FILE]-(e:Evidence)
              <-[:SUPPORTED_BY]-(c:Claim)
        RETURN DISTINCT c.claim_id AS claim_id
        """
    )
    assert [r["claim_id"] for r in dependents] == ["claim-1"]
