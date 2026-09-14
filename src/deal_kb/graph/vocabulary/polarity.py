"""Whether a Claim asserts or negates its predicate."""

from enum import StrEnum


class Polarity(StrEnum):
    """Distinguishes positive from negated assertions.

    Without this, "shall not compete" materialises as "shall compete".
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
