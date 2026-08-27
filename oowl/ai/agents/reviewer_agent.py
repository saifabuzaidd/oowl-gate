"""AI Reviewer Agent module for executing Blue Team IaC remediation and policy audit."""

import json
import logging
import re
import time
from typing import Any, Dict, List

from oowl.ai.adapters.llm_provider import BaseLLMProvider
from oowl.ai.models import Remediation, ReviewerAnalysis

logger = logging.getLogger(__name__)


class AIReviewer:
    """Simulates Blue Team defensive review, policy drift analysis, and remediation generation."""

    SYSTEM_PROMPT = (
        "You are an AI Reviewer (Blue Team Security Architect). Analyze the provided IaC "
        "and risk report to detect policy drifts and formulate remediation plans. "
        "Return ONLY a valid raw JSON object with keys: "
        "'executive_summary' (string), "
        "'policy_drift_detected' (boolean), and "
        "'remediations' (list of objects with keys: 'resource_name', 'explanation', 'suggested_code'). "
        "Do not include markdown blocks, intros, or extraneous explanations."
    )

    def __init__(self, provider: BaseLLMProvider) -> None:
        """Initialize the AIReviewer agent with a designated LLM provider.

        Args:
            provider: Concrete implementation of BaseLLMProvider.
        """
        self.provider = provider

    def analyze(
        self,
        raw_iac: str,
        infra_model: Any,
        graph: Any,
        risk_report: Any,
        retries: int = 2,
        backoff_seconds: float = 1.0,
    ) -> ReviewerAnalysis:
        """Perform defensive review and policy verification with automatic retry capability.

        Args:
            raw_iac: Raw string content of the IaC file(s).
            infra_model: Parsed infrastructure model topology.
            graph: Graph engine network topology model.
            risk_report: Evaluation output from the deterministic risk engine.
            retries: Maximum number of execution retries upon model or parsing errors.
            backoff_seconds: Delay duration in seconds between retries.

        Returns:
            ReviewerAnalysis populated with structured remediations or fallback defaults.
        """
        user_content = f"RAW IAC:\n{raw_iac}\n\nRISK REPORT:\n{str(risk_report)}"

        for attempt in range(retries + 1):
            try:
                response = self.provider.generate_response(
                    system_prompt=self.SYSTEM_PROMPT, user_content=user_content
                )
                data = self._parse_json_payload(response)

                remediations_raw = data.get("remediations", [])
                remediations: List[Remediation] = []
                for item in remediations_raw:
                    if isinstance(item, dict):
                        res_name = item.get("resource_name") or item.get("target_resource") or ""
                        sug_code = item.get("suggested_code") or item.get("suggested_code_fix") or ""
                        remediations.append(
                            Remediation(
                                resource_name=str(res_name),
                                explanation=str(item.get("explanation", "")),
                                suggested_code=str(sug_code),
                            )
                        )

                return ReviewerAnalysis(
                    executive_summary=str(data.get("executive_summary", "No summary provided.")),
                    policy_drift_detected=bool(data.get("policy_drift_detected", False)),
                    remediations=remediations,
                )
            except Exception as exc:
                logger.warning(
                    "AIReviewer analysis attempt %d/%d failed: %s",
                    attempt + 1,
                    retries + 1,
                    exc,
                )
                if attempt < retries:
                    time.sleep(backoff_seconds)

        logger.error("AIReviewer failed all %d execution attempts.", retries + 1)
        return ReviewerAnalysis(
            executive_summary="Failed to extract structured response from model output.",
            policy_drift_detected=False,
            remediations=[],
        )

    @staticmethod
    def _parse_json_payload(raw_response: str) -> Dict[str, Any]:
        """Extract and parse a JSON dictionary from raw model text response.

        Args:
            raw_response: Unfiltered text output from LLM provider.

        Returns:
            Parsed dictionary representing the structured JSON object.

        Raises:
            ValueError: If no valid JSON payload pattern is found.
            json.JSONDecodeError: If JSON decoding fails.
        """
        text = (raw_response or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON payload structure detected in model response.")
        return json.loads(match.group(0))
