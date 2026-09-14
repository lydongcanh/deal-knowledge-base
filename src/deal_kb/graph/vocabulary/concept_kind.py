"""What category of thing a Concept describes."""

from enum import StrEnum


class ConceptKind(StrEnum):
    ENTITY_TYPE = "entity_type"
    EVENT_TYPE = "event_type"
    AGREEMENT_TYPE = "agreement_type"
    CLAUSE_TYPE = "clause_type"
    OBLIGATION_TYPE = "obligation_type"
    DOCUMENT_TYPE = "document_type"
    RISK_TYPE = "risk_type"
