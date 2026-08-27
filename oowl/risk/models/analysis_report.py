from dataclasses import dataclass, field
from typing import List
from oowl.risk.models.finding import SecurityFinding
from oowl.risk.models.attack_path import AttackPath

@dataclass(frozen=True)
class SecurityAnalysisReport:
    findings: List[SecurityFinding] = field(default_factory=list)
    attack_paths: List[AttackPath] = field(default_factory=list)
    risk_score: float = 0.0

