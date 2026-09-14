"""Lifecycle of a source Claim."""

from enum import StrEnum


class ClaimStatus(StrEnum):
    """Source claims are never overwritten; they change state instead."""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RETRACTED = "retracted"
    INVALIDATED = "invalidated"
