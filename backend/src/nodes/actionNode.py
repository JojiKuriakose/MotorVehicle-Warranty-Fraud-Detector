from src.state import ClaimState
from src.utils.llm_util import llm
from src.utils.policy_util import policy_text
from langchain_core.prompts import PromptTemplate
from pathlib import Path

# Load action agent prompt template
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
with open(PROMPTS_DIR / "v1_action_agent_prompt.txt", "r") as f:
    action_prompt_template_str = f.read()

action_prompt_template = PromptTemplate(
    template=action_prompt_template_str,
    input_variables=["policy_text", "claim", "policy_check", "fraud_score", "evidence"],
    template_format="f-string"
)

#4.Action Agent
def action_agent(state: ClaimState) -> ClaimState:
    # Prefer an LLM-informed final decision that considers previous agents' outputs.
    # Build a compact prompt summarizing the claim and previous agent outputs.
    claim = state.get("claim", {})
    policy_check = state.get("policy_check", "")
    fraud_score = state.get("fraud_score", 0.0)
    evidence = state.get("evidence", "")

    prompt = action_prompt_template.format(
        policy_text=policy_text,
        claim=claim,
        policy_check=policy_check,
        fraud_score=fraud_score,
        evidence=evidence
    )

    decision_text = ""
    try:
        response = llm.invoke(prompt)
        res_text = response.content.strip()
        # Try to parse the first line as the decision
        first_line = res_text.splitlines()[0].strip()
        normalized = first_line.lower()
        if "approve" in normalized:
            decision_text = "Approve claim"
        elif "reject" in normalized:
            decision_text = "Reject claim"
        elif "escalate" in normalized or "hitl" in normalized or "human" in normalized:
            decision_text = "Escalate to HITL"
        else:
            # If parsing fails, fall back to rule-based decision
            decision_text = ""

        # Record the full LLM response in the trace
        state.setdefault("trace", []).append({
            "agent": "action_agent",
            "prompt": prompt,
            "response": res_text,
        })
    except Exception:
        # LLM failed — leave res_text empty and fall back
        res_text = ""

    # If LLM didn't produce a clear decision, use conservative rule-based fallback
    if not decision_text:
        if policy_check == "Not covered by policy":
            decision_text = "Reject claim"
        elif fraud_score > 0.5:
            decision_text = "Escalate to HITL"
        else:
            decision_text = "Approve claim"

        # record fallback decision step in trace (clear about being rule-based)
        state.setdefault("trace", []).append({
            "agent": "action_agent",
            "prompt": "(rule-based fallback)",
            "response": decision_text,
        })

    state["decision"] = decision_text
    return state
