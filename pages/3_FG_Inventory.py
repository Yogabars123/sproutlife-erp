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
.kpi-box { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:16px 18px; }
.kpi-box-label { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:6px; }
.kpi-box-value { font-size:26px; font-weight:800; font-family:'JetBrains Mono',monospace; color:#e2e8f0; }
.kpi-box-sub   { font-size:11px; color:#334155; margin-top:4px; }
.kpi-box.teal  { border-color:#134e4a; } .kpi-box.teal  .kpi-box-value { color:#99f6e4; }
.kpi-box.blue  { border-color:#1e3a5f; } .kpi-box.blue  .kpi-box-value { color:#93c5fd; }
.kpi-box.amber { border-color:#78350f; } .kpi-box.amber .kpi-box-value { color:#fde68a; }
.kpi-box.red   { border-color:#7f1d1d; } .kpi-box.red   .kpi-box-value { color:#fca5a5; }

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
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:10px 0 6px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
div[data-testid="stDataFrame"] { border-radius:10px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_fg():
    df = load_sheet("FG-Inventory")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    if "Qty Available" in df.columns:
        df["Qty Available"] = pd.to_numeric(df["Qty Available"], errors="coerce").fillna(0)
    today = pd.Timestamp(datetime.today().date())
    for col in ["Expiry Date", "MFG Date"]:
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

df_fg  = load_fg()
df_stn = load_stn()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📦</div>
        <div>
            <div class="hdr-title">FG Inventory</div>
            <div class="hdr-sub">YogaBar · Finished Goods + STN Transfer</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if df_fg.empty:
    st.error("⚠️ No FG data found.")
    st.stop()

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2.5, 1.8, 1.8, 1.8, 1.8])
with c1:
    search = st.text_input("s", placeholder="🔍 Search item name / SKU…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_fg["Warehouse"].dropna().astype(str).unique().tolist()) if "Warehouse" in df_fg.columns else ["All Warehouses"]
    sel_wh = st.selectbox("fw", wh_opts, label_visibility="collapsed")
with c3:
    stn_wh_col = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None) if not df_stn.empty else None
    stn_wh_opts = ["All STN WH"]
    if stn_wh_col and not df_stn.empty:
        stn_wh_opts += sorted(df_stn[stn_wh_col].dropna().astype(str).unique().tolist())
    sel_stn_wh = st.selectbox("sw", stn_wh_opts, label_visibility="collapsed")
with c4:
    stat_col = next((c for c in df_stn.columns if "status" in c.lower()), None) if not df_stn.empty else None
    stat_opts = ["All Status"]
    if stat_col and not df_stn.empty:
        stat_opts += sorted(df_stn[stat_col].dropna().astype(str).unique().tolist())
    sel_stat = st.selectbox("ss", stat_opts, label_visibility="collapsed")
with c5:
    shelf_opts = ["All Shelf Life","Below 90%","Below 80%","Below 70%","Below 50%"]
    sel_shelf  = st.selectbox("sh", shelf_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS TO FG ───────────────────────────────────────────────────────
df = df_fg.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_wh]
if "Shelf Life %" in df.columns:
    shelf_map = {"Below 90%": 90, "Below 80%": 80, "Below 70%": 70, "Below 50%": 50}
    if sel_shelf in shelf_map:
        df = df[df["Shelf Life %"] < shelf_map[sel_shelf]]

# ── APPLY FILTERS TO STN ─────────────────────────────────────────────────────
df_stn_f = df_stn.copy() if not df_stn.empty else pd.DataFrame()
if not df_stn_f.empty:
    fg_code_col = next((c for c in df_stn_f.columns if "fg code" in c.lower()), None)
    req_col     = next((c for c in df_stn_f.columns if "request no" in c.lower()), None)
    to_wh_col   = next((c for c in df_stn_f.columns if "to warehouse" in c.lower()), None)
    stat_col    = next((c for c in df_stn_f.columns if "status" in c.lower()), None)

    # Filter STN by search (match on FG code / name if possible)
    if search and fg_code_col:
        df_stn_f = df_stn_f[df_stn_f.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    if sel_stn_wh != "All STN WH" and to_wh_col:
        df_stn_f = df_stn_f[df_stn_f[to_wh_col].astype(str) == sel_stn_wh]
    if sel_stat != "All Status" and stat_col:
        df_stn_f = df_stn_f[df_stn_f[stat_col].astype(str) == sel_stat]

# ── KPI CARDS ────────────────────────────────────────────────────────────────
total_qty    = df["Qty Available"].sum() if "Qty Available" in df.columns else 0
total_skus   = df["Item SKU"].nunique() if "Item SKU" in df.columns else 0
low_shelf    = int((df["Shelf Life %"] < 50).sum()) if "Shelf Life %" in df.columns else 0
stn_total    = int(df_stn_f["Qty"].sum()) if not df_stn_f.empty and "Qty" in df_stn_f.columns else 0

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-box teal">
    <div class="kpi-box-label">Total Qty Available</div>
    <div class="kpi-box-value">{total_qty:,.0f}</div>
    <div class="kpi-box-sub">Across filtered warehouses</div>
  </div>
  <div class="kpi-box blue">
    <div class="kpi-box-label">Unique SKUs</div>
    <div class="kpi-box-value">{total_skus:,}</div>
    <div class="kpi-box-sub">In current filter</div>
  </div>
  <div class="kpi-box red">
    <div class="kpi-box-label">Low Shelf Life (&lt;50%)</div>
    <div class="kpi-box-value">{low_shelf:,}</div>
    <div class="kpi-box-sub">Rows needing attention</div>
  </div>
  <div class="kpi-box amber">
    <div class="kpi-box-label">STN Transfer Qty</div>
    <div class="kpi-box-value">{stn_total:,}</div>
    <div class="kpi-box-sub">Filtered STN records</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS: FG Inventory | STN Transfers ───────────────────────────────────────
tab1, tab2 = st.tabs(["📦  FG Inventory", "🚚  STN Transfers"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FG INVENTORY (clean, no STN columns mixed in)
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <div class="tbl-hdr">
        <span class="tbl-lbl">📋 Finished Goods Inventory</span>
        <span class="tbl-badge">{len(df):,} rows</span>
    </div>""", unsafe_allow_html=True)

    # Export
    buf1 = io.BytesIO()
    with pd.ExcelWriter(buf1, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="FG Inventory")
    st.download_button("⬇  Export FG to Excel", buf1.getvalue(), "FG_Inventory.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ No FG records match the current filters.")
    else:
        # Only FG columns — no STN columns at all
        fg_priority = ["Item Name","Item SKU","Category","Warehouse",
                       "Qty Available","Shelf Life %","MFG Date","Expiry Date",
                       "Batch No","UoM","Value (Inc Tax)","Value (Ex Tax)"]
        fg_cols = [c for c in fg_priority if c in df.columns]
        fg_cols += [c for c in df.columns if c not in fg_cols and not c.startswith("STN")]
        df_show = df[fg_cols].copy()

        for c in ["MFG Date","Expiry Date"]:
            if c in df_show.columns:
                df_show[c] = pd.to_datetime(df_show[c], errors="coerce").dt.strftime("%d-%b-%Y").fillna("-")

        def shelf_colour(row):
            sl = row.get("Shelf Life %", 100)
            if pd.isna(sl): return [""] * len(row)
            if sl < 50:  return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
            if sl < 70:  return ["background-color:#2d1f00; color:#fde68a"] * len(row)
            if sl < 90:  return ["background-color:#0d1a00; color:#d9f99d"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_show.style.apply(shelf_colour, axis=1),
            use_container_width=True, height=520, hide_index=True,
            column_config={
                "Qty Available": st.column_config.NumberColumn("Qty Available", format="%.0f"),
                "Shelf Life %":  st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
                "Value (Inc Tax)": st.column_config.NumberColumn("Val (Inc)", format="%.0f"),
                "Value (Ex Tax)":  st.column_config.NumberColumn("Val (Ex)",  format="%.0f"),
            }
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — STN TRANSFERS (clean dedicated table)
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    if df_stn_f.empty:
        st.warning("⚠️ No STN data found or no records match the current filters.")
    else:
        st.markdown(f"""
        <div class="tbl-hdr">
            <span class="tbl-lbl">🚚 STN Transfer Records</span>
            <span class="tbl-badge">{len(df_stn_f):,} rows</span>
        </div>""", unsafe_allow_html=True)

        # Export
        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as w:
            df_stn_f.to_excel(w, index=False, sheet_name="STN Transfers")
        st.download_button("⬇  Export STN to Excel", buf2.getvalue(), "STN_Transfers.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

        # Format date
        df_stn_disp = df_stn_f.copy()
        if "Date" in df_stn_disp.columns:
            df_stn_disp["Date"] = pd.to_datetime(df_stn_disp["Date"], errors="coerce").dt.strftime("%d-%b-%Y").fillna("-")

        # Clean column config
        col_cfg = {}
        if "Qty" in df_stn_disp.columns:
            col_cfg["Qty"] = st.column_config.NumberColumn("Qty", format="%.0f")

        # Status badge colour
        def stn_colour(row):
            s = str(row.get("Status", "")).lower() if "Status" in row.index else ""
            if "pending"   in s: return ["background-color:#1a1500; color:#fde68a"] * len(row)
            if "approved"  in s or "complete" in s: return ["background-color:#061410; color:#99f6e4"] * len(row)
            if "reject"    in s or "cancel" in s:   return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_stn_disp.style.apply(stn_colour, axis=1),
            use_container_width=True, height=520, hide_index=True,
            column_config=col_cfg
        )

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · STN</div>', unsafe_allow_html=True)
