# Motor Vehicle Warranty Fraud Detector
### Problem Statement
The motor vehicle warranty fraud detector project aims to identify potentially fraudulent warranty claims submitted by customers. Using structured claim data and domain policies, the system should analyze each warranty claim to detect anomalies, inconsistent evidence, and policy violations that indicate fraud. The goal is to reduce false approvals, improve investigation efficiency, and protect the business from fraudulent payouts by automatically flagging suspicious claims for review.
### Solution Overview
The warranty fraud detector project is built as a modular system that evaluates warranty claims using a combination of data processing, rule-based checks, and AI-assisted reasoning.

**Key components**<br><br>
<img width="20" height="20" alt="folder" src="https://github.com/user-attachments/assets/2515f6c4-45ac-478b-876c-328763ed74bf" /> Backend

- `main.py`: orchestrates the claim evaluation workflow.
- `config/settings.py`: holds configuration and environment settings.
- `src/nodes/`\
    `actionNode.py`: decides next actions for claims based on analysis.\
    `evidenceCollectorNode.py`: gathers and validates claim evidence.\
    `fraudScoreNode.py`: computes a fraud risk score.\
    `policyCheckNode.py`: checks claims against warranty policy rules.
- `src/tools/`\
   `processClaim.py`: performs claim processing and transforms raw claim data.
- `src/utils/`\
    `llm_util.py`: integrates LLM/prompt logic for reasoning.\
    `policy_util.py`: contains policy validation helpers.
- `prompts/`: text templates for AI-guided claim evaluation and node behavior.

<img width="20" height="20" alt="folder" src="https://github.com/user-attachments/assets/2515f6c4-45ac-478b-876c-328763ed74bf" /> Frontend

- `app.py`: provides a user interface for submitting claims and reviewing fraud assessments.
- `streamlit.sh`: starts the Streamlit frontend.

**How it works**
1. A claim is ingested and preprocessed.
2. Evidence and claim fields are evaluated by the evidence collector.
3. Policy checks verify whether the claim violates warranty rules.
4. A fraud score is generated to rank risk.
5. An action node decides whether to approve, reject, or escalate the claim.
6. The frontend visualizes results and flags suspicious claims for review.

**Purpose**\
The solution helps detect suspicious warranty claims automatically, reduce fraudulent approvals, and support faster, more consistent investigation decisions.
