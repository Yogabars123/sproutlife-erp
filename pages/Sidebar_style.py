import streamlit as st

PAGES = [
    ("🏠", "Home",                    "app.py"),
    ("🗄️", "RM Inventory",            "pages/1_RM_Inventory.py"),
    ("📥", "GRN Data",                "pages/2_GRN_Data.py"),
    ("📦", "FG Inventory",            "pages/3_FG_Inventory.py"),
    ("🏭", "Consumption",             "pages/4_Consumption.py"),
    ("📊", "Forecast",                "pages/5_Forecast.py"),
    ("🛒", "Replenishment",           "pages/6_Replenishment.py"),
    ("📈", "Consumption vs Forecast", "pages/7_Consumption_vs_Forecast.py"),
]

def inject_sidebar(current_page: str = ""):
    with st.sidebar:
        # ── Brand ──────────────────────────────────────────────
        st.markdown("""
        <div style="
            background: linear-gradient(135deg,#0f2460,#1A56DB 60%,#22c55e);
            border-radius: 16px; padding: 20px 16px 16px;
            margin-bottom: 8px; text-align: center;">
            <div style="font-size:32px;line-height:1;">🌱</div>
            <div style="color:#fff;font-size:17px;font-weight:800;margin-top:6px;">Sproutlife</div>
            <div style="color:rgba(255,255,255,.6);font-size:11px;margin-top:3px;">Inventory Management</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Sidebar CSS ────────────────────────────────────────
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] > div:first-child {
            background: #0f172a !important;
            padding: 12px 10px !important;
        }
        /* Hide Streamlit's default auto-generated nav */
        section[data-testid="stSidebar"] ul { display:none !important; }

        .snav-label {
            font-size:10px; font-weight:700; color:#475569;
            letter-spacing:1.4px; text-transform:uppercase;
            padding:14px 8px 6px; display:block;
        }

        /* Style st.page_link items */
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
            display:flex !important; align-items:center !important;
            padding:9px 12px !important; border-radius:10px !important;
            font-size:13.5px !important; font-weight:500 !important;
            color:#94a3b8 !important; text-decoration:none !important;
            transition:background .15s,color .15s !important;
            margin-bottom:2px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background:rgba(99,102,241,.15) !important;
            color:#a5b4fc !important;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink-active"] a {
            background:rgba(26,86,219,.25) !important;
            color:#60a5fa !important;
            font-weight:700 !important;
        }
        /* Remove default padding around page_link */
        section[data-testid="stSidebar"] [data-testid="stPageLink"] {
            padding: 0 !important;
            margin: 0 !important;
        }

        .snav-footer {
            font-size:11px; color:#334155;
            text-align:center; padding-top:12px;
        }
        section[data-testid="stSidebar"] { min-width:230px !important; }
        </style>
        """, unsafe_allow_html=True)

        # ── Nav links using st.page_link ───────────────────────
        st.markdown('<span class="snav-label">Navigation</span>', unsafe_allow_html=True)

        for icon, label, path in PAGES:
            st.page_link(path, label=f"{icon}  {label}")

        st.markdown('<hr style="border-color:#1e293b;margin:10px 0">', unsafe_allow_html=True)
        st.markdown('<div class="snav-footer">© 2025 Sproutlife Foods</div>', unsafe_allow_html=True)
