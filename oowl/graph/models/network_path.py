from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class DiscoveredNetworkPath:
    """
    Represents a normalized, deterministic network path through the infrastructure topology.
    Does NOT contain risk scores, vulnerability labels, or security severity.
    """
    path: List[str]  # Ordered list of node IDs from entry to exit

