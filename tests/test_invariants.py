"""Each non-negotiable invariant is actually enforced.

A checker that never fires is worthless, so every test here breaks one rule and
asserts that exactly that rule is reported.
"""

import pytest

from deal_kb.graph import GraphStore, InvariantChecker
from knowledge_fixture import build_valid_claim


@pytest.fixture
def populated(store: GraphStore) -> GraphStore:
    build_valid_claim(store)
    return store


def violations_for(store: GraphStore) -> set[str]:
    return {v.invariant for v in InvariantChecker(store).check()}


def test_valid_claim_has_no_violations(populated: GraphStore) -> None:
    assert InvariantChecker(populated).check() == []


def test_claim_without_evidence_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Claim)-[r:SUPPORTED_BY]->(:Evidence) DELETE r")
    assert "claim_has_evidence" in violations_for(populated)


def test_claim_without_extraction_run_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Claim)-[r:GENERATED_BY]->(:ExtractionRun) DELETE r")
    assert "claim_has_extraction_run" in violations_for(populated)


def test_claim_outside_a_data_room_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Claim)-[r:IN_DATA_ROOM]->(:DataRoom) DELETE r")
    assert "room_scoped" in violations_for(populated)


def test_claim_without_subject_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Claim)-[r:HAS_SUBJECT]->(:Entity) DELETE r")
    assert "claim_has_one_subject" in violations_for(populated)


def test_claim_without_predicate_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Claim)-[r:USES_PREDICATE]->(:Predicate) DELETE r")
    assert "claim_has_one_predicate" in violations_for(populated)


def test_claim_without_object_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Claim)-[r:HAS_OBJECT_ENTITY]->(:Entity) DELETE r")
    assert "claim_has_one_object" in violations_for(populated)


def test_claim_with_both_object_kinds_is_reported(populated: GraphStore) -> None:
    """Exactly one object relationship is permitted: entity or value."""
    populated.execute("""CREATE (:Value {value_id:'val-1', datatype:'text',
                         canonical_value:'x'})""")
    populated.execute("""MATCH (c:Claim {claim_id:'claim-1'}), (v:Value {value_id:'val-1'})
                         CREATE (c)-[:HAS_OBJECT_VALUE]->(v)""")
    assert "claim_has_one_object" in violations_for(populated)


def test_claim_missing_modality_is_reported(populated: GraphStore) -> None:
    """Without polarity, a negated clause materialises as its opposite."""
    populated.execute("MATCH (c:Claim {claim_id:'claim-1'}) SET c.polarity = NULL")
    assert "claim_records_modality" in violations_for(populated)


def test_evidence_without_a_file_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Evidence)-[r:FROM_FILE]->(:DocumentFile) DELETE r")
    assert "evidence_has_file" in violations_for(populated)


def test_entity_without_a_concept_is_reported(populated: GraphStore) -> None:
    populated.execute("MATCH (:Entity)-[r:INSTANCE_OF]->(:Concept) DELETE r")
    assert "entity_has_concept" in violations_for(populated)


def test_canonical_statement_without_support_is_reported(populated: GraphStore) -> None:
    populated.execute("""CREATE (:CanonicalStatement {canonical_statement_id:'cs-1',
                         canonical_status:'accepted', canonical_confidence:0.9})""")
    populated.execute("""MATCH (s:CanonicalStatement {canonical_statement_id:'cs-1'}),
                               (r:DataRoom {data_room_id:'room-1'})
                         CREATE (s)-[:IN_DATA_ROOM]->(r)""")
    assert "canonical_has_support" in violations_for(populated)


def test_untraceable_projection_edge_is_reported(populated: GraphStore) -> None:
    """A domain edge with no canonical_statement_id cannot be explained."""
    populated.use_graph("domain")
    populated.execute("CREATE (:Company {name:'A'})")
    populated.execute("CREATE (:Company {name:'B'})")
    populated.execute("""MATCH (a:Company {name:'A'}), (b:Company {name:'B'})
                         CREATE (a)-[:PARTY_TO]->(b)""")
    populated.use_graph("main")
    assert "projection_traceable" in violations_for(populated)
