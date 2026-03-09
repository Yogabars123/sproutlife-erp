import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="GRN Data · Sproutlife",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("GRN Data")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── GLOBAL ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"], .main {
    background: #080b12 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1rem 1.2rem 3rem 1.2rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── HEADER ── */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 14px; border-bottom: 1px solid #161d2e; margin-bottom: 16px;
}
.hdr-left { display: flex; align-items: center; gap: 10px; }
.hdr-logo {
    width: 40px; height: 40px; min-width: 40px;
    background: #0c1f3a; border: 1px solid #1e3a5f; border-radius: 11px;
    display: flex; align-items: center; justify-content: center; font-size: 19px;
}
.hdr-title { font-size: 16px; font-weight: 800; color: #f1f5f9; white-space: nowrap; }
.hdr-sub   { font-size: 11px; color: #64748b; white-space: nowrap; }

/* ── 4 KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 18px;
}
@media (max-width: 768px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
.kpi-card {
    border-radius: 16px; padding: 18px 20px;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-card.blue   { background: linear-gradient(135deg, #0c1f3a, #0f2d5e); border: 1px solid #1e3a5f; }
.kpi-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-card.green  { background: linear-gradient(135deg, #052e16, #064e3b); border: 1px solid #166534; }
.kpi-card.green::before  { background: linear-gradient(90deg, #22c55e, #4ade80); }
.kpi-card.amber  { background: linear-gradient(135deg, #1c1500, #2d1f00); border: 1px solid #854d0e; }
.kpi-card.amber::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-card.red    { background: linear-gradient(135deg, #1f0707, #3b0a0a); border: 1px solid #991b1b; }
.kpi-card.red::before    { background: linear-gradient(90deg, #ef4444, #f87171); }

.kpi-lbl {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; margin-bottom: 8px;
}
.kpi-card.blue  .kpi-lbl { color: #60a5fa; }
.kpi-card.green .kpi-lbl { color: #4ade80; }
.kpi-card.amber .kpi-lbl { color: #fbbf24; }
.kpi-card.red   .kpi-lbl { color: #f87171; }

.kpi-num {
    font-size: 28px; font-weight: 800; color: #f1f5f9;
    letter-spacing: -1px; line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-cap { font-size: 11px; color: #475569; margin-top: 5px; }

/* ── SEARCH ── */
.search-wrap {
    background: #0d1117; border: 1px solid #1e2535;
    border-radius: 14px; padding: 12px 14px; margin-bottom: 14px;
}
.search-label {
    font-size: 10px; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}
.search-label::after { content: ''; flex: 1; height: 1px; background: #1e2535; }

[data-testid="stTextInput"] > div > div {
    background: #111827 !important; border: 1.5px solid #1e2d45 !important; border-radius: 9px !important;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
[data-testid="stTextInput"] input {
    background: transparent !important; color: #f1f5f9 !important;
    font-size: 13px !important; padding: 9px 12px !important;
    border: none !important; box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #334155 !important; }
[data-testid="stWidgetLabel"] { display: none !important; }

/* ── TABLE ── */
.sec-div {
    font-size: 10px; font-weight: 700; color: #334155; text-transform: uppercase;
    letter-spacing: 1.2px; padding: 12px 0 8px 0;
    display: flex; align-items: center; gap: 7px;
}
.sec-div::after { content: ''; flex: 1; height: 1px; background: #161d2e; }
.tbl-hdr { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; }
.tbl-lbl { font-size: 10px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.2px; }
.tbl-badge {
    background: #0f172a; border: 1px solid #1e2d45; color: #60a5fa;
    font-size: 11px; font-weight: 700; padding: 3px 11px;
    border-radius: 20px; font-family: 'JetBrains Mono', monospace;
}
div[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important; border: 1px solid #1e2535 !important;
}

.app-footer {
    margin-top: 2rem; padding-top: 12px; border-top: 1px solid #161d2e;
    text-align: center; font-size: 10px; font-weight: 600; color: #334155;
    letter-spacing: 1.5px; font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════
@st.cache_data
def load_data():
    df = load_sheet("GRN-Data")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

for col in ["QuantityOrdered", "QuantityReceived", "QuantityRejected"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

base_df = df[
    (df["Warehouse"] == "Central") &
    (df["PO No"].notna()) &
    (df["PO No"].astype(str).str.strip() != "") &
    (df["PO No"].astype(str).str.strip() != "-")
]

# ════════════════════════════════════════
# HEADER
# ════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📥</div>
        <div>
            <div class="hdr-title">GRN Data</div>
            <div class="hdr-sub">Sproutlife Foods · Goods Received Notes</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# SEARCH
# ════════════════════════════════════════
st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
st.markdown('<div class="search-label">🔍 Search</div>', unsafe_allow_html=True)
search_text = st.text_input("_search", placeholder="Search GRN No / Item Code / Item Name / PO No…",
                             label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

filtered_df = base_df.copy()
if search_text:
    s = search_text.lower()
    filtered_df = filtered_df[
        filtered_df.apply(lambda row:
            s in str(row.get("GRN No","")).lower() or
            s in str(row.get("Item Code","")).lower() or
            s in str(row.get("Item Name","")).lower() or
            s in str(row.get("PO No","")).lower(), axis=1)
    ]

# ════════════════════════════════════════
# KPI CARDS
# ════════════════════════════════════════
total_ordered  = filtered_df["QuantityOrdered"].sum()
total_received = filtered_df["QuantityReceived"].sum()
total_rejected = filtered_df["QuantityRejected"].sum()
pending_qty    = total_ordered - total_received

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card blue">
        <div class="kpi-lbl">Ordered Quantity</div>
        <div class="kpi-num">{total_ordered:,.0f}</div>
        <div class="kpi-cap">Total PO qty raised</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-lbl">Received Quantity</div>
        <div class="kpi-num">{total_received:,.0f}</div>
        <div class="kpi-cap">Total GRN qty received</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-lbl">Pending Quantity</div>
        <div class="kpi-num">{pending_qty:,.0f}</div>
        <div class="kpi-cap">Ordered − Received</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-lbl">Rejected Quantity</div>
        <div class="kpi-num">{total_rejected:,.0f}</div>
        <div class="kpi-cap">Quality rejections</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# TABLE
# ════════════════════════════════════════
st.markdown('<div class="sec-div">GRN Records — Central + Valid PO Only</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 All columns</span>
    <span class="tbl-badge">{len(filtered_df):,} rows</span>
</div>
""", unsafe_allow_html=True)

st.dataframe(filtered_df, use_container_width=True, height=520, hide_index=True)

st.markdown('<div class="app-footer">SPROUTLIFE FOODS · GRN DATA</div>', unsafe_allow_html=True)
