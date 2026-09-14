"""What ontology change an OntologyProposal requests."""

from enum import StrEnum


class ProposalType(StrEnum):
    NEW_CONCEPT = "new_concept"
    NEW_PREDICATE = "new_predicate"
    NEW_ALIAS = "new_alias"
    NEW_MAPPING = "new_mapping"
    NEW_CONSTRAINT = "new_constraint"
