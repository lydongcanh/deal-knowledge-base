"""Lifecycle of a derived Finding."""

from enum import StrEnum


class FindingStatus(StrEnum):
    """Values are not enumerated in the schema doc; these are the minimum
    needed for findings to be recomputed without losing reviewer intent."""

    OPEN = "open"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"
