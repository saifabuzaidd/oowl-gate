from typing import Any, List, Dict, Optional
from .models import PolicyContext, SecurityDecision, DecisionStatus
from .evidence import EvidenceVerifier
from .engine import DecisionEngine

def evaluate_and_enforce(
    infrastructure_model: Any,
    topology_graph: Any,
    network_paths: List[Any],
    risk_report: Any,
    ai_assessment: Any,
    policy_config: Optional[Dict[str, Any]] = None,
    render_console: bool = True
) -> SecurityDecision:
    """
    Main Public Entrypoint for Project 05 (Lightweight).
    Consumes pipeline outputs, verifies AI evidence, applies decision matrix,
    and returns immutable decision object.
    """
    # 1. Initialize Policy
    policy = PolicyContext(**(policy_config or {}))

    # 2. Verify AI Evidence against Deterministic Paths
    ai_confidence = EvidenceVerifier.verify_ai_paths(ai_assessment, network_paths)

    # 3. Calculate Composite Risk Index and final decision status
    cri, status, reasons = DecisionEngine.calculate_decision(
        risk_report=risk_report,
        ai_assessment=ai_assessment,
        ai_confidence=ai_confidence,
        policy=policy
    )

    # 4. Agnostic mapping to OS exit codes
    exit_code_map = {
        DecisionStatus.PASS: 0,
        DecisionStatus.FAIL: 1,
        DecisionStatus.WARN: 2
    }

    # 5. Create immutable decision object (without SarifBuilder dependency)
    decision = SecurityDecision(
        decision_status=status,
        exit_code=exit_code_map[status],
        composite_risk_index=cri,
        blocking_reasons=reasons,
        evidence_artifacts={}  
    )

    return decision
