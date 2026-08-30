<!-- ===================================================================== -->
<!-- PROJECT DOCUMENTATION METADATA                                        -->
<!-- Project: OOWL-GATE | Version: 1.0.0 | Date: 2026-08-27               -->
<!-- Authors: Saif AbuZaid, Ahmed Kandil, Malek Mostafa                    -->
<!-- Repository: https://github.com/saifabuzaidd/oowl-gate                 -->
<!-- License: MIT License                                                  -->
<!-- ===================================================================== -->

# 🦉 OOWL-GATE: AI-Augmented IaC Security Intelligence Engine

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-orange.svg)](#-architectural-framework) [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/saifabuzaidd/oowl-gate/actions)

**OOWL-GATE** is a security intelligence engine designed to detect logical exploit paths, contextual access misconfigurations, and multi-hop attack vectors in Infrastructure-as-Code (IaC). 

Unlike traditional static analysis tools that rely solely on isolated pattern-matching rules, OOWL-GATE parses IaC declarations into a directed topology graph. It evaluates graph topologies using a hybrid analysis model: a deterministic rule engine paired with an autonomous multi-agent AI reasoning engine (Red Team / Blue Team dynamics).

---

## 🏗️ Architectural Framework

OOWL-GATE follows the **Ports and Adapters (Hexagonal Architecture)** design pattern. Core domain logic is decoupled from presentation layers, CLI entry points, and CI/CD execution environments.

```text
                    ┌──────────────────────────────┐
                    │      INPUT TARGET IaC        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │   OOWL CORE ENGINE (BOUND)   │
                    │                              │
                    │ Ingestion ──► Graph ──► Risk │
                    │                   ▲      │   │
                    │                   │      ▼   │
                    │ Decision  ◄───────┴───  AI   │
                    └──────────────┬───────────────┘
                                   │
                             PipelineResult
                                   │
                                   ▼
                             ┌───────────┐
                             │    CLI    │
                             │  Adapter  │
                             └───────────┘

```

Core Design Principles:
Canonical Data Contracts: Internal stages communicate via immutable, strongly typed data contracts, preventing untyped dictionary mutations across boundaries.
Unified Output Schema (PipelineResult): Downstream presentation adapters consume a single, normalized result model.
Deterministic Baseline, AI Augmented: Base risk scoring remains fully reproducible through static rule validation, while the AI layer enriches findings with exploitability verification and code-level remediation.
Resilient Provider Fallback: The AI orchestration layer features automated provider failover (e.g., fallback to Google Gemini if primary LLM endpoints encounter rate limits).

⚙️ Analysis Pipeline Stages

The evaluation lifecycle processes target manifests through six distinct pipeline phases:

```text
[ Target IaC ]
     │
     ▼
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌───────────────┐    ┌──────────────┐    ┌───────────┐
│ Stage 0  │──► │  Stage 1  │──► │  Stage 2  │──► │    Stage 3    │──► │   Stage 4    │──► │  Stage 5  │
│ Target   │    │ Ingestion │    │ Graph     │    │ Deterministic │    │ AI Cognitive │    │ Decision  │
│ Resolver │    │ Engine    │    │ Topology  │    │ Risk Engine   │    │ Engine       │    │ Engine    │
└──────────┘    └───────────┘    └───────────┘    └───────────────┘    └──────────────┘    └───────────┘
                                                                                                 │
                                                                                           PipelineResult

```

Stage 0: Target Resolution & Input Boundary (oowl/ingestion/) Isolates supported infrastructure definitions (.tf, .tf.json), ignores state/cache artifacts (.terraform/), and constructs the execution scope.

Stage 1: Ingestion & Infrastructure Normalization (oowl/ingestion/adapters/terraform/) Parses HCL manifests into universal domain primitives (InfrastructureModel), extracting Resource entities and structural dependencies.
Stage 2: Graph Topology Engine & Attack Path Analysis (oowl/graph/) Builds a directed network graph (networkx.DiGraph) representing compute nodes, databases, storage, IAM bindings, and exposure parameters. Traverses entry points via depth-first and breadth-first algorithms to discover viable AttackPath chains.
Stage 3: Deterministic Risk Engine (oowl/risk/) Evaluates static security rules (internet_to_critical.py, unencrypted_transit.py) against graph topologies to generate contextual Finding entities and compute a baseline risk score (0.0−100.0).
Stage 4: AI Cognitive Engine (Red / Blue Dynamics) (oowl/ai/) Executes multi-agent adversarial evaluation:
Virtual Hacker Agent (hacker_agent.py): Red Team simulation evaluating real exploitability (1.0−10.0) and lateral movement potential.
AI Reviewer Agent (reviewer_agent.py): Blue Team engine synthesizing root-cause policy drift and producing functional HCL remediations.
Stage 5: Decision Engine & Enforcement (oowl/decision/) Synthesizes deterministic findings and AI evaluation metrics to calculate the Composite Risk Index (CRI) and emit gate enforcement decisions.

📊 Risk Scoring & Enforcement Model

Composite Risk Index (CRI)

The final risk index balances static topological rules with AI-validated exploitability:
CRI=(Base Risk Score×0.70)+((AI Exploitability Score×10)×0.30)

Decision Matrix & Exit Codes

| Gate Status | CRI Range | Exit Code | Action |
| --- | --- | --- | --- |
| PASS | CRI<40.0 | 0 | Pipeline execution approved for deployment. |
| WARN | 40.0≤CRI<70.0 | 2 | Manual security review required; warnings flagged. |
| FAIL | CRI≥70.0 | 1 | Deployment blocked due to critical exploit paths. |

Critical Escalation Guardrail: If the AI Exploitability Score reaches ≥8.0/10.0, the Decision Engine automatically escalates the status to WARN or FAIL, overriding low baseline static scores.

📁 Project Structure

```text
.
├── app/
│   └── run_project.py           # Pipeline runner & entry point
├── Dockerfile                   # Container build configuration
├── labs_for_test/              # Local IaC test environments & validation scenarios
│   ├── lab1/                   # High-risk lab (Public DB, SSH exposure)
│   ├── lab2/                   # Moderate-risk lab
│   └── lab3/                   # Compliant/Secure lab
├── LICENSE                      # MIT Open Source License
├── oowl/                       # Core Application Package
│   ├── ai/                     # Stage 4: AI Cognitive Domain
│   │   ├── adapters/           # Provider interface (Gemini / LLM fallback)
│   │   ├── agents/             # Hacker (Red) & Reviewer (Blue) agents
│   │   ├── models/             # AI DTO schemas
│   │   ├── orchestrator/       # AI execution pipeline conductor
│   │   └── utils/              # Context generation & IaC readers
│   ├── cli/                    # Presentation Layer: CLI interfaces
│   ├── core/                   # Canonical domain infrastructure models
│   ├── decision/               # Stage 5: CRI calculation & enforcement
│   ├── graph/                  # Stage 2: Topology engine & path traversal
│   ├── ingestion/              # Stage 1: Terraform parsing & AST mapping
│   ├── pipeline/               # Main multi-stage orchestrator
│   └── risk/                   # Stage 3: Static rule engine & findings
├── pyproject.toml              # Build dependencies & project metadata
└── README.md                   # Engine documentation

```

🚀 Quick Start

1. Installation & Environment Setup

Clone the repository and set up a Python 3.11+ virtual environment:

```bash
# Clone the repository
git clone [https://github.com/saifabuzaidd/oowl-gate.git](https://github.com/saifabuzaidd/oowl-gate.git)
cd oowl-gate

# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .

```

2. Configure API Keys

Export your Gemini API key (or primary LLM credentials):

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"

```

3. Run Pipeline Assessment

Run an analysis pipeline pass against a test lab environment:

```bash
python3 app/run_project.py labs_for_test/lab1

```

🤖 CI/CD Integration

To integrate OOWL-GATE into automated deployment workflows, configure .github/workflows/oowl-gate.yml:

```yaml
name: OOWL-GATE IaC Security Gate

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  security-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .

      - name: Execute OOWL Security Gate Scan
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python app/run_project.py labs_for_test/lab1

```

⚙️ Environment Variables

| Variable | Required | Default Model | Description |
| --- | --- | --- | --- |
| GEMINI_API_KEY | Required | gemini-3.6-flash / pro | Primary API Key used for AI Red/Blue Team reasoning engines. |

👥 Authors & Contributors
Saif AbuZaid - @saifabuzaidd | saifahmedcontact@gmail.com

Ahmed Kandil - @ATKCODING

Malek Mostafa

📜 License
Distributed under the MIT License. See LICENSE for more information.
