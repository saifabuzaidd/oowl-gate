import os
from typing import Any

from oowl.ai.orchestrator.ai_orchestrator import AIOrchestrator
from oowl.ai.models import AIAssessment
from oowl.ai.adapters.llm_provider import (
    GeminiProvider,
    MockLLMProvider,
    FallbackLLMProvider
)


def _load_env_file(env_path: str = ".env") -> None:
    """
    Reads key-value pairs from a local .env file and sets environment variables.
    Requires no external dependencies.
    """
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip("'\""))


# Automatically load local environment variables upon module import
_load_env_file()


def _build_llm_chain() -> FallbackLLMProvider:
    """
    Constructs the LLM fallback chain, prioritizing Gemini if an API key is provided.
    """
    providers = []

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            providers.append(GeminiProvider(api_key=gemini_key))
        except Exception as e:
            print(f"[AI Config] Failed to initialize Gemini provider: {e}")

    providers.append(MockLLMProvider())

    return FallbackLLMProvider(providers)


def run_ai_assessment(
    iac_directory_path: str,
    infrastructure_model: Any,
    topology_graph: Any,
    risk_report: Any
) -> AIAssessment:
    """
    Executes AI-assisted reasoning over the parsed infrastructure, topology, and risk models.
    """
    smart_provider = _build_llm_chain()
    orchestrator = AIOrchestrator(smart_provider)

    return orchestrator.run(
        iac_directory_path=iac_directory_path,
        infrastructure_model=infrastructure_model,
        topology_graph=topology_graph,
        risk_report=risk_report
    )
