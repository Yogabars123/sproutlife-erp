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
.kpi-row { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; margin-bottom:16px; }
.kpi-box { border-radius:16px; padding:20px 24px; border:1px solid; position:relative; overflow:hidden; }
.kpi-box::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-box.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-box.teal::before  { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-box.violet { background:linear-gradient(135deg,#130a2a,#1e0f40); border-color:#3b1f6e; }
.kpi-box.violet::before { background:linear-gradient(90deg,#a855f7,#818cf8); }
.kpi-inner { display:flex; align-items:flex-start; justify-content:space-between; }
.kpi-label { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:8px; }
.kpi-value { font-size:34px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-sub   { font-size:11px; margin-top:6px; }
.kpi-ico   { font-size:28px; opacity:.6; margin-top:2px; }
.kpi-box.teal   .kpi-label { color:#5bc8c0; } .kpi-box.teal   .kpi-value { color:#99f6e4; } .kpi-box.teal   .kpi-sub { color:#0d9488; }
.kpi-box.violet .kpi-label { color:#c084fc; } .kpi-box.violet .kpi-value { color:#e9d5ff; } .kpi-box.violet .kpi-sub { color:#7c3aed; }
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
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

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

# ── DEBUG (remove after confirming data loads) ────────────────────────────────
with st.expander("🔍 Debug — click to inspect column names", expanded=False):
    st.write("**FG columns:**", list(df_fg.columns))
    st.write("**STN columns:**", list(df_stn.columns) if not df_stn.empty else "STN empty")
    if not df_stn.empty:
        st.write("**STN sample (3 rows):**")
        st.dataframe(df_stn.head(3))

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
    stn_to_wh_opts = ["All STN WH"]
    if not df_stn.empty and "To Warehouse" in df_stn.columns:
        stn_to_wh_opts += sorted(df_stn["To Warehouse"].dropna().astype(str).unique().tolist())
    sel_stn_wh = st.selectbox("sw", stn_to_wh_opts, label_visibility="collapsed")
with c4:
    stat_opts = ["All Status"]
    if not df_stn.empty and "Status" in df_stn.columns:
        stat_opts += sorted(df_stn["Status"].dropna().astype(str).unique().tolist())
    sel_stat = st.selectbox("ss", stat_opts, label_visibility="collapsed")
with c5:
    shelf_opts = ["All Shelf Life","Below 90%","Below 80%","Below 70%","Below 50%"]
    sel_shelf  = st.selectbox("sh", shelf_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_fg.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_wh]
shelf_map = {"Below 90%": 90, "Below 80%": 80, "Below 70%": 70, "Below 50%": 50}
if sel_shelf in shelf_map and "Shelf Life %" in df.columns:
    df = df[df["Shelf Life %"] < shelf_map[sel_shelf]]

df_stn_f = df_stn.copy() if not df_stn.empty else pd.DataFrame()
if not df_stn_f.empty:
    if search:
        df_stn_f = df_stn_f[df_stn_f.astype(str).apply(
            lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    if sel_stn_wh != "All STN WH" and "To Warehouse" in df_stn_f.columns:
        df_stn_f = df_stn_f[df_stn_f["To Warehouse"].astype(str) == sel_stn_wh]
    if sel_stat != "All Status" and "Status" in df_stn_f.columns:
        df_stn_f = df_stn_f[df_stn_f["Status"].astype(str) == sel_stat]

# ── KPI ───────────────────────────────────────────────────────────────────────
total_qty  = df["Qty Available"].sum() if "Qty Available" in df.columns else 0
stn_raised = df_stn_f["Qty"].sum() if not df_stn_f.empty and "Qty" in df_stn_f.columns else 0

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-box teal">
    <div class="kpi-inner">
      <div>
        <div class="kpi-label">Total Qty Available</div>
        <div class="kpi-value">{total_qty:,.0f}</div>
        <div class="kpi-sub">Across filtered warehouses</div>
      </div>
      <div class="kpi-ico">📦</div>
    </div>
  </div>
  <div class="kpi-box violet">
    <div class="kpi-inner">
      <div>
        <div class="kpi-label">STN Qty Raised</div>
        <div class="kpi-value">{stn_raised:,.0f}</div>
        <div class="kpi-sub">Total quantity raised via STN transfers</div>
      </div>
      <div class="kpi-ico">🚚</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── BUILD STN VIEW ────────────────────────────────────────────────────────────
def build_stn_view(stn_df, fg_df):
    if stn_df.empty:
        return pd.DataFrame()

    stn = stn_df.copy()

    # Auto-detect the FG code column in STN sheet
    # Possible names: "FG Code", "Item Code", "SKU", "Item SKU" etc.
    fg_code_col = None
    for candidate in ["FG Code","Item Code","Item SKU","SKU","fg code","item code"]:
        if candidate in stn.columns:
            fg_code_col = candidate
            break
    # Fallback: any column with "code" or "sku" in name
    if fg_code_col is None:
        for col in stn.columns:
            if "code" in col.lower() or "sku" in col.lower():
                fg_code_col = col
                break

    # Auto-detect Request No column
    req_col = next((c for c in stn.columns if "request" in c.lower()), None)
    to_wh_col = next((c for c in stn.columns if "to warehouse" in c.lower() or c.lower() == "to wh"), None)
    from_wh_col = next((c for c in stn.columns if "from warehouse" in c.lower() or c.lower() == "from wh"), None)
    stat_col = next((c for c in stn.columns if c.lower() == "status"), None)
    date_col = next((c for c in stn.columns if c.lower() == "date"), None)
    qty_col  = next((c for c in stn.columns if c.lower() == "qty"), None)
    fg_name_col = next((c for c in stn.columns if "fg name" in c.lower() or "item name" in c.lower()), None)
    fg_cat_col  = next((c for c in stn.columns if "fg category" in c.lower() or ("category" in c.lower() and "fg" in c.lower())), None)

    # Build FG lookup: Item SKU → Item Name, Category, Warehouse, total Qty, avg Shelf Life
    if not fg_df.empty and "Item SKU" in fg_df.columns and "Qty Available" in fg_df.columns:
        fg_grp = fg_df.copy()
        fg_grp["_sku_key"] = fg_grp["Item SKU"].astype(str).str.strip().str.upper()

        # Simple groupby without named agg (most compatible)
        fg_qty   = fg_grp.groupby("_sku_key")["Qty Available"].sum().reset_index()
        fg_shelf = fg_grp.groupby("_sku_key")["Shelf Life %"].mean().reset_index() if "Shelf Life %" in fg_grp.columns else None
        fg_first = fg_grp.drop_duplicates("_sku_key")[["_sku_key"] +
                   [c for c in ["Item Name","Category","Warehouse"] if c in fg_grp.columns]]

        fg_lookup = fg_first.merge(fg_qty, on="_sku_key", how="left")
        if fg_shelf is not None:
            fg_lookup = fg_lookup.merge(fg_shelf, on="_sku_key", how="left")
        else:
            fg_lookup["Shelf Life %"] = 0.0
    else:
        fg_lookup = pd.DataFrame(columns=["_sku_key","Item Name","Category","Warehouse","Qty Available","Shelf Life %"])

    # Create join key on STN
    if fg_code_col:
        stn["_sku_key"] = stn[fg_code_col].astype(str).str.strip().str.upper()
    else:
        stn["_sku_key"] = ""

    # Merge
    stn = stn.merge(fg_lookup, on="_sku_key", how="left")

    # Fallbacks from STN sheet's own columns
    if fg_name_col and "Item Name" in stn.columns:
        stn["Item Name"] = stn["Item Name"].fillna(stn[fg_name_col])
    elif fg_name_col:
        stn["Item Name"] = stn[fg_name_col]

    if fg_cat_col and "Category" in stn.columns:
        stn["Category"] = stn["Category"].fillna(stn[fg_cat_col])
    elif fg_cat_col:
        stn["Category"] = stn[fg_cat_col]

    if "Item Name"     not in stn.columns: stn["Item Name"]     = ""
    if "Category"      not in stn.columns: stn["Category"]      = ""
    if "Warehouse"     not in stn.columns: stn["Warehouse"]     = ""
    if "Qty Available" not in stn.columns: stn["Qty Available"] = 0
    if "Shelf Life %"  not in stn.columns: stn["Shelf Life %"]  = 0.0

    stn["Item SKU"] = stn["_sku_key"]

    # Rename STN operational columns
    rename_map = {}
    if req_col:     rename_map[req_col]     = "STN No"
    if qty_col:     rename_map[qty_col]     = "STN Quantity"
    if to_wh_col:   rename_map[to_wh_col]   = "STN WH"
    if stat_col:    rename_map[stat_col]    = "STN Status"
    if date_col:    rename_map[date_col]    = "STN Date"
    if from_wh_col: rename_map[from_wh_col] = "From WH"
    stn = stn.rename(columns=rename_map)

    wanted = ["Item Name","Item SKU","Category","Warehouse",
              "Qty Available","Shelf Life %",
              "STN No","STN Quantity","STN WH","STN Status","STN Date","From WH"]
    return stn[[c for c in wanted if c in stn.columns]].copy()


df_stn_view = build_stn_view(df_stn_f, df_fg)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📦  FG Inventory", "🚚  STN Transfers"])

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

with tab2:
    if df_stn_view.empty:
        st.warning("⚠️ No STN data found or no records match filters.")
        # Show raw STN for debugging
        if not df_stn_f.empty:
            st.info(f"Raw STN has {len(df_stn_f)} rows. Showing raw data below:")
            st.dataframe(df_stn_f.head(20), use_container_width=True, height=300)
    else:
        st.markdown(f"""
        <div class="tbl-hdr">
            <span class="tbl-lbl">🚚 STN Transfer Records</span>
            <span class="tbl-badge">{len(df_stn_view):,} rows</span>
        </div>""", unsafe_allow_html=True)

        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as w:
            df_stn_view.to_excel(w, index=False, sheet_name="STN Transfers")
        st.download_button("⬇  Export STN to Excel", buf2.getvalue(), "STN_Transfers.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

        df_stn_disp = df_stn_view.copy()
        if "STN Date" in df_stn_disp.columns:
            df_stn_disp["STN Date"] = (
                pd.to_datetime(df_stn_disp["STN Date"], errors="coerce")
                .dt.strftime("%d-%b-%Y").fillna("-")
            )

        st.dataframe(df_stn_disp, use_container_width=True, height=540, hide_index=True,
            column_config={
                "Qty Available": st.column_config.NumberColumn("Qty Available", format="%.0f"),
                "Shelf Life %":  st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
                "STN Quantity":  st.column_config.NumberColumn("STN Quantity",  format="%.0f"),
            })

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · STN</div>', unsafe_allow_html=True)
