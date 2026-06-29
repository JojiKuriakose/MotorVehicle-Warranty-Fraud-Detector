import pandas as pd
from typing import Optional, Callable
from src.state import ClaimState
from src.nodes.actionNode import action_agent
from src.nodes.evidenceCollectorNode import evidence_collector_agent
from src.nodes.fraudScoreNode import fraud_scoring_agent
from src.nodes.policyCheckNode import policy_check_agent

# Function to process claims
def process_claims(claims_df: pd.DataFrame, progress_callback: Optional[Callable[[int, int], None]] = None) -> pd.DataFrame:
    """Process claims and return a flattened DataFrame.

    Args:
        claims_df: input claims as a DataFrame (each row a claim)
        progress_callback: optional callable(current, total) to report progress

    Returns:
        DataFrame with original claim columns plus: policy_check, fraud_score, evidence, decision
    """
    results = []
    total = len(claims_df)
    for i, (_, claim_row) in enumerate(claims_df.iterrows(), start=1):
        claim_dict = claim_row.to_dict()
        state = ClaimState(claim=claim_dict, policy_check="", fraud_score=0.0, evidence="", decision="")
        state = policy_check_agent(state)
        state = fraud_scoring_agent(state)
        state = evidence_collector_agent(state)
        state = action_agent(state)

        # Flatten: merge original claim columns with generated outputs
        flat = dict(claim_dict)
        flat.update({
            "policy_check": state.get("policy_check", ""),
            "fraud_score": state.get("fraud_score", 0.0),
            "evidence": state.get("evidence", ""),
            "decision": state.get("decision", ""),
            "agent_trace": state.get("trace", []),
        })
        results.append(flat)

        # report progress if callback provided
        if progress_callback:
            try:
                progress_callback(i, total)
            except Exception:
                # ignore progress callback failures
                pass

    return pd.DataFrame(results)
