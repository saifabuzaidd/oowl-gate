from dataclasses import dataclass
from oowl.graph.models.network_path import DiscoveredNetworkPath
from oowl.risk.models.finding import SecurityFinding

@dataclass(frozen=True)
class AttackPath:
    """
    An AttackPath is born only when a DiscoveredNetworkPath 
    matches a deterministic SecurityFinding.
    """
    path: DiscoveredNetworkPath
    finding: SecurityFinding

