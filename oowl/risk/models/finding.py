from dataclasses import dataclass

@dataclass(frozen=True)
class SecurityFinding:
    rule_id: str
    title: str
    description: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    node_id: str

