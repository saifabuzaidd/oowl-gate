import networkx as nx
from typing import List
from oowl.graph.models.network_path import DiscoveredNetworkPath
from oowl.risk.models.analysis_report import SecurityAnalysisReport
from oowl.risk.engine.risk_engine import RiskEngine

def analyze_risk(graph: nx.MultiDiGraph, paths: List[DiscoveredNetworkPath]) -> SecurityAnalysisReport:
    """
    Public Contract API for the Risk & Security Engine boundary.
    
    Args:
        graph: Read-only MultiDiGraph from the Graph Engine.
        paths: Read-only list of discovered topological paths.
        
    Returns:
        SecurityAnalysisReport: Immutable final output with findings and risk scores.
    """
    engine = RiskEngine()
    return engine.process(graph, paths)

