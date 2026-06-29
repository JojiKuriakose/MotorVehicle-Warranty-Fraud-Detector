from pathlib import Path
from langchain_core.prompts import PromptTemplate
from src.state import ClaimState
from src.utils.llm_util import llm
from src.utils.policy_util import policy_text

# Load fraud scoring agent prompt template
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
with open(PROMPTS_DIR / "v1_fraud_score_prompt.txt", "r") as f:
    fraud_score_prompt_template_str = f.read()

fraud_score_prompt_template = PromptTemplate(
    template=fraud_score_prompt_template_str,
    input_variables=["policy_text", "claim", "policy_check"],
    template_format="f-string"
)


# 2. Fraud Scoring Agent
def fraud_scoring_agent(state: ClaimState) -> ClaimState:
    claim = state["claim"]
    policy_check = state.get("policy_check", "")

    prompt = fraud_score_prompt_template.format(
        policy_text=policy_text,
        claim=claim,
        policy_check=policy_check
    )
    
    
    response = llm.invoke(prompt)
    res_text = response.content.strip()
    try:
        score = float(res_text)
    except:
        score = 0.5
    state.setdefault("trace", []).append({
        "agent": "fraud_scoring_agent",
        "prompt": prompt,
        "response": res_text,
    })
    state["fraud_score"] = score
    return state
