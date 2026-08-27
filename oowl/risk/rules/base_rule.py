from abc import ABC, abstractmethod
from typing import List, Tuple
import networkx as nx
from oowl.graph.models.network_path import DiscoveredNetworkPath
from oowl.risk.models.finding import SecurityFinding
from oowl.risk.models.attack_path import AttackPath

class SecurityRule(ABC):
    """
    Abstract Base Class for all deterministic security rules.
    Rules must not mutate the graph or the paths.
    """
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Returns the unique identifier for the rule."""
        pass

    @abstractmethod
    def evaluate(
        self, graph: nx.MultiDiGraph, paths: List[DiscoveredNetworkPath]
    ) -> Tuple[List[SecurityFinding], List[AttackPath]]:
        """
        Evaluates the infrastructure graph and paths deterministically.
        
        Args:
            graph: Read-only MultiDiGraph from the Graph Engine.
            paths: Read-only list of discovered topological paths.
            
        Returns:
            A tuple containing:
            - List of isolated SecurityFindings (node/edge specific).
            - List of AttackPaths (path specific findings).
        """
        pass

