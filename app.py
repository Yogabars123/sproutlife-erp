import streamlit as st

st.set_page_config(
    page_title="Sproutlife ERP",
    layout="wide",
    page_icon="🌱",
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

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #0f2460 0%, #1A56DB 50%, #0d9e5c 100%);
    border-radius: 20px;
    padding: 48px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-emoji  { font-size: 52px; margin-bottom: 12px; }
.hero-title  { font-size: 32px; font-weight: 800; color: #fff; letter-spacing: -0.5px; margin-bottom: 8px; }
.hero-sub    { font-size: 15px; color: rgba(255,255,255,0.7); max-width: 520px; line-height: 1.6; }

/* ── SECTION LABEL ── */
.sec-label {
    font-size: 10px; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 1.4px;
    padding: 20px 0 10px 0; display: flex; align-items: center; gap: 8px;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: #1e2535; }

/* ── NAV CARDS ── */
.nav-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 28px;
}
@media (max-width: 900px) { .nav-grid { grid-template-columns: repeat(2, 1fr); } }

.nav-card {
    background: #0d1117;
    border: 1px solid #1e2535;
    border-radius: 16px;
    padding: 20px 22px;
    text-decoration: none !important;
    display: block;
    transition: border-color 0.2s, transform 0.15s, background 0.2s;
    cursor: pointer;
}
.nav-card:hover {
    border-color: #3b82f6;
    background: #111827;
    transform: translateY(-2px);
}
.nav-card-icon  { font-size: 28px; margin-bottom: 10px; }
.nav-card-title {
    font-size: 14px; font-weight: 700; color: #f1f5f9;
    margin-bottom: 4px;
}
.nav-card-desc  { font-size: 12px; color: #475569; line-height: 1.5; }

/* ── FOOTER ── */
.home-footer {
    text-align: center; font-size: 11px; font-weight: 600;
    color: #1e2535; letter-spacing: 1.5px;
    font-family: 'JetBrains Mono', monospace;
    padding-top: 16px; border-top: 1px solid #161d2e;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-emoji">🌱</div>
    <div class="hero-title">Sproutlife ERP Dashboard</div>
    <div class="hero-sub">
        Real-time inventory, forecasting, and production insights
        for Sproutlife Foods. Select a module from the sidebar or below.
    </div>
</div>
""", unsafe_allow_html=True)

# ── NAV CARDS ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Modules</div>', unsafe_allow_html=True)

st.markdown("""
<div class="nav-grid">
    <a class="nav-card" href="/1_RM_Inventory" target="_self">
        <div class="nav-card-icon">🗄️</div>
        <div class="nav-card-title">RM Inventory</div>
        <div class="nav-card-desc">Raw material stock levels, days of supply, and warehouse-wise breakdown.</div>
    </a>
    <a class="nav-card" href="/2_GRN_Data" target="_self">
        <div class="nav-card-icon">📥</div>
        <div class="nav-card-title">GRN Data</div>
        <div class="nav-card-desc">Goods received notes — ordered, received, pending and rejected quantities.</div>
    </a>
    <a class="nav-card" href="/3_FG_Inventory" target="_self">
        <div class="nav-card-icon">📦</div>
        <div class="nav-card-title">FG Inventory</div>
        <div class="nav-card-desc">Finished goods stock with shelf life tracking and expiry alerts.</div>
    </a>
    <a class="nav-card" href="/4_Consumption" target="_self">
        <div class="nav-card-icon">🏭</div>
        <div class="nav-card-title">Consumption</div>
        <div class="nav-card-desc">Batch-wise material consumption and total production quantities.</div>
    </a>
    <a class="nav-card" href="/5_Forecast" target="_self">
        <div class="nav-card-icon">📊</div>
        <div class="nav-card-title">Forecast</div>
        <div class="nav-card-desc">Demand forecast vs SOH with critical stock alerts by days of supply.</div>
    </a>
    <a class="nav-card" href="/6_Replenishment" target="_self">
        <div class="nav-card-icon">🛒</div>
        <div class="nav-card-title">Replenishment</div>
        <div class="nav-card-desc">Auto-generated order suggestions for items under 10 days of stock.</div>
    </a>
    <a class="nav-card" href="/7_Consumption_vs_Forecast" target="_self">
        <div class="nav-card-icon">📈</div>
        <div class="nav-card-title">Consumption vs Forecast</div>
        <div class="nav-card-desc">Variance analysis — actual consumption compared against forecast per material.</div>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="home-footer">SPROUTLIFE FOODS · INVENTORY MANAGEMENT SYSTEM</div>',
            unsafe_allow_html=True)
