import streamlit as st

LOGO_URI = "data:image/webp;base64,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"

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
        st.markdown(f"""
        <div style="
            background: #5bc8c0;
            border-radius: 16px; padding: 16px 16px 12px;
            margin-bottom: 8px; text-align: center;">
            <img src="{LOGO_URI}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;margin-bottom:6px;">
            <div style="color:#fff;font-size:17px;font-weight:800;margin-top:4px;letter-spacing:0.3px;">YogaBar</div>
            <div style="color:rgba(255,255,255,.75);font-size:11px;margin-top:2px;">Inventory Management</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        /* ── Force sidebar always open ── */
        section[data-testid="stSidebar"] {
            transform: none !important;
            min-width: 230px !important;
            width: 230px !important;
            visibility: visible !important;
            display: block !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: none !important;
            margin-left: 0 !important;
        }
        /* Hide the collapse arrow button */
        button[data-testid="collapsedControl"],
        button[kind="header"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] > div:first-child {
            background: #0f172a !important;
            padding: 12px 10px !important;
        }
        section[data-testid="stSidebar"] ul { display:none !important; }
        .snav-label {
            font-size:10px; font-weight:700; color:#475569;
            letter-spacing:1.4px; text-transform:uppercase;
            padding:14px 8px 6px; display:block;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
            display:flex !important; align-items:center !important;
            padding:9px 12px !important; border-radius:10px !important;
            font-size:13.5px !important; font-weight:500 !important;
            color:#94a3b8 !important; text-decoration:none !important;
            transition:background .15s,color .15s !important;
            margin-bottom:2px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background:rgba(91,200,192,.15) !important;
            color:#5bc8c0 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink-active"] a {
            background:rgba(91,200,192,.2) !important;
            color:#5bc8c0 !important;
            font-weight:700 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] {
            padding: 0 !important; margin: 0 !important;
        }
        .snav-footer {
            font-size:11px; color:#334155;
            text-align:center; padding-top:12px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<span class="snav-label">Navigation</span>', unsafe_allow_html=True)

        for icon, label, path in PAGES:
            st.page_link(path, label=f"{icon}  {label}")

        st.markdown('<hr style="border-color:#1e293b;margin:10px 0">', unsafe_allow_html=True)
        st.markdown('<div class="snav-footer">© 2025 YogaBar</div>', unsafe_allow_html=True)
