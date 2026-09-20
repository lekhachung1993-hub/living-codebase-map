"""Reusable repository-state orchestration independent from CLI and MCP."""

from dataclasses import dataclass
import time

from .graph_cache import build_incremental_graph


@dataclass
class EngineResult:
    index: dict
    graph: dict
    index_stats: dict
    graph_stats: dict
    index_seconds: float
    graph_seconds: float


class RepositoryEngine:
    """Compose pluggable index and graph builders behind one stable contract."""

    def __init__(self, index_builder, graph_builder):
        self.index_builder = index_builder
        self.graph_builder = graph_builder

    def build(self, root_dir, index_cache_path, graph_cache_path):
        started = time.perf_counter()
        index, index_stats = self.index_builder(root_dir, index_cache_path)
        index_seconds = time.perf_counter() - started
        started = time.perf_counter()
        graph, graph_stats = build_incremental_graph(
            index,
            root_dir,
            graph_cache_path,
            index_stats,
            self.graph_builder,
        )
        graph_seconds = time.perf_counter() - started
        return EngineResult(
            index, graph, index_stats, graph_stats, index_seconds, graph_seconds,
        )
