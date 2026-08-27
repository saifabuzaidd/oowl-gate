from typing import List, Tuple
import networkx as nx
from oowl.graph.models.network_path import DiscoveredNetworkPath
from oowl.risk.models.finding import SecurityFinding
from oowl.risk.models.attack_path import AttackPath
from oowl.risk.rules.base_rule import SecurityRule

class InternetToCriticalRule(SecurityRule):
    @property
    def rule_id(self) -> str:
        return "RISK-001-INTERNET-TO-CRITICAL"

    def evaluate(
        self, graph: nx.MultiDiGraph, paths: List[DiscoveredNetworkPath]
    ) -> Tuple[List[SecurityFinding], List[AttackPath]]:
        
        attack_paths = []
        
        for path_obj in paths:
            # Fallback for dynamic path property resolution
            node_list = getattr(path_obj, 'path', getattr(path_obj, 'nodes', []))
            
            if not node_list:
                continue
                
            source_node = node_list[0]
            target_node = node_list[-1]
            
            # Read-only access to graph attributes
            source_attrs = graph.nodes.get(source_node, {})
            target_attrs = graph.nodes.get(target_node, {})
            
            # Deterministic rule logic
            is_public = source_attrs.get("is_public", False)
            sensitivity = target_attrs.get("sensitivity", "low")
            
            if is_public and sensitivity == "high":
                finding = SecurityFinding(
                    rule_id=self.rule_id,
                    title="Public Access to Critical Resource",
                    description=f"Path exists from public node '{source_node}' to highly sensitive node '{target_node}'.",
                    severity="CRITICAL",
                    node_id=target_node
                )
                attack_paths.append(AttackPath(path=path_obj, finding=finding))
                
        return ([], attack_paths)
