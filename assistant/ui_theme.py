from __future__ import annotations

import streamlit as st


FIGMA_STYLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

:root {
  --bg-primary: #f4f7fb;
  --bg-secondary: #edf4ff;
  --surface: rgba(255, 255, 255, 0.88);
  --surface-strong: #ffffff;
  --text-primary: #10233f;
  --text-secondary: #64748b;
  --border: rgba(148, 163, 184, 0.22);
  --shadow-lg: 0 24px 60px rgba(15, 23, 42, 0.10);
  --shadow-md: 0 14px 32px rgba(15, 23, 42, 0.08);
  --accent: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  --accent-soft: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --radius-xl: 24px;
  --radius-lg: 18px;
  --radius-md: 14px;
}

.stApp {
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 28%),
    radial-gradient(circle at top right, rgba(124, 58, 237, 0.10), transparent 26%),
    linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
}

.block-container {
  padding-top: 1.6rem;
  padding-bottom: 2rem;
}

.hero-card {
  background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(248,250,252,0.88));
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 1.6rem 1.8rem;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(16px);
  margin-bottom: 1rem;
}

.glass-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.1rem;
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(14px);
}

.section-card {
  background: var(--surface-strong);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.2rem;
  box-shadow: var(--shadow-md);
}

.status-pill {
  display: inline-block;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: var(--accent-soft);
  color: #3730a3;
  font-size: 0.82rem;
  font-weight: 700;
  border: 1px solid rgba(99, 102, 241, 0.14);
  margin-right: 0.4rem;
  margin-bottom: 0.35rem;
}

.kpi-shell {
  background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,250,252,0.90));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.95rem 1rem;
  box-shadow: var(--shadow-md);
}

.stButton > button,
.stDownloadButton > button {
  border-radius: 14px !important;
  border: 0 !important;
  min-height: 2.8rem !important;
  font-weight: 700 !important;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18) !important;
}

.stButton > button {
  background: var(--accent) !important;
  color: white !important;
}

.stDownloadButton > button {
  background: white !important;
  color: #1e3a8a !important;
  border: 1px solid rgba(37, 99, 235, 0.18) !important;
}

[data-testid="stSidebar"] {
  background: rgba(255,255,255,0.92);
  border-right: 1px solid var(--border);
}

div[data-testid="stMetric"] {
  background: rgba(255,255,255,0.88);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 0.8rem 0.9rem;
  box-shadow: var(--shadow-md);
}

div[data-testid="stMetricLabel"] {
  color: var(--text-secondary);
  font-weight: 700;
}

div[data-testid="stMetricValue"] {
  color: var(--text-primary);
}

.streamlit-expanderHeader {
  font-weight: 700;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
  border-radius: 14px !important;
}

.chart-shell {
  background: rgba(255,255,255,0.82);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.75rem;
  box-shadow: var(--shadow-md);
  margin-top: 0.75rem;
}

.footer-note {
  text-align: center;
  color: var(--text-secondary);
  margin-top: 1rem;
}
</style>
"""


def apply_figma_theme(page_title: str, subtitle: str, badge_text: str = "Figma-style UI") -> None:
    st.markdown(FIGMA_STYLE_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="hero-card">
            <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap;">
                <div>
                    <div class="status-pill">{badge_text}</div>
                    <h1 style="margin:0.35rem 0 0.25rem 0;font-family:'Space Grotesk',sans-serif;font-size:2.5rem;color:#0f172a;">
                        {page_title}
                    </h1>
                    <p style="margin:0;color:#64748b;font-size:1rem;">
                        {subtitle}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_card() -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)


def close_card() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
