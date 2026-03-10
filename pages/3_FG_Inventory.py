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
def load_all():
    # ── FG Inventory ──────────────────────────────────────────────────────────
    df_fg = load_sheet("FG-Inventory")
    if df_fg.empty:
        return pd.DataFrame()
    df_fg.columns = df_fg.columns.str.strip()

    # Numeric
    if "Qty Available" in df_fg.columns:
        df_fg["Qty Available"] = pd.to_numeric(df_fg["Qty Available"], errors="coerce").fillna(0)

    # Shelf life %
    today = pd.Timestamp(datetime.today().date())
    for col in ["Expiry Date", "MFG Date"]:
        if col in df_fg.columns:
            df_fg[col] = pd.to_datetime(df_fg[col], errors="coerce")
    if "Expiry Date" in df_fg.columns and "MFG Date" in df_fg.columns:
        rem   = (df_fg["Expiry Date"] - today).dt.days
        total = (df_fg["Expiry Date"] - df_fg["MFG Date"]).dt.days
        valid = total > 0
        pct   = pd.Series(0.0, index=df_fg.index)
        pct[valid] = ((rem[valid] / total[valid]) * 100).clip(0, 100)
        df_fg["Shelf Life %"] = pct.round(1)
    else:
        df_fg["Shelf Life %"] = 0.0

    # ── STN — latest transfer per FG SKU ─────────────────────────────────────
    df_stn = load_sheet("STN")
    if not df_stn.empty:
        df_stn.columns = df_stn.columns.str.strip()
        if "Date" in df_stn.columns:
            df_stn["Date"] = pd.to_datetime(df_stn["Date"], errors="coerce")
        if "Qty" in df_stn.columns:
            df_stn["Qty"] = pd.to_numeric(df_stn["Qty"], errors="coerce").fillna(0)

        fg_code_col = next((c for c in df_stn.columns if "fg code" in c.lower()), None)
        to_wh_col   = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        req_col     = next((c for c in df_stn.columns if "request no" in c.lower()), None)

        if fg_code_col:
            df_stn[fg_code_col] = df_stn[fg_code_col].astype(str).str.strip()
            # Latest transfer per SKU
            if "Date" in df_stn.columns:
                df_stn = df_stn.sort_values("Date", ascending=False)
            df_stn_latest = df_stn.drop_duplicates(subset=[fg_code_col]).copy()

            # Rename to STN columns
            rmap = {fg_code_col: "_stn_sku"}
            if req_col:    rmap[req_col]    = "STN No"
            if "Date" in df_stn_latest.columns: rmap["Date"] = "STN Date"
            if to_wh_col:  rmap[to_wh_col]  = "STN WH"
            if "Qty" in df_stn_latest.columns:  rmap["Qty"]  = "STN Qty"
            if "Status" in df_stn_latest.columns: rmap["Status"] = "STN Status"
            df_stn_latest = df_stn_latest.rename(columns=rmap)

            keep = ["_stn_sku"] + [c for c in ["STN No","STN Date","STN WH","STN Qty","STN Status"] if c in df_stn_latest.columns]
            df_stn_latest = df_stn_latest[keep]

            # Merge on Item SKU
            sku_col = next((c for c in df_fg.columns if "item sku" in c.lower() or c.lower() == "sku"), None)
            if sku_col:
                df_fg[sku_col] = df_fg[sku_col].astype(str).str.strip()
                df_fg = df_fg.merge(df_stn_latest, left_on=sku_col, right_on="_stn_sku", how="left")
                df_fg.drop(columns=["_stn_sku"], errors="ignore", inplace=True)

    return df_fg

df_raw = load_all()

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

if df_raw.empty:
    st.error("⚠️ No FG data found.")
    st.stop()

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2.5, 1.8, 1.8, 1.8, 1.8])

with c1:
    search = st.text_input("s", placeholder="🔍 Search item name / SKU…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().astype(str).unique().tolist()) if "Warehouse" in df_raw.columns else ["All Warehouses"]
    sel_wh = st.selectbox("fw", wh_opts, label_visibility="collapsed")
with c3:
    stn_wh_opts = ["All STN WH"]
    if "STN WH" in df_raw.columns:
        stn_wh_opts += sorted(df_raw["STN WH"].dropna().astype(str).unique().tolist())
    sel_stn_wh = st.selectbox("sw", stn_wh_opts, label_visibility="collapsed")
with c4:
    stat_opts = ["All Status"]
    if "STN Status" in df_raw.columns:
        stat_opts += sorted(df_raw["STN Status"].dropna().astype(str).unique().tolist())
    sel_stat = st.selectbox("ss", stat_opts, label_visibility="collapsed")
with c5:
    shelf_opts = [
        "All Shelf Life",
        "Below 90%",
        "Below 80%",
        "Below 70%",
        "Below 50%",
    ]
    sel_shelf = st.selectbox("sh", shelf_opts, label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_wh]
if sel_stn_wh != "All STN WH" and "STN WH" in df.columns:
    df = df[df["STN WH"].astype(str) == sel_stn_wh]
if sel_stat != "All Status" and "STN Status" in df.columns:
    df = df[df["STN Status"].astype(str) == sel_stat]
if "Shelf Life %" in df.columns:
    shelf_map = {"Below 90%": 90, "Below 80%": 80, "Below 70%": 70, "Below 50%": 50}
    if sel_shelf in shelf_map:
        df = df[df["Shelf Life %"] < shelf_map[sel_shelf]]

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">FG Records + STN Transfer</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 FG Inventory</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="FG Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "FG_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    # Build display with only required columns
    item_name_col = next((c for c in df.columns if "item name" in c.lower()), None)
    item_sku_col  = next((c for c in df.columns if "item sku"  in c.lower() or c.lower() == "sku"), None)
    cat_col       = next((c for c in df.columns if "category"  in c.lower()), None)
    wh_col        = "Warehouse" if "Warehouse" in df.columns else None

    ordered_cols = []
    for c in [item_name_col, item_sku_col, cat_col, wh_col,
              "Qty Available", "Shelf Life %",
              "STN No", "STN Qty", "STN WH", "STN Status", "STN Date"]:
        if c and c in df.columns:
            ordered_cols.append(c)

    disp = df[ordered_cols].copy() if ordered_cols else df.copy()

    # Format STN Date
    if "STN Date" in disp.columns:
        disp["STN Date"] = pd.to_datetime(disp["STN Date"], errors="coerce").dt.strftime("%d-%b-%Y").fillna("-")

    # ── Single standard colour — no shelf-life-based row colouring ──
    # (colour_row function removed; no .style.apply() used)

    # Rename for clean display
    rename = {}
    if item_name_col: rename[item_name_col] = "Item Name"
    if item_sku_col:  rename[item_sku_col]  = "Item SKU"
    if cat_col:       rename[cat_col]        = "Category"
    disp = disp.rename(columns=rename)

    st.dataframe(
        disp,                          # plain DataFrame — no colour styling
        use_container_width=True, height=560, hide_index=True,
        column_config={
            "Qty Available": st.column_config.NumberColumn("Qty Available", format="%.0f"),
            "Shelf Life %":  st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
            "STN Qty":       st.column_config.NumberColumn("STN Qty",       format="%.0f"),
        }
    )

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · STN</div>', unsafe_allow_html=True)
