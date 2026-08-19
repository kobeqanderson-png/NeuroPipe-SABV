"""
NeuroPipe-SABV — Home Page

Multi-page app entry point. Navigate to different sections through the sidebar.
Run with: streamlit run app.py
"""

import streamlit as st
from pathlib import Path
import sys

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.animations import (
    inject_animation_css,
)
from src.navigation import apply_global_chrome, render_top_navigation

st.set_page_config(
    page_title="NeuroPipe-SABV",
    page_icon=None,
    layout="wide"
)

# Inject animations globally
inject_animation_css()
apply_global_chrome()
render_top_navigation("Home")

# Apply dark Brainlife-inspired theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #090b11;
        --bg-panel: #111524;
        --bg-soft: #191f33;
        --text-main: #e6ebf5;
        --text-muted: #9ca7bf;
        --accent: #ff6a5f;
        --accent-soft: #ff857b;
        --accent-deep: #8f302c;
        --line: #2b344c;
        --line-soft: #232b41;
        --hero-1: #0f1426;
        --hero-2: #1a2340;
    }

    html, body, [class*="css"] {
        font-family: "Manrope", "Sora", "Avenir Next", sans-serif !important;
        background:
            radial-gradient(circle at 18% -5%, #1f2b4f 0%, transparent 42%),
            radial-gradient(circle at 90% 0%, #2c1735 0%, transparent 34%),
            var(--bg-main) !important;
        color: var(--text-main) !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 18% -5%, #1f2b4f 0%, transparent 42%),
            radial-gradient(circle at 90% 0%, #2c1735 0%, transparent 34%),
            var(--bg-main) !important;
        color: var(--text-main) !important;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .stMarkdown, .stText, .stCaption, label, p, h1, h2, h3, h4 {
        color: var(--text-main) !important;
    }

    h1, h2, h3, h4 {
        font-family: "Sora", "Manrope", sans-serif !important;
        letter-spacing: -0.02em;
    }

    .section-band {
        position: relative;
        padding: 1.8rem 0 1.2rem;
        margin-top: 0.8rem;
    }

    .section-band::after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--line) 14%, var(--line) 86%, transparent 100%);
    }

    .hero-shell {
        background: linear-gradient(130deg, var(--hero-1) 0%, var(--hero-2) 100%);
        border: 1px solid var(--line);
        border-radius: 0;
        padding: 1.7rem 1.3rem;
        box-shadow: 0 24px 48px rgba(0, 0, 0, 0.36);
        animation: fadeIn 0.6s ease-out;
    }

    .hero-tag {
        display: inline-block;
        font-size: 0.75rem;
        color: var(--text-muted);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .hero-title {
        font-size: clamp(2rem, 5vw, 3.6rem);
        line-height: 1.04;
        margin: 0.1rem 0 0.9rem;
        color: #f2f5ff;
        max-width: 14ch;
    }

    .hero-copy {
        color: #bdc8df;
        font-size: 1.02rem;
        max-width: 60ch;
        margin-bottom: 0;
    }

    .hero-kpis {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.7rem;
        margin-top: 1.2rem;
    }

    .hero-kpi {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--line-soft);
        padding: 0.75rem;
    }

    .hero-kpi b {
        display: block;
        font-family: "Sora", sans-serif;
        font-size: 1.1rem;
        color: #ffffff;
    }

    .hero-kpi span {
        color: var(--text-muted);
        font-size: 0.8rem;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 0.3rem;
    }

    .workflow-strip {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 0.55rem;
        margin-top: 0.4rem;
    }

    .workflow-step {
        background: linear-gradient(180deg, #121a2f 0%, #0e1528 100%);
        border: 1px solid var(--line-soft);
        padding: 0.7rem 0.55rem;
        text-align: center;
        min-height: 84px;
    }

    .workflow-step b {
        display: block;
        color: #ff9f97;
        font-size: 0.82rem;
        margin-bottom: 0.25rem;
    }

    .workflow-step span {
        color: #d1d8ea;
        font-size: 0.78rem;
        line-height: 1.3;
    }

    .feature-card {
        background: linear-gradient(180deg, #101526 0%, #0d1222 100%);
        border: 1px solid var(--line-soft);
        padding: 1rem;
        animation: fadeIn 0.5s ease-out;
    }

    .feature-card h4 {
        margin: 0 0 0.35rem;
        font-size: 1rem;
        color: #f8f9ff;
    }

    .feature-card p {
        margin: 0;
        font-size: 0.92rem;
        color: var(--text-muted);
        line-height: 1.55;
    }

    .coffee-btn {
        display: inline-block;
        margin-top: 0.75rem;
        padding: 0.48rem 0.95rem;
        border: 1px solid rgba(255, 133, 123, 0.55);
        color: #ffd9d5 !important;
        background: rgba(255, 133, 123, 0.08);
        text-decoration: none !important;
        font-weight: 600;
        letter-spacing: 0.01em;
        transition: all 0.25s ease;
    }

    .coffee-btn:hover {
        border-color: #ffb0a9;
        background: rgba(255, 133, 123, 0.2);
        transform: translateY(-1px);
    }

    a {
        color: var(--accent) !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: transparent !important;
        color: #f4f6ff !important;
        border: 1px solid #f4f6ff !important;
        border-radius: 0 !important;
        font-family: "Sora", sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
        transition: all 0.3s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #f4f6ff !important;
        color: #0b1020 !important;
        border-color: #f4f6ff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 255, 255, 0.18) !important;
    }

    .stButton > button:focus,
    .stDownloadButton > button:focus,
    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: 2px solid var(--accent-soft) !important;
        outline-offset: 2px !important;
        box-shadow: none !important;
    }

    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stTextArea > div > div,
    .stDateInput > div > div {
        background-color: var(--bg-soft) !important;
        border: 1px solid var(--line-soft) !important;
        color: var(--text-main) !important;
        transition: all 0.3s ease;
    }

    div[data-baseweb="select"] > div:focus-within,
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stDateInput > div > div:focus-within {
        border-color: var(--accent-soft) !important;
        box-shadow: 0 0 0 2px rgba(255, 106, 95, 0.35) !important;
    }

    div[data-baseweb="slider"] [role="slider"] {
        background-color: var(--accent-soft) !important;
    }

    div[data-baseweb="slider"] > div > div {
        background-color: rgba(255, 106, 95, 0.25) !important;
    }

    .stCheckbox input:checked + div,
    .stRadio input:checked + div {
        background-color: var(--accent-soft) !important;
        border-color: var(--accent-soft) !important;
    }

    button[role="tab"][aria-selected="true"] {
        color: #f7d7d3 !important;
        border-bottom: 2px solid var(--accent-soft) !important;
    }

    .stDataFrame, [data-testid="stTable"] {
        border: 1px solid var(--line-soft);
        border-radius: 0;
        overflow: hidden;
    }

    .stAlert {
        background: var(--bg-panel) !important;
        border: 1px solid var(--accent-deep) !important;
    }

    hr {
        border-color: var(--line-soft) !important;
    }

    @media (max-width: 860px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }

        .hero-kpis {
            grid-template-columns: 1fr;
        }

        .workflow-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for shared data across pages
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df_processed' not in st.session_state:
    st.session_state.df_processed = None

# Internal defaults (not user-editable in public UI)
if 'sex_threshold' not in st.session_state:
    st.session_state.sex_threshold = 16
if 'sheet_name' not in st.session_state:
    st.session_state.sheet_name = 0
if 'fill_missing' not in st.session_state:
    st.session_state.fill_missing = True
if 'remove_dupes' not in st.session_state:
    st.session_state.remove_dupes = True
if 'strip_ws' not in st.session_state:
    st.session_state.strip_ws = True
if 'add_log' not in st.session_state:
    st.session_state.add_log = True
if 'branding_enabled' not in st.session_state:
    st.session_state.branding_enabled = True

# Hero section
st.markdown(
    """
    <section class="section-band">
        <p style="margin-bottom: 0.7rem; color: #c8d1e6; font-size: 0.95rem;">
            <strong>NIH</strong> = National Institutes of Health • <strong>SABV</strong> = Sex as a Biological Variable
        </p>
        <div class="hero-shell">
            <span class="hero-tag">NeuroPipe-SABV • Research Workflow Platform</span>
            <h1 class="hero-title">NeuroPipe-SABV</h1>
            <p class="hero-copy">
                An NIH SABV-compliant pipeline for preclinical behavioral neuroscience.
                Upload, curate, classify, compare, visualize, and model — in a single guided workflow.
            </p>
            <div class="hero-kpis">
                <div class="hero-kpi"><b>7-step</b><span>guided analysis path</span></div>
                <div class="hero-kpi"><b>NIH-ready</b><span>sex-based variable support</span></div>
                <div class="hero-kpi"><b>Excel exports</b><span>publication-focused outputs</span></div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown("<section class='section-band'><h3>Pipeline Overview</h3></section>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="workflow-strip">
        <div class="workflow-step"><b>1</b><span>Upload<br>Data</span></div>
        <div class="workflow-step"><b>2</b><span>Explore<br>Raw Data</span></div>
        <div class="workflow-step"><b>3</b><span>Process &<br>Classify</span></div>
        <div class="workflow-step"><b>4</b><span>Analyze<br>Differences</span></div>
        <div class="workflow-step"><b>5</b><span>Create<br>Visualizations</span></div>
        <div class="workflow-step"><b>6</b><span>Build<br>Models</span></div>
        <div class="workflow-step"><b>7</b><span>Download<br>Results</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section-band">
        <h3>Core Capabilities</h3>
        <div class="feature-grid">
            <article class="feature-card">
                <h4>Automatic Classification</h4>
                <p>Animal ID-based sex classification with threshold controls and multiple processing modes.</p>
            </article>
            <article class="feature-card">
                <h4>Data Quality Controls</h4>
                <p>Missing-value handling, duplicate removal, whitespace cleanup, and consistent ingestion checks.</p>
            </article>
            <article class="feature-card">
                <h4>Statistical Comparison</h4>
                <p>Welch tests, effect sizes, and multi-variable summaries tailored to SABV questions.</p>
            </article>
            <article class="feature-card">
                <h4>Visual + Modeling Stack</h4>
                <p>Distribution plots, correlations, and regression diagnostics from the same processed dataset.</p>
            </article>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section-band">
        <h3>Quick Start Path</h3>
        <p style="margin-bottom: 0.45rem; color: #b8c3db;">1. Use the top navigation to move through each step in order.</p>
        <p style="margin-bottom: 0.45rem; color: #b8c3db;">2. Pages reuse session state, so your data persists during analysis.</p>
        <p style="margin-bottom: 0.45rem; color: #b8c3db;">3. Navigate back anytime to revise assumptions or thresholds.</p>
        <p style="margin-bottom: 0; color: #b8c3db;">4. Export polished outputs once processing and modeling are complete.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.caption("NeuroPipe-SABV | Built with Streamlit | Dark Brainlife-inspired theme")

st.divider()
st.divider()
st.caption("Navigate through pages using the top menu • Your data persists across pages")

st.markdown(
    """
    <section class="section-band" style="margin-top: 1.2rem; padding-bottom: 0.2rem;">
        <div class="feature-card" style="max-width: 720px; margin: 0 auto; text-align: center;">
            <h3 style="margin-bottom: 0.5rem;">Contact</h3>
            <p style="margin-bottom: 0.35rem; color: #b8c3db;">Questions about NeuroPipe-SABV, the workflow, or exports?</p>
            <p style="margin-bottom: 0; color: #dce5ff; font-weight: 600;">
                Email <a href="mailto:kobescodes@gmail.com">kobescodes@gmail.com</a>
            </p>
            <a class="coffee-btn" href="https://buymeacoffee.com/kobescodes" target="_blank" rel="noopener noreferrer">
                Buy me a coffee if you like it!
            </a>
            <p style="margin-top: 0.55rem; margin-bottom: 0; color: rgba(156, 167, 191, 0.16); font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase;">
                kobescodes
            </p>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)








