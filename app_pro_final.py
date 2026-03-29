from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import streamlit_confetti as st_confetti
import plotly.graph_objects as go
# import pandas as pd  # removed for policy

from assistant.config import DEFAULT_MODEL, get_available_models, validate_keys
from assistant.llm import LiteLLMClient
from assistant.logging_utils import LOG_FILE
from assistant.rag import auto_seed_rag, rag, load_csv_to_rag, get_all_tickets_df
from assistant.service import analyze_ticket, build_agent_service, bulk_analyze_tickets
from assistant.agent import run_agent
from assistant.tools import TOOLS
from assistant.ui_theme import apply_figma_theme

st.set_page_config(page_title="AI Support Pro", layout="wide")

# Fallbacks for optional

PLOTLY_AVAILABLE = True


def safe_render_table(data: Any, max_rows: int = 100) -> None:
    """Render tabular data without requiring pyarrow."""
    if data is None:
        st.info("No data available.")
        return

    try:
        if hasattr(data, "empty") and getattr(data, "empty"):
            st.info("No data available.")
            return
    except Exception:
        pass

    rows: list[Any] = []

    try:
        if hasattr(data, "to_dict"):
            maybe_rows = data.to_dict(orient="records")
            rows = maybe_rows if isinstance(maybe_rows, list) else [maybe_rows]
        elif isinstance(data, list):
            rows = data
        else:
            rows = [data]
    except Exception:
        rows = [data]

    if not rows:
        st.info("No data available.")
        return

    for idx, row in enumerate(rows[:max_rows], start=1):
        if isinstance(row, dict):
            with st.expander(f"Row {idx}", expanded=idx <= 5):
                for key, value in row.items():
                    st.write(f"**{key}:** {value}")
        else:
            st.write(row)

    if len(rows) > max_rows:
        st.caption(f"Showing first {max_rows} rows of {len(rows)} total.")


def inject_styles():
    st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');
:root {
  --bg: #f8fbff;
  --panel: #ffffff;
  --text: #102540;
  --border: #d5e4f7;
}
[data-theme="dark"] {
  --bg: #0f172a;
  --panel: #1e293b;
  --text: #f1f5f9;
  --border: #334155;
}
body { font-family: 'Manrope', sans-serif; }
.hero { background: linear-gradient(135deg, var(--panel), #eef6ff); border-radius: 20px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid var(--border); }
.kpi { background: var(--panel); border-radius: 12px; padding: 1rem; border: 1px solid var(--border); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.stButton > button { background: linear-gradient(90deg, #1266eb, #16aa82) !important; color: white !important; border-radius: 12px !important; }
.panel { background: var(--panel); border-radius: 12px; padding: 1.5rem; border: 1px solid var(--border); margin: 1rem 0; }
.tag { background: #f0f8ff; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid #bfdbfe; margin: 0.25rem; display: inline-block; }
</style>
    ''', unsafe_allow_html=True)

inject_styles()
apply_figma_theme(
    "🚀 AI Support Pro Dashboard",
    "Professional, error-free AI triage with a cleaner Figma-style presentation layer.",
    "Support workspace",
)

st.session_state.setdefault('history', [])
st.session_state.setdefault('ticket_text', '')
st.session_state.setdefault('reply_draft', '')
st.session_state.setdefault('last_result', {})

with st.sidebar:
    st.header("Controls")
    theme = st.selectbox("Theme", ["Light", "Dark"])
    st.markdown(f'<body data-theme="{theme.lower()}"></body>', unsafe_allow_html=True)

    if validate_keys().get("HF_TOKEN"):
        st.success("✅ HF Active")
    else:
        st.info("Free mode")

    model = st.selectbox("Model", get_available_models() or [DEFAULT_MODEL])
    depth = st.slider("Creativity", 0.0, 0.5, 0.2)

    col_a, col_b = st.columns(2)
    if col_a.button("Seed Demo Data", use_container_width=True):
        st.success(f"Seeded {auto_seed_rag(rag, 50)} tickets")

    csv_path = "data/sample_tickets.csv"
    if col_b.button("Load CSV", use_container_width=True):
        loaded = load_csv_to_rag(csv_path, rag)
        st.success(f"Loaded {loaded} tickets from CSV!")

    if st.button("Clear Session", use_container_width=True):
        st.session_state.history = []
        st.session_state.ticket_text = ""
        st.session_state.reply_draft = ""
        st.session_state.chat_history = []
        st.session_state.last_result = {}
        st.success("Session cleared.")

tab1, tab2, tab3, tab4 = st.tabs(["Tickets", "Build Agent", "Realtime Chat", "Bulk Analysis"])


with tab3:
    st.header("🤖 Realtime Chat Agent")
    st.caption("Use this tab for quick support-copilot answers based on the selected model.")
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("chat_input", "")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Ask the support agent..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = run_agent(prompt, model)
            st.write(response["response"])
            if response.get("error"):
                st.caption("Fallback response shown because the model was unavailable.")

        st.session_state.chat_history.append({"role": "assistant", "content": response["response"]})


with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📊 Bulk Analysis")
    tickets_df = get_all_tickets_df(rag)

    if tickets_df:
        st.caption(f"{len(tickets_df)} tickets available for bulk analysis.")
        safe_render_table(tickets_df)
    else:
        st.info("No tickets available yet. Use Seed Demo Data or Load CSV first.")

    if st.button("Analyze All Tickets", use_container_width=True):
        if tickets_df:
            with st.spinner("Bulk analyzing..."):
                analyses = bulk_analyze_tickets(tickets_df)
            safe_render_table(analyses)

            pri_count = {}
            cat_count = {}
            for analysis in analyses:
                pri = analysis.get("priority", "Unknown")
                cat = analysis.get("category", "Unknown")
                pri_count[pri] = pri_count.get(pri, 0) + 1
                cat_count[cat] = cat_count.get(cat, 0) + 1

            fig_pri = go.Figure(data=[go.Pie(labels=list(pri_count.keys()), values=list(pri_count.values()))])
            fig_pri.update_layout(title="Priority Distribution")
            st.plotly_chart(fig_pri, use_container_width=True)

            fig_cat = go.Figure(data=[go.Bar(x=list(cat_count.keys()), y=list(cat_count.values()))])
            fig_cat.update_layout(title="Categories")
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.warning("Add ticket data before running bulk analysis.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if st.button("Payment Issue", use_container_width=True):
        st.session_state.ticket_text = "Payment failed twice, worried about charge."
    
    ticket = st.text_area(
        "Support Ticket",
        value=st.session_state.ticket_text,
        height=200,
        placeholder="Paste the customer message here for analysis...",
    )
    
    col1, col2 = st.columns(2)
    tone = col1.selectbox("Tone", ["professional", "empathetic"])
    language = col2.selectbox("Language", ["English"])
    
    if st.button("Analyze Ticket", use_container_width=True):
        if ticket.strip():
            try:
                with st.spinner("AI Processing..."):
                    client = LiteLLMClient(model)
                    result, _, _ = analyze_ticket(
                        ticket,
                        client,
                        tone,
                        language,
                        include_followups=True,
                        include_internal_notes=True,
                        include_tags=True,
                        redact=True,
                        temperature=depth,
                        max_output_tokens=1000,
                    )
                st.session_state.last_result = result
                st.session_state.ticket_text = ticket
                st.session_state.reply_draft = result.get("reply", "")
                st.session_state.history.append(result)
                st.success("✅ Analysis Complete")
                st.caption("Priority, category, sentiment, reply draft, and history charts updated below.")
            except Exception as e:
                st.error(f"Failed: {e}")
        else:
            st.warning("Enter ticket to analyze")
    
    last_result = st.session_state.get('last_result')
    if last_result is not None and isinstance(last_result, dict) and last_result:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Priority", last_result.get('priority', '?'))
        col2.metric("Category", last_result.get('category', '?'))
        col3.metric("Sentiment", last_result.get('sentiment', '?'))
        col4.metric("Reply Ready", "Yes")
        
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.download_button(
                "Download Analysis JSON",
                data=json.dumps(last_result, indent=2),
                file_name="ticket_analysis.json",
                mime="application/json",
                use_container_width=True,
            )
        with action_col2:
            st.download_button(
                "Download Reply TXT",
                data=st.session_state.reply_draft,
                file_name="reply_draft.txt",
                mime="text/plain",
                use_container_width=True,
            )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**Reply:**")
            st.text_area("Reply Draft", value=st.session_state.reply_draft, height=200)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**Insights:**")
            for k, v in last_result.items():  # type: ignore[union-attr]
                st.markdown(f"**{k}:** {v}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.history:
            st.subheader("History Summary")
            pri_count = {}
            cat_count = {}
            for item in st.session_state.history:
                pri = item.get('priority', 'Unknown')
                cat = item.get('category', 'Unknown')
                pri_count[pri] = pri_count.get(pri, 0) + 1
                cat_count[cat] = cat_count.get(cat, 0) + 1

            fig_pri = go.Figure(data=[go.Pie(labels=list(pri_count.keys()), values=list(pri_count.values()))])
            fig_pri.update_layout(title="History Priority")
            st.plotly_chart(fig_pri, use_container_width=True)

            fig_cat = go.Figure(data=[go.Bar(x=list(cat_count.keys()), y=list(cat_count.values()))])
            fig_cat.update_layout(title="History Categories")
            st.plotly_chart(fig_cat, use_container_width=True)

            st.download_button(
                "Download History JSON",
                data=json.dumps(st.session_state.history, indent=2),
                file_name="analysis_history.json",
                mime="application/json",
                use_container_width=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("Agent Builder")
    st.caption("Generate a starter support-agent config from the tools and goal you provide.")
    tools_input = st.text_input("Tools (comma separated)", "chatgpt, tools")
    goal = st.text_area("Goal", "Support copilot")
    if st.button("Generate Agent", use_container_width=True):
        if goal.strip():
            try:
                tools_list = [t.strip() for t in tools_input.split(",") if t.strip()]
                config = build_agent_service(tools_list, goal, model)
                st.success("Agent configuration generated.")
                st.json(config)
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Enter an agent goal before generating.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p class="footer-note">✅ Professional, error-free AI dashboard with safe Figma-style polish applied.</p>', unsafe_allow_html=True)
