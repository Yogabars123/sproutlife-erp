import streamlit as st

PAGES = [
    ("🏠", "Home",                    "/"),
    ("🗄️", "RM Inventory",            "/1_RM_Inventory"),
    ("📥", "GRN Data",                "/2_GRN_Data"),
    ("📦", "FG Inventory",            "/3_FG_Inventory"),
    ("🏭", "Consumption",             "/4_Consumption"),
    ("📊", "Forecast",                "/5_Forecast"),
    ("🔁", "Replenishment",           "/6_Replenishment"),
    ("📈", "Consumption vs Forecast", "/7_Consumption_vs_Forecast"),
]

def inject_sidebar(current_page: str = ""):
    with st.sidebar:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg,#0f2460,#1A56DB 60%,#22c55e);
            border-radius: 16px; padding: 20px 16px 16px;
            margin-bottom: 4px; text-align: center;">
            <div style="font-size:32px;line-height:1;">🌱</div>
            <div style="color:#fff;font-size:17px;font-weight:800;margin-top:6px;">Sproutlife</div>
            <div style="color:rgba(255,255,255,.6);font-size:11px;margin-top:3px;">Inventory Management</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
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
        a.snav-link {
            display:flex; align-items:center; gap:10px;
            padding:9px 12px; border-radius:10px;
            font-size:13.5px; font-weight:500;
            color:#94a3b8 !important; text-decoration:none !important;
            transition:background .15s,color .15s; margin-bottom:2px;
        }
        a.snav-link:hover { background:rgba(99,102,241,.15); color:#a5b4fc !important; }
        a.snav-link.active { background:rgba(26,86,219,.25); color:#60a5fa !important; font-weight:700; }
        .snav-icon { font-size:16px; width:22px; text-align:center; }
        .snav-footer { font-size:11px; color:#334155; text-align:center; padding-top:12px; }
        section[data-testid="stSidebar"] { min-width:230px !important; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<span class="snav-label">Navigation</span>', unsafe_allow_html=True)

        links_html = ""
        for icon, label, path in PAGES:
            active_cls = "active" if label == current_page else ""
            links_html += f'<a href="{path}" target="_self" class="snav-link {active_cls}"><span class="snav-icon">{icon}</span><span>{label}</span></a>'

        st.markdown(links_html, unsafe_allow_html=True)
        st.markdown('<hr style="border-color:#1e293b;margin:10px 0">', unsafe_allow_html=True)
        st.markdown('<div class="snav-footer">© 2025 Sproutlife Foods</div>', unsafe_allow_html=True)

