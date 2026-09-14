"""Role a TermLabel plays for its Concept or Predicate."""

from enum import StrEnum


class LabelType(StrEnum):
    PREFERRED = "preferred"
    ALIAS = "alias"
    ABBREVIATION = "abbreviation"
    LEGACY = "legacy"
