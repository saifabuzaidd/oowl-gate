from typing import Any, List, Set

class EvidenceVerifier:
    """
    Anti-Hallucination Guardrail: Validates AI-proposed attack paths
    against deterministic topology graphs produced by Project 02.
    """

    @staticmethod
    def verify_ai_paths(ai_assessment: Any, network_paths: List[Any]) -> float:
        if not ai_assessment:
            return 0.0

        # Extract steps correctly from hacker_analysis object
        hacker = getattr(ai_assessment, "hacker_analysis", None) or ai_assessment
        ai_steps = getattr(hacker, "lateral_movement_steps", [])
        
        if not ai_steps:
            return 1.0

        # Build a set of node names that actually exist in the infrastructure graph
        known_nodes: Set[str] = set()
        if network_paths:
            for path in network_paths:
                nodes = getattr(path, "nodes", [])
                for node in nodes:
                    known_nodes.add(str(node).lower())

        if not known_nodes:
            return 1.0

        # Verify that the AI's textual steps mention actual components of the graph
        valid_steps = 0
        total_ai_steps = len(ai_steps)

        for step in ai_steps:
            step_str = str(step).lower()
            # If the AI mentions any real node within its attack path step
            if any(node in step_str for node in known_nodes):
                valid_steps += 1

        if total_ai_steps == 0:
            return 1.0

        return float(valid_steps / total_ai_steps)

