import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(
    page_title="RM Inventory · Sproutlife",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="expanded"
)

from pages.Sidebar_style import inject_sidebar
inject_sidebar("RM Inventory")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── GLOBAL BACKGROUND ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main {
    background: #080b12 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] {
    visibility: hidden !important;
}
.block-container {
    padding: 1rem 1.2rem 3rem 1.2rem !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ══════════════════════════════════
   HEADER
══════════════════════════════════ */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 14px; border-bottom: 1px solid #161d2e;
    margin-bottom: 14px;
}
.hdr-left { display: flex; align-items: center; gap: 10px; }
.hdr-logo {
    width: 40px; height: 40px; min-width: 40px;
    background: #0f2e1a; border: 1px solid #1a5c30; border-radius: 11px;
    display: flex; align-items: center; justify-content: center; font-size: 19px;
}
.hdr-title { font-size: 16px; font-weight: 800; color: #f1f5f9; white-space: nowrap; }
.hdr-sub   { font-size: 11px; color: #64748b; white-space: nowrap; }

.live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #071a0f; border: 1px solid #166534;
    border-radius: 20px; padding: 5px 11px;
    font-size: 10px; font-weight: 700; color: #22c55e;
    letter-spacing: 1px; font-family: 'JetBrains Mono', monospace; flex-shrink: 0;
}
.live-dot {
    width: 6px; height: 6px; min-width: 6px;
    background: #22c55e; border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity:1; box-shadow:0 0 5px #22c55e; }
    50%      { opacity:0.2; box-shadow:none; }
}

/* ══════════════════════════════════
   KPI CARD
══════════════════════════════════ */
.kpi-card {
    background: linear-gradient(135deg, #1a0533 0%, #0c1a40 55%, #001a1a 100%);
    border: 1px solid #2d1b5e; border-radius: 18px;
    padding: 20px 22px; margin-bottom: 16px;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #a855f7, #3b82f6, #06b6d4, #10b981);
    border-radius: 18px 18px 0 0;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: -30px; right: -30px;
    width: 130px; height: 130px;
    background: radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.kpi-row { display: flex; align-items: center; justify-content: space-between; }
.kpi-lbl {
    font-size: 10px; font-weight: 700; color: #a78bfa;
    text-transform: uppercase; letter-spacing: 1.3px; margin-bottom: 6px;
}
.kpi-num {
    font-size: 36px; font-weight: 800;
    background: linear-gradient(135deg, #e879f9, #818cf8, #38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -1.5px; line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-cap { font-size: 11px; color: #64748b; margin-top: 5px; }
.kpi-ico {
    width: 54px; height: 54px; min-width: 54px;
    background: rgba(168,85,247,0.1); border: 1px solid rgba(168,85,247,0.25);
    border-radius: 15px; display: flex; align-items: center; justify-content: center;
    font-size: 26px; position: relative; z-index: 1;
}

/* ══════════════════════════════════
   FILTER BOX
══════════════════════════════════ */
.filter-wrap {
    background: #0d1117; border: 1px solid #1e2535;
    border-radius: 14px; padding: 12px 14px; margin-bottom: 14px;
}
.filter-title {
    font-size: 10px; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin-bottom: 10px; display: flex; align-items: center; gap: 6px;
}
.filter-title::after { content: ''; flex: 1; height: 1px; background: #1e2535; }

[data-testid="stHorizontalBlock"] { gap: 8px !important; align-items: flex-end !important; }

[data-testid="stTextInput"] > div > div {
    background: #111827 !important; border: 1.5px solid #1e2d45 !important;
    border-radius: 9px !important;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
[data-testid="stTextInput"] input {
    background: transparent !important; color: #f1f5f9 !important;
    font-size: 13px !important; padding: 9px 12px !important;
    border: none !important; box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #334155 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #111827 !important; border: 1.5px solid #1e2d45 !important;
    border-radius: 9px !important; color: #e2e8f0 !important;
    font-size: 12.5px !important; min-height: 38px !important;
}
[data-testid="stWidgetLabel"] { display: none !important; }

.stButton > button {
    width: 100% !important; background: #0d1117 !important;
    border: 1.5px solid #1e2535 !important; border-radius: 9px !important;
    color: #64748b !important; font-size: 13px !important;
    font-weight: 600 !important; padding: 9px !important;
    transition: all 0.2s !important; margin-bottom: 6px !important;
}
.stButton > button:hover {
    border-color: #7c3aed !important; color: #a78bfa !important;
    background: #160b2e !important;
}

.stDownloadButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #0f172a, #1e1b4b) !important;
    border: 1.5px solid #4338ca !important; border-radius: 9px !important;
    color: #a5b4fc !important; font-size: 13px !important;
    font-weight: 700 !important; padding: 10px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #1e1b4b, #312e81) !important;
    color: #fff !important;
}

/* ══════════════════════════════════
   RESULT BANNER
══════════════════════════════════ */
.result-banner {
    background: linear-gradient(135deg, #071a0f, #070d1a);
    border: 1px solid #14532d; border-left: 3px solid #22c55e;
    border-radius: 12px; padding: 14px 18px; margin: 8px 0 14px 0;
    display: flex; align-items: center; justify-content: space-between;
}
.rb-lbl { font-size: 10px; font-weight: 700; color: #16a34a; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px; }
.rb-val { font-size: 28px; font-weight: 800; color: #dcfce7; font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; line-height: 1; }
.rb-right { text-align: right; flex-shrink: 0; }
.rb-cnt { font-size: 22px; font-weight: 700; color: #4ade80; font-family: 'JetBrains Mono', monospace; }
.rb-sub { font-size: 10px; color: #166534; margin-top: 2px; }

/* ══════════════════════════════════
   TABLE
══════════════════════════════════ */
.tbl-hdr { display: flex; align-items: center; justify-content: space-between; padding: 10px 0 6px 0; }
.tbl-lbl { font-size: 10px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.2px; }
.tbl-badge {
    background: #0f172a; border: 1px solid #1e2d45; color: #818cf8;
    font-size: 11px; font-weight: 700; padding: 3px 11px;
    border-radius: 20px; font-family: 'JetBrains Mono', monospace;
}
.sec-div {
    font-size: 10px; font-weight: 700; color: #334155;
    text-transform: uppercase; letter-spacing: 1.2px;
    padding: 12px 0 8px 0; display: flex; align-items: center; gap: 7px;
}
.sec-div::after { content: ''; flex: 1; height: 1px; background: #161d2e; }

div[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid #1e2535 !important;
}
[data-testid="stAlert"] {
    background: #1a1200 !important; border: 1px solid #78350f !important;
    border-radius: 10px !important; color: #fbbf24 !important;
}
.app-footer {
    margin-top: 2rem; padding-top: 12px; border-top: 1px solid #161d2e;
    text-align: center; font-size: 10px; font-weight: 600; color: #334155;
    letter-spacing: 1.5px; font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════
@st.cache_data
def load_rm():
    fp = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(fp):
        fp = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(fp, sheet_name="RM-Inventory")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    for c in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if c in df.columns: df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ["Qty Available","Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_forecast():
    fp = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(fp):
        fp = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    xl = pd.ExcelFile(fp)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    if not sheet: return pd.DataFrame(columns=["Item code","Forecast"])
    df = pd.read_excel(fp, sheet_name=sheet)
    df.columns = df.columns.str.strip()
    if "Location" in df.columns:
        df = df[df["Location"].astype(str).str.strip().str.lower() == "plant"]
    if "Forecast" in df.columns:
        df["Forecast"] = pd.to_numeric(df["Forecast"], errors="coerce").fillna(0)
        df = df[df["Forecast"] > 0]
    ic = "Item code" if "Item code" in df.columns else "Item Code"
    df[ic] = df[ic].astype(str).str.strip()
    return df[[ic,"Forecast"]].rename(columns={ic:"Item code"}).drop_duplicates(subset="Item code")

df_raw   = load_rm()
df_fcast = load_forecast()

ALLOWED_WH = [
    "Central","Central Production -Bar Line","Central Production - Oats Line",
    "Central Production - Peanut Line","Central Production - Muesli Line",
    "RM Warehouse Tumkur","Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM","Tumkur Warehouse",
    "Central Production -Packing","Tumkur New Warehouse",
    "HF Factory FG Warehouse","Sproutlife Foods Private Ltd (SNOWMAN)"
]
SOH_WH = [
    "Central","RM Warehouse Tumkur","Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse","Tumkur New Warehouse",
    "HF Factory FG Warehouse","Sproutlife Foods Private Ltd (SNOWMAN)"
]

df_raw = df_raw[df_raw["Warehouse"].isin(ALLOWED_WH)]
df_soh = df_raw[df_raw["Warehouse"].isin(SOH_WH)]

soh_sku = df_soh.groupby("Item SKU")["Qty Available"].sum().reset_index()
soh_sku.columns = ["Item SKU","SOH"]
soh_sku["_k"] = soh_sku["Item SKU"].astype(str).str.upper()
df_fcast["_k"] = df_fcast["Item code"].astype(str).str.upper()
soh_sku = soh_sku.merge(df_fcast[["_k","Forecast"]], on="_k", how="left")
soh_sku["Forecast"] = soh_sku["Forecast"].fillna(0)
soh_sku["Days of Stock"] = soh_sku.apply(
    lambda r: round(r["SOH"]/(r["Forecast"]/26),1) if r["Forecast"]>0 else None, axis=1)
soh_sku = soh_sku.drop(columns=["_k"])

# ════════════════════════════════════════
# HEADER
# ════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📦</div>
        <div>
            <div class="hdr-title">RM Inventory</div>
            <div class="hdr-sub">Sproutlife Foods · Raw Material Stock</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ════════════════════════════════════════
# KPI
# ════════════════════════════════════════
total_soh = df_raw[df_raw["Warehouse"].isin(SOH_WH)]["Qty Available"].sum()
st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-row">
        <div>
            <div class="kpi-lbl">Total Stock on Hand</div>
            <div class="kpi-num">{total_soh:,.0f}</div>
            <div class="kpi-cap">Across all storage warehouses</div>
        </div>
        <div class="kpi-ico">📦</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# FILTERS
# ════════════════════════════════════════
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2.2, 2, 1.6, 1.6])
with c1:
    search = st.text_input("s", placeholder="🔍 Search SKU / name / batch…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    sel_wh  = st.selectbox("w", wh_opts, label_visibility="collapsed")
with c3:
    cat_opts = (["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
                if "Category" in df_raw.columns else ["All Categories"])
    sel_cat  = st.selectbox("c", cat_opts, label_visibility="collapsed")
with c4:
    sel_st   = st.selectbox("st", ["All Stock","Available Only","Zero / Neg"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════
# APPLY FILTERS
# ════════════════════════════════════════
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh  != "All Warehouses":  df = df[df["Warehouse"] == sel_wh]
if sel_cat != "All Categories" and "Category" in df_raw.columns:
    df = df[df["Category"].astype(str) == sel_cat]
if sel_st == "Available Only":   df = df[df["Qty Available"] > 0]
elif sel_st == "Zero / Neg":     df = df[df["Qty Available"] <= 0]

is_filtered = bool(search) or sel_wh != "All Warehouses" or sel_cat != "All Categories" or sel_st != "All Stock"
if is_filtered:
    f_qty = df[df["Warehouse"].isin(SOH_WH)]["Qty Available"].sum()
    ctx   = (f'"{search}"' if search else
             sel_wh[:28] if sel_wh != "All Warehouses" else
             sel_cat[:28] if sel_cat != "All Categories" else sel_st)
    st.markdown(f"""
    <div class="result-banner">
        <div><div class="rb-lbl">Filtered · {ctx}</div><div class="rb-val">{f_qty:,.0f}</div></div>
        <div class="rb-right"><div class="rb-cnt">{len(df):,}</div><div class="rb-sub">records</div></div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════
# TABLE
# ════════════════════════════════════════
st.markdown('<div class="sec-div">Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 All columns</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="RM Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️  No records match the current filters.")
else:
    df_m = df.merge(soh_sku[["Item SKU","Forecast","Days of Stock"]], on="Item SKU", how="left")
    priority = [
        "Item Name","Item SKU","Category","Warehouse","UoM",
        "Qty Available","Forecast","Days of Stock",
        "Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)",
        "Batch No","MFG Date","Expiry Date","Current Aging (Days)",
        "Inventory Date","Item Type","Primary Supplier"
    ]
    cols = [c for c in priority if c in df_m.columns]
    cols += [c for c in df_m.columns if c not in cols]
    df_show = df_m[cols].copy()
    for c in ["Inventory Date","Expiry Date","MFG Date"]:
        if c in df_show.columns:
            df_show[c] = df_show[c].dt.strftime("%d-%b-%Y").fillna("")

    st.dataframe(df_show, use_container_width=True, height=500, hide_index=True,
        column_config={
            "Qty Available":        st.column_config.NumberColumn("Qty Avail",  format="%.0f"),
            "Forecast":             st.column_config.NumberColumn("Forecast",   format="%.0f"),
            "Days of Stock":        st.column_config.NumberColumn("DoS",        format="%.1f"),
            "Qty Inward":           st.column_config.NumberColumn("Inward",     format="%.0f"),
            "Qty (Issue / Hold)":   st.column_config.NumberColumn("Issue/Hold", format="%.0f"),
            "Value (Inc Tax)":      st.column_config.NumberColumn("Val (Inc)",  format="%.0f"),
            "Value (Ex Tax)":       st.column_config.NumberColumn("Val (Ex)",   format="%.0f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging (d)",  format="%d"),
        })

st.markdown('<div class="app-footer">SPROUTLIFE FOODS · RM INVENTORY</div>', unsafe_allow_html=True)
