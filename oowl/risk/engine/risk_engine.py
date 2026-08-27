from typing import List
import networkx as nx
from oowl.graph.models.network_path import DiscoveredNetworkPath
from oowl.risk.models.analysis_report import SecurityAnalysisReport
from oowl.risk.rules.internet_to_critical import InternetToCriticalRule
from oowl.risk.rules.unencrypted_transit import UnencryptedTransitRule

class RiskEngine:
    def __init__(self):
        # Deterministically initialize the rules
        self.rules = [
            InternetToCriticalRule(),
            UnencryptedTransitRule()
        ]
        
        # Hardcoded, deterministic severity mapping for the score
        self.severity_weights = {
            "LOW": 1.0,
            "MEDIUM": 3.0,
            "HIGH": 7.0,
            "CRITICAL": 10.0
        }

    def process(self, graph: nx.MultiDiGraph, paths: List[DiscoveredNetworkPath]) -> SecurityAnalysisReport:
        all_findings = []
        all_attack_paths = []
        
        # Sequentially evaluate all injected paths and graph topologies
        for rule in self.rules:
            findings, attack_paths = rule.evaluate(graph, paths)
            all_findings.extend(findings)
            all_attack_paths.extend(attack_paths)
            
        risk_score = self._calculate_risk_score(all_findings, all_attack_paths)
        
        return SecurityAnalysisReport(
            findings=all_findings,
            attack_paths=all_attack_paths,
            risk_score=risk_score
        )
        
    def _calculate_risk_score(self, findings: list, attack_paths: list) -> float:
        score = 0.0
        
        # Calculate isolated finding scores
        for f in findings:
            score += self.severity_weights.get(f.severity.upper(), 0.0)
            
        # Calculate path-based finding scores
        for ap in attack_paths:
            score += self.severity_weights.get(ap.finding.severity.upper(), 0.0)
            
        # Cap max score to 100 deterministically 
        return min(score, 100.0)

