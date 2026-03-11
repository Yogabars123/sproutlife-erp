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

/* HEADER */
.app-header { display:flex; align-items:center; justify-content:space-between; padding-bottom:14px; border-bottom:1px solid #161d2e; margin-bottom:14px; }
.hdr-left { display:flex; align-items:center; gap:10px; }
.hdr-logo { width:40px; height:40px; min-width:40px; background:#0f1f3a; border:1px solid #1a3a5c; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:19px; }
.hdr-title { font-size:16px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 11px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }

/* KPI ROW */
.kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.kpi-box { border-radius:16px; padding:18px 20px; border:1px solid; position:relative; overflow:hidden; }
.kpi-box::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-box.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-box.teal::before  { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-box.violet { background:linear-gradient(135deg,#130a2a,#1e0f40); border-color:#3b1f6e; }
.kpi-box.violet::before { background:linear-gradient(90deg,#a855f7,#818cf8); }
.kpi-box.amber  { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-box.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-box.green  { background:linear-gradient(135deg,#061a0a,#0a2e12); border-color:#14532d; }
.kpi-box.green::before  { background:linear-gradient(90deg,#22c55e,#4ade80); }
.kpi-box.red    { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-box.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-inner { display:flex; align-items:flex-start; justify-content:space-between; }
.kpi-label { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:6px; }
.kpi-value { font-size:28px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-sub   { font-size:11px; margin-top:5px; }
.kpi-ico   { font-size:24px; opacity:.6; margin-top:2px; }
.kpi-box.teal   .kpi-label { color:#5bc8c0; } .kpi-box.teal   .kpi-value { color:#99f6e4; } .kpi-box.teal   .kpi-sub { color:#0d9488; }
.kpi-box.violet .kpi-label { color:#c084fc; } .kpi-box.violet .kpi-value { color:#e9d5ff; } .kpi-box.violet .kpi-sub { color:#7c3aed; }
.kpi-box.amber  .kpi-label { color:#fbbf24; } .kpi-box.amber  .kpi-value { color:#fde68a; } .kpi-box.amber  .kpi-sub { color:#d97706; }
.kpi-box.green  .kpi-label { color:#4ade80; } .kpi-box.green  .kpi-value { color:#bbf7d0; } .kpi-box.green  .kpi-sub { color:#16a34a; }
.kpi-box.red    .kpi-label { color:#f87171; } .kpi-box.red    .kpi-value { color:#fecaca; } .kpi-box.red    .kpi-sub { color:#dc2626; }

/* FILTER */
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

/* TABS */
[data-testid="stTabs"] [data-baseweb="tab-list"] { background:#0d1117 !important; border-radius:12px 12px 0 0 !important; border:1px solid #1e2535 !important; border-bottom:none !important; padding:6px 8px 0 !important; gap:4px !important; }
[data-testid="stTabs"] [data-baseweb="tab"] { background:transparent !important; border-radius:8px 8px 0 0 !important; color:#475569 !important; font-size:12px !important; font-weight:700 !important; padding:8px 18px !important; border:none !important; }
[data-testid="stTabs"] [aria-selected="true"] { background:#111827 !important; color:#5bc8c0 !important; border-bottom:2px solid #5bc8c0 !important; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] { background:#0d1117 !important; border:1px solid #1e2535 !important; border-radius:0 0 12px 12px !important; padding:14px !important; }

/* TABLE */
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:8px 0 6px; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }
div[data-testid="stDataFrame"] { border-radius:10px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:10px 0 6px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ── OPEN SO STATUSES ──────────────────────────────────────────────────────────
CLOSED_STATUSES = {"cancelled", "closed"}   # lowercase — everything else = Open

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
def load_sos():
    """Load Sales Order Status sheet (SOS)."""
    df = load_sheet("SOS")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    # Numeric
    for col in ["Order Qty","Dispatch Qty","Rate","Order Value","Total Amount","GST"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    # Dates
    for col in ["Order Date","PO Date","PO Expiry Date","Invoice Date","Last Dispatch Date","Appointment Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

df_fg  = load_fg()
df_sos = load_sos()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📦</div>
        <div>
            <div class="hdr-title">FG Inventory</div>
            <div class="hdr-sub">YogaBar · Finished Goods · CFA Stock vs Open Orders</div>
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

# ── IDENTIFY CFA WAREHOUSES ───────────────────────────────────────────────────
# CFA warehouses = any warehouse name containing "CFA" in FG Inventory
all_fg_wh = df_fg["Warehouse"].dropna().astype(str).unique().tolist() if "Warehouse" in df_fg.columns else []
cfa_warehouses = sorted([w for w in all_fg_wh if "cfa" in w.lower()])

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([2.5, 2, 2, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search SKU / product name…", label_visibility="collapsed")
with c2:
    # CFA filter for FG tab
    fg_wh_opts = ["All Warehouses"] + sorted(all_fg_wh)
    sel_fg_wh  = st.selectbox("fg_wh", fg_wh_opts, label_visibility="collapsed")
with c3:
    cfa_opts = ["All CFAs"] + cfa_warehouses
    sel_cfa  = st.selectbox("cfa", cfa_opts, label_visibility="collapsed")
with c4:
    shelf_opts = ["All Shelf Life","Below 90%","Below 80%","Below 70%","Below 50%"]
    sel_shelf  = st.selectbox("sh", shelf_opts, label_visibility="collapsed")
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

# ── KPI (overall) ─────────────────────────────────────────────────────────────
total_fg_qty   = df["Qty Available"].sum() if "Qty Available" in df.columns else 0
cfa_fg_qty     = df[df["Warehouse"].astype(str).str.contains("cfa", case=False, na=False)]["Qty Available"].sum() if "Warehouse" in df.columns else 0

# Open PO = SO Status NOT in cancelled/closed
open_so_qty = 0
open_so_val = 0
if not df_sos.empty and "SO Status" in df_sos.columns and "Order Qty" in df_sos.columns:
    open_mask  = ~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)
    open_so    = df_sos[open_mask]
    open_so_qty = open_so["Order Qty"].sum()
    open_so_val = open_so["Total Amount"].sum() if "Total Amount" in open_so.columns else 0

net_available = cfa_fg_qty - open_so_qty

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-box teal">
    <div class="kpi-inner">
      <div>
        <div class="kpi-label">Total FG Stock</div>
        <div class="kpi-value">{total_fg_qty:,.0f}</div>
        <div class="kpi-sub">All warehouses · filtered</div>
      </div>
      <div class="kpi-ico">📦</div>
    </div>
  </div>
  <div class="kpi-box violet">
    <div class="kpi-inner">
      <div>
        <div class="kpi-label">CFA Stock</div>
        <div class="kpi-value">{cfa_fg_qty:,.0f}</div>
        <div class="kpi-sub">Stock at CFA warehouses</div>
      </div>
      <div class="kpi-ico">🏭</div>
    </div>
  </div>
  <div class="kpi-box amber">
    <div class="kpi-inner">
      <div>
        <div class="kpi-label">Open PO Qty</div>
        <div class="kpi-value">{open_so_qty:,.0f}</div>
        <div class="kpi-sub">Excl. Cancelled &amp; Closed · ₹{open_so_val:,.0f}</div>
      </div>
      <div class="kpi-ico">📋</div>
    </div>
  </div>
  <div class="kpi-box {'green' if net_available >= 0 else 'red'}">
    <div class="kpi-inner">
      <div>
        <div class="kpi-label">Net Available</div>
        <div class="kpi-value">{net_available:,.0f}</div>
        <div class="kpi-sub">CFA Stock − Open PO Qty</div>
      </div>
      <div class="kpi-ico">{'✅' if net_available >= 0 else '⚠️'}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📦  FG Inventory", "📊  CFA Stock vs Open Orders"])

# ═══ TAB 1 — FG INVENTORY ════════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <div class="tbl-hdr">
        <span class="tbl-lbl">📋 Finished Goods Inventory</span>
        <span class="tbl-badge">{len(df):,} rows</span>
    </div>""", unsafe_allow_html=True)

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
        fg_cols = [c for c in fg_priority if c in df.columns]
        fg_cols += [c for c in df.columns if c not in fg_cols]
        df_show = df[fg_cols].copy()
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

# ═══ TAB 2 — CFA STOCK vs OPEN ORDERS ════════════════════════════════════════
with tab2:
    if df_sos.empty:
        st.warning("⚠️ Sales Order data (SOS sheet) not found.")
        st.stop()

    # ── Step 1: FG stock at CFA warehouses only ───────────────────────────────
    df_cfa_fg = df_fg[df_fg["Warehouse"].astype(str).str.contains("cfa", case=False, na=False)].copy() \
                if "Warehouse" in df_fg.columns else pd.DataFrame()

    if sel_cfa != "All CFAs" and not df_cfa_fg.empty:
        df_cfa_fg = df_cfa_fg[df_cfa_fg["Warehouse"].astype(str) == sel_cfa]

    if search and not df_cfa_fg.empty:
        df_cfa_fg = df_cfa_fg[df_cfa_fg.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]

    # Aggregate FG stock: SKU + CFA Warehouse → total Qty, avg Shelf Life
    if not df_cfa_fg.empty and "Item SKU" in df_cfa_fg.columns:
        fg_cfa_agg = (
            df_cfa_fg
            .groupby(["Item SKU", "Warehouse"], as_index=False)
            .agg(
                Item_Name   =("Item Name",    "first"),
                Category    =("Category",     "first"),
                FG_Stock    =("Qty Available","sum"),
                Shelf_Life  =("Shelf Life %", "mean"),
            )
        )
        fg_cfa_agg.columns = ["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"]
        fg_cfa_agg["Shelf Life %"] = fg_cfa_agg["Shelf Life %"].round(1)
    else:
        fg_cfa_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"])

    # ── Step 2: Open POs from SOS (not Cancelled / Closed) ───────────────────
    sos = df_sos.copy()
    if search and not sos.empty:
        sos = sos[sos.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]

    # Filter open orders only
    open_mask = ~sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES) \
                if "SO Status" in sos.columns else pd.Series([True] * len(sos))
    sos_open = sos[open_mask].copy()

    # Aggregate open PO: SKU + Warehouse → total Open Order Qty, count of orders
    sku_col_so = next((c for c in sos_open.columns if "product sku" in c.lower() or c.lower() == "sku"), None)
    wh_col_so  = next((c for c in sos_open.columns if c.lower() == "warehouse"), None)
    qty_col_so = next((c for c in sos_open.columns if "order qty" in c.lower()), None)
    val_col_so = next((c for c in sos_open.columns if "total amount" in c.lower()), None)

    if sku_col_so and wh_col_so and qty_col_so and not sos_open.empty:
        sos_open["_sku"] = sos_open[sku_col_so].astype(str).str.strip()
        sos_open["_wh"]  = sos_open[wh_col_so].astype(str).str.strip()

        # Apply CFA filter on SOS side too
        if sel_cfa != "All CFAs":
            sos_open = sos_open[sos_open["_wh"] == sel_cfa]

        agg_cols = {"Open PO Qty": (qty_col_so, "sum"), "Open Orders": (qty_col_so, "count")}
        if val_col_so:
            agg_cols["Open PO Value"] = (val_col_so, "sum")

        so_agg = sos_open.groupby(["_sku","_wh"]).agg(**{k: v for k, v in agg_cols.items()}).reset_index()
        so_agg.columns = ["Item SKU","CFA Warehouse"] + list(agg_cols.keys())
    else:
        so_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Open PO Qty","Open Orders"])

    # ── Step 3: Join FG CFA stock with Open POs on (SKU + CFA Warehouse) ─────
    if not fg_cfa_agg.empty and not so_agg.empty:
        merged = fg_cfa_agg.merge(so_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    elif not fg_cfa_agg.empty:
        merged = fg_cfa_agg.copy()
        merged["Open PO Qty"]   = 0
        merged["Open Orders"]   = 0
        if "Open PO Value" not in merged.columns:
            merged["Open PO Value"] = 0.0
    elif not so_agg.empty:
        merged = so_agg.copy()
        merged["Item Name"]   = ""
        merged["Category"]    = ""
        merged["FG Stock"]    = 0
        merged["Shelf Life %"]= 0.0
    else:
        merged = pd.DataFrame()

    if not merged.empty:
        merged["FG Stock"]      = merged["FG Stock"].fillna(0)
        merged["Open PO Qty"]   = merged["Open PO Qty"].fillna(0)
        merged["Open Orders"]   = merged["Open Orders"].fillna(0).astype(int)
        merged["Net Available"] = merged["FG Stock"] - merged["Open PO Qty"]
        merged["Shelf Life %"]  = merged.get("Shelf Life %", pd.Series(0.0, index=merged.index)).fillna(0.0)
        if "Open PO Value" in merged.columns:
            merged["Open PO Value"] = merged["Open PO Value"].fillna(0)

        # Sort: shortfall first, then by CFA Warehouse
        merged = merged.sort_values(["Net Available","CFA Warehouse"], ascending=[True, True])

        # Display columns
        disp_cols = ["Item Name","Item SKU","Category","CFA Warehouse",
                     "FG Stock","Shelf Life %","Open PO Qty","Open Orders","Net Available"]
        if "Open PO Value" in merged.columns:
            disp_cols.append("Open PO Value")
        disp_cols = [c for c in disp_cols if c in merged.columns]
        df_disp = merged[disp_cols].copy()

        # ── Summary KPIs for tab ──────────────────────────────────────────────
        total_cfa_stock  = df_disp["FG Stock"].sum()
        total_open_po    = df_disp["Open PO Qty"].sum()
        total_net        = df_disp["Net Available"].sum()
        shortfall_skus   = int((df_disp["Net Available"] < 0).sum())

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("CFA Total Stock",  f"{total_cfa_stock:,.0f}")
        s2.metric("Open PO Qty",      f"{total_open_po:,.0f}")
        s3.metric("Net Available",    f"{total_net:,.0f}")
        s4.metric("Shortfall SKUs",   str(shortfall_skus), delta=f"-{shortfall_skus}" if shortfall_skus else "0", delta_color="inverse")

        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-div">CFA Warehouse · SKU · Stock vs Open Orders</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="tbl-hdr">
            <span class="tbl-lbl">📊 Stock vs Open PO by SKU &amp; CFA</span>
            <span class="tbl-badge">{len(df_disp):,} rows</span>
        </div>""", unsafe_allow_html=True)

        # Export
        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as w:
            df_disp.to_excel(w, index=False, sheet_name="CFA Stock vs PO")
        st.download_button("⬇  Export to Excel", buf2.getvalue(), "CFA_Stock_vs_OpenPO.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

        # Row colour: red = shortfall, amber = low (<20%), green = healthy
        def colour_row(row):
            net = row.get("Net Available", 0)
            if pd.isna(net): return [""] * len(row)
            if net < 0:   return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
            stock = row.get("FG Stock", 1)
            if stock > 0 and (net / stock) < 0.2:
                return ["background-color:#2d1f00; color:#fde68a"] * len(row)
            return ["background-color:#061410; color:#d1fae5"] * len(row)

        col_cfg = {
            "FG Stock":      st.column_config.NumberColumn("FG Stock",       format="%.0f"),
            "Shelf Life %":  st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
            "Open PO Qty":   st.column_config.NumberColumn("Open PO Qty",    format="%.0f"),
            "Open Orders":   st.column_config.NumberColumn("# Orders",       format="%d"),
            "Net Available": st.column_config.NumberColumn("Net Available ✅", format="%.0f"),
        }
        if "Open PO Value" in df_disp.columns:
            col_cfg["Open PO Value"] = st.column_config.NumberColumn("Open PO Value (₹)", format="%.0f")

        st.dataframe(
            df_disp.style.apply(colour_row, axis=1),
            use_container_width=True, height=560, hide_index=True,
            column_config=col_cfg
        )

        # ── Per-CFA expander breakdown ────────────────────────────────────────
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-div">Breakdown by CFA Warehouse</div>', unsafe_allow_html=True)
        for cfa_wh in sorted(df_disp["CFA Warehouse"].dropna().unique()):
            cfa_data = df_disp[df_disp["CFA Warehouse"] == cfa_wh].copy()
            cfa_stock   = cfa_data["FG Stock"].sum()
            cfa_open    = cfa_data["Open PO Qty"].sum()
            cfa_net     = cfa_data["Net Available"].sum()
            cfa_short   = int((cfa_data["Net Available"] < 0).sum())
            with st.expander(f"🏭  {cfa_wh}   ·   Stock: {cfa_stock:,.0f}   ·   Open PO: {cfa_open:,.0f}   ·   Net: {cfa_net:,.0f}   {'⚠️ '+str(cfa_short)+' shortfall' if cfa_short else '✅'}"):
                st.dataframe(
                    cfa_data.style.apply(colour_row, axis=1),
                    use_container_width=True,
                    height=min(60 + len(cfa_data) * 36, 400),
                    hide_index=True,
                    column_config=col_cfg
                )
    else:
        st.warning("⚠️ No CFA stock or open order data found. Check that FG Inventory has warehouses containing 'CFA' in the name and SOS sheet has data.")

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · CFA STOCK vs OPEN ORDERS</div>', unsafe_allow_html=True)
