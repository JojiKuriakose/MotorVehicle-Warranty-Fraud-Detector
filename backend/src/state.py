from typing import TypedDict

# Define the ClaimState type
class ClaimState(TypedDict):
    claim: dict
    policy_check: str
    fraud_score: float
    evidence: str
    decision: str
    trace: list
