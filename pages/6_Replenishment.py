import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Replenishment · YogaBar", layout="wide", page_icon="🛒", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("Replenishment")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], .main {
    background: #080b12 !important; font-family: 'Inter', sans-serif !important; color: #e2e8f0 !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1rem 1.2rem 3rem 1.2rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.app-header { display:flex; align-items:center; justify-content:space-between; padding-bottom:14px; border-bottom:1px solid #161d2e; margin-bottom:14px; }
.hdr-left { display:flex; align-items:center; gap:10px; }
.hdr-logo { width:40px; height:40px; min-width:40px; background:#1a0808; border:1px solid #7f1d1d; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:19px; }
.hdr-title { font-size:16px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 11px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.kpi-card { border-radius:16px; padding:16px 18px; position:relative; overflow:hidden; border:1px solid; min-height:100px; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-card.red    { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-card.orange { background:linear-gradient(135deg,#1a0800,#2a1000); border-color:#7c2d12; }
.kpi-card.orange::before { background:linear-gradient(90deg,#f97316,#fb923c); }
.kpi-card.amber  { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before   { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-lbl { font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.kpi-card.red    .kpi-lbl { color:#f87171; } .kpi-card.orange .kpi-lbl { color:#fb923c; }
.kpi-card.amber  .kpi-lbl { color:#fbbf24; } .kpi-card.teal   .kpi-lbl { color:#5bc8c0; }
.kpi-num { font-size:26px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-card.red    .kpi-num { color:#fecaca; } .kpi-card.orange .kpi-num { color:#fed7aa; }
.kpi-card.amber  .kpi-num { color:#fde68a; } .kpi-card.teal   .kpi-num { color:#99f6e4; }
.kpi-cap { font-size:11px; margin-top:5px; }
.kpi-card.red    .kpi-cap { color:#7f1d1d; } .kpi-card.orange .kpi-cap { color:#7c2d12; }
.kpi-card.amber  .kpi-cap { color:#78350f; } .kpi-card.teal   .kpi-cap { color:#134e4a; }
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }
[data-testid="stTextInput"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:#5bc8c0 !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:#f1f5f9 !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }
.stDownloadButton > button { width:100% !important; background:linear-gradient(135deg,#2d0000,#4a0808) !important; border:1.5px solid #991b1b !important; border-radius:9px !important; color:#fca5a5 !important; font-size:13px !important; font-weight:700 !important; padding:10px !important; }
.stButton > button { width:100% !important; background:#0d1117 !important; border:1.5px solid #1e2535 !important; border-radius:9px !important; color:#64748b !important; font-size:13px !important; font-weight:600 !important; padding:9px !important; transition:all .2s !important; margin-bottom:6px !important; }
.stButton > button:hover { border-color:#5bc8c0 !important; color:#5bc8c0 !important; }
.legend-bar { display:flex; gap:16px; align-items:center; background:#0d1117; border:1px solid #1e2535; border-radius:10px; padding:8px 14px; margin-bottom:12px; font-size:11px; }
.legend-dot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:5px; }
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:10px 0 6px; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:12px 0 8px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    SOH_WH = [
        "Central", "RM Warehouse Tumkur",
        "Central Warehouse - Cold Storage RM",
        "Tumkur Warehouse", "Tumkur New Warehouse",
        "HF Factory FG Warehouse",
        "Sproutlife Foods Private Ltd (SNOWMAN)"
    ]

    # ── RM Inventory SOH ─────────────────────────────────────────────────────
    df_rm = load_sheet("RM-Inventory")
    if df_rm.empty:
        return pd.DataFrame()
    df_rm.columns  = df_rm.columns.str.strip()
    df_rm["Warehouse"]     = df_rm["Warehouse"].astype(str).str.strip()
    df_rm["Qty Available"] = pd.to_numeric(df_rm.get("Qty Available", 0), errors="coerce").fillna(0)

    soh = (
        df_rm[df_rm["Warehouse"].isin(SOH_WH)]
        .groupby("Item SKU")
        .agg(SOH=("Qty Available","sum"), Item_Name=("Item Name","first"),
             Category=("Category","first"), UoM=("UoM","first"))
        .reset_index()
    )

    # ── Forecast — Plant only ─────────────────────────────────────────────────
    df_fc = load_sheet("Forecast")
    if df_fc.empty:
        return pd.DataFrame()
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    df_fc["Forecast"] = pd.to_numeric(df_fc.get("Forecast", 0), errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]

    if "Item code" not in df_fc.columns:
        return pd.DataFrame()

    df_fc["_key"] = df_fc["Item code"].astype(str).str.strip().str.upper()
    fc_agg = df_fc.groupby("_key")["Forecast"].sum().reset_index()

    # ── Merge ─────────────────────────────────────────────────────────────────
    soh["_key"] = soh["Item SKU"].astype(str).str.strip().str.upper()
    merged = soh.merge(fc_agg, on="_key", how="inner").drop(columns=["_key"])

    # ── Calculations ──────────────────────────────────────────────────────────
    merged["Per Day Req"]   = (merged["Forecast"] / 24).round(2)
    merged["Days of Stock"] = (merged["SOH"] / merged["Per Day Req"]).round(1).where(merged["Per Day Req"] > 0)

    # ── Filter: only < 10 days ────────────────────────────────────────────────
    critical = merged[merged["Days of Stock"] < 10].copy()
    critical["Suggested Order Qty"] = ((critical["Per Day Req"] * 30) - critical["SOH"]).clip(lower=0).round(0)
    critical = critical.sort_values("Days of Stock")

    return critical

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">🛒</div>
        <div>
            <div class="hdr-title">Replenishment Planner</div>
            <div class="hdr-sub">YogaBar · Items &lt; 10 Days of Stock · Plant Forecast</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df = load_data()

if df.empty:
    st.error("⚠️ No data loaded. Check Excel file.")
    st.stop()

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search SKU / item name…", label_visibility="collapsed")
with c2:
    if "Category" in df.columns:
        cat_opts = ["All Categories"] + sorted(df["Category"].dropna().astype(str).unique().tolist())
    else:
        cat_opts = ["All Categories"]
    sel_cat = st.selectbox("c", cat_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

df_view = df.copy()
if search:
    df_view = df_view[df_view.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_cat != "All Categories" and "Category" in df_view.columns:
    df_view = df_view[df_view["Category"].astype(str) == sel_cat]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
zero_stock   = (df_view["Days of Stock"] <= 0).sum()
under5       = ((df_view["Days of Stock"] > 0) & (df_view["Days of Stock"] < 5)).sum()
under10      = ((df_view["Days of Stock"] >= 5) & (df_view["Days of Stock"] < 10)).sum()
total_order  = df_view["Suggested Order Qty"].sum()

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card red">
        <div class="kpi-lbl">Zero / No Stock</div>
        <div class="kpi-num">{zero_stock:,}</div>
        <div class="kpi-cap">Immediate action needed</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-lbl">Under 5 Days</div>
        <div class="kpi-num">{under5:,}</div>
        <div class="kpi-cap">Urgent ordering required</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-lbl">5–10 Days</div>
        <div class="kpi-num">{under10:,}</div>
        <div class="kpi-cap">Plan orders this week</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-lbl">Total Order Qty</div>
        <div class="kpi-num">{total_order:,.0f}</div>
        <div class="kpi-cap">To cover 30 days stock</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">Critical Items</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">🚨 Items Needing Replenishment</span>
    <span class="tbl-badge">{len(df_view):,} items</span>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="legend-bar">
    <span><span class="legend-dot" style="background:#ef4444"></span><span style="color:#f87171">Zero stock</span></span>
    <span><span class="legend-dot" style="background:#f97316"></span><span style="color:#fb923c">Under 5 days</span></span>
    <span><span class="legend-dot" style="background:#f59e0b"></span><span style="color:#fbbf24">5–10 days</span></span>
    <span style="color:#475569; margin-left:auto; font-size:10px; font-family:'JetBrains Mono',monospace;">Per Day Req = Forecast ÷ 24 &nbsp;|&nbsp; DoS = SOH ÷ Per Day Req &nbsp;|&nbsp; Order = (30d × Daily) − SOH</span>
</div>
""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df_view.rename(columns={"Item_Name": "Item Name"}).to_excel(w, index=False, sheet_name="Replenishment")
st.download_button("⬇  Download Order List", buf.getvalue(), "Replenishment_Plan.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df_view.empty:
    st.success("✅ No critical items match the current filters.")
else:
    def colour_dos(row):
        dos = row.get("Days of Stock", None)
        if pd.isna(dos) or dos is None: return [""] * len(row)
        if dos <= 0:   return ["background-color:#2d0000; color:#fca5a5"] * len(row)
        if dos < 5:    return ["background-color:#2d1000; color:#fed7aa"] * len(row)
        return         ["background-color:#2d1f00; color:#fde68a"] * len(row)

    disp = df_view.rename(columns={"Item_Name": "Item Name"}).copy()
    st.dataframe(
        disp.style.apply(colour_dos, axis=1),
        use_container_width=True, hide_index=True, height=530,
        column_config={
            "SOH":                 st.column_config.NumberColumn("SOH",               format="%.2f"),
            "Forecast":            st.column_config.NumberColumn("Forecast",          format="%.0f"),
            "Per Day Req":         st.column_config.NumberColumn("Per Day Req",       format="%.2f"),
            "Days of Stock":       st.column_config.NumberColumn("Days of Stock ⏱",  format="%.1f"),
            "Suggested Order Qty": st.column_config.NumberColumn("Order Qty (30d)",   format="%.0f"),
        }
    )

st.markdown('<div class="app-footer">YOGABAR · REPLENISHMENT PLANNER</div>', unsafe_allow_html=True)
