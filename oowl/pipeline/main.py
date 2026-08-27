from oowl.ingestion.api import ingest
from oowl.graph.api import analyze_topology
from oowl.risk.api import analyze_risk
from oowl.ai.api import run_ai_assessment
from oowl.decision.api import evaluate_and_enforce

def run_security_pipeline(iac_source: str, policy_config: dict = None):
    """
    Main OWL-GATE Pipeline.
    Executes all engines sequentially, passing outputs as inputs in-memory.
    """

    # ---------------------------------------------------------
    # STAGE 1: INGESTION
    # ---------------------------------------------------------
    infrastructure_model = ingest(source=iac_source)
    print("[-] Ingestion Stage: Done")

    # ---------------------------------------------------------
    # STAGE 2: GRAPH CONSTRUCTION & PATH DISCOVERY
    # ---------------------------------------------------------
    topology_graph, network_paths = analyze_topology(infrastructure_model)
    print("[-] Graph Engine Stage: Done")

    # ---------------------------------------------------------
    # STAGE 3: RISK ENGINE & ATTACK PATHS
    # ---------------------------------------------------------
    risk_report = analyze_risk(topology_graph, network_paths)
    print("[-] Risk Engine Stage: Done")

    # ---------------------------------------------------------
    # STAGE 4: AI REASONING LAYER
    # ---------------------------------------------------------
    ai_assessment = run_ai_assessment(
        iac_directory_path=iac_source,
        infrastructure_model=infrastructure_model,
        topology_graph=topology_graph,
        risk_report=risk_report
    )
    print("[-] AI Reasoning Stage: Done")

    # ---------------------------------------------------------
    # STAGE 5: DECISION & ENFORCEMENT LAYER
    # ---------------------------------------------------------
    decision = evaluate_and_enforce(
        infrastructure_model=infrastructure_model,
        topology_graph=topology_graph,
        network_paths=network_paths,
        risk_report=risk_report,
        ai_assessment=ai_assessment,
        policy_config=policy_config
    )
    print("[-] Decision & Enforcement Stage: Done")

    # ---------------------------------------------------------
    # FINAL OUTPUT STATE
    # ---------------------------------------------------------
    return {
        "infrastructure_model": infrastructure_model,
        "topology_graph": topology_graph,
        "network_paths": network_paths,
        "risk_report": risk_report,
        "ai_assessment": ai_assessment,
        "decision": decision
    }
