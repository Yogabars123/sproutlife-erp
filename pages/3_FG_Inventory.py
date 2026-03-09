import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

st.set_page_config(
    page_title="FG Inventory · YogaBar",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="expanded"
)

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("FG Inventory")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

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
    padding-bottom: 14px; border-bottom: 1px solid #161d2e; margin-bottom: 14px;
}
.hdr-left { display: flex; align-items: center; gap: 10px; }
.hdr-logo {
    width: 40px; height: 40px; min-width: 40px;
    background: #0f1f3a; border: 1px solid #1a3a5c; border-radius: 11px;
    display: flex; align-items: center; justify-content: center; font-size: 19px;
}
.hdr-title { font-size: 16px; font-weight: 800; color: #f1f5f9; }
.hdr-sub   { font-size: 11px; color: #94a3b8; }
.live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #071a0f; border: 1px solid #166534;
    border-radius: 20px; padding: 5px 11px;
    font-size: 10px; font-weight: 700; color: #22c55e;
    letter-spacing: 1px; font-family: 'JetBrains Mono', monospace;
}
.live-dot {
    width: 6px; height: 6px; background: #22c55e; border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }

/* ── KPI CARDS ── */
.kpi-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 16px; }
.kpi-card {
    border-radius: 16px; padding: 18px 20px;
    position: relative; overflow: hidden;
    border: 1px solid; min-height: 110px;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    border-radius:16px 16px 0 0;
}
.kpi-card.blue  { background:linear-gradient(135deg,#0c1a3a,#0f2460); border-color:#1a3a6e; }
.kpi-card.blue::before  { background:linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-card.amber { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-card.amber::before { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.red   { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-card.red::before   { background:linear-gradient(90deg,#ef4444,#f87171); }

.kpi-lbl  { font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.kpi-card.blue  .kpi-lbl { color:#60a5fa; }
.kpi-card.amber .kpi-lbl { color:#fbbf24; }
.kpi-card.red   .kpi-lbl { color:#f87171; }
.kpi-num  {
    font-size:32px; font-weight:800; line-height:1;
    font-family:'JetBrains Mono',monospace; letter-spacing:-1px;
}
.kpi-card.blue  .kpi-num { color:#bfdbfe; }
.kpi-card.amber .kpi-num { color:#fde68a; }
.kpi-card.red   .kpi-num { color:#fecaca; }
.kpi-cap  { font-size:11px; margin-top:5px; }
.kpi-card.blue  .kpi-cap { color:#3b5a8a; }
.kpi-card.amber .kpi-cap { color:#78540a; }
.kpi-card.red   .kpi-cap { color:#7a2020; }

/* ── FILTER BOX ── */
.filter-wrap {
    background:#0d1117; border:1px solid #1e2535;
    border-radius:14px; padding:12px 14px; margin-bottom:14px;
}
.filter-title {
    font-size:10px; font-weight:700; color:#475569;
    text-transform:uppercase; letter-spacing:1.2px;
    margin-bottom:10px; display:flex; align-items:center; gap:6px;
}
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }

[data-testid="stTextInput"] > div > div {
    background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important;
}
[data-testid="stTextInput"] > div > div:focus-within { border-color:#5bc8c0 !important; }
[data-testid="stTextInput"] input {
    background:transparent !important; color:#f1f5f9 !important;
    font-size:13px !important; padding:9px 12px !important; border:none !important;
}
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div {
    background:#111827 !important; border:1.5px solid #1e2d45 !important;
    border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important;
}
[data-testid="stWidgetLabel"] { display:none !important; }

.stDownloadButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#0f172a,#1e1b4b) !important;
    border:1.5px solid #4338ca !important; border-radius:9px !important;
    color:#a5b4fc !important; font-size:13px !important;
    font-weight:700 !important; padding:10px !important;
}
.stDownloadButton > button:hover { background:linear-gradient(135deg,#1e1b4b,#312e81) !important; color:#fff !important; }

.stButton > button {
    width:100% !important; background:#0d1117 !important;
    border:1.5px solid #1e2535 !important; border-radius:9px !important;
    color:#64748b !important; font-size:13px !important;
    font-weight:600 !important; padding:9px !important;
    transition:all .2s !important; margin-bottom:6px !important;
}
.stButton > button:hover { border-color:#5bc8c0 !important; color:#5bc8c0 !important; background:#061413 !important; }

/* ── TABLE ── */
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:10px 0 6px; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge {
    background:#0f172a; border:1px solid #1e2d45; color:#818cf8;
    font-size:11px; font-weight:700; padding:3px 11px;
    border-radius:20px; font-family:'JetBrains Mono',monospace;
}
.sec-div {
    font-size:10px; font-weight:700; color:#334155; text-transform:uppercase;
    letter-spacing:1.2px; padding:12px 0 8px;
    display:flex; align-items:center; gap:7px;
}
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }

div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.app-footer {
    margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e;
    text-align:center; font-size:10px; font-weight:600; color:#334155;
    letter-spacing:1.5px; font-family:'JetBrains Mono',monospace;
}
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ────────────────────────────────────────────────────────────
@st.cache_data
def load_fg():
    # Data loaded from OneDrive via data_loader
    df = load_sheet("FG-Inventory")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)",
                "Value (Inc Tax)", "Value (Ex Tax)", "Current Aging (Days)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df_raw = load_fg()

today = pd.Timestamp(datetime.today().date())
if "Expiry Date" in df_raw.columns:
    remaining_days = (df_raw["Expiry Date"] - today).dt.days
    df_raw["_remaining_days"] = remaining_days.fillna(0).astype(int)
    if "MFG Date" in df_raw.columns:
        total_days = (df_raw["Expiry Date"] - df_raw["MFG Date"]).dt.days
        valid = total_days > 0
        pct = pd.Series(0.0, index=df_raw.index)
        pct[valid] = ((remaining_days[valid] / total_days[valid]) * 100).clip(0, 100)
        df_raw["Remaining Shelf Life (%)"] = pct.round(1)
    else:
        df_raw["Remaining Shelf Life (%)"] = 0.0

# ── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📦</div>
        <div>
            <div class="hdr-title">FG Inventory</div>
            <div class="hdr-sub">YogaBar · Finished Goods Stock</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ── FILTERS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2.5, 2, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search item / SKU / batch…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    sel_wh  = st.selectbox("w", wh_opts, label_visibility="collapsed")
with c3:
    sel_shelf = st.selectbox("sh", ["All", "Expiring in 30 days", "Expired"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ───────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh != "All Warehouses":
    df = df[df["Warehouse"] == sel_wh]
if "_remaining_days" in df.columns:
    if sel_shelf == "Expiring in 30 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 30)]
    elif sel_shelf == "Expired":
        df = df[df["_remaining_days"] < 0]

# ── KPI CARDS ───────────────────────────────────────────────────────────────
total_qty         = df["Qty Available"].sum()
expiring_qty      = df[df["_remaining_days"].between(0, 30)]["Qty Available"].sum() if "_remaining_days" in df.columns else 0
expired_qty       = df[df["_remaining_days"] < 0]["Qty Available"].sum()            if "_remaining_days" in df.columns else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card blue">
        <div class="kpi-lbl">Total Available Qty</div>
        <div class="kpi-num">{total_qty:,.0f}</div>
        <div class="kpi-cap">{len(df):,} records shown</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-lbl">Expiring in 30 Days · Qty</div>
        <div class="kpi-num">{expiring_qty:,.0f}</div>
        <div class="kpi-cap">Requires immediate attention</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-lbl">Expired · Qty</div>
        <div class="kpi-num">{expired_qty:,.0f}</div>
        <div class="kpi-cap">Past expiry date</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABLE ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 FG Records</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.drop(columns=["_remaining_days"], errors="ignore").to_excel(w, index=False, sheet_name="FG Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "FG_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️  No records match the current filters.")
else:
    display_df = df.drop(columns=["_remaining_days"], errors="ignore").copy()
    for c in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if c in display_df.columns:
            display_df[c] = display_df[c].dt.strftime("%d-%b-%Y").fillna("")
    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True,
        column_config={
            "Qty Available":              st.column_config.NumberColumn("Qty Avail",   format="%.0f"),
            "Qty Inward":                 st.column_config.NumberColumn("Inward",      format="%.0f"),
            "Qty (Issue / Hold)":         st.column_config.NumberColumn("Issue/Hold",  format="%.0f"),
            "Value (Inc Tax)":            st.column_config.NumberColumn("Val (Inc)",   format="%.0f"),
            "Value (Ex Tax)":             st.column_config.NumberColumn("Val (Ex)",    format="%.0f"),
            "Current Aging (Days)":       st.column_config.NumberColumn("Aging (d)",   format="%d"),
            "Remaining Shelf Life (%)":   st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
        })

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY</div>', unsafe_allow_html=True)
