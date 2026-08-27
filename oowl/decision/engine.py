from typing import Any, List, Tuple
from .models import PolicyContext, DecisionStatus

class DecisionEngine:
    """
    Calculates Composite Risk Index (CRI) and applies institutional thresholds.
    """

    @staticmethod
    def calculate_decision(
        risk_report: Any,
        ai_assessment: Any,
        ai_confidence: float,
        policy: PolicyContext
    ) -> Tuple[float, DecisionStatus, List[str]]:
        reasons: List[str] = []

        # 1. Deterministic Score
        det_score = 0.0
        if risk_report and hasattr(risk_report, "overall_risk_score"):
            det_score = float(risk_report.overall_risk_score)

        # 2. AI Score (Correct mapping from exploitability_score 1-10 to scale 10-100)
        raw_ai_score = 0.0
        hacker = getattr(ai_assessment, "hacker_analysis", None)
        if hacker and hasattr(hacker, "exploitability_score"):
            raw_ai_score = float(getattr(hacker, "exploitability_score", 0)) * 10.0

        validated_ai_score = raw_ai_score * ai_confidence

        if ai_confidence < 1.0 and raw_ai_score > 0:
            reasons.append(
                f"AI score downgraded from {raw_ai_score:.1f} to {validated_ai_score:.1f} "
                f"due to {round((1.0 - ai_confidence) * 100, 1)}% unverified hallucinated path steps."
            )

        # 3. Composite Risk Index
        cri = (det_score * policy.weight_deterministic) + (validated_ai_score * policy.weight_ai)

        # 4. Fail-safe Override (Prevents masking of critical logical exploits)
        if validated_ai_score >= 80.0 and cri < policy.warn_threshold:
            cri = policy.warn_threshold + 5.0
            reasons.append("CRI elevated: Critical logical exploit path detected by AI Red Team.")
            

        reviewer = getattr(ai_assessment, "reviewer_analysis", None)
        if reviewer and getattr(reviewer, "policy_drift_detected", False):
            if cri < policy.warn_threshold:
                cri = policy.warn_threshold + 5.0
                reasons.append("CRI elevated: Severe Policy Drift and misconfigurations detected by AI Blue Team.")

        # 5. Apply Thresholds
        status = DecisionStatus.PASS
        if cri >= policy.fail_threshold:
            status = DecisionStatus.FAIL
            reasons.append(
                f"Pipeline BLOCKED: Composite Risk Index ({cri:.1f}) reached critical "
                f"threshold ({policy.fail_threshold})."
            )
        elif cri >= policy.warn_threshold:
            status = DecisionStatus.WARN
            reasons.append(
                f"Pipeline WARNING: Composite Risk Index ({cri:.1f}) requires manual review "
                f"(Threshold: {policy.warn_threshold})."
            )

        return cri, status, reasons

