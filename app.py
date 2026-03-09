import streamlit as st

st.set_page_config(
    page_title="YogaBar ERP",
    layout="wide",
    page_icon="🥗",
    initial_sidebar_state="expanded"
)

from pages.Sidebar_style import inject_sidebar
inject_sidebar("Home")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"], .main {
    background: #080b12 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 100% !important; }

.hero {
    background: linear-gradient(135deg, #0d6b63 0%, #5bc8c0 50%, #0d9e5c 100%);
    border-radius: 20px; padding: 48px 40px; margin-bottom: 28px;
}
.hero-title { font-size: 32px; font-weight: 800; color: #fff; letter-spacing: -0.5px; margin-bottom: 8px; }
.hero-sub   { font-size: 15px; color: rgba(255,255,255,0.85); max-width: 520px; line-height: 1.6; }

.sec-label {
    font-size: 10px; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 1.4px;
    padding: 20px 0 10px 0; display: flex; align-items: center; gap: 8px;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: #1e2535; }

.mod-card {
    background: #0d1117; border: 1px solid #1e2535;
    border-radius: 16px; padding: 20px 22px 10px 22px; margin-bottom: 4px;
}
.mod-icon  { font-size: 28px; margin-bottom: 10px; }
.mod-title { font-size: 14px; font-weight: 700; color: #f1f5f9; margin-bottom: 4px; }
.mod-desc  { font-size: 12px; color: #475569; line-height: 1.5; margin-bottom: 14px; }

div[data-testid="stButton"] > button {
    background: #111827 !important; border: 1px solid #1e4d4a !important;
    border-radius: 8px !important; color: #5bc8c0 !important;
    font-size: 12px !important; font-weight: 600 !important;
    padding: 6px 12px !important; width: 100% !important;
    transition: all 0.15s !important; margin-bottom: 14px !important;
}
div[data-testid="stButton"] > button:hover {
    background: #0d2e2c !important; border-color: #5bc8c0 !important; color: #fff !important;
}

.home-footer {
    text-align: center; font-size: 11px; font-weight: 600; color: #1e2535;
    letter-spacing: 1.5px; font-family: 'JetBrains Mono', monospace;
    padding-top: 16px; border-top: 1px solid #161d2e; margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🥗 YogaBar ERP Dashboard</div>
    <div class="hero-sub">
        Real-time inventory, forecasting, and production insights
        for YogaBar. Select a module from the sidebar or below.
    </div>
</div>
""", unsafe_allow_html=True)

# ── MODULE CARDS ──────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Modules</div>', unsafe_allow_html=True)

MODULES = [
    ("🗄️", "RM Inventory",            "Raw material stock levels, days of supply, and warehouse-wise breakdown.",   "pages/1_RM_Inventory.py"),
    ("📥", "GRN Data",                "Goods received notes — ordered, received, pending and rejected quantities.", "pages/2_GRN_Data.py"),
    ("📦", "FG Inventory",            "Finished goods stock with shelf life tracking and expiry alerts.",            "pages/3_FG_Inventory.py"),
    ("🏭", "Consumption",             "Batch-wise material consumption and total production quantities.",            "pages/4_Consumption.py"),
    ("📊", "Forecast",                "Demand forecast vs SOH with critical stock alerts by days of supply.",        "pages/5_Forecast.py"),
    ("🛒", "Replenishment",           "Auto-generated order suggestions for items under 10 days of stock.",         "pages/6_Replenishment.py"),
    ("📈", "Consumption vs Forecast", "Variance analysis — actual consumption compared against forecast.",          "pages/7_Consumption_vs_Forecast.py"),
]

for row_start in range(0, len(MODULES), 3):
    row = MODULES[row_start:row_start + 3]
    cols = st.columns(3)
    for col, (icon, title, desc, path) in zip(cols, row):
        with col:
            st.markdown(f"""
            <div class="mod-card">
                <div class="mod-icon">{icon}</div>
                <div class="mod-title">{title}</div>
                <div class="mod-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Open {title} →", key=f"nav_{title}"):
                st.switch_page(path)

st.markdown('<div class="home-footer">YOGABAR · INVENTORY MANAGEMENT SYSTEM</div>',
            unsafe_allow_html=True)
