"""Converts Cypher query rows into streamlit-agraph nodes/edges for rendering."""

from streamlit_agraph import Edge, Node

_COLORS = {
    "Deal": "#1f77b4",
    "Document": "#ff7f0e",
    "Entity": "#2ca02c",
    "Clause": "#9467bd",
    "RiskFlag": "#d62728",
    "Topic": "#8c564b",
}


class GraphView:
    """Builds a de-duplicated node/edge set for a streamlit-agraph render."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[tuple[str, str, str], Edge] = {}

    def add_node(self, node_id: str, label: str, node_type: str) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = Node(id=node_id, label=label, color=_COLORS.get(node_type, "#7f7f7f"), size=18)

    def add_edge(self, source: str, target: str, label: str = "") -> None:
        key = (source, target, label)
        if key not in self._edges:
            self._edges[key] = Edge(source=source, target=target, label=label)

    @property
    def nodes(self) -> list[Node]:
        return list(self._nodes.values())

    @property
    def edges(self) -> list[Edge]:
        return list(self._edges.values())
