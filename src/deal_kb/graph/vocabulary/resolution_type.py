"""What kind of target a ResolutionDecision selected."""

from enum import StrEnum


class ResolutionType(StrEnum):
    ENTITY = "entity"
    CONCEPT = "concept"
    PREDICATE = "predicate"
    VALUE = "value"
