"""Shared fixtures for graph knowledge base tests."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from deal_kb.graph import GraphStore, SchemaInstaller


@pytest.fixture
def store(tmp_path: Path) -> Iterator[GraphStore]:
    """An installed, empty knowledge base in a throwaway database."""
    with GraphStore(tmp_path / "test.lbdb") as graph_store:
        SchemaInstaller(graph_store).install()
        yield graph_store
