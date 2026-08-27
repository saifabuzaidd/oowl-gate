import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from oowl.pipeline.main import run_security_pipeline

def write_detailed_log(results: dict, log_file: str):
    """
    Extracts execution results from the pipeline and writes a detailed report to a log file.
    """
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== OWL-GATE PIPELINE EXECUTION LOG ===\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*40 + "\n\n")

        # ---------------------------------------------------------
        # STAGE 1 (Ingestion)
        # ---------------------------------------------------------
        f.write("### STAGE 1: INGESTION (Infrastructure Model) ###\n")
        model = results.get("infrastructure_model")
        if model:
            f.write(f"Total Resources Parsed: {len(model.resources)}\n")
            for res in model.resources:
                f.write(f"  - Resource: [{res.type}] {res.id}\n")

            f.write(f"\nTotal Relationships Parsed: {len(model.relationships)}\n")
            for rel in model.relationships:
                f.write(f"  - Link: {rel.source} --({rel.relationship_type})--> {rel.target}\n")
        else:
            f.write("No Infrastructure Model returned.\n")
        f.write("-" * 40 + "\n\n")

        # ---------------------------------------------------------
        # STAGE 2 (Graph Engine)
        # ---------------------------------------------------------
        f.write("### STAGE 2: GRAPH ENGINE (Topology & Paths) ###\n")
        graph = results.get("topology_graph")
        paths = results.get("network_paths")

        if graph is not None and paths is not None:
            f.write(f"Graph Created: {graph.number_of_nodes()} Nodes, {graph.number_of_edges()} Edges.\n")

            f.write(f"\nDiscovered Network Paths ({len(paths)} found):\n")
            for i, p in enumerate(paths, 1):
                path_list = getattr(p, 'nodes', getattr(p, 'path', []))
                path_str = " -> ".join(path_list)
                f.write(f"  [Path {i}]: {path_str}\n")
        else:
            f.write("No Graph or Paths returned.\n")
        f.write("-" * 40 + "\n\n")

        # ---------------------------------------------------------
        # STAGE 3 (Risk Engine)
        # ---------------------------------------------------------
        f.write("### STAGE 3: RISK ENGINE (Findings & Attack Paths) ###\n")
        risk_report = results.get("risk_report")

        if risk_report:
            f.write(f"Overall Risk Score: {getattr(risk_report, 'overall_risk_score', 0.0)} / 100\n\n")

            f.write(f"Isolated Findings ({len(risk_report.findings)} found):\n")
            for fnd in risk_report.findings:
                f.write(f"  - [{fnd.severity}] {fnd.rule_id} on '{fnd.node_id}':\n")
                f.write(f"      Description: {fnd.description}\n")

            f.write(f"\nConfirmed Attack Paths ({len(risk_report.attack_paths)} found):\n")
            for ap in risk_report.attack_paths:
                path_list = getattr(ap.path, 'nodes', getattr(ap.path, 'path', []))
                path_str = " -> ".join(path_list)
                f.write(f"  - [{ap.finding.severity}] {ap.finding.rule_id}:\n")
                f.write(f"      Target: {ap.finding.node_id}\n")
                f.write(f"      Path: {path_str}\n")
                f.write(f"      Description: {ap.finding.description}\n")
        else:
            f.write("No Risk Report returned.\n")
        f.write("-" * 40 + "\n\n")

        # ---------------------------------------------------------
        # STAGE 4 (AI Reasoning Layer) 
        # ---------------------------------------------------------
        f.write("### STAGE 4: AI REASONING LAYER ###\n")
        ai_assessment = results.get("ai_assessment")

        if ai_assessment:
            hacker = getattr(ai_assessment, "hacker_analysis", None)
            if hacker:
                f.write("[RED TEAM - VIRTUAL HACKER]\n")
                f.write(f"  Exploitability Score: {getattr(hacker, 'exploitability_score', 'N/A')}/10\n")
                f.write(f"  Narrative: {getattr(hacker, 'narrative', 'N/A')}\n")

                lateral_steps = getattr(hacker, 'lateral_movement_steps', [])
                if lateral_steps:
                    f.write("  Lateral Movement Steps:\n")
                    for step in lateral_steps:
                        f.write(f"    -> {step}\n")
                f.write("\n")

            reviewer = getattr(ai_assessment, "reviewer_analysis", None)
            if reviewer:
                f.write("[BLUE TEAM - AI REVIEWER]\n")
                f.write(f"  Executive Summary: {getattr(reviewer, 'executive_summary', 'N/A')}\n")
                f.write(f"  Policy Drift Detected: {getattr(reviewer, 'policy_drift_detected', False)}\n\n")

                remediations = getattr(reviewer, 'remediations', [])
                if remediations:
                    f.write("  Remediations:\n")
                    for r in remediations:
                        f.write(f"    - Target Resource: {getattr(r, 'resource_name', 'Unknown')}\n")
                        f.write(f"      Explanation: {getattr(r, 'explanation', 'No explanation')}\n")
                        f.write(f"      Suggested Code Fix:\n")
                        code = getattr(r, 'suggested_code', '')
                        for line in code.split('\n'):
                            f.write(f"          {line}\n")
                        f.write("\n")
        else:
            f.write("No AI Assessment returned.\n")
        f.write("-" * 40 + "\n\n")

        # ---------------------------------------------------------
        # STAGE 5 (Decision & Enforcement Layer) 
        # ---------------------------------------------------------
        f.write("### STAGE 5: DECISION & ENFORCEMENT LAYER ###\n")
        decision = results.get("decision")
        
        if decision:
            status = getattr(decision.decision_status, 'value', str(decision.decision_status)) if hasattr(decision, 'decision_status') else "UNKNOWN"
            f.write(f"Decision Status: {status}\n")
            f.write(f"Exit Code: {decision.exit_code}\n")
            f.write(f"Composite Risk Index (CRI): {decision.composite_risk_index:.2f} / 100\n\n")
            
            f.write("Reasons & Findings:\n")
            if decision.blocking_reasons:
                for reason in decision.blocking_reasons:
                    f.write(f"  - {reason}\n")
            else:
                f.write("  - No blocking issues or risk threshold violations found.\n")
                
            f.write("\nEvidence Artifacts Generated:\n")
            if hasattr(decision, 'evidence_artifacts') and decision.evidence_artifacts:
                for artifact_key in decision.evidence_artifacts.keys():
                    f.write(f"  - {artifact_key}\n")
        else:
            f.write("No Decision returned.\n")

        f.write("\n" + "="*40 + "\n")
        f.write("END OF LOG\n")

def run():
    parser = argparse.ArgumentParser(description="Run OOWL-GATE E2E Test Pipeline")
    parser.add_argument(
        "target_dir", 
        nargs="?", 
        default="labs_for_test/lab1", 
        help="Path to the target IaC directory (e.g., labs_for_test/lab3)"
    )
    args = parser.parse_args()

    iac_source_dir = args.target_dir
    log_file = "pipeline_execution.log"

    if not os.path.exists(iac_source_dir):
        print(f"[-] Error: Target directory '{iac_source_dir}' does not exist!")
        sys.exit(1)

    print(f"[*] Starting E2E Test with IaC directory: {iac_source_dir}")

    try:
        pipeline_results = run_security_pipeline(iac_source=iac_source_dir)
        write_detailed_log(pipeline_results, log_file)

        print(f"\n[+] Pipeline executed successfully!")
        print(f"[+] Detailed execution log saved to: {log_file}")

        decision = pipeline_results.get("decision")
        if decision:
            print(f"[*] Pipeline exiting with OS Code: {decision.exit_code}")
            sys.exit(decision.exit_code)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"\n[-] Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run()

