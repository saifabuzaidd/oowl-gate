from typing import List, Tuple
import networkx as nx
from oowl.graph.models.network_path import DiscoveredNetworkPath
from oowl.risk.models.finding import SecurityFinding
from oowl.risk.models.attack_path import AttackPath
from oowl.risk.rules.base_rule import SecurityRule

class UnencryptedTransitRule(SecurityRule):
    @property
    def rule_id(self) -> str:
        return "RISK-002-UNENCRYPTED-TRANSIT"

    def evaluate(
        self, graph: nx.MultiDiGraph, paths: List[DiscoveredNetworkPath]
    ) -> Tuple[List[SecurityFinding], List[AttackPath]]:
        
        findings = []
        
        # Iterating over edges in the graph deterministically without mutation
        for u, v, key, data in graph.edges(keys=True, data=True):
            protocol = data.get("protocol", "unknown").upper()
            is_encrypted = data.get("is_encrypted", False)
            
            if protocol in ["HTTP", "TELNET", "FTP"] and not is_encrypted:
                finding = SecurityFinding(
                    rule_id=self.rule_id,
                    title="Unencrypted Transit Protocol",
                    description=f"Unencrypted traffic ({protocol}) allowed from '{u}' to '{v}'.",
                    severity="HIGH",
                    node_id=u
                )
                findings.append(finding)
                
        return (findings, [])

