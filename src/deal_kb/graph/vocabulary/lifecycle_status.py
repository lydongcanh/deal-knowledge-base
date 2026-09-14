"""Governance state of an ontology term."""

from enum import StrEnum


class LifecycleStatus(StrEnum):
    """Applies to both Concept and Predicate."""

    CANONICAL = "canonical"
    PROVISIONAL = "provisional"
    DEPRECATED = "deprecated"
    MAPPED = "mapped"
    REJECTED = "rejected"

    @classmethod
    def usable_for_extraction(cls) -> frozenset["LifecycleStatus"]:
        """Terms new extraction may legitimately use."""
        return frozenset({cls.CANONICAL, cls.PROVISIONAL})
