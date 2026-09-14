"""Lifecycle of a reconciled CanonicalStatement."""

from enum import StrEnum


class CanonicalStatus(StrEnum):
    """`DISPUTED` lets reconciliation decline to force an answer."""

    ACCEPTED = "accepted"
    DISPUTED = "disputed"
    SUPERSEDED = "superseded"
    INVALIDATED = "invalidated"
