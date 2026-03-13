import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="FG Inventory · YogaBar", layout="wide", page_icon="📦", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("FG Inventory")

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
.hdr-logo { width:40px; height:40px; min-width:40px; background:#0f1f3a; border:1px solid #1a3a5c; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:19px; }
.hdr-title { font-size:16px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 11px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }
.kpi-row { display:grid; grid-template-columns:repeat(5,1fr); gap:11px; margin-bottom:16px; }
.kpi-box { border-radius:15px; padding:16px 18px; border:1px solid; position:relative; overflow:hidden; }
.kpi-box::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:15px 15px 0 0; }
.kpi-box.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-box.teal::before  { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-box.violet { background:linear-gradient(135deg,#130a2a,#1e0f40); border-color:#3b1f6e; }
.kpi-box.violet::before { background:linear-gradient(90deg,#a855f7,#818cf8); }
.kpi-box.blue   { background:linear-gradient(135deg,#060e1a,#0a1a2e); border-color:#1e3a5f; }
.kpi-box.blue::before   { background:linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-box.amber  { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-box.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-box.green  { background:linear-gradient(135deg,#061a0a,#0a2e12); border-color:#14532d; }
.kpi-box.green::before  { background:linear-gradient(90deg,#22c55e,#4ade80); }
.kpi-box.red    { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-box.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-inner { display:flex; align-items:flex-start; justify-content:space-between; }
.kpi-label { font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:6px; }
.kpi-value { font-size:26px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-sub   { font-size:10.5px; margin-top:5px; }
.kpi-ico   { font-size:22px; opacity:.6; margin-top:2px; }
.kpi-box.teal   .kpi-label{color:#5bc8c0;} .kpi-box.teal   .kpi-value{color:#99f6e4;} .kpi-box.teal   .kpi-sub{color:#0d9488;}
.kpi-box.violet .kpi-label{color:#c084fc;} .kpi-box.violet .kpi-value{color:#e9d5ff;} .kpi-box.violet .kpi-sub{color:#7c3aed;}
.kpi-box.blue   .kpi-label{color:#60a5fa;} .kpi-box.blue   .kpi-value{color:#bfdbfe;} .kpi-box.blue   .kpi-sub{color:#2563eb;}
.kpi-box.amber  .kpi-label{color:#fbbf24;} .kpi-box.amber  .kpi-value{color:#fde68a;} .kpi-box.amber  .kpi-sub{color:#d97706;}
.kpi-box.green  .kpi-label{color:#4ade80;} .kpi-box.green  .kpi-value{color:#bbf7d0;} .kpi-box.green  .kpi-sub{color:#16a34a;}
.kpi-box.red    .kpi-label{color:#f87171;} .kpi-box.red    .kpi-value{color:#fecaca;} .kpi-box.red    .kpi-sub{color:#dc2626;}
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
[data-testid="stTabs"] [data-baseweb="tab-list"] { background:#0d1117 !important; border-radius:12px 12px 0 0 !important; border:1px solid #1e2535 !important; border-bottom:none !important; padding:6px 8px 0 !important; gap:4px !important; }
[data-testid="stTabs"] [data-baseweb="tab"] { background:transparent !important; border-radius:8px 8px 0 0 !important; color:#475569 !important; font-size:12px !important; font-weight:700 !important; padding:8px 18px !important; border:none !important; }
[data-testid="stTabs"] [aria-selected="true"] { background:#111827 !important; color:#5bc8c0 !important; border-bottom:2px solid #5bc8c0 !important; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] { background:#0d1117 !important; border:1px solid #1e2535 !important; border-radius:0 0 12px 12px !important; padding:14px !important; }
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:8px 0 6px; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }
div[data-testid="stDataFrame"] { border-radius:10px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:10px 0 6px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
.formula-bar { background:#0a0f1a; border:1px solid #1e2d45; border-radius:10px; padding:10px 16px; margin-bottom:12px; font-size:11px; font-family:'JetBrains Mono',monospace; color:#64748b; display:flex; gap:24px; flex-wrap:wrap; }
.formula-bar span { color:#94a3b8; } .formula-bar b { color:#5bc8c0; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

CLOSED_STATUSES   = {"cancelled", "closed"}
STN_OPEN_STATUSES = {"raised", "approved", "in transit", "intransit", "in-transit", "pending"}

# ── CFA WAREHOUSE LIST ────────────────────────────────────────────────────────
# Explicit list: Mithra Associates added, Quarantine Delhi CFA & Quarantine Kerala CFA excluded
CFA_WAREHOUSES = [
    "Mumbai CFA",
    "Chennai CFA",
    "Kerala CFA",
    "Delhi -CFA GHEVRA",
    "Ahmedabad CFA",
    "Kolkata CFA",
    "Pune CFA",
    "Mithra Associates",
    "BENGALURU CFA",
]

def is_cfa(warehouse_name: str) -> bool:
    """Returns True if the warehouse is in the approved CFA list."""
    return str(warehouse_name).strip() in CFA_WAREHOUSES

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_fg():
    df = load_sheet("FG-Inventory")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    for col in ["Qty Available","Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    today = pd.Timestamp(datetime.today().date())
    for col in ["Expiry Date","MFG Date","Inventory Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "Expiry Date" in df.columns and "MFG Date" in df.columns:
        rem   = (df["Expiry Date"] - today).dt.days
        total = (df["Expiry Date"] - df["MFG Date"]).dt.days
        valid = total > 0
        pct   = pd.Series(0.0, index=df.index)
        pct[valid] = ((rem[valid] / total[valid]) * 100).clip(0, 100)
        df["Shelf Life %"] = pct.round(1)
    else:
        df["Shelf Life %"] = 0.0
    return df

@st.cache_data(ttl=300)
def load_stn():
    df = load_sheet("STN")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if "Qty" in df.columns:
        df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0)
    return df

@st.cache_data(ttl=300)
def load_sos():
    df = load_sheet("SOS")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    for col in ["Order Qty","Dispatch Qty","Rate","Order Value","Total Amount","GST"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["Order Date","PO Date","Invoice Date","Last Dispatch Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

@st.cache_data(ttl=300)
def load_mapper():
    df = load_sheet("Mapper")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    return df

df_fg     = load_fg()
df_stn    = load_stn()
df_sos    = load_sos()
df_mapper = load_mapper()

# ── CHANNEL STOCK WAREHOUSES ──────────────────────────────────────────────────
CHANNEL_STOCK_WAREHOUSES = [
    "Tumkur New Warehouse",
    "Central",
    "YB FG Warehouse",
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📦</div>
        <div>
            <div class="hdr-title">FG Inventory</div>
            <div class="hdr-sub">YogaBar · FG Stock + STN In-Transit vs Open Orders · CFA Analysis</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if df_fg.empty:
    st.error("⚠️ No FG Inventory data found.")
    st.stop()

# ── WAREHOUSE LISTS FOR FILTERS ───────────────────────────────────────────────
all_fg_wh = sorted(df_fg["Warehouse"].dropna().astype(str).unique().tolist()) if "Warehouse" in df_fg.columns else []
# CFA dropdown uses the explicit list, filtered to what actually exists in data
cfa_warehouses = sorted([w for w in CFA_WAREHOUSES if w in all_fg_wh])

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([2.5, 2, 2, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search SKU / product name…", label_visibility="collapsed")
with c2:
    sel_fg_wh = st.selectbox("fg_wh", ["All Warehouses"] + all_fg_wh, label_visibility="collapsed")
with c3:
    sel_cfa   = st.selectbox("cfa",   ["All CFAs"] + cfa_warehouses,  label_visibility="collapsed")
with c4:
    sel_shelf = st.selectbox("sh",    ["All Shelf Life","Below 90%","Below 80%","Below 70%","Below 50%"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FG FILTERS ──────────────────────────────────────────────────────────
df = df_fg.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_fg_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_fg_wh]
shelf_map = {"Below 90%": 90, "Below 80%": 80, "Below 70%": 70, "Below 50%": 50}
if sel_shelf in shelf_map and "Shelf Life %" in df.columns:
    df = df[df["Shelf Life %"] < shelf_map[sel_shelf]]

# ── GLOBAL KPIs ───────────────────────────────────────────────────────────────
total_fg    = df["Qty Available"].sum() if "Qty Available" in df.columns else 0
cfa_fg      = df[df["Warehouse"].astype(str).apply(is_cfa)]["Qty Available"].sum() \
              if "Warehouse" in df.columns else 0
stn_cfa_qty = 0
if not df_stn.empty and "To Warehouse" in df_stn.columns and "Status" in df_stn.columns and "Qty" in df_stn.columns:
    stn_cfa_qty = df_stn[
        df_stn["To Warehouse"].astype(str).apply(is_cfa) &
        df_stn["Status"].astype(str).str.strip().str.lower().isin(STN_OPEN_STATUSES)
    ]["Qty"].sum()
open_so_qty = 0
if not df_sos.empty and "SO Status" in df_sos.columns and "Order Qty" in df_sos.columns:
    open_so_qty = df_sos[~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)]["Order Qty"].sum()
total_available = cfa_fg + stn_cfa_qty
diff            = total_available - open_so_qty

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-box teal"><div class="kpi-inner"><div>
    <div class="kpi-label">Total FG Stock</div><div class="kpi-value">{total_fg:,.0f}</div>
    <div class="kpi-sub">All warehouses</div></div><div class="kpi-ico">📦</div></div></div>
  <div class="kpi-box violet"><div class="kpi-inner"><div>
    <div class="kpi-label">CFA FG Stock</div><div class="kpi-value">{cfa_fg:,.0f}</div>
    <div class="kpi-sub">At CFA warehouses</div></div><div class="kpi-ico">🏭</div></div></div>
  <div class="kpi-box blue"><div class="kpi-inner"><div>
    <div class="kpi-label">STN In-Transit to CFA</div><div class="kpi-value">{stn_cfa_qty:,.0f}</div>
    <div class="kpi-sub">Raised / Approved STNs → CFA</div></div><div class="kpi-ico">🚚</div></div></div>
  <div class="kpi-box amber"><div class="kpi-inner"><div>
    <div class="kpi-label">Open PO Qty</div><div class="kpi-value">{open_so_qty:,.0f}</div>
    <div class="kpi-sub">Excl. Cancelled &amp; Closed</div></div><div class="kpi-ico">📋</div></div></div>
  <div class="kpi-box {'green' if diff>=0 else 'red'}"><div class="kpi-inner"><div>
    <div class="kpi-label">Diff (FG+STN−PO)</div><div class="kpi-value">{diff:,.0f}</div>
    <div class="kpi-sub">{'Surplus ✅' if diff>=0 else 'Shortfall ⚠️'}</div></div>
    <div class="kpi-ico">{'✅' if diff>=0 else '⚠️'}</div></div></div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦  FG Inventory", "📊  CFA Stock vs Open Orders", "🏪  Channel Analysis"])

# ═══ TAB 1 ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📋 Finished Goods Inventory</span><span class="tbl-badge">{len(df):,} rows</span></div>', unsafe_allow_html=True)
    buf1 = io.BytesIO()
    with pd.ExcelWriter(buf1, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="FG Inventory")
    st.download_button("⬇  Export FG to Excel", buf1.getvalue(), "FG_Inventory.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
    if df.empty:
        st.warning("⚠️ No FG records match the current filters.")
    else:
        fg_priority = ["Item Name","Item SKU","Category","Primary Category","Warehouse","UoM",
                       "Qty Available","Shelf Life %","Batch No","MFG Date","Expiry Date",
                       "Inventory Date","Item Type","Current Aging (Days)",
                       "Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)"]
        fg_cols  = [c for c in fg_priority if c in df.columns]
        fg_cols += [c for c in df.columns if c not in fg_cols]
        df_show  = df[fg_cols].copy()
        for c in ["MFG Date","Expiry Date","Inventory Date"]:
            if c in df_show.columns:
                df_show[c] = pd.to_datetime(df_show[c], errors="coerce").dt.strftime("%d-%b-%Y").fillna("-")
        st.dataframe(df_show, use_container_width=True, height=540, hide_index=True,
            column_config={
                "Qty Available":      st.column_config.NumberColumn("Qty Available", format="%.0f"),
                "Shelf Life %":       st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
                "Qty Inward":         st.column_config.NumberColumn("Qty Inward",    format="%.0f"),
                "Qty (Issue / Hold)": st.column_config.NumberColumn("Issue / Hold",  format="%.0f"),
                "Value (Inc Tax)":    st.column_config.NumberColumn("Val (Inc)",     format="%.0f"),
                "Value (Ex Tax)":     st.column_config.NumberColumn("Val (Ex)",      format="%.0f"),
            })

# ═══ TAB 2 ════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="formula-bar">
        <span>📐 Formula:</span>
        <b>FG Stock</b> <span>= Qty at CFA warehouse</span> <span>+</span>
        <b>STN In-Transit</b> <span>= Raised/Approved STNs → CFA</span> <span>−</span>
        <b>Open PO Qty</b> <span>= Order Qty (excl. Cancelled &amp; Closed)</span> <span>=</span> <b>Diff</b>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 1: FG — CFA only ─────────────────────────────────────────────────
    df_cfa = df_fg[df_fg["Warehouse"].astype(str).apply(is_cfa)].copy() \
             if "Warehouse" in df_fg.columns else pd.DataFrame()
    if sel_cfa != "All CFAs" and not df_cfa.empty:
        df_cfa = df_cfa[df_cfa["Warehouse"].astype(str) == sel_cfa]
    if search and not df_cfa.empty:
        df_cfa = df_cfa[df_cfa.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]

    if not df_cfa.empty and "Item SKU" in df_cfa.columns:
        fg_agg = df_cfa.groupby(["Item SKU","Warehouse"]).agg(
            Item_Name =("Item Name",    "first"),
            Category  =("Category",     "first"),
            FG_Stock  =("Qty Available","sum"),
            Shelf_Life=("Shelf Life %", "mean"),
        ).reset_index()
        fg_agg.columns = ["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"]
        fg_agg["Shelf Life %"] = fg_agg["Shelf Life %"].round(1)
    else:
        fg_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"])

    # ── STEP 2: STN — CFA only ────────────────────────────────────────────────
    stn_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","STN In-Transit","STN Transfers"])
    if not df_stn.empty:
        fg_code_col = next((c for c in df_stn.columns if "fg code" in c.lower()), None) or \
                      next((c for c in df_stn.columns if "code" in c.lower() or "sku" in c.lower()), None)
        to_wh_col  = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        stat_col   = next((c for c in df_stn.columns if c.lower() == "status"), None)
        qty_col    = next((c for c in df_stn.columns if c.lower() == "qty"), None)

        if fg_code_col and to_wh_col and stat_col and qty_col:
            stn_filt = df_stn[
                df_stn[to_wh_col].astype(str).apply(is_cfa) &
                df_stn[stat_col].astype(str).str.strip().str.lower().isin(STN_OPEN_STATUSES)
            ].copy()
            if sel_cfa != "All CFAs":
                stn_filt = stn_filt[stn_filt[to_wh_col].astype(str) == sel_cfa]
            if search:
                stn_filt = stn_filt[stn_filt.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            if not stn_filt.empty:
                stn_filt["_sku"] = stn_filt[fg_code_col].astype(str).str.strip()
                stn_filt["_wh"]  = stn_filt[to_wh_col].astype(str).str.strip()
                stn_agg = stn_filt.groupby(["_sku","_wh"]).agg(
                    STN_In_Transit=(qty_col, "sum"),
                    STN_Transfers =(qty_col, "count"),
                ).reset_index()
                stn_agg.columns = ["Item SKU","CFA Warehouse","STN In-Transit","STN Transfers"]

    # ── STEP 3: SOS — CFA warehouses only ────────────────────────────────────
    so_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Open PO Qty","Open Orders"])
    if not df_sos.empty and "SO Status" in df_sos.columns:
        sku_col_so = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
        wh_col_so  = next((c for c in df_sos.columns if c.lower() == "warehouse"), None)
        qty_col_so = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
        val_col_so = next((c for c in df_sos.columns if "total amount" in c.lower()), None)

        if sku_col_so and wh_col_so and qty_col_so:
            open_mask = ~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)
            sos_open  = df_sos[open_mask].copy()
            # Use explicit CFA list instead of string match
            sos_open  = sos_open[sos_open[wh_col_so].astype(str).apply(is_cfa)]
            if sel_cfa != "All CFAs":
                sos_open = sos_open[sos_open[wh_col_so].astype(str) == sel_cfa]
            if search:
                sos_open = sos_open[sos_open.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            if not sos_open.empty:
                sos_open["_sku"] = sos_open[sku_col_so].astype(str).str.strip()
                sos_open["_wh"]  = sos_open[wh_col_so].astype(str).str.strip()
                agg_dict = {"Open PO Qty": (qty_col_so, "sum"), "Open Orders": (qty_col_so, "count")}
                if val_col_so:
                    agg_dict["Open PO Value (₹)"] = (val_col_so, "sum")
                so_agg = sos_open.groupby(["_sku","_wh"]).agg(**agg_dict).reset_index()
                so_agg.columns = ["Item SKU","CFA Warehouse"] + list(agg_dict.keys())

    # ── STEP 4: Merge ─────────────────────────────────────────────────────────
    merged = fg_agg.copy() if not fg_agg.empty else \
             pd.DataFrame(columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"])

    if not stn_agg.empty:
        merged = merged.merge(stn_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    else:
        merged["STN In-Transit"] = 0
        merged["STN Transfers"]  = 0

    if not so_agg.empty:
        merged = merged.merge(so_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    else:
        merged["Open PO Qty"]  = 0
        merged["Open Orders"]  = 0

    if merged.empty:
        st.warning("⚠️ No CFA data found.")
    else:
        merged["FG Stock"]       = merged["FG Stock"].fillna(0)
        merged["STN In-Transit"] = merged["STN In-Transit"].fillna(0)
        merged["STN Transfers"]  = merged["STN Transfers"].fillna(0).astype(int)
        merged["Open PO Qty"]    = merged["Open PO Qty"].fillna(0)
        merged["Open Orders"]    = merged["Open Orders"].fillna(0).astype(int)
        merged["Shelf Life %"]   = merged["Shelf Life %"].fillna(0.0).round(1)
        if "Open PO Value (₹)" in merged.columns:
            merged["Open PO Value (₹)"] = merged["Open PO Value (₹)"].fillna(0)

        # Use explicit CFA list instead of string match
        merged = merged[merged["CFA Warehouse"].astype(str).apply(is_cfa)]

        merged["Total Available"] = merged["FG Stock"] + merged["STN In-Transit"]
        merged["Diff"]            = merged["Total Available"] - merged["Open PO Qty"]

        # Fill Item Name / Category
        fg_name_map = df_fg.drop_duplicates("Item SKU").set_index("Item SKU")[["Item Name","Category"]].to_dict("index") \
                      if "Item SKU" in df_fg.columns else {}
        def fill_name(row):
            if pd.isna(row.get("Item Name")) or str(row.get("Item Name","")) == "":
                info = fg_name_map.get(str(row["Item SKU"]).strip(), {})
                row["Item Name"] = info.get("Item Name", row["Item SKU"])
                row["Category"]  = info.get("Category", "")
            return row
        merged = merged.apply(fill_name, axis=1)
        merged = merged.sort_values("Diff", ascending=True)

        # Summary metrics
        t_fg   = merged["FG Stock"].sum()
        t_stn  = merged["STN In-Transit"].sum()
        t_po   = merged["Open PO Qty"].sum()
        t_diff = merged["Diff"].sum()
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("CFA FG Stock",   f"{t_fg:,.0f}")
        s2.metric("STN In-Transit", f"{t_stn:,.0f}")
        s3.metric("Total Available",f"{(t_fg+t_stn):,.0f}", help="FG + STN")
        s4.metric("Open PO Qty",    f"{t_po:,.0f}")
        s5.metric("Net Diff",       f"{t_diff:,.0f}",
                  delta=f"{'Surplus' if t_diff>=0 else 'Shortfall'}: {abs(t_diff):,.0f}",
                  delta_color="normal" if t_diff>=0 else "inverse")

        st.markdown("<div style='margin-bottom:14px'></div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════════════════════
        # FILL RATE  +  EXPIRY HEATMAP — CFA only
        # ══════════════════════════════════════════════════════════════════════
        today_ts = pd.Timestamp(datetime.today().date())

        # ── Fill Rate ─────────────────────────────────────────────────────────
        fill_rows = []
        for cfa_wh in sorted(merged["CFA Warehouse"].dropna().astype(str).unique()):
            cfa_m       = merged[merged["CFA Warehouse"] == cfa_wh]
            total_po    = cfa_m["Open PO Qty"].sum()
            fulfillable = cfa_m.apply(
                lambda r: min(r["Total Available"], r["Open PO Qty"]), axis=1
            ).sum()
            fill_pct    = (fulfillable / total_po * 100) if total_po > 0 else 100.0
            fill_pct    = min(fill_pct, 100.0)
            short_skus  = int((cfa_m["Diff"] < 0).sum())
            fill_rows.append({"CFA": cfa_wh, "Fill Rate %": round(fill_pct, 1),
                               "Total Available": cfa_m["Total Available"].sum(),
                               "Open PO Qty": total_po,
                               "Shortfall SKUs": short_skus})
        fill_df = pd.DataFrame(fill_rows).sort_values("Fill Rate %", ascending=True) \
                  if fill_rows else pd.DataFrame()

        # ── Expiry buckets ────────────────────────────────────────────────────
        expiry_rows = []
        if not df_cfa.empty and "Expiry Date" in df_cfa.columns:
            exp_data = df_cfa[["Warehouse","Qty Available","Expiry Date"]].copy()
            exp_data["Expiry Date"]  = pd.to_datetime(exp_data["Expiry Date"], errors="coerce")
            exp_data["days_to_exp"] = (exp_data["Expiry Date"] - today_ts).dt.days
            for cfa_wh in sorted(exp_data["Warehouse"].dropna().astype(str).unique()):
                cfa_e = exp_data[exp_data["Warehouse"] == cfa_wh]
                expiry_rows.append({
                    "CFA":        cfa_wh,
                    "Expired":    cfa_e[cfa_e["days_to_exp"] <  0]["Qty Available"].sum(),
                    "< 30 days":  cfa_e[cfa_e["days_to_exp"].between(0,  30, inclusive="both")]["Qty Available"].sum(),
                    "31–60 days": cfa_e[cfa_e["days_to_exp"].between(31, 60, inclusive="both")]["Qty Available"].sum(),
                    "61–90 days": cfa_e[cfa_e["days_to_exp"].between(61, 90, inclusive="both")]["Qty Available"].sum(),
                    "> 90 days":  cfa_e[cfa_e["days_to_exp"] > 90]["Qty Available"].sum(),
                })
        expiry_df = pd.DataFrame(expiry_rows) if expiry_rows else pd.DataFrame()

        # ── Render side by side ───────────────────────────────────────────────
        col_fill, col_exp = st.columns([1, 1.6], gap="medium")

        with col_fill:
            st.markdown('<div class="sec-div">📊 Fill Rate by CFA</div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-size:10px;color:#475569;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">
              Fill Rate = % of open PO demand fulfillable with FG + STN stock</div>""", unsafe_allow_html=True)

            if fill_df.empty:
                st.info("No open PO data for CFA warehouses.")
            else:
                for _, fr in fill_df.iterrows():
                    pct   = float(fr["Fill Rate %"])
                    avl   = float(fr["Total Available"])
                    po    = float(fr["Open PO Qty"])
                    short = int(fr["Shortfall SKUs"])
                    bar_c = "#22c55e" if pct>=90 else "#f59e0b" if pct>=60 else "#ef4444"
                    txt_c = "#bbf7d0" if pct>=90 else "#fde68a" if pct>=60 else "#fca5a5"
                    bdg_bg= "#061a0a" if pct>=90 else "#2d1f00" if pct>=60 else "#2d0a0a"
                    bdg_b = "#14532d" if pct>=90 else "#78350f" if pct>=60 else "#7f1d1d"
                    bar_w = min(pct, 100)
                    cfa_name = fr['CFA']
                    avl_fmt  = f"{avl:,.0f}"
                    po_fmt   = f"{po:,.0f}"
                    pct_fmt  = f"{pct:.1f}%"
                    short_html = ""
                    if short > 0:
                        s_label = f"&#9888;&#65039; {short} SKU{'s' if short!=1 else ''}"
                        short_html = f'<span style="font-size:10px;color:#f87171;margin-left:6px;">{s_label}</span>'

                    html = (
                        f'<div style="background:#0d1117;border:1px solid #1e2535;border-radius:11px;padding:11px 14px;margin-bottom:8px;">'
                        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;">'
                        f'<span style="font-size:12px;font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px;">{cfa_name}</span>'
                        f'<div style="display:flex;align-items:center;gap:6px;">'
                        f'{short_html}'
                        f'<span style="background:{bdg_bg};border:1px solid {bdg_b};border-radius:20px;padding:2px 10px;font-size:12px;font-weight:800;color:{txt_c};font-family:JetBrains Mono,monospace;">{pct_fmt}</span>'
                        f'</div></div>'
                        f'<div style="background:#1e2535;border-radius:5px;height:8px;margin-bottom:5px;">'
                        f'<div style="width:{bar_w:.1f}%;background:{bar_c};height:8px;border-radius:5px;"></div>'
                        f'</div>'
                        f'<div style="display:flex;justify-content:space-between;font-size:10px;font-family:JetBrains Mono,monospace;">'
                        f'<span style="color:#475569;">Available: <b style="color:#94a3b8;">{avl_fmt}</b></span>'
                        f'<span style="color:#475569;">Open PO: <b style="color:#94a3b8;">{po_fmt}</b></span>'
                        f'</div></div>'
                    )
                    st.markdown(html, unsafe_allow_html=True)

        with col_exp:
            st.markdown('<div class="sec-div">🔥 Expiry Heatmap by CFA</div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-size:10px;color:#475569;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">
              Qty expiring within each window · cell intensity = urgency</div>""", unsafe_allow_html=True)

            if expiry_df.empty:
                st.info("No expiry data — ensure FG Inventory has an Expiry Date column.")
            else:
                buckets  = ["Expired","< 30 days","31–60 days","61–90 days","> 90 days"]
                bkt_cols = ["#7f1d1d","#b91c1c","#d97706","#ca8a04","#15803d"]
                bkt_bg   = ["#1a0000","#2d0a0a","#2d1800","#2d2200","#061a0a"]
                bkt_bdr  = ["#450a0a","#7f1d1d","#78350f","#713f12","#14532d"]
                max_vals = {b: max(expiry_df[b].max(), 1) for b in buckets}

                hdr = '<div style="display:grid;grid-template-columns:150px repeat(5,1fr);gap:4px;margin-bottom:6px;">'
                hdr += '<div style="font-size:10px;color:#334155;font-weight:700;font-family:JetBrains Mono,monospace;">CFA</div>'
                for b, bc in zip(buckets, bkt_cols):
                    hdr += f'<div style="font-size:9px;color:{bc};font-weight:700;text-align:center;font-family:JetBrains Mono,monospace;line-height:1.3;">{b}</div>'
                hdr += '</div>'
                st.markdown(hdr, unsafe_allow_html=True)

                for _, er in expiry_df.sort_values("< 30 days", ascending=False).iterrows():
                    row = '<div style="display:grid;grid-template-columns:150px repeat(5,1fr);gap:4px;margin-bottom:5px;align-items:center;">'
                    row += f'<div style="font-size:11px;font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{er["CFA"]}</div>'
                    for b, bc, bbg, bbdr in zip(buckets, bkt_cols, bkt_bg, bkt_bdr):
                        val       = float(er[b])
                        intensity = val / max_vals[b] if max_vals[b] > 0 else 0
                        opacity   = min(0.4 + max(0.08, intensity), 1.0)
                        val_str   = f"{val:,.0f}" if val > 0 else "&#8212;"
                        val_color = bc if val > 0 else "#1e2535"
                        row += (
                            f'<div style="background:{bbg};border:1px solid {bbdr};border-radius:7px;'
                            f'padding:5px 4px;text-align:center;opacity:{opacity:.2f};">'
                            f'<div style="font-size:11px;font-weight:800;color:{val_color};'
                            f'font-family:JetBrains Mono,monospace;line-height:1;">{val_str}</div>'
                            f'</div>'
                        )
                    row += '</div>'
                    st.markdown(row, unsafe_allow_html=True)

                tot = '<div style="display:grid;grid-template-columns:150px repeat(5,1fr);gap:4px;margin-top:8px;padding-top:8px;border-top:1px solid #1e2535;">'
                tot += '<div style="font-size:10px;font-weight:700;color:#475569;font-family:JetBrains Mono,monospace;">TOTAL</div>'
                for b, bc in zip(buckets, bkt_cols):
                    tot += f'<div style="text-align:center;font-size:11px;font-weight:800;color:{bc};font-family:JetBrains Mono,monospace;">{expiry_df[b].sum():,.0f}</div>'
                tot += '</div>'
                st.markdown(tot, unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid #161d2e;margin:14px 0;">', unsafe_allow_html=True)

        # ── Fill Rate column in main table ────────────────────────────────────
        if not fill_df.empty:
            fill_rate_map = dict(zip(fill_df["CFA"], fill_df["Fill Rate %"]))
            merged["Fill Rate %"] = merged["CFA Warehouse"].map(fill_rate_map).fillna(0.0)
        else:
            merged["Fill Rate %"] = 0.0

        # ── Batch lookup ──────────────────────────────────────────────────────
        batch_lookup = {}
        if not df_cfa.empty and "Item SKU" in df_cfa.columns:
            for (sku, wh), grp in df_cfa.groupby(["Item SKU","Warehouse"]):
                batches = []
                for _, r in grp.iterrows():
                    exp = r.get("Expiry Date", None)
                    batches.append({
                        "Batch No":    str(r.get("Batch No","—")) if "Batch No" in r.index else "—",
                        "Qty":         float(r.get("Qty Available", 0)),
                        "Shelf Life %":round(float(r.get("Shelf Life %", 0)), 1),
                        "Expiry Date": exp.strftime("%d-%b-%Y") if pd.notna(exp) else "—",
                    })
                batch_lookup[(str(sku).strip(), str(wh).strip())] = batches

        def shelf_label(row):
            key = (str(row["Item SKU"]).strip(), str(row["CFA Warehouse"]).strip())
            n   = len(batch_lookup.get(key, []))
            avg = row.get("Shelf Life %", 0)
            return f"{avg:.1f}% · {n} batch{'es' if n>1 else ''}" if n else f"{avg:.1f}%"
        merged["Shelf Life"] = merged.apply(shelf_label, axis=1)

        # ── Display columns ───────────────────────────────────────────────────
        disp_cols = ["Item Name","Item SKU","Category","CFA Warehouse",
                     "FG Stock","STN In-Transit","STN Transfers",
                     "Shelf Life","Fill Rate %","Open PO Qty","Open Orders","Total Available","Diff"]
        if "Open PO Value (₹)" in merged.columns:
            disp_cols.insert(disp_cols.index("Diff"), "Open PO Value (₹)")
        disp_cols = [c for c in disp_cols if c in merged.columns]
        df_disp   = merged[disp_cols].copy()

        # Export
        df_export = merged[["Item Name","Item SKU","Category","CFA Warehouse",
                             "FG Stock","STN In-Transit","STN Transfers","Shelf Life %",
                             "Fill Rate %","Open PO Qty","Open Orders","Total Available","Diff"] +
                            (["Open PO Value (₹)"] if "Open PO Value (₹)" in merged.columns else [])].copy()
        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as w:
            df_export.to_excel(w, index=False, sheet_name="CFA Analysis")

        # Row colouring
        def colour_row(row):
            d = row.get("Diff", 0)
            if pd.isna(d): return [""] * len(row)
            if d < 0:      return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
            tot = row.get("Total Available", 1)
            if tot > 0 and d / tot < 0.15:
                return ["background-color:#2d1f00; color:#fde68a"] * len(row)
            return ["background-color:#061410; color:#d1fae5"] * len(row)

        col_cfg = {
            "FG Stock":        st.column_config.NumberColumn("FG Stock",           format="%.0f"),
            "STN In-Transit":  st.column_config.NumberColumn("STN In-Transit 🚚",   format="%.0f"),
            "STN Transfers":   st.column_config.NumberColumn("# STNs",             format="%d"),
            "Shelf Life":      st.column_config.TextColumn("Shelf Life 📦",         help="avg · N batches — click row to expand"),
            "Fill Rate %":     st.column_config.ProgressColumn("Fill Rate % 🎯",    min_value=0, max_value=100, format="%.1f%%"),
            "Open PO Qty":     st.column_config.NumberColumn("Open PO Qty",        format="%.0f"),
            "Open Orders":     st.column_config.NumberColumn("# Orders",           format="%d"),
            "Total Available": st.column_config.NumberColumn("Total Available",    format="%.0f"),
            "Diff":            st.column_config.NumberColumn("Diff ✅",             format="%.0f"),
        }
        if "Open PO Value (₹)" in df_disp.columns:
            col_cfg["Open PO Value (₹)"] = st.column_config.NumberColumn("PO Value (₹)", format="%.0f")

        # ── Batch panel ───────────────────────────────────────────────────────
        if "batch_sel_tab2" not in st.session_state:
            st.session_state["batch_sel_tab2"] = None

        sel_key       = st.session_state.get("batch_sel_tab2")
        lookup_key    = (sel_key[0], sel_key[2]) if sel_key and len(sel_key)==3 else None
        batches_show  = batch_lookup.get(lookup_key, []) if lookup_key else []

        if sel_key and batches_show:
            batch_df       = pd.DataFrame(batches_show).sort_values("Shelf Life %", ascending=True)
            batch_rows_html = ""
            for _, b in batch_df.iterrows():
                pct      = float(b["Shelf Life %"])
                bar_w    = max(2, int(pct))
                batch_no = str(b["Batch No"])
                qty_fmt  = f"{b['Qty']:,.0f}"
                pct_fmt  = f"{pct:.1f}%"
                exp_str  = str(b["Expiry Date"])
                batch_rows_html += (
                    '<div style="display:flex;align-items:center;gap:14px;margin-bottom:7px;">'
                    f'<span style="min-width:130px;max-width:130px;color:#94a3b8;font-family:JetBrains Mono,monospace;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{batch_no}</span>'
                    '<div style="flex:1;background:#1e2535;border-radius:5px;height:12px;max-width:280px;">'
                    f'<div style="width:{bar_w}%;background:#5bc8c0;height:12px;border-radius:5px;"></div>'
                    '</div>'
                    f'<span style="min-width:48px;text-align:right;color:#e2e8f0;font-weight:800;font-family:JetBrains Mono,monospace;font-size:12px;">{pct_fmt}</span>'
                    f'<span style="min-width:88px;text-align:right;color:#64748b;font-family:JetBrains Mono,monospace;font-size:11px;">{qty_fmt} units</span>'
                    f'<span style="min-width:96px;color:#475569;font-size:11px;">Exp: {exp_str}</span>'
                    '</div>'
                )

            n_batches  = len(batch_df)
            batch_lbl  = f"{n_batches} batch{'es' if n_batches>1 else ''}"
            wh_display = sel_key[2] if len(sel_key) > 2 else ""
            sku_display= sel_key[0]

            panel_html = (
                '<div style="background:#060d18;border:1.5px solid #5bc8c0;border-radius:14px;padding:16px 20px;margin-bottom:12px;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
                '<div>'
                '<div style="font-size:10px;color:#5bc8c0;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:3px;">📦 Batch Shelf Life Breakdown</div>'
                f'<div style="font-size:13px;color:#f1f5f9;font-weight:700;">{wh_display}'
                f'<span style="color:#818cf8;font-family:JetBrains Mono,monospace;font-size:12px;margin-left:8px;">{sku_display}</span>'
                '</div>'
                '</div>'
                f'<div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:6px 14px;font-size:11px;color:#60a5fa;font-family:JetBrains Mono,monospace;font-weight:700;">{batch_lbl}</div>'
                '</div>'
                f'{batch_rows_html}'
                '</div>'
            )
            st.markdown(panel_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#060d18;border:1px dashed #1e2535;border-radius:14px;
                        padding:14px 20px;margin-bottom:12px;text-align:center;
                        color:#334155;font-size:11px;font-family:'JetBrains Mono',monospace;">
              👆 Select a row below to see batch-level shelf life &amp; expiry breakdown
            </div>""", unsafe_allow_html=True)

        # ── Table ─────────────────────────────────────────────────────────────
        hc1, hc2 = st.columns([3, 1])
        with hc1:
            st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📊 SKU · CFA · FG + STN vs Open PO</span><span class="tbl-badge">{len(df_disp):,} SKUs</span></div>', unsafe_allow_html=True)
        with hc2:
            st.download_button("⬇  Export", buf2.getvalue(), "CFA_Stock_Analysis.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

        event = st.dataframe(
            df_disp.style.apply(colour_row, axis=1),
            use_container_width=True, height=480, hide_index=False,
            column_config=col_cfg,
            on_select="rerun", selection_mode="single-row", key="cfa_table"
        )

        selected_rows = event.selection.get("rows", []) if hasattr(event, "selection") else []
        if selected_rows:
            r       = df_disp.iloc[selected_rows[0]]
            new_key = (str(r["Item SKU"]).strip(), str(r.get("Item Name","")).strip(), str(r["CFA Warehouse"]).strip())
            if st.session_state.get("batch_sel_tab2") != new_key:
                st.session_state["batch_sel_tab2"] = new_key
                st.rerun()

        # ── Per-CFA expanders ─────────────────────────────────────────────────
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-div">Breakdown by CFA Warehouse</div>', unsafe_allow_html=True)
        for cfa_wh in sorted(df_disp["CFA Warehouse"].dropna().astype(str).unique()):
            cfa_data = df_disp[df_disp["CFA Warehouse"] == cfa_wh]
            c_fg    = cfa_data["FG Stock"].sum()
            c_stn   = cfa_data["STN In-Transit"].sum()
            c_po    = cfa_data["Open PO Qty"].sum()
            c_diff  = cfa_data["Diff"].sum()
            c_short = int((cfa_data["Diff"] < 0).sum())
            label   = f"🏭  {cfa_wh}   |   FG: {c_fg:,.0f}  +  STN: {c_stn:,.0f}  −  PO: {c_po:,.0f}  =  Diff: {c_diff:,.0f}   {'⚠️ '+str(c_short)+' shortfall' if c_short else '✅ Healthy'}"
            with st.expander(label, expanded=False):
                st.dataframe(cfa_data.style.apply(colour_row, axis=1),
                             use_container_width=True,
                             height=min(60 + len(cfa_data)*36, 420),
                             hide_index=True, column_config=col_cfg)

# ═══ TAB 3 — CHANNEL ANALYSIS ════════════════════════════════════════════════
with tab3:

    st.markdown("""
    <div class="formula-bar">
        <span>📐 Formula:</span>
        <b>Stock</b> <span>= Tumkur New Warehouse + Central + YB FG Warehouse</span> <span>−</span>
        <b>Open PO Qty</b> <span>= per Channel (Mapper → Customer Name)</span> <span>=</span> <b>Diff</b>
    </div>
    """, unsafe_allow_html=True)

    # ── Validate required data ────────────────────────────────────────────────
    if df_mapper.empty:
        st.error("⚠️ Mapper sheet not found or empty.")
    elif df_sos.empty:
        st.error("⚠️ SOS sheet not found or empty.")
    elif df_fg.empty:
        st.error("⚠️ FG Inventory sheet not found or empty.")
    else:
        # ── Step 1: Channel stock (3 warehouses only) ─────────────────────────
        stock_base = df_fg[
            df_fg["Warehouse"].astype(str).isin(CHANNEL_STOCK_WAREHOUSES)
        ].copy() if "Warehouse" in df_fg.columns else pd.DataFrame()

        # SKU-level stock totals
        if not stock_base.empty and "Item SKU" in stock_base.columns:
            sku_stock = stock_base.groupby("Item SKU").agg(
                Item_Name   =("Item Name",     "first"),
                Category    =("Category",      "first"),
                Stock_Avail =("Qty Available", "sum"),
            ).reset_index()
            sku_stock.columns = ["Item SKU","Item Name","Category","Stock Available"]
        else:
            sku_stock = pd.DataFrame(columns=["Item SKU","Item Name","Category","Stock Available"])

        # ── Step 2: Mapper — customer → channel ───────────────────────────────
        # Detect column names defensively
        cust_col_m    = next((c for c in df_mapper.columns if "customer" in c.lower()), None)
        channel_col_m = next((c for c in df_mapper.columns if "channel" in c.lower()), None)

        if not cust_col_m or not channel_col_m:
            st.error(f"⚠️ Mapper sheet must have Customer Name and Channel columns. Found: {list(df_mapper.columns)}")
            st.stop()

        mapper_clean = df_mapper[[cust_col_m, channel_col_m]].copy()
        mapper_clean.columns = ["Customer Name", "Channel"]
        mapper_clean["Customer Name"] = mapper_clean["Customer Name"].astype(str).str.strip()
        mapper_clean["Channel"]       = mapper_clean["Channel"].astype(str).str.strip()
        customer_channel_map          = dict(zip(mapper_clean["Customer Name"], mapper_clean["Channel"]))

        # ── Step 3: Open SOS — join channel from mapper ───────────────────────
        sku_col_so  = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
        cust_col_so = next((c for c in df_sos.columns if "customer" in c.lower()), None)
        qty_col_so  = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
        dsp_col_so  = next((c for c in df_sos.columns if "dispatch qty" in c.lower()), None)
        nm_col_so   = next((c for c in df_sos.columns if "item name" in c.lower() or "product name" in c.lower()), None)

        if not sku_col_so or not qty_col_so:
            st.error(f"⚠️ SOS sheet missing Product SKU or Order Qty column. Found: {list(df_sos.columns)}")
            st.stop()

        open_sos = df_sos[
            ~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)
        ].copy() if "SO Status" in df_sos.columns else df_sos.copy()

        open_sos["_sku"]      = open_sos[sku_col_so].astype(str).str.strip()
        open_sos["_customer"] = open_sos[cust_col_so].astype(str).str.strip() if cust_col_so else ""
        open_sos["_channel"]  = open_sos["_customer"].map(customer_channel_map).fillna("Unknown")
        open_sos["_order_qty"]= pd.to_numeric(open_sos[qty_col_so], errors="coerce").fillna(0)
        open_sos["_dispatch"] = pd.to_numeric(open_sos[dsp_col_so], errors="coerce").fillna(0) if dsp_col_so else 0

        if nm_col_so:
            open_sos["_item_name"] = open_sos[nm_col_so].astype(str).str.strip()
        else:
            open_sos["_item_name"] = open_sos["_sku"]

        # ── Step 4: All channels present ──────────────────────────────────────
        all_channels = sorted([c for c in open_sos["_channel"].unique() if c != "Unknown"])
        if "Unknown" in open_sos["_channel"].values:
            all_channels.append("Unknown")

        if not all_channels:
            st.warning("⚠️ No channel data found. Check Mapper customer names match SOS.")
        else:
            # ── Channel-level KPI bar ─────────────────────────────────────────
            ch_kpi = open_sos.groupby("_channel").agg(
                Total_PO =("_order_qty","sum"),
                Orders   =("_order_qty","count"),
            ).reset_index()

            total_channel_po   = ch_kpi["Total_PO"].sum()
            total_channel_stock= sku_stock["Stock Available"].sum() if not sku_stock.empty else 0
            total_channel_diff = total_channel_stock - total_channel_po

            st.markdown(f"""
            <div class="kpi-row" style="grid-template-columns:repeat(3,1fr);">
              <div class="kpi-box teal"><div class="kpi-inner"><div>
                <div class="kpi-label">Stock (3 Warehouses)</div>
                <div class="kpi-value">{total_channel_stock:,.0f}</div>
                <div class="kpi-sub">Tumkur New + Central + YB FG</div>
              </div><div class="kpi-ico">📦</div></div></div>
              <div class="kpi-box amber"><div class="kpi-inner"><div>
                <div class="kpi-label">Total Open PO (All Channels)</div>
                <div class="kpi-value">{total_channel_po:,.0f}</div>
                <div class="kpi-sub">{len(all_channels)} channels · {int(ch_kpi["Orders"].sum()):,} orders</div>
              </div><div class="kpi-ico">📋</div></div></div>
              <div class="kpi-box {"green" if total_channel_diff>=0 else "red"}"><div class="kpi-inner"><div>
                <div class="kpi-label">Net Diff (Stock − PO)</div>
                <div class="kpi-value">{total_channel_diff:,.0f}</div>
                <div class="kpi-sub">{"Surplus ✅" if total_channel_diff>=0 else "Shortfall ⚠️"}</div>
              </div><div class="kpi-ico">{"✅" if total_channel_diff>=0 else "⚠️"}</div></div></div>
            </div>
            """, unsafe_allow_html=True)

            # ── Shortfall toggle ──────────────────────────────────────────────
            show_shortfall_only = st.toggle("⚠️ Show shortfall SKUs only", value=False, key="ch_shortfall_toggle")

            # ── Channel sub-tabs ──────────────────────────────────────────────
            ch_tab_labels = [f"{'🔴' if open_sos[open_sos['_channel']==ch]['_order_qty'].sum() > 0 else '⚪'}  {ch}" for ch in all_channels]
            ch_tabs = st.tabs(ch_tab_labels)

            for ch_tab, channel in zip(ch_tabs, all_channels):
                with ch_tab:
                    ch_sos = open_sos[open_sos["_channel"] == channel].copy()

                    if ch_sos.empty:
                        st.info(f"No open orders found for channel: {channel}")
                        continue

                    # SKU summary for this channel
                    ch_sku_summary = ch_sos.groupby("_sku").agg(
                        Item_Name   =("_item_name",  "first"),
                        Open_PO     =("_order_qty",  "sum"),
                        Dispatched  =("_dispatch",   "sum"),
                        Orders      =("_order_qty",  "count"),
                        Customers   =("_customer",   "nunique"),
                    ).reset_index()
                    ch_sku_summary.columns = ["Item SKU","Item Name","Open PO Qty","Dispatch Qty","# Orders","# Customers"]

                    # Merge with stock
                    ch_merged = ch_sku_summary.merge(
                        sku_stock[["Item SKU","Category","Stock Available"]],
                        on="Item SKU", how="left"
                    )
                    ch_merged["Stock Available"] = ch_merged["Stock Available"].fillna(0)
                    ch_merged["Shortfall Qty"]   = ch_merged["Stock Available"] - ch_merged["Open PO Qty"]

                    # Forecast for Days of Stock
                    forecast_col = None
                    if not df_sos.empty:
                        # Use monthly forecast from Forecast sheet if available
                        pass

                    # Days of stock = Stock / (Open PO as proxy for demand)
                    ch_merged["Days of Stock"] = ch_merged.apply(
                        lambda r: round(r["Stock Available"] / (r["Open PO Qty"] / 26), 1)
                        if r["Open PO Qty"] > 0 else 0.0, axis=1
                    )

                    ch_merged = ch_merged.sort_values("Shortfall Qty", ascending=True)

                    if show_shortfall_only:
                        ch_merged = ch_merged[ch_merged["Shortfall Qty"] < 0]

                    # ── Channel KPIs ──────────────────────────────────────────
                    c_stock   = ch_merged["Stock Available"].sum()
                    c_po      = ch_merged["Open PO Qty"].sum()
                    c_diff    = ch_merged["Shortfall Qty"].sum()
                    c_short_n = int((ch_merged["Shortfall Qty"] < 0).sum())
                    c_cust_n  = ch_sos["_customer"].nunique()

                    k1,k2,k3,k4,k5 = st.columns(5)
                    k1.metric("Stock Available",  f"{c_stock:,.0f}")
                    k2.metric("Open PO Qty",       f"{c_po:,.0f}")
                    k3.metric("Net Diff",           f"{c_diff:,.0f}",
                              delta=f"{'Surplus' if c_diff>=0 else 'Shortfall'}: {abs(c_diff):,.0f}",
                              delta_color="normal" if c_diff>=0 else "inverse")
                    k4.metric("Shortfall SKUs",    f"{c_short_n}")
                    k5.metric("Customers",         f"{c_cust_n}")

                    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

                    if ch_merged.empty:
                        st.info("No shortfall SKUs for this channel." if show_shortfall_only else "No SKUs found.")
                        continue

                    # ── Row colouring ─────────────────────────────────────────
                    def colour_ch(row):
                        d = row.get("Shortfall Qty", 0)
                        if pd.isna(d): return [""] * len(row)
                        if d < 0:     return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
                        tot = row.get("Stock Available", 1)
                        if tot > 0 and d / max(tot, 1) < 0.15:
                            return ["background-color:#2d1f00; color:#fde68a"] * len(row)
                        return ["background-color:#061410; color:#d1fae5"] * len(row)

                    ch_col_cfg = {
                        "Open PO Qty":     st.column_config.NumberColumn("Open PO Qty",    format="%.0f"),
                        "Dispatch Qty":    st.column_config.NumberColumn("Dispatch Qty",   format="%.0f"),
                        "Stock Available": st.column_config.NumberColumn("Stock Available", format="%.0f"),
                        "Shortfall Qty":   st.column_config.NumberColumn("Diff (Stock−PO)", format="%.0f"),
                        "Days of Stock":   st.column_config.NumberColumn("Days of Stock",  format="%.1f"),
                        "# Orders":        st.column_config.NumberColumn("# Orders",       format="%d"),
                        "# Customers":     st.column_config.NumberColumn("# Customers",    format="%d"),
                    }

                    # ── Summary table ─────────────────────────────────────────
                    disp_ch = ch_merged[["Item Name","Item SKU","Category",
                                         "Open PO Qty","Dispatch Qty","Stock Available",
                                         "Shortfall Qty","Days of Stock","# Orders","# Customers"]].copy()

                    st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📊 {channel} — SKU Summary</span><span class="tbl-badge">{len(disp_ch):,} SKUs</span></div>', unsafe_allow_html=True)

                    # Export
                    buf_ch = io.BytesIO()
                    # Build customer drill for export
                    cust_detail = ch_sos.groupby(["_sku","_customer"]).agg(
                        Open_PO   =("_order_qty","sum"),
                        Dispatched=("_dispatch", "sum"),
                        Orders    =("_order_qty","count"),
                    ).reset_index()
                    cust_detail.columns = ["Item SKU","Customer Name","Open PO Qty","Dispatch Qty","# Orders"]
                    cust_detail = cust_detail.merge(
                        sku_stock[["Item SKU","Stock Available"]], on="Item SKU", how="left"
                    )
                    cust_detail["Stock Available"] = cust_detail["Stock Available"].fillna(0)
                    cust_detail["Channel"] = channel

                    with pd.ExcelWriter(buf_ch, engine="openpyxl") as wx:
                        disp_ch.to_excel(wx, index=False, sheet_name="SKU Summary")
                        cust_detail.to_excel(wx, index=False, sheet_name="Customer Drill")

                    hch1, hch2 = st.columns([4,1])
                    with hch2:
                        st.download_button(f"⬇ Export {channel}", buf_ch.getvalue(),
                            f"Channel_{channel}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)

                    st.dataframe(
                        disp_ch.style.apply(colour_ch, axis=1),
                        use_container_width=True, height=420, hide_index=True,
                        column_config=ch_col_cfg
                    )

                    # ── Drill-down: per-SKU customer breakdown ─────────────────
                    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
                    st.markdown('<div class="sec-div">👤 Customer Drill-Down by SKU</div>', unsafe_allow_html=True)

                    for _, sku_row in ch_merged.iterrows():
                        sku      = sku_row["Item SKU"]
                        sku_name = sku_row["Item Name"]
                        s_diff   = sku_row["Shortfall Qty"]
                        s_stock  = sku_row["Stock Available"]
                        s_po     = sku_row["Open PO Qty"]
                        status   = "⚠️ Shortfall" if s_diff < 0 else "✅ OK"

                        exp_label = (
                            f"{status}  ·  {sku} — {sku_name}  "
                            f"|  Stock: {s_stock:,.0f}  ·  PO: {s_po:,.0f}  ·  Diff: {s_diff:,.0f}"
                        )

                        with st.expander(exp_label, expanded=(s_diff < 0)):
                            sku_cust = ch_sos[ch_sos["_sku"] == sku].groupby("_customer").agg(
                                Open_PO   =("_order_qty","sum"),
                                Dispatched=("_dispatch", "sum"),
                                Orders    =("_order_qty","count"),
                            ).reset_index()
                            sku_cust.columns = ["Customer Name","Open PO Qty","Dispatch Qty","# Orders"]
                            sku_cust["Channel"]         = channel
                            sku_cust["Stock Available"] = s_stock
                            sku_cust["Shortfall Qty"]   = s_stock - sku_cust["Open PO Qty"]
                            sku_cust = sku_cust.sort_values("Shortfall Qty", ascending=True)

                            def colour_cust(row):
                                d = row.get("Shortfall Qty", 0)
                                if pd.isna(d): return [""] * len(row)
                                if d < 0:     return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
                                return ["background-color:#061410; color:#d1fae5"] * len(row)

                            st.dataframe(
                                sku_cust.style.apply(colour_cust, axis=1),
                                use_container_width=True,
                                height=min(60 + len(sku_cust)*36, 380),
                                hide_index=True,
                                column_config={
                                    "Open PO Qty":     st.column_config.NumberColumn("Open PO Qty",    format="%.0f"),
                                    "Dispatch Qty":    st.column_config.NumberColumn("Dispatch Qty",   format="%.0f"),
                                    "Stock Available": st.column_config.NumberColumn("Stock Available", format="%.0f"),
                                    "Shortfall Qty":   st.column_config.NumberColumn("Diff",           format="%.0f"),
                                    "# Orders":        st.column_config.NumberColumn("# Orders",       format="%d"),
                                }
                            )

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · CFA ANALYSIS</div>', unsafe_allow_html=True)
