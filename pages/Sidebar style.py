"""
sidebar_style.py
────────────────
Place this file next to your pages/ folder.
Call apply_sidebar_style() at the top of EVERY page (including app.py).

from sidebar_style import apply_sidebar_style
apply_sidebar_style()
"""

import streamlit as st


SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── global font ── */
html, body, * { font-family: 'Inter', sans-serif !important; }

/* ── sidebar shell ── */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #161d2e !important;
    min-width: 230px !important;
    max-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 0.9rem !important;
}

/* ── brand block ── */
.sb-brand {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 14px;
    border-bottom: 1px solid #161d2e;
    margin-bottom: 16px;
}
.sb-logo {
    width: 36px; height: 36px; min-width: 36px;
    background: #0f2e1a; border: 1px solid #1a5c30;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
}
.sb-name    { font-size: 13px; font-weight: 800; color: #f1f5f9; line-height: 1.1; }
.sb-tagline { font-size: 10px; color: #94a3b8; }

/* ── section label ── */
.sb-section {
    font-size: 9.5px; font-weight: 700; color: #64748b;
    text-transform: uppercase; letter-spacing: 1.4px;
    margin: 16px 4px 6px 4px;
}

/* ── nav links — Streamlit native ── */
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNavItems"] a {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 9px 10px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #e2e8f0 !important;
    text-decoration: none !important;
    margin-bottom: 2px !important;
    transition: background 0.15s, color 0.15s !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNavItems"] a:hover {
    background: #1e2d45 !important;
    color: #ffffff !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNavItems"] a[aria-current="page"] {
    background: linear-gradient(135deg, #1a0533, #0c1a40) !important;
    color: #e9d5ff !important;
    border: 1px solid #2d1b5e !important;
    font-weight: 700 !important;
}

/* hide default Streamlit nav icons */
[data-testid="stSidebarNav"] svg,
[data-testid="stSidebarNavItems"] svg { display: none !important; }

/* ── page_link widget override ── */
[data-testid="stPageLink"] a {
    background: transparent !important;
    border-radius: 9px !important;
    padding: 9px 10px !important;
    color: #e2e8f0 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    display: block !important;
    transition: background 0.15s, color 0.15s !important;
    margin-bottom: 2px !important;
}
[data-testid="stPageLink"] a:hover {
    background: #1e2d45 !important;
    color: #ffffff !important;
}

/* ── footer at bottom ── */
.sb-footer {
    font-size: 9.5px; color: #64748b;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
    border-top: 1px solid #1e2d45;
    padding-top: 10px; text-align: center;
    margin-top: 24px;
}
</style>

"""


def apply_sidebar_style(active_page: str = ""):
    """
    Call at the top of every page file to apply the dark sidebar.
    Pass active_page to highlight the current nav link.

    Example:
        from sidebar_style import apply_sidebar_style
        apply_sidebar_style("RM Inventory")
    """
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # ── Brand
        st.markdown("""
        <div class="sb-brand">
            <div class="sb-logo">🌱</div>
            <div>
                <div class="sb-name">Sproutlife</div>
                <div class="sb-tagline">Inventory Suite</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Nav using st.page_link (Streamlit ≥ 1.26)
        # Replace the page paths with your actual file paths inside pages/
        st.markdown('<div class="sb-section">Menu</div>', unsafe_allow_html=True)

        pages = [
            ("📦", "RM Inventory",          "pages/1_RM_Inventory.py"),
            ("📋", "GRN Data",              "pages/2_GRN_Data.py"),
            ("🏭", "FG Inventory",          "pages/3_FG_Inventory.py"),
            ("🍽️", "Consumption",           "pages/4_Consumption.py"),
            ("📈", "Forecast",              "pages/5_Forecast.py"),
            ("🔄", "Replenishment",         "pages/6_Replenishment.py"),
            ("⚖️", "Consumption vs Forecast","pages/7_Consumption_vs_Forecast.py"),
            ("🤖", "ERP Assistant",         "pages/8_ERP_Assistant.py"),
        ]

        for icon, label, path in pages:
            try:
                st.page_link(path, label=f"{icon}  {label}", use_container_width=True)
            except Exception:
                # Fallback if page_link not available or path wrong
                st.markdown(
                    f'<div style="padding:9px 10px;border-radius:9px;font-size:13px;'
                    f'font-weight:600;color:#e2e8f0;margin-bottom:2px;">'
                    f'{icon}  {label}</div>',
                    unsafe_allow_html=True
                )

        st.markdown('<div class="sb-footer">SPROUTLIFE FOODS v2.0</div>',
                    unsafe_allow_html=True)
