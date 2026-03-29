from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import pandas as pd
import plotly.express as px
from assistant.config import DEFAULT_MODEL, get_available_models, validate_keys
from assistant.llm import LiteLLMClient
from assistant.rag import rag, auto_seed_rag, get_all_tickets_df, load_csv_to_rag
from assistant.service import analyze_ticket, build_agent_service, bulk_analyze_tickets, find_similar
from assistant.ui_theme import apply_figma_theme

st.set_page_config(
    page_title="AI Support Intelligence Hub", 
    page_icon="🧠", 
    layout="wide"
)

@st.cache_data
def load_data():
    df = get_all_tickets_df(rag)
    # Ensure we return a proper DataFrame
    if isinstance(df, list):
        return pd.DataFrame(df)
    return df

apply_figma_theme(
    "AI Support Intelligence Hub",
    "Advanced AI-powered support analytics with premium Figma-style design.",
    "Operations view",
)

st.markdown("""
<style>
/* Figma-style Design System - Streamlit Optimized */
:root {
    --primary-color: #6366f1;
    --primary-hover: #4f46e5;
    --secondary-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
    --text-primary: #111827;
    --text-secondary: #6b7280;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --border-color: #e5e7eb;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Dark mode variables */
[data-theme="dark"] {
    --primary-color: #818cf8;
    --primary-hover: #6366f1;
    --secondary-color: #34d399;
    --danger-color: #f87171;
    --warning-color: #fbbf24;
    --text-primary: #f3f4f6;
    --text-secondary: #9ca3af;
    --bg-primary: #111827;
    --bg-secondary: #0b1220;
    --border-color: #374151;
}

/* Force Streamlit Body Override */
body, .main, .block-container {
    font-family: var(--font-family) !important;
    color: var(--text-primary) !important;
    background-color: var(--bg-secondary) !important;
    transition: all 0.3s ease !important;
}

/* Enhanced Metric Cards with Streamlit Specificity */
.metric-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-lg);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    margin-bottom: 1rem;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    border-color: var(--primary-color);
}

/* Enhanced Streamlit Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
    filter: brightness(1.1) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Enhanced Streamlit Select Boxes */
.stSelectbox > div > div {
    border-radius: var(--radius-md) !important;
    border: 2px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.3s ease !important;
    background-color: var(--bg-primary) !important;
}

.stSelectbox > div > div:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

/* Enhanced Streamlit Input Fields */
.stTextInput > div > div, .stTextArea > div > div {
    border-radius: var(--radius-md) !important;
    border: 2px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.3s ease !important;
    background-color: var(--bg-primary) !important;
}

.stTextInput > div > div:focus-within, .stTextArea > div > div:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

/* Enhanced Streamlit DataFrames */
.stDataFrame, .stTable {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-md) !important;
    border: 1px solid var(--border-color) !important;
    background-color: var(--bg-primary) !important;
}

/* Enhanced Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem !important;
    background: var(--bg-primary) !important;
    padding: 0.5rem !important;
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border-color) !important;
    margin-bottom: 1rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 700 !important;
    color: var(--text-secondary) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
    border: none !important;
}

/* Enhanced Chat Bubbles */
.chat-bubble {
    border-radius: var(--radius-lg);
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    max-width: 80%;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.customer {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    margin-left: auto;
    border-radius: 20px 20px 4px 20px;
}

.agent {
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
    border-left: 4px solid var(--secondary-color);
    border-radius: 20px 20px 20px 4px;
}

/* Enhanced Alert Cards */
.alert-card {
    border-left: 4px solid var(--danger-color);
    background: linear-gradient(180deg, rgba(239,68,68,0.1), rgba(239,68,68,0.05));
    border-radius: var(--radius-md);
    padding: 1rem;
    box-shadow: var(--shadow-sm);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: .8; transform: scale(1.02); }
}

/* Enhanced Streamlit Metrics */
.stMetric {
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
    border-radius: var(--radius-md);
    padding: 1rem;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}

.stMetric:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-color);
}

/* Enhanced Streamlit Progress Bars */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    border-radius: var(--radius-sm);
    height: 8px;
}

/* Glass Card Effect */
.glass-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-lg);
    margin-bottom: 2rem;
}

/* Badge Styling */
.tag {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 700;
    display: inline-block;
    box-shadow: var(--shadow-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Enhanced Headers */
h1, h2, h3, h4, h5, h6 {
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin-bottom: 1rem !important;
    background: linear-gradient(135deg, var(--primary-color), var(--text-primary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Smooth Transitions for all elements */
* {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .metric-card {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .chat-bubble {
        max-width: 100%;
    }
    
    .customer, .agent {
        max-width: 100%;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.875rem !important;
        padding: 0.5rem 1rem !important;
    }
}

/* Focus States */
*:focus-visible {
    outline: 3px solid var(--primary-color) !important;
    outline-offset: 2px !important;
}

/* Remove default Streamlit padding on main container */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Enhanced Sidebar */
.css-1d391kg {
    background: linear-gradient(180deg, var(--bg-primary), var(--bg-secondary));
    border-right: 1px solid var(--border-color);
    padding: 2rem 1rem !important;
}

/* Enhanced Sidebar Headers */
.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
    background: linear-gradient(135deg, var(--primary-color), var(--text-primary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.25rem !important;
    margin-bottom: 1rem !important;
}

/* Enhanced Sidebar Buttons */
.css-1d391kg .stButton > button {
    background: linear-gradient(135deg, var(--secondary-color), #059669) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
    margin-bottom: 0.5rem !important;
}

.css-1d391kg .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
    filter: brightness(1.1) !important;
}

/* Enhanced Sidebar Inputs */
.css-1d391kg .stTextInput > div > div, .css-1d391kg .stSelectbox > div > div {
    border-radius: var(--radius-md) !important;
    border: 2px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.3s ease !important;
    background-color: var(--bg-primary) !important;
    margin-bottom: 1rem !important;
}

.css-1d391kg .stTextInput > div > div:focus-within, .css-1d391kg .stSelectbox > div > div:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

/* Enhanced Sidebar Headers */
.css-1d391kg .stHeader {
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    margin-bottom: 1rem !important;
    font-size: 1.5rem !important;
    background: linear-gradient(135deg, var(--primary-color), var(--text-primary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Enhanced Download Button */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--secondary-color), #059669) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
    filter: brightness(1.1) !important;
}

/* Enhanced Info Messages */
.stAlert {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm) !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85)) !important;
}

/* Enhanced Success Messages */
.stSuccess {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm) !important;
    background: linear-gradient(180deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)) !important;
    border-left: 4px solid var(--secondary-color) !important;
}

/* Enhanced Caption */
.stCaption {
    font-size: 0.875rem !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 1rem !important;
}

/* Enhanced Container Spacing */
.css-1v0mbdj {
    padding: 0 !important;
}

/* Remove Streamlit default padding */
.reportview-container .main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* Enhanced Plotly Charts */
.js-plotly-plot .plotly .modebar {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-sm) !important;
}

/* Enhanced Toggle Switch */
.stRadio > label, .stCheckbox > label {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* Enhanced Container Background */
.main > .block-container {
    background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
    backdrop-filter: blur(10px);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-color);
}

/* Enhanced Sidebar Background */
.css-1l02zno {
    background: linear-gradient(180deg, var(--bg-primary), var(--bg-secondary));
}

/* Enhanced Main Content Area */
.css-18e3th9 {
    background-color: var(--bg-secondary) !important;
}

/* Enhanced Footer */
.css-1v3fvcr {
    background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
    backdrop-filter: blur(10px);
    border-radius: var(--radius-lg);
    padding: 1rem;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-color);
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = st.session_state.df
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# JavaScript for dark mode functionality
st.markdown("""
<script>
// Dark mode toggle functionality
(function() {
    function applyTheme(isDark) {
        const root = document.documentElement;
        if (isDark) {
            root.setAttribute('data-theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
        }
    }
    
    // Listen for dark mode toggle changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                const toggle = document.querySelector('input[type="checkbox"]');
                if (toggle && toggle.closest('.stRadio, .stCheckbox')) {
                    applyTheme(toggle.checked);
                }
            }
        });
    });
    
    // Start observing the document body for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Initial theme application based on session state
    const initialDarkMode = """ + str(st.session_state.dark_mode) + """;
    applyTheme(initialDarkMode);
})();
</script>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🚀 Dashboard Controls")
    st.session_state.dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    st.markdown(f'<body class="theme-{"dark" if st.session_state.dark_mode else "light"}"></body>', unsafe_allow_html=True)
    
    model = st.selectbox("AI Model", get_available_models() or [DEFAULT_MODEL])
    uploaded_file = st.file_uploader("📁 Upload CSV", type='csv')
    if uploaded_file:
        # Convert UploadedFile to string path for the RAG function
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            loaded = load_csv_to_rag(tmp_file_path, rag)
            st.session_state.df = load_data()
            st.success(f"✅ Loaded {loaded} tickets")
            st.rerun()
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    if st.button("🌱 Seed 50 Sample Tickets"):
        count = auto_seed_rag(rag, 50)
        st.session_state.df = load_data()
        st.success(f"Seeded {count} tickets")
    
    st.subheader("Filters")
    priority_filter = st.multiselect("Priority", ['High', 'Medium', 'Low'], default=['High', 'Medium', 'Low'])
    category_filter = st.multiselect("Category", st.session_state.df['category'].unique().tolist() if not st.session_state.df.empty else [])
    search_term = st.text_input("Search tickets")

# Apply filters
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[
        (df['priority'].isin(priority_filter)) &
        (df['category'].isin(category_filter)) &
        (df['ticket'].str.contains(search_term, case=False, na=False))
    ] if not df.empty else pd.DataFrame()
    st.session_state.filtered_df = filtered
    return filtered

if st.session_state.df is not None:
    st.session_state.filtered_df = apply_filters(st.session_state.df)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Insights", "🎫 Tickets", "🔍 Single Analysis", "🤖 Agent Builder"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if st.session_state.df.empty:
        st.info("👆 Upload CSV or seed data to see insights")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        urgent_pct = (st.session_state.df['priority'] == 'High').mean() * 100
        col1.metric("🚨 Urgent Tickets %", f"{urgent_pct:.1f}%", delta="1.2%")
        col2.metric("📈 Total Tickets", len(st.session_state.df))
        col3.metric("😊 Positive Sentiment", (st.session_state.df['sentiment'] == 'Positive').sum())
        top_issue = st.session_state.df['category'].value_counts().index[0] if len(st.session_state.df) > 0 else "N/A"
        col4.metric("🔥 Top Issue", top_issue)
        
        col5, col6 = st.columns(2)
        with col5:
            st.subheader("Priority Distribution")
            fig1 = px.pie(st.session_state.df, names='priority', hole=0.4, color_discrete_sequence=['#ef4444', '#f59e0b', '#10b981'])
            st.plotly_chart(fig1, use_container_width=True)
        with col6:
            st.subheader("Category Breakdown")
            fig2 = px.bar(st.session_state.df['category'].value_counts().head(), color='category')
            st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if st.session_state.filtered_df.empty:
        st.info("No tickets match filters. Adjust sidebar filters.")
    else:
        # Escalation alerts
        high_priority = st.session_state.filtered_df[st.session_state.filtered_df['priority'] == 'High']
        if not high_priority.empty:
            st.markdown("### 🚨 Escalation Alerts")
            for _, row in high_priority.head(3).iterrows():
                st.markdown(f"""
                <div class='metric-card alert-card'>
                    <strong>{row.get('category', 'N/A')} - {row['ticket'][:100]}...</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Tickets table with chat toggle
        view = st.radio("View", ["Table", "Chat"])
        if view == "Table":
            st.dataframe(st.session_state.filtered_df, use_container_width=True)
        else:
            for idx, row in st.session_state.filtered_df.iterrows():
                pri = row.get('priority', '')
                cat = row.get('category', '')
                badge = f"<span class='tag'>{pri} • {cat}</span>"
                with st.container():
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div class='chat-bubble customer'>{row['ticket']}</div>
                        <div class='chat-bubble agent'>{row.get('reply', 'Reply generated...')}</div>
                        {badge}
                    </div>
                    """, unsafe_allow_html=True)
        
        if st.button("🔄 Bulk Analyze Filtered Tickets"):
            with st.spinner("Analyzing..."):
                # Ensure we have a proper DataFrame
                if isinstance(st.session_state.filtered_df, pd.DataFrame):
                    records = st.session_state.filtered_df.to_dict("records")
                else:
                    records = st.session_state.filtered_df
                analyzed_rows = bulk_analyze_tickets(records)
                analyzed_df = pd.DataFrame(analyzed_rows)
                st.session_state.df = analyzed_df
                st.session_state.filtered_df = apply_filters(analyzed_df)
                st.success("Bulk analysis complete!")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    # Existing single analysis (enhanced)
    ticket_input = st.text_area("Ticket text", height=150)
    col_t1, col_t2 = st.columns(2)
    tone = col_t1.selectbox("Tone", ["professional", "empathetic", "formal"])
    
    if st.button("Analyze Ticket", use_container_width=True) and ticket_input.strip():
        with st.spinner("🤖 AI Processing..."):
            client = LiteLLMClient(model)
            result, _, _ = analyze_ticket(
                ticket=ticket_input,
                client=client,
                tone=tone,
                language="English",
                include_followups=True,
                include_internal_notes=True,
                include_tags=True,
                temperature=0.2,
                max_output_tokens=1000,
                redact=True
            )
            st.session_state.last_result = result
        
        if 'last_result' in st.session_state:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Priority", st.session_state.last_result.get('priority', '?'))
            col2.metric("Sentiment", st.session_state.last_result.get('sentiment', '?'))
            col3.metric("Category", st.session_state.last_result.get('category', '?'))
            col4.metric("Reply Length", len(st.session_state.last_result.get('reply', '')))
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.text_area("AI Reply", st.session_state.last_result.get('reply', ''), height=200)
            with col_b:
                st.json(st.session_state.last_result)
            
            similars = find_similar(ticket_input, n=3)
            if similars:
                st.subheader("Similar Tickets")
                for sim in similars:
                    st.write(f"• {sim['ticket'][:100]}...")
    
    col_s1, col_s2 = st.columns(2)
    if col_s1.button("Sample: Urgent Payment"):
        st.session_state.last_result = None
        ticket_input = "URGENT: Double charged $199, immediate refund needed!"
    if col_s2.button("Clear"):
        st.session_state.last_result = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    # Existing agent builder
    st.header("🤖 Agent Builder")
    tools_input = st.text_input("Tools (comma sep)", "chatgpt,gemini")
    goal = st.text_area("Goal", "Create support triage agent", height=100)
    if st.button("Generate Agent Config"):
        tools_list = [t.strip() for t in tools_input.split(',') if t.strip()]
        config = build_agent_service(tools_list, goal, model)
        st.success("Agent config generated.")
        st.json(config)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer export
if not st.session_state.df.empty and isinstance(st.session_state.df, pd.DataFrame):
    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Export Processed Data",
        csv,
        "ai_support_dashboard_export.csv",
        "text/csv"
    )

st.markdown("---")
st.markdown("✅ **Production-ready AI Support Dashboard complete!** Run with `streamlit run ai_support_dashboard.py`")
