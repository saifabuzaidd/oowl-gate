from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class DecisionStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

class PolicyContext(BaseModel):
    """
    Defines organizational risk appetite and enforcement thresholds.
    """
    weight_deterministic: float = Field(default=0.7, description="Weight W1 for deterministic rules score")
    weight_ai: float = Field(default=0.3, description="Weight W2 for validated AI risk score")
    allow_ai_warnings: bool = Field(default=True, description="Whether AI findings can trigger warnings")
    fail_threshold: float = Field(default=75.0, description="CRI cutoff for pipeline hard block (FAIL)")
    warn_threshold: float = Field(default=40.0, description="CRI cutoff for pipeline soft fail (WARN)")

class SecurityDecision(BaseModel):
    """
    Immutable decision deliverable produced by Project 05.
    """
    decision_status: DecisionStatus
    exit_code: int
    composite_risk_index: float
    blocking_reasons: List[str] = Field(default_factory=list)
    evidence_artifacts: Dict[str, Any] = Field(default_factory=dict)

