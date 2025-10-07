# app.py
import json
import streamlit as st
from typing import Any, Dict, List, Tuple

# Your backend
from src.orchestrator import plan_for          # returns ActionPlan (Pydantic) or dict
from src.executor import execute_plan          # expected to return (summary: str, output: Any)

# ---------- Page config ----------
st.set_page_config(page_title="DQ Agent", page_icon="🧰", layout="wide")

# ---------- Minimal dark styling to match the look ----------
st.markdown("""
<style>
/* Dark-ish base */
:root, .stApp { background-color: #0f1216; }
section.main > div { padding-top: 1.5rem; }

/* Headings */
h1, h2, h3, h4, h5, h6, .stMarkdown { color: #ffffffde; }

/* Chat bubbles */
.bubble {
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 10px;
  color: #eaeaf0;
  background: #1a1f27;
  border: 1px solid #252a33;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
}
.bubble.user::before { content: "🧠"; margin-right: 8px; }
.bubble.assistant::before { content: "🪄"; margin-right: 8px; }

/* Inputs */
input, textarea {
  background: #1b1f27 !important;
  color: #eaeaf0 !important;
  border: 1px solid #2a2f39 !important;
  border-radius: 12px !important;
}

/* Buttons */
div.stButton > button {
  height: 44px;
  border-radius: 12px;
  border: 1px solid #2a2f39;
  background: #ff4b4b;
  color: white;
  font-weight: 600;
}
div.stButton > button[kind="secondary"] {
  background: #1f2937;
  color: #e5e7eb;
}
div.stButton > button:disabled {
  opacity: 0.5;
}

/* JSON pretty area */
.block-container .stJson { background: #0f1216; }
</style>
""", unsafe_allow_html=True)

st.title("DQ Agent")

# ---------- Session state ----------
ss = st.session_state
ss.setdefault("chat", [])              # list[{"role": "user"/"assistant", "content": str}]
ss.setdefault("query", "")
ss.setdefault("plan", None)
ss.setdefault("plan_query", None)
ss.setdefault("last_output", None)     # tool output from executor
ss.setdefault("last_summary", None)    # summary from executor
ss.setdefault("is_running", False)

# ---------- Helpers ----------
def _to_dict(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return obj

def generate_plan_and_store():
    plan_obj = plan_for(ss.query.strip())
    ss.plan = _to_dict(plan_obj)
    ss.plan_query = ss.query

def run_with_saved_query():
    summary, output = execute_plan(ss.query.strip())  # backend loads data & runs
    ss.last_summary = summary
    ss.last_output  = output

# ---------- Layout: two columns ----------
left, right = st.columns([1, 1], gap="large")

# ---------- Left: AI Assistant ----------
with left:
    st.markdown("## AI Assistant")

    # Chat history (simple bubbles)
    for msg in ss.chat:
        role_cls = "assistant" if msg["role"] == "assistant" else "user"
        st.markdown(f'<div class="bubble {role_cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    # Prompt + Send
    st.markdown("**Your prompt**")
    st.text_input("Your prompt", key="query", label_visibility="collapsed",
                  placeholder="For a PD model, run data quality check (only missing value).")
    send = st.button("Send", use_container_width=True)

    if send and ss.query.strip():
        # Add user bubble
        ss.chat.append({"role": "user", "content": ss.query})

        # Generate plan immediately and acknowledge
        with st.spinner("Generating plan..."):
            generate_plan_and_store()
        ss.chat.append({"role": "assistant",
                        "content": "Plan generated. See **Execution Window** on the right and click **Run**."})
        st.rerun()

# ---------- Right: Execution Window ----------
with right:
    st.markdown("## Execution Window")

    # Show Generated Plan (if any)
    st.markdown("### Generated Plan")
    if ss.plan is None:
        st.info("No plan yet. Write a prompt on the left and click **Send**.")
    else:
        st.json(ss.plan, expanded=False)

    # Buttons row
    run_col, edit_col = st.columns([1, 1])
    with run_col:
        run_btn = st.button("▶️ Run Plan", type="primary", use_container_width=True)
    with edit_col:
        st.button("✏️ Edit (Coming Soon)", disabled=True, use_container_width=True)

    # Handle Run click
    if run_btn and not ss.is_running:
        if not ss.query.strip():
            st.warning("Please enter a prompt on the left and click **Send** first.")
        else:
            ss.is_running = True
            st.rerun()

    # Do the run while flagged
    if ss.is_running:
        with st.spinner("Running plan and summarizing..."):
            try:
                run_with_saved_query()
            finally:
                ss.is_running = False
        st.success("Run complete.")
        st.rerun()

    # After run: Tabs appear for Results & Summary
    if ss.last_output is not None or ss.last_summary is not None:
        tabs = st.tabs(["Results", "Summary"])

        with tabs[0]:
            st.subheader("Results")
            if isinstance(ss.last_output, (dict, list)):
                st.json(ss.last_output, expanded=False)
            else:
                st.write(ss.last_output if ss.last_output is not None else "No results.")

        with tabs[1]:
            st.subheader("Summary")
            st.write(ss.last_summary or "No summary.")
