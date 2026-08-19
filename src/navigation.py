"""Shared top navigation and UI chrome helpers for the Streamlit app."""

from __future__ import annotations

import streamlit as st


NAV_ITEMS = [
    ("Home", "app.py", "Home"),
    ("Upload", "pages/1_Upload_Data.py", "Upload"),
    ("Process", "pages/2_Process_Data.py", "Process"),
    ("Sex Analysis", "pages/3_Sex_Analysis.py", "Sex Analysis"),
    ("Visualize", "pages/4_Visualizations.py", "Visualize"),
    ("Regression", "pages/5_Regression.py", "Regression"),
    ("Download", "pages/6_Download.py", "Download"),
]


def apply_global_chrome() -> None:
    """Apply shared dark styling and remove default sidebar page navigation."""
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
            --line: #2b344c;
            --line-soft: #232b41;
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
            max-width: 1180px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stSidebarNav"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1020 0%, #090d18 100%) !important;
            border-right: 1px solid var(--line-soft);
        }

        [data-testid="stSidebarCollapsedControl"] {
            top: 0.7rem;
        }

        .stMarkdown, .stText, .stCaption, label, p, h1, h2, h3, h4 {
            color: var(--text-main) !important;
        }

        h1, h2, h3, h4 {
            font-family: "Sora", "Manrope", sans-serif !important;
            letter-spacing: -0.02em;
        }

        .stPageLink a {
            display: block !important;
            text-align: center;
            background: linear-gradient(180deg, #151b2d 0%, #111726 100%);
            border: 1px solid var(--line-soft);
            color: #dce5ff !important;
            padding: 0.5rem 0.6rem;
            font-weight: 600;
            text-decoration: none !important;
            min-height: 44px;
        }

        .stPageLink a:hover {
            border-color: var(--accent-soft);
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.28);
        }

        .top-nav-active {
            text-align: center;
            background: linear-gradient(180deg, #ff857b 0%, #ff6a5f 100%);
            border: 1px solid #ff9b92;
            color: #0e111d;
            padding: 0.5rem 0.6rem;
            font-weight: 700;
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .top-nav-wrap {
            background: linear-gradient(180deg, rgba(18, 24, 39, 0.9) 0%, rgba(12, 16, 27, 0.9) 100%);
            border: 1px solid var(--line);
            padding: 0.8rem;
            margin-bottom: 1.1rem;
        }

        .top-nav-title {
            color: #d8e3ff;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }

        .site-watermark {
            position: fixed;
            right: 14px;
            bottom: 10px;
            color: rgba(212, 220, 240, 0.22);
            font-size: 11px;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font-weight: 600;
            pointer-events: none;
            user-select: none;
            z-index: 9999;
            mix-blend-mode: screen;
        }

        @media (max-width: 860px) {
            .site-watermark {
                right: 10px;
                bottom: 8px;
                font-size: 9px;
                letter-spacing: 0.12em;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='site-watermark'>kobescodes</div>", unsafe_allow_html=True)


def render_top_navigation(current_page: str) -> None:
    """Render a horizontal top navigation bar for all app pages."""
    st.markdown("<div class='top-nav-wrap'><div class='top-nav-title'>NeuroPipe-SABV</div>", unsafe_allow_html=True)

    cols = st.columns(len(NAV_ITEMS))
    for col, (key, path, label) in zip(cols, NAV_ITEMS):
        with col:
            if key == current_page:
                st.markdown(f"<div class='top-nav-active'>{label}</div>", unsafe_allow_html=True)
            else:
                st.page_link(path, label=label)

    st.markdown("</div>", unsafe_allow_html=True)
