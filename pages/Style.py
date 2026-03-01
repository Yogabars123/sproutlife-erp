import streamlit as st

def apply_global_styles():
    st.markdown("""
    <style>
    /* ─── GOOGLE FONTS ─────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    /* ─── ROOT VARIABLES ───────────────────────────── */
    :root {
        --primary:       #1A56DB;
        --primary-light: #EBF2FF;
        --primary-dark:  #1140A8;
        --accent:        #0EA5E9;
        --success:       #16A34A;
        --success-bg:    #F0FDF4;
        --warning:       #B45309;
        --warning-bg:    #FFFBEB;
        --danger:        #DC2626;
        --danger-bg:     #FEF2F2;
        --bg:            #F8FAFC;
        --surface:       #FFFFFF;
        --border:        #E2E8F0;
        --border-focus:  #93C5FD;
        --text-primary:  #0F172A;
        --text-secondary:#475569;
        --text-muted:    #94A3B8;
        --shadow-sm:     0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
        --shadow-md:     0 4px 16px rgba(15,23,42,0.08), 0 2px 4px rgba(15,23,42,0.04);
        --shadow-lg:     0 10px 32px rgba(15,23,42,0.10), 0 4px 8px rgba(15,23,42,0.06);
        --radius-sm:     8px;
        --radius-md:     12px;
        --radius-lg:     16px;
        --transition:    all 0.18s cubic-bezier(0.4,0,0.2,1);
    }

    /* ─── GLOBAL RESET ─────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* ─── APP BACKGROUND ───────────────────────────── */
    .stApp {
        background: var(--bg) !important;
    }

    /* ─── SIDEBAR ──────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 2px 0 16px rgba(15,23,42,0.05) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
    }
    [data-testid="stSidebarNavLink"] {
        border-radius: var(--radius-sm) !important;
        margin: 2px 8px !important;
        padding: 8px 12px !important;
        transition: var(--transition) !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebarNavLink"]:hover {
        background: var(--primary-light) !important;
        color: var(--primary) !important;
    }
    [data-testid="stSidebarNavLink"][aria-selected="true"] {
        background: var(--primary-light) !important;
        color: var(--primary) !important;
        font-weight: 600 !important;
        border-left: 3px solid var(--primary) !important;
    }

    /* ─── MAIN CONTENT AREA ────────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1280px !important;
    }

    /* ─── PAGE HEADING (h1) ────────────────────────── */
    h1 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.15rem !important;
        line-height: 1.2 !important;
    }
    h2 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.01em !important;
    }
    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
    }

    /* ─── SUBTITLE / CAPTION ───────────────────────── */
    .subtitle {
        color: var(--text-muted) !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        margin-bottom: 1.5rem !important;
    }

    /* ─── BUTTONS ──────────────────────────────────── */
    .stButton > button {
        background: var(--primary) !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.55rem 1.4rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 1px 3px rgba(26,86,219,0.25) !important;
        transition: var(--transition) !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background: var(--primary-dark) !important;
        box-shadow: 0 4px 12px rgba(26,86,219,0.30) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ─── TEXT INPUT / SEARCH ──────────────────────── */
    .stTextInput > div > div > input,
    .stTextInput input {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.55rem 1rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: var(--transition) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(147,197,253,0.30) !important;
        outline: none !important;
    }

    /* ─── SELECT BOX ───────────────────────────────── */
    .stSelectbox > div > div {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: var(--shadow-sm) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
        transition: var(--transition) !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(147,197,253,0.30) !important;
    }

    /* ─── DATAFRAME / TABLE ────────────────────────── */
    .stDataFrame, [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stDataFrame"] th {
        background: #F1F5F9 !important;
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid var(--border) !important;
    }
    [data-testid="stDataFrame"] td {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.82rem !important;
        color: var(--text-primary) !important;
        padding: 9px 14px !important;
        border-bottom: 1px solid #F1F5F9 !important;
    }
    [data-testid="stDataFrame"] tr:hover td {
        background: var(--primary-light) !important;
    }

    /* ─── TOGGLE ────────────────────────────────────── */
    .stToggle span {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }

    /* ─── DIVIDER ───────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ─── METRIC CARDS (via st.metric) ─────────────── */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.2rem 1.5rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: var(--transition) !important;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }

    /* ─── HIDE STREAMLIT CHROME ─────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    /* ─── SPINNER ───────────────────────────────────── */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    </style>
    """, unsafe_allow_html=True)


# ─── REUSABLE STAT CARD HTML ─────────────────────────────────────────────────
def stat_card(label: str, value: str, sub: str = "", color: str = "#1A56DB", icon: str = ""):
    """
    Render a professional KPI stat card.

    Usage:
        st.markdown(stat_card("Total QTY Available", "16,300,788", "2,414 records"), unsafe_allow_html=True)
    """
    return f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {color}cc 100%);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        color: #fff;
        box-shadow: 0 6px 20px {color}40;
        margin-bottom: 1rem;
        transition: all 0.18s ease;
    ">
        <div style="font-size:0.7rem; font-weight:700; letter-spacing:0.08em;
                    text-transform:uppercase; opacity:0.8; margin-bottom:0.4rem;">
            {icon} {label}
        </div>
        <div style="font-size:2.1rem; font-weight:800; letter-spacing:-0.03em;
                    line-height:1.1; margin-bottom:0.3rem;">
            {value}
        </div>
        <div style="font-size:0.78rem; opacity:0.7; font-weight:400;">
            {sub}
        </div>
    </div>
    """


def page_header(icon: str, title: str, subtitle: str = ""):
    """
    Render a clean page header with icon, title, and subtitle.

    Usage:
        page_header("📦", "RM Inventory", "Live raw material stock")
    """
    st.markdown(f"""
    <div style="margin-bottom: 1.8rem; padding-bottom: 1.2rem;
                border-bottom: 1px solid #E2E8F0;">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.3rem;">
            <span style="font-size:1.8rem; line-height:1;">{icon}</span>
            <h1 style="margin:0; font-family:'DM Sans',sans-serif; font-size:1.75rem;
                       font-weight:700; color:#0F172A; letter-spacing:-0.02em;">
                {title}
            </h1>
        </div>
        <p style="margin:0; font-size:0.875rem; color:#94A3B8; font-weight:400;
                  padding-left:2.6rem;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)


def section_label(text: str):
    """Small uppercase section label above filters or groups."""
    st.markdown(f"""
    <div style="font-size:0.7rem; font-weight:700; letter-spacing:0.08em;
                text-transform:uppercase; color:#94A3B8; margin-bottom:0.4rem;">
        {text}
    </div>
    """, unsafe_allow_html=True)
