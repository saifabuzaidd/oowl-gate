from pydantic import BaseModel
from typing import List

class HackerAnalysis(BaseModel):
    narrative: str
    exploitability_score: int
    lateral_movement_steps: List[str]

class Remediation(BaseModel):
    resource_name: str
    suggested_code: str
    explanation: str

class ReviewerAnalysis(BaseModel):
    executive_summary: str
    policy_drift_detected: bool
    remediations: List[Remediation]

class AIAssessment(BaseModel):
    hacker_analysis: HackerAnalysis
    reviewer_analysis: ReviewerAnalysis

