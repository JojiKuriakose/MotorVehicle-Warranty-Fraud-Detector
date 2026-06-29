import pandas as pd
import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Fraud Detection App",
    layout="wide"
)

API_BASE_URL = st.secrets["api"]["backend_url"]

STYLE = """
<style>
.stApp {
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 40%, #f5fbff 100%);
    background-attachment: fixed;
    color: #0b1220;
}
.header {
    background: linear-gradient(90deg, rgba(14,165,167,0.12) 0%, rgba(15,23,42,0.06) 100%);
    padding: 24px 18px;
    border-radius: 10px;
    color: #071127;
    text-align: center;
    box-shadow: 0 6px 18px rgba(2,6,23,0.06);
    margin-bottom: 12px;
    border: 1px solid rgba(10,25,47,0.04);
}
.small {
    font-size: 13px;
    color: #475569;
}
.stButton>button {
    background: linear-gradient(90deg, #06b6d4, #7c3aed);
    color: white;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
    border-radius: 8px;
    box-shadow: 0 6px 14px rgba(124,58,237,0.12);
}
.stButton>button:hover {
    filter: brightness(1.03);
}
.kpi-card {
    padding: 14px;
    border-radius: 8px;
    color: white;
    text-align: center;
}
.kpi-approve {
    background: linear-gradient(90deg, #16a34a, #60a5fa);
}
.kpi-reject {
    background: linear-gradient(90deg, #ef4444, #fb923c);
}
.kpi-escalate {
    background: linear-gradient(90deg, #f59e0b, #f97316);
}
.kpi-total {
    background: linear-gradient(90deg, #e6f7ff, #eef2ff);
    color: #071127;
    box-shadow: 0 4px 10px rgba(2, 6, 23, 0.04);
    border: 1px solid rgba(10, 25, 47, 0.04);
}
</style>
"""

APP_HEADER = "Motor Vehicle Warranty Fraud Detector"
APP_SUBHEADER = "Upload warranty claims, run the detector, review results and export."

RESULTS_SESSION_KEY = "results_df"

results_df = None


def init_session_state() -> None:
    if RESULTS_SESSION_KEY not in st.session_state:
        st.session_state[RESULTS_SESSION_KEY] = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_styles() -> None:
    st.markdown(STYLE, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        f"""
        <div class="header">
            <h1 style="margin:0">{APP_HEADER}</h1>
            <div class="small">{APP_SUBHEADER}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Upload Guidance")
        #st.markdown("### Upload Guidance")
        st.markdown(
            "**:red[Upload a CSV file containing one warranty claim per row.]**"
            #":green[The detector will append policy check, fraud score, evidence, and agent decision columns.]"
        )
        st.markdown("---")
        st.markdown("### Helpful tips")
        st.info(
            "Use a clean CSV with claim descriptions and policy fields. "
            "If the detector is slow, reduce batch size or upload fewer rows."
        )
        if st.button("Clear results"):
            st.session_state[RESULTS_SESSION_KEY] = None
            st.session_state.messages = []
            st.rerun()


def render_upload_panel() -> tuple[pd.DataFrame | None, bool]:
    st.markdown("## Upload Claims file")
    uploaded_file = st.file_uploader("Choose a CSV file with warranty claims", type=["csv"])
    st.markdown(
        "<div class='small'>Expected: one claim per row. The app will add policy_check, fraud_score, evidence, and decision columns.</div>",
        unsafe_allow_html=True,
    )

    generate_button = st.button("Generate Results", key="generate", width='stretch')

    claims = None
    if uploaded_file is not None:
        try:
            claims = pd.read_csv(uploaded_file)
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

    return claims, generate_button


def render_data_preview(claims: pd.DataFrame) -> None:
    st.markdown("### Preview uploaded data")
    st.dataframe(claims.head(10), width='stretch')


def run_claim_processing(claims: pd.DataFrame) -> pd.DataFrame:
    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_cb(current: int, total: int) -> None:
        percent = int(current / total * 100)
        progress_bar.progress(percent)
        status_text.info(f"Processing {current}/{total}")

    with st.spinner("Analyzing claims — this may take a few moments..."):
        try:
            # Make API request
            api_url = f"{API_BASE_URL}"
            response = requests.post(api_url, json=claims.to_dict(orient="records"))

            if response.status_code == 200:
                response_data = response.json()

            else:
                error_msg = f"API request failed with status code {response.status_code}"
                st.error(f"❌ {error_msg}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "error": error_msg
                })

        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            st.error(f"❌ {error_msg}")
            st.session_state.messages.append({
                "role": "assistant",
                "error": error_msg 
            })
        #results_df = process_claims(claims, progress_callback=progress_callback)
        results_df = pd.DataFrame(response_data)

    progress_bar.progress(100)
    status_text.success("Processing complete...")
    return results_df


def style_decision(val: str) -> str:
    if val == "Approve claim":
        return "background-color: #d1fae5; color: #065f46"
    if val == "Reject claim":
        return "background-color: #fee2e2; color: #7f1d1d"
    if val == "Escalate to HITL":
        return "background-color: #fff7ed; color: #92400e"
    return ""


def render_results_summary(results_df: pd.DataFrame) -> None:
    st.markdown("## Results summary")
    total = len(results_df)
    approves = int((results_df["decision"] == "Approve claim").sum())
    rejects = int((results_df["decision"] == "Reject claim").sum())
    escalates = int((results_df["decision"] == "Escalate to HITL").sum())

    k1, k2, k3, k4 = st.columns([1, 1, 1, 2])
    k1.markdown(
        f"<div class='kpi-card kpi-total'><strong>Total</strong><div style='font-size:28px'>{total}</div></div>",
        unsafe_allow_html=True,
    )
    k2.markdown(
        f"<div class='kpi-card kpi-approve'><strong>Approved</strong><div style='font-size:28px'>{approves}</div></div>",
        unsafe_allow_html=True,
    )
    k3.markdown(
        f"<div class='kpi-card kpi-reject'><strong>Rejected</strong><div style='font-size:28px'>{rejects}</div></div>",
        unsafe_allow_html=True,
    )
    k4.markdown(
        f"<div class='kpi-card kpi-escalate'><strong>Escalated</strong><div style='font-size:28px'>{escalates}</div><div class='small'>Claims flagged for manual review</div></div>",
        unsafe_allow_html=True,
    )


def render_results_table(results_df: pd.DataFrame) -> None:
    st.markdown("### Detailed Results")
    styled = results_df.style.map(style_decision, subset=["decision"])
    st.dataframe(styled, width='stretch')

    csv_bytes = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Results as CSV",
        data=csv_bytes,
        file_name="processed_claims.csv",
        mime="text/csv",
    )


def render_agent_trace(results_df: pd.DataFrame) -> None:
    st.markdown("---")
    st.markdown("### Agent conversation trace")

    if results_df.empty:
        st.info("No claims available to inspect.")
        return

    sel_idx = st.selectbox(
        "Select a claim to inspect the agent conversation",
        options=list(range(len(results_df))),
        format_func=lambda idx: f"Row {idx} - {results_df.index[idx]}",
    )

    trace = results_df.iloc[sel_idx].get("agent_trace", [])
    if not trace:
        st.info("No agent trace available for this claim.")
        return

    for step in trace:
        agent = step.get("agent", "Agent")
        prompt = step.get("prompt", "")
        response = step.get("response", "")
        with st.expander(agent):
            st.markdown("**Prompt**")
            st.code(prompt, language="")
            st.markdown("**Response**")
            st.code(response, language="")


def main() -> None:
    init_session_state()
    render_styles()
    render_header()
    render_sidebar()

    col1, col2 = st.columns([4, 1])

    with col1:
        claims, generate_button = render_upload_panel()

        if claims is not None:
            render_data_preview(claims)

            if generate_button:
                results_df = run_claim_processing(claims)
                st.session_state[RESULTS_SESSION_KEY] = results_df
            elif st.session_state[RESULTS_SESSION_KEY] is None:
                st.info("Press 'Generate Results' to start processing.")

        else:
            st.info("Please upload a CSV file to get started.")

        if st.session_state[RESULTS_SESSION_KEY] is not None:
            render_results_summary(st.session_state[RESULTS_SESSION_KEY])
            render_results_table(st.session_state[RESULTS_SESSION_KEY])
            #render_agent_trace(st.session_state[RESULTS_SESSION_KEY])

    with col2:
        st.markdown("## INFO...")
        st.markdown(
            "- Review uploaded data before generating results\n"
            "- Use the traces in Langsmith platform to inspect model decisions\n"
            "- Download processed claims for auditing"
        )


if __name__ == "__main__":
    main()
