"""What a Predicate may point at."""

from enum import StrEnum


class ObjectKind(StrEnum):
    ENTITY = "entity"
    VALUE = "value"
    EITHER = "either"
