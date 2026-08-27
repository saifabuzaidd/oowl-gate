import networkx as nx
from typing import List
from oowl.graph.models.network_path import DiscoveredNetworkPath

class NetworkPathAnalyzer:
    @staticmethod
    def analyze(graph: nx.MultiDiGraph) -> List[DiscoveredNetworkPath]:
        """
        Discovers network topological paths deterministically.
        Extracts paths from entry nodes (in-degree 0) to exit nodes (out-degree 0).
        """
        discovered_paths = []
        
        # Identify logical entry and exit points deterministically
        entry_nodes = sorted([n for n, d in graph.in_degree() if d == 0])
        exit_nodes = sorted([n for n, d in graph.out_degree() if d == 0])
        
        for start_node in entry_nodes:
            for end_node in exit_nodes:
                if start_node != end_node and nx.has_path(graph, start_node, end_node):
                    # all_simple_paths prevents infinite loops in cyclic topologies
                    for raw_path in nx.all_simple_paths(graph, start_node, end_node):
                        discovered_paths.append(DiscoveredNetworkPath(path=raw_path))
                        
        # Ensure deterministic output ordering for downstream consumers
        # Sort primarily by path length, secondarily by alphabetical node order
        discovered_paths.sort(key=lambda p: (len(p.path), p.path))
        
        return discovered_paths

