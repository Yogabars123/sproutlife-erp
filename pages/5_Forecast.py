import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Forecast · YogaBar", layout="wide", page_icon="📊", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("Forecast")

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
.hdr-logo { width:40px; height:40px; min-width:40px; background:#0c1a10; border:1px solid #14532d; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:19px; }
.hdr-title { font-size:16px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 11px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.kpi-card { border-radius:16px; padding:16px 18px; position:relative; overflow:hidden; border:1px solid; min-height:100px; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-card.blue { background:linear-gradient(135deg,#0c1a3a,#0f2460); border-color:#1a3a6e; }
.kpi-card.blue::before { background:linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-card.teal { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-card.purple { background:linear-gradient(135deg,#12082a,#1e1040); border-color:#3b1a5c; }
.kpi-card.purple::before { background:linear-gradient(90deg,#a855f7,#c084fc); }
.kpi-card.red { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-card.red::before { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-lbl { font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.kpi-card.blue .kpi-lbl { color:#60a5fa; } .kpi-card.teal .kpi-lbl { color:#5bc8c0; }
.kpi-card.purple .kpi-lbl { color:#c084fc; } .kpi-card.red .kpi-lbl { color:#f87171; }
.kpi-num { font-size:26px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-card.blue .kpi-num { color:#bfdbfe; } .kpi-card.teal .kpi-num { color:#99f6e4; }
.kpi-card.purple .kpi-num { color:#e9d5ff; } .kpi-card.red .kpi-num { color:#fecaca; }
.kpi-cap { font-size:11px; margin-top:5px; }
.kpi-card.blue .kpi-cap { color:#1e3a6e; } .kpi-card.teal .kpi-cap { color:#134e4a; }
.kpi-card.purple .kpi-cap { color:#3b1a5c; } .kpi-card.red .kpi-cap { color:#7f1d1d; }
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }
[data-testid="stTextInput"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:#5bc8c0 !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:#f1f5f9 !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }
.stDownloadButton > button { width:100% !important; background:linear-gradient(135deg,#0f172a,#1e1b4b) !important; border:1.5px solid #4338ca !important; border-radius:9px !important; color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; padding:10px !important; }
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
    # Load Forecast sheet
    df_fc = load_sheet("Forecast")
    if df_fc.empty:
        return pd.DataFrame()
    df_fc.columns = df_fc.columns.str.strip()

    # Filter: Plant location only
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()

    # Numeric
    if "Forecast" in df_fc.columns:
        df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
        df_fc = df_fc[df_fc["Forecast"] > 0].copy()

    # Per Day Req = Forecast / 24
    df_fc["Per Day Req"] = (df_fc["Forecast"] / 24).round(2)

    # Load RM Inventory with same SOH warehouses as RM Inventory page KPI
    df_rm = load_sheet("RM-Inventory")
    if not df_rm.empty:
        df_rm.columns = df_rm.columns.str.strip()
        df_rm["Warehouse"]     = df_rm["Warehouse"].astype(str).str.strip()
        df_rm["Qty Available"] = pd.to_numeric(df_rm.get("Qty Available", 0), errors="coerce").fillna(0)

        SOH_WH = [
            "Central", "RM Warehouse Tumkur",
            "Central Warehouse - Cold Storage RM",
            "Tumkur Warehouse", "Tumkur New Warehouse",
            "HF Factory FG Warehouse",
            "Sproutlife Foods Private Ltd (SNOWMAN)"
        ]
        soh_by_sku = (
            df_rm[df_rm["Warehouse"].isin(SOH_WH)]
            .groupby("Item SKU")["Qty Available"].sum()
            .reset_index()
            .rename(columns={"Item SKU": "_sku", "Qty Available": "SOH"})
        )

        if "Item code" in df_fc.columns:
            df_fc["Item code"] = df_fc["Item code"].astype(str).str.strip()
            df_fc = df_fc.merge(soh_by_sku, left_on="Item code", right_on="_sku", how="left")
            df_fc["SOH"] = df_fc["SOH"].fillna(0)
            df_fc.drop(columns=["_sku"], errors="ignore", inplace=True)

    # Days of Stock = SOH / Per Day Req
    if "SOH" in df_fc.columns:
        df_fc["Days of Stock"] = df_fc.apply(
            lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None, axis=1
        )

    return df_fc

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📊</div>
        <div>
            <div class="hdr-title">Forecast</div>
            <div class="hdr-sub">YogaBar · Days of Stock Analysis · Plant Location Only</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df_raw = load_data()
if df_raw.empty:
    st.error("⚠️ No forecast data found. Check the Excel file and sheet name.")
    st.stop()

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search item code / name…", label_visibility="collapsed")
with c2:
    dos_opts = ["All", "🔴 Critical (< 7 days)", "🟡 Low (7–14 days)", "✅ Healthy (> 14 days)"]
    dos_filter = st.selectbox("d", dos_opts, label_visibility="collapsed")
with c3:
    if "Category" in df_raw.columns:
        cat_opts = ["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
    else:
        cat_opts = ["All Categories"]
    sel_cat = st.selectbox("c", cat_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if "Days of Stock" in df.columns:
    if dos_filter == "🔴 Critical (< 7 days)":
        df = df[df["Days of Stock"] < 7]
    elif dos_filter == "🟡 Low (7–14 days)":
        df = df[(df["Days of Stock"] >= 7) & (df["Days of Stock"] <= 14)]
    elif dos_filter == "✅ Healthy (> 14 days)":
        df = df[df["Days of Stock"] > 14]
if sel_cat != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == sel_cat]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_items    = df["Item code"].nunique()        if "Item code"     in df.columns else len(df)
total_forecast = df["Forecast"].sum()             if "Forecast"      in df.columns else 0
total_soh      = df["SOH"].sum()                  if "SOH"           in df.columns else 0
critical_count = (df["Days of Stock"] < 7).sum()  if "Days of Stock" in df.columns else 0
avg_dos        = df["Days of Stock"].mean()        if "Days of Stock" in df.columns else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card blue">
        <div class="kpi-lbl">Total Forecast Qty</div>
        <div class="kpi-num">{total_forecast:,.0f}</div>
        <div class="kpi-cap">{total_items:,} items · Plant only</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-lbl">Total SOH (RM)</div>
        <div class="kpi-num">{total_soh:,.0f}</div>
        <div class="kpi-cap">From SOH warehouses</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-lbl">Avg Days of Stock</div>
        <div class="kpi-num">{avg_dos:.1f}</div>
        <div class="kpi-cap">SOH ÷ (Forecast ÷ 24)</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-lbl">Critical Items</div>
        <div class="kpi-num">{critical_count:,}</div>
        <div class="kpi-cap">Below 7 days of stock</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 Forecast · Days of Stock</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="legend-bar">
    <span><span class="legend-dot" style="background:#ef4444"></span><span style="color:#f87171">Critical &lt; 7 days</span></span>
    <span><span class="legend-dot" style="background:#f59e0b"></span><span style="color:#fbbf24">Low 7–14 days</span></span>
    <span><span class="legend-dot" style="background:#22c55e"></span><span style="color:#4ade80">Healthy &gt; 14 days</span></span>
    <span style="color:#475569; margin-left:auto; font-size:10px; font-family:'JetBrains Mono',monospace;">Days of Stock = SOH ÷ (Forecast ÷ 24)</span>
</div>
""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="Forecast DoS")
st.download_button("⬇  Export to Excel", buf.getvalue(), "Forecast_DoS.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_dos(row):
        dos = row.get("Days of Stock", None)
        if pd.isna(dos) or dos is None:
            return [""] * len(row)
        if dos < 7:
            return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
        elif dos <= 14:
            return ["background-color:#2d1f00; color:#fde68a"] * len(row)
        return ["background-color:#0a1f0a; color:#bbf7d0"] * len(row)

    disp = df.drop(columns=["Item SKU"], errors="ignore").copy()
    st.dataframe(
        disp.style.apply(colour_dos, axis=1),
        use_container_width=True, hide_index=True, height=520,
        column_config={
            "Forecast":      st.column_config.NumberColumn("Forecast",      format="%.0f"),
            "SOH":           st.column_config.NumberColumn("SOH (RM)",      format="%.0f"),
            "Per Day Req":   st.column_config.NumberColumn("Per Day Req",   format="%.2f"),
            "Days of Stock": st.column_config.NumberColumn("Days of Stock", format="%.1f ⏱"),
            "Norm":          st.column_config.NumberColumn("Norm",          format="%.0f"),
        }
    )

st.markdown('<div class="app-footer">YOGABAR · FORECAST · DAYS OF STOCK</div>', unsafe_allow_html=True)
