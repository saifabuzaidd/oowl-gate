from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class SecurityContext:
    """Canonical representation of a resource's security properties."""
    exposure: str = "UNKNOWN"
    sensitivity: str = "UNKNOWN"

@dataclass
class Resource:
    """Canonical representation of an infrastructure resource."""
    id: str
    type: str
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    security_context: SecurityContext = field(default_factory=SecurityContext)

@dataclass
class Relationship:
    """Canonical representation of a directed relationship between two resources."""
    source: str
    target: str
    relationship_type: str

@dataclass
class InfrastructureModel:
    """The unified, normalized infrastructure model passed to downstream engines."""
    resources: List[Resource] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
