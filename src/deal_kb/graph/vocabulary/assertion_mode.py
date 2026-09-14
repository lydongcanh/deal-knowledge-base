"""How strongly a source commits to a Claim."""

from enum import StrEnum


class AssertionMode(StrEnum):
    """Prevents forecasts, intentions and estimates being treated as fact."""

    ASSERTED = "asserted"
    REPORTED = "reported"
    ESTIMATED = "estimated"
    FORECAST = "forecast"
    INTENDED = "intended"
    POSSIBLE = "possible"
    HYPOTHETICAL = "hypothetical"

    @classmethod
    def factual(cls) -> frozenset["AssertionMode"]:
        """Modes that may be materialised as established fact."""
        return frozenset({cls.ASSERTED, cls.REPORTED})
