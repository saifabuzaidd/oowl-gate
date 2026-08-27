"""AI Orchestrator module coordinating Red Team and Blue Team agents execution."""

import os
import time
from typing import Any

from oowl.ai.adapters.llm_provider import BaseLLMProvider
from oowl.ai.agents.hacker_agent import VirtualHacker
from oowl.ai.agents.reviewer_agent import AIReviewer
from oowl.ai.models import AIAssessment
from oowl.ai.utils.iac_reader import read_raw_iac


class AIOrchestrator:
    """Orchestrates security reasoning stages between adversarial and defensive agents."""

    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        """Initialize orchestrator components with shared LLM provider.

        Args:
            llm_provider: Concrete implementation of BaseLLMProvider.
        """
        self.llm_provider = llm_provider
        self.hacker = VirtualHacker(self.llm_provider)
        self.reviewer = AIReviewer(self.llm_provider)

    def run(
        self,
        iac_directory_path: str,
        infrastructure_model: Any,
        topology_graph: Any,
        risk_report: Any,
    ) -> AIAssessment:
        """Execute sequential security assessment across VirtualHacker and AIReviewer.

        Args:
            iac_directory_path: Path to target IaC source directory.
            infrastructure_model: Parsed infrastructure model topology.
            topology_graph: Network topology graph representation.
            risk_report: Output report from deterministic risk engine.

        Returns:
            AIAssessment encapsulating both Red Team and Blue Team outputs.
        """
        raw_iac_text = read_raw_iac(iac_directory_path)

        hacker_result = self.hacker.analyze(
            raw_iac_text, infrastructure_model, topology_graph, risk_report
        )

        delay = float(os.getenv("OWL_AI_DELAY", 1.5))
        if delay > 0:
            time.sleep(delay)

        reviewer_result = self.reviewer.analyze(
            raw_iac_text, infrastructure_model, topology_graph, risk_report
        )

        return AIAssessment(
            hacker_analysis=hacker_result,
            reviewer_analysis=reviewer_result,
        )
