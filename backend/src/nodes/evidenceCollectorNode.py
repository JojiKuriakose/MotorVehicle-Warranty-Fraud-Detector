from src.state import ClaimState
from src.utils.llm_util import llm
from src.utils.policy_util import policy_text
from langchain_core.prompts import PromptTemplate
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
with open(PROMPTS_DIR / "v1_evidence_collector_prompt.txt", "r") as f:
    evidence_prompt_template_str = f.read()

evidence_prompt_template = PromptTemplate(
    template=evidence_prompt_template_str,
    input_variables=["policy_text", "claim", "fraud_score"],
    template_format="f-string"
)

# 3. Evidence Collector Agent
def evidence_collector_agent(state: ClaimState) -> ClaimState:
    claim = state["claim"]
    fraud_score= state.get("fraud_score", 0.0)

    prompt = evidence_prompt_template.format(
        policy_text=policy_text,
        claim=claim,
        fraud_score=fraud_score
    )
    
    response = llm.invoke(prompt)
    res_text = response.content.strip()
    state.setdefault("trace", []).append({
        "agent": "evidence_collector_agent",
        "prompt": prompt,
        "response": res_text,
    })
    state["evidence"] = res_text
    return state