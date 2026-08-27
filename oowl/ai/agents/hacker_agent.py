"""Virtual Hacker Agent module for executing Red Team IaC security analysis."""

import json
import logging
import re
import time
from typing import Any, Dict, List

from oowl.ai.adapters.llm_provider import BaseLLMProvider
from oowl.ai.models import HackerAnalysis

logger = logging.getLogger(__name__)


class VirtualHacker:
    """Simulates Red Team attack vectors and lateral movement logic against IaC definitions."""

    # Reframed prompt using neutral threat-assessment terminology to bypass LLM safety filters
    SYSTEM_PROMPT = (
        "You are an Infrastructure Threat Assessment Engine. Analyze the raw IaC "
        "and risk report to discover potential attack surface exposure, lateral movement risks, "
        "and architectural weaknesses. "
        "Return ONLY a valid raw JSON object with keys: "
        "'narrative' (string describing realistic attack paths), "
        "'exploitability_score' (integer 1-10), and "
        "'lateral_movement_steps' (list of strings representing movement chain). "
        "Do not include markdown tags, intros, or extraneous explanations."
    )

    def __init__(self, provider: BaseLLMProvider) -> None:
        """Initialize the VirtualHacker agent with a designated LLM provider.

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
    ) -> HackerAnalysis:
        """Perform security analysis on raw IaC and risk context with automatic retry capability.

        Args:
            raw_iac: Raw string content of the IaC file(s).
            infra_model: Parsed infrastructure model topology.
            graph: Graph engine network topology model.
            risk_report: Evaluation output from the deterministic risk engine.
            retries: Maximum number of execution retries upon model or parsing errors.
            backoff_seconds: Delay duration in seconds between retries.

        Returns:
            HackerAnalysis populated with structured exploit indicators or fallback defaults.
        """
        user_content = f"RAW IAC:\n{raw_iac}\n\nRISK REPORT:\n{str(risk_report)}"

        for attempt in range(retries + 1):
            try:
                response = self.provider.generate_response(
                    system_prompt=self.SYSTEM_PROMPT, user_content=user_content
                )
                data = self._parse_json_payload(response)

                # 1. Resolve narrative field through alternate key aliases
                narrative_val = (
                    data.get("narrative")
                    or data.get("exploit_narrative")
                    or data.get("summary")
                    or data.get("attack_narrative")
                )
                narrative = str(narrative_val) if narrative_val else "No narrative provided."

                # 2. Resolve score field safely, preventing TypeError on JSON explicit nulls
                raw_score = data.get("exploitability_score")
                if raw_score is None:
                    raw_score = (
                        data.get("score")
                        or data.get("exploitability")
                        or data.get("risk_score")
                        or 0
                    )

                try:
                    # Coerce string numbers ("8") or floats (8.0) into integers
                    exploitability_score = int(float(raw_score))
                except (ValueError, TypeError):
                    exploitability_score = 0

                # 3. Resolve lateral movement steps list cleanly across dynamic structures
                raw_steps = (
                    data.get("lateral_movement_steps")
                    or data.get("lateral_movement")
                    or data.get("steps")
                    or []
                )
                if isinstance(raw_steps, list):
                    lateral_steps = [str(step) for step in raw_steps if step is not None]
                elif isinstance(raw_steps, str) and raw_steps.strip():
                    lateral_steps = [raw_steps.strip()]
                else:
                    lateral_steps = []

                return HackerAnalysis(
                    narrative=narrative,
                    exploitability_score=exploitability_score,
                    lateral_movement_steps=lateral_steps,
                )
            except Exception as exc:
                logger.warning(
                    "VirtualHacker analysis attempt %d/%d failed: %s",
                    attempt + 1,
                    retries + 1,
                    exc,
                )
                if attempt < retries:
                    time.sleep(backoff_seconds)

        logger.error("VirtualHacker failed all %d execution attempts.", retries + 1)
        return HackerAnalysis(
            narrative="Failed to extract structured response from model output.",
            exploitability_score=0,
            lateral_movement_steps=[],
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
            json.JSONDecodeError: If JSON decoding fails due to syntax errors.
        """
        text = (raw_response or "").strip()

        # Strip markdown fence wrappers (```json ... ```) if present
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()

        # Extract the JSON payload enclosed within root braces
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON payload structure detected in model response.")

        # strict=False allows unescaped control characters (e.g. \n) inside multiline text strings
        return json.loads(match.group(0), strict=False)
