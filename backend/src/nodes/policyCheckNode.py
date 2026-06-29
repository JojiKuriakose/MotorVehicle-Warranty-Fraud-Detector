from pathlib import Path
from langchain_core.prompts import PromptTemplate
from src.state import ClaimState
from src.utils.llm_util import llm
from src.utils.policy_util import policy_text


# Load action agent prompt template
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
with open(PROMPTS_DIR / "v1_policy_check_prompt.txt", "r") as f:
    policy_check_prompt_template_str = f.read()

policy_check_prompt_template = PromptTemplate(
    template=policy_check_prompt_template_str,
    input_variables=["policy_text", "vtype", "claim"],
    template_format="f-string"
)

# 1. Policy Check Agent
def policy_check_agent(state: ClaimState) -> ClaimState:
    claim = state["claim"]
    vtype = "Four-Wheeler" if "Four-Wheeler" in claim["model"] else "Two-Wheeler"
    
    prompt = policy_check_prompt_template.format(
        policy_text=policy_text,
        vtype=vtype,
        claim=claim
    )
    
    response = llm.invoke(prompt)
    res_text = response.content.strip()
    state.setdefault("trace", []).append({
        "agent": "policy_check_agent",
        "prompt": prompt,
        "response": res_text,
    })
    state["policy_check"] = res_text
    return state