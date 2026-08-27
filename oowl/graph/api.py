import networkx as nx
from typing import Tuple, List
from oowl.graph.builder.graph_builder import GraphBuilder
from oowl.graph.analyzer.network_path_analyzer import NetworkPathAnalyzer
from oowl.graph.models.network_path import DiscoveredNetworkPath

def analyze_topology(model: 'InfrastructureModel') -> Tuple[nx.MultiDiGraph, List[DiscoveredNetworkPath]]:
    """
    Main API for the Graph Engine boundary.
    
    Args:
        model: Read-only InfrastructureModel from the Ingestion boundary (oowl.core.models.infrastructure).
        
    Returns:
        A tuple containing the deterministic topological graph and a list of discovered network paths.
    """
    graph = GraphBuilder.build(model)
    paths = NetworkPathAnalyzer.analyze(graph)
    
    return graph, paths

