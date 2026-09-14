"""One breach of a schema invariant."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Violation:
    """Identifies what rule was broken and which object broke it."""

    invariant: str
    node_id: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.invariant}] {self.node_id}: {self.detail}"
