import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="RM Inventory · YogaBar", layout="wide", page_icon="📦", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("RM Inventory")

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

/* HEADER */
.app-header { display:flex; align-items:center; justify-content:space-between; padding-bottom:14px; border-bottom:1px solid #161d2e; margin-bottom:16px; }
.hdr-left { display:flex; align-items:center; gap:10px; }
.hdr-logo { width:42px; height:42px; min-width:42px; background:#0f2e1a; border:1px solid #1a5c30; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px; }
.hdr-title { font-size:17px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 12px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 6px #22c55e;} 50%{opacity:.2;box-shadow:none;} }

/* KPI GRID — 4 cards */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }
.kpi-card {
    border-radius:18px; padding:20px 22px; position:relative;
    overflow:hidden; border:1px solid; min-height:118px;
    transition: transform .15s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:18px 18px 0 0; }
.kpi-card::after  { content:''; position:absolute; bottom:-40px; right:-40px; width:120px; height:120px; border-radius:50%; opacity:.12; }

.kpi-card.violet { background:linear-gradient(135deg,#130a2a,#1e0f40); border-color:#3b1f6e; }
.kpi-card.violet::before { background:linear-gradient(90deg,#a855f7,#818cf8); }
.kpi-card.violet::after  { background:radial-gradient(circle,#a855f7,transparent); }

.kpi-card.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before   { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-card.teal::after    { background:radial-gradient(circle,#5bc8c0,transparent); }

.kpi-card.amber  { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.amber::after   { background:radial-gradient(circle,#f59e0b,transparent); }

.kpi-card.red    { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-card.red::after     { background:radial-gradient(circle,#ef4444,transparent); }

.kpi-inner { display:flex; align-items:flex-start; justify-content:space-between; }
.kpi-lbl  { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:8px; }
.kpi-num  { font-size:32px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1.5px; }
.kpi-cap  { font-size:11px; margin-top:6px; }
.kpi-ico  { font-size:28px; opacity:.6; margin-top:2px; }

.kpi-card.violet .kpi-lbl { color:#c084fc; } .kpi-card.violet .kpi-num { color:#e9d5ff; } .kpi-card.violet .kpi-cap { color:#4a2a7a; }
.kpi-card.teal   .kpi-lbl { color:#5bc8c0; } .kpi-card.teal   .kpi-num { color:#99f6e4; } .kpi-card.teal   .kpi-cap { color:#134e4a; }
.kpi-card.amber  .kpi-lbl { color:#fbbf24; } .kpi-card.amber  .kpi-num { color:#fde68a; } .kpi-card.amber  .kpi-cap { color:#78540a; }
.kpi-card.red    .kpi-lbl { color:#f87171; } .kpi-card.red    .kpi-num { color:#fecaca; } .kpi-card.red    .kpi-cap { color:#7a2020; }

/* FILTER */
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }
[data-testid="stTextInput"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:#a855f7 !important; box-shadow:0 0 0 3px rgba(168,85,247,.12) !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:#f1f5f9 !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }
.stButton > button { width:100% !important; background:#0d1117 !important; border:1.5px solid #1e2535 !important; border-radius:9px !important; color:#64748b !important; font-size:13px !important; font-weight:600 !important; padding:9px !important; transition:all .2s !important; margin-bottom:6px !important; }
.stButton > button:hover { border-color:#a855f7 !important; color:#c084fc !important; background:#130a2a !important; }
.stDownloadButton > button { width:100% !important; background:linear-gradient(135deg,#0f172a,#1e1b4b) !important; border:1.5px solid #4338ca !important; border-radius:9px !important; color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; padding:10px !important; }

/* CHARTS */
.chart-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:16px; }
.chart-box { background:#0d1117; border:1px solid #1e2535; border-radius:16px; padding:16px 18px; }
.chart-title { font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:7px; }
.chart-title::after { content:''; flex:1; height:1px; background:#1e2535; }

/* TABLE */
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:12px 0 8px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:6px 0; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.legend-bar { display:flex; gap:16px; align-items:center; background:#0d1117; border:1px solid #1e2535; border-radius:10px; padding:8px 14px; margin-bottom:8px; font-size:11px; }
.ldot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:4px; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
SOH_WH = [
    "Central","RM Warehouse Tumkur","Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse","Tumkur New Warehouse",
    "HF Factory FG Warehouse","Sproutlife Foods Private Ltd (SNOWMAN)"
]
ALLOWED_WH = SOH_WH + [
    "Central Production -Bar Line","Central Production - Oats Line",
    "Central Production - Peanut Line","Central Production - Muesli Line",
    "Central Production -Dry Fruits Line","Central Production -Packing",
]

@st.cache_data(ttl=300)
def load_rm():
    df = load_sheet("RM-Inventory")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date","Expiry Date","MFG Date"]:
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["Qty Available","Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)"]:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df[df["Warehouse"].isin(ALLOWED_WH)]

@st.cache_data(ttl=300)
def load_forecast_agg():
    df_fc = load_sheet("Forecast")
    if df_fc.empty:
        return pd.DataFrame(columns=["_k","Forecast","Per Day Req"])
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    if "Forecast" not in df_fc.columns:
        return pd.DataFrame(columns=["_k","Forecast","Per Day Req"])
    df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]
    ic = "Item code" if "Item code" in df_fc.columns else ("Item Code" if "Item Code" in df_fc.columns else None)
    if ic is None:
        return pd.DataFrame(columns=["_k","Forecast","Per Day Req"])
    df_fc["_k"] = df_fc[ic].astype(str).str.strip().str.upper()
    agg = df_fc.groupby("_k")["Forecast"].sum().reset_index()
    agg["Per Day Req"] = (agg["Forecast"] / 24).round(2)
    return agg

def build_soh_sku(df_rm, fc_agg):
    df_soh = df_rm[df_rm["Warehouse"].isin(SOH_WH)]
    soh = df_soh.groupby("Item SKU")["Qty Available"].sum().reset_index()
    soh.columns = ["Item SKU","SOH"]
    soh["_k"] = soh["Item SKU"].astype(str).str.upper()
    if not fc_agg.empty and "_k" in fc_agg.columns:
        soh = soh.merge(fc_agg[["_k","Forecast","Per Day Req"]], on="_k", how="left")
    else:
        soh["Forecast"] = 0.0
        soh["Per Day Req"] = 0.0
    soh["Forecast"]    = soh["Forecast"].fillna(0)
    soh["Per Day Req"] = soh["Per Day Req"].fillna(0)
    soh["Days of Stock"] = soh.apply(
        lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None, axis=1)
    soh.drop(columns=["_k"], inplace=True)
    return soh

df_raw  = load_rm()
fc_agg  = load_forecast_agg()
soh_sku = build_soh_sku(df_raw, fc_agg) if not df_raw.empty else pd.DataFrame()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📦</div>
        <div>
            <div class="hdr-title">RM Inventory</div>
            <div class="hdr-sub">YogaBar · Raw Material Stock · Forecast · Days of Stock</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if df_raw.empty:
    st.error("⚠️ No RM Inventory data found."); st.stop()

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_soh   = df_raw[df_raw["Warehouse"].isin(SOH_WH)]["Qty Available"].sum() if not df_raw.empty else 0
total_fc    = soh_sku["Forecast"].sum()                   if not soh_sku.empty else 0
critical    = int((soh_sku["Days of Stock"] < 7).sum())   if not soh_sku.empty else 0
no_forecast = int((soh_sku["Days of Stock"].isna()).sum()) if not soh_sku.empty else 0
avg_dos     = soh_sku["Days of Stock"].mean()             if not soh_sku.empty else 0
avg_dos     = avg_dos if pd.notna(avg_dos) else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card violet">
        <div class="kpi-inner">
            <div>
                <div class="kpi-lbl">Total Stock on Hand</div>
                <div class="kpi-num">{total_soh:,.0f}</div>
                <div class="kpi-cap">Across all SOH warehouses</div>
            </div>
            <div class="kpi-ico">📦</div>
        </div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-inner">
            <div>
                <div class="kpi-lbl">Total Forecast Qty</div>
                <div class="kpi-num">{total_fc:,.0f}</div>
                <div class="kpi-cap">Plant location · Forecast/24 per day</div>
            </div>
            <div class="kpi-ico">📈</div>
        </div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-inner">
            <div>
                <div class="kpi-lbl">Avg Days of Stock</div>
                <div class="kpi-num">{avg_dos:.1f}</div>
                <div class="kpi-cap">SOH ÷ Per Day Req</div>
            </div>
            <div class="kpi-ico">⏱</div>
        </div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-inner">
            <div>
                <div class="kpi-lbl">Critical (&lt; 7 Days)</div>
                <div class="kpi-num">{critical:,}</div>
                <div class="kpi-cap">{no_forecast:,} items have no forecast</div>
            </div>
            <div class="kpi-ico">🚨</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CHARTS REMOVED ──

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2.5, 1.8, 1.8, 1.8, 1.8])
with c1:
    search = st.text_input("s", placeholder="🔍 Search SKU / name / batch…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    sel_wh  = st.selectbox("w", wh_opts, label_visibility="collapsed")
with c3:
    cat_opts = (["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
                if "Category" in df_raw.columns else ["All Categories"])
    sel_cat = st.selectbox("c", cat_opts, label_visibility="collapsed")
with c4:
    sel_st = st.selectbox("st", ["All Stock","Available Only","Zero / Neg"], label_visibility="collapsed")
with c5:
    dos_opts = ["All DoS","🔴 Critical (< 7d)","🟡 Low (7–14d)","✅ Healthy (> 14d)","⚫ No Forecast"]
    sel_dos  = st.selectbox("d", dos_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh  != "All Warehouses":  df = df[df["Warehouse"] == sel_wh]
if sel_cat != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == sel_cat]
if sel_st == "Available Only": df = df[df["Qty Available"] > 0]
elif sel_st == "Zero / Neg":   df = df[df["Qty Available"] <= 0]

# Merge forecast & DoS into view
df_m = df.merge(soh_sku[["Item SKU","Forecast","Per Day Req","Days of Stock"]], on="Item SKU", how="left")

if sel_dos == "🔴 Critical (< 7d)":
    df_m = df_m[df_m["Days of Stock"] < 7]
elif sel_dos == "🟡 Low (7–14d)":
    df_m = df_m[(df_m["Days of Stock"] >= 7) & (df_m["Days of Stock"] <= 14)]
elif sel_dos == "✅ Healthy (> 14d)":
    df_m = df_m[df_m["Days of Stock"] > 14]
elif sel_dos == "⚫ No Forecast":
    df_m = df_m[df_m["Days of Stock"].isna()]

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">Detailed Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 RM Inventory · Forecast · Days of Stock</span>
    <span class="tbl-badge">{len(df_m):,} rows</span>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="legend-bar">
    <span><span class="ldot" style="background:#ef4444"></span><span style="color:#f87171">Critical &lt; 7 days</span></span>
    <span><span class="ldot" style="background:#f59e0b"></span><span style="color:#fbbf24">Low 7–14 days</span></span>
    <span><span class="ldot" style="background:#5bc8c0"></span><span style="color:#99f6e4">Healthy &gt; 14 days</span></span>
    <span style="color:#475569;margin-left:auto;font-size:10px;font-family:'JetBrains Mono',monospace;">DoS = SOH ÷ (Forecast ÷ 24)</span>
</div>
""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df_m.to_excel(w, index=False, sheet_name="RM Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df_m.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_row(row):
        dos = row.get("Days of Stock", None)
        if pd.isna(dos) or dos is None: return [""] * len(row)
        if dos < 7:   return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
        if dos <= 14: return ["background-color:#2d1f00; color:#fde68a"] * len(row)
        return ["background-color:#061410; color:#99f6e4"] * len(row)

    priority = ["Item Name","Item SKU","Category","Warehouse","UoM",
                "Qty Available","Forecast","Per Day Req","Days of Stock",
                "Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)",
                "Batch No","MFG Date","Expiry Date","Inventory Date"]
    cols = [c for c in priority if c in df_m.columns]
    cols += [c for c in df_m.columns if c not in cols]
    df_show = df_m[cols].copy()
    for c in ["Inventory Date","Expiry Date","MFG Date"]:
        if c in df_show.columns:
            df_show[c] = df_show[c].dt.strftime("%d-%b-%Y").fillna("")

    st.dataframe(df_show.style.apply(colour_row, axis=1),
        use_container_width=True, height=520, hide_index=True,
        column_config={
            "Qty Available":      st.column_config.NumberColumn("Qty Avail",   format="%.0f"),
            "Forecast":           st.column_config.NumberColumn("Forecast",    format="%.0f"),
            "Per Day Req":        st.column_config.NumberColumn("Per Day Req", format="%.2f"),
            "Days of Stock":      st.column_config.NumberColumn("Days of Stock ⏱", format="%.1f"),
            "Qty Inward":         st.column_config.NumberColumn("Inward",      format="%.0f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Issue/Hold",  format="%.0f"),
            "Value (Inc Tax)":    st.column_config.NumberColumn("Val (Inc)",   format="%.0f"),
            "Value (Ex Tax)":     st.column_config.NumberColumn("Val (Ex)",    format="%.0f"),
        })

st.markdown('<div class="app-footer">YOGABAR · RM INVENTORY</div>', unsafe_allow_html=True)
