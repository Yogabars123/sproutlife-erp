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
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.kpi-card { border-radius:16px; padding:16px 18px; position:relative; overflow:hidden; border:1px solid; min-height:100px; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-card.blue   { background:linear-gradient(135deg,#0c1a3a,#0f2460); border-color:#1a3a6e; }
.kpi-card.blue::before   { background:linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-card.amber  { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.red    { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-card.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before   { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-lbl { font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.kpi-card.blue  .kpi-lbl { color:#60a5fa; } .kpi-card.amber .kpi-lbl { color:#fbbf24; }
.kpi-card.red   .kpi-lbl { color:#f87171; } .kpi-card.teal  .kpi-lbl { color:#5bc8c0; }
.kpi-num { font-size:28px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-card.blue  .kpi-num { color:#bfdbfe; } .kpi-card.amber .kpi-num { color:#fde68a; }
.kpi-card.red   .kpi-num { color:#fecaca; } .kpi-card.teal  .kpi-num { color:#99f6e4; }
.kpi-cap { font-size:11px; margin-top:5px; }
.kpi-card.blue  .kpi-cap { color:#3b5a8a; } .kpi-card.amber .kpi-cap { color:#78540a; }
.kpi-card.red   .kpi-cap { color:#7a2020; } .kpi-card.teal  .kpi-cap { color:#134e4a; }
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
    # FG Inventory
    df_fg = load_sheet("FG-Inventory")
    if df_fg.empty:
        return pd.DataFrame()
    df_fg.columns = df_fg.columns.str.strip()
    df_fg["Warehouse"] = df_fg["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df_fg.columns:
            df_fg[col] = pd.to_datetime(df_fg[col], errors="coerce")
    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)", "Current Aging (Days)"]:
        if col in df_fg.columns:
            df_fg[col] = pd.to_numeric(df_fg[col], errors="coerce").fillna(0)

    # Shelf life %
    today = pd.Timestamp(datetime.today().date())
    if "Expiry Date" in df_fg.columns:
        rem = (df_fg["Expiry Date"] - today).dt.days
        df_fg["_remaining_days"] = rem.fillna(0).astype(int)
        if "MFG Date" in df_fg.columns:
            total = (df_fg["Expiry Date"] - df_fg["MFG Date"]).dt.days
            valid = total > 0
            pct = pd.Series(0.0, index=df_fg.index)
            pct[valid] = ((rem[valid] / total[valid]) * 100).clip(0, 100)
            df_fg["Shelf Life %"] = pct.round(1)
        else:
            df_fg["Shelf Life %"] = 0.0
    else:
        df_fg["_remaining_days"] = 0
        df_fg["Shelf Life %"] = 0.0

    # STN - aggregate latest transfer per Item SKU
    df_stn = load_sheet("STN")
    if not df_stn.empty:
        df_stn.columns = df_stn.columns.str.strip()
        # Parse date
        if "Date" in df_stn.columns:
            df_stn["Date"] = pd.to_datetime(df_stn["Date"], errors="coerce")
        if "Qty" in df_stn.columns:
            df_stn["Qty"] = pd.to_numeric(df_stn["Qty"], errors="coerce").fillna(0)

        # Find FG Code column
        fg_code_col = next((c for c in df_stn.columns if "fg code" in c.lower()), None)
        to_wh_col   = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        req_col     = next((c for c in df_stn.columns if "request no" in c.lower()), None)

        if fg_code_col:
            df_stn[fg_code_col] = df_stn[fg_code_col].astype(str).str.strip()
            # Get latest STN per FG Code
            if "Date" in df_stn.columns:
                df_stn_latest = df_stn.sort_values("Date", ascending=False).drop_duplicates(subset=[fg_code_col])
            else:
                df_stn_latest = df_stn.drop_duplicates(subset=[fg_code_col])

            rename_map = {}
            if fg_code_col: rename_map[fg_code_col] = "_stn_sku"
            if to_wh_col:   rename_map[to_wh_col]   = "STN WH"
            if req_col:     rename_map[req_col]      = "STN No"
            if "Date" in df_stn_latest.columns: rename_map["Date"] = "STN Date"
            if "Status" in df_stn_latest.columns: rename_map["Status"] = "STN Status"
            if "Qty" in df_stn_latest.columns: rename_map["Qty"] = "STN Qty"

            df_stn_latest = df_stn_latest.rename(columns=rename_map)
            keep = ["_stn_sku"] + [v for v in ["STN No","STN Date","STN WH","STN Qty","STN Status"] if v in df_stn_latest.columns]
            df_stn_latest = df_stn_latest[keep]

            # Merge into FG
            sku_col = "Item SKU" if "Item SKU" in df_fg.columns else next((c for c in df_fg.columns if "sku" in c.lower()), None)
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
            <div class="hdr-sub">YogaBar · Finished Goods Stock + STN Transfer</div>
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
    search = st.text_input("s", placeholder="🔍 Search item / SKU / batch…", label_visibility="collapsed")
with c2:
    fg_wh_opts = ["All FG WH"] + sorted(df_raw["Warehouse"].dropna().astype(str).unique().tolist())
    sel_fg_wh  = st.selectbox("fw", fg_wh_opts, label_visibility="collapsed")
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
    sel_shelf = st.selectbox("sh", ["All", "Expiring in 30 days", "Expired"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_fg_wh != "All FG WH":
    df = df[df["Warehouse"].astype(str) == sel_fg_wh]
if sel_stn_wh != "All STN WH" and "STN WH" in df.columns:
    df = df[df["STN WH"].astype(str) == sel_stn_wh]
if sel_stat != "All Status" and "STN Status" in df.columns:
    df = df[df["STN Status"].astype(str) == sel_stat]
if "_remaining_days" in df.columns:
    if sel_shelf == "Expiring in 30 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 30)]
    elif sel_shelf == "Expired":
        df = df[df["_remaining_days"] < 0]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_qty    = df["Qty Available"].sum() if "Qty Available" in df.columns else 0
expiring_qty = df[df["_remaining_days"].between(0, 30)]["Qty Available"].sum() if "_remaining_days" in df.columns else 0
expired_qty  = df[df["_remaining_days"] < 0]["Qty Available"].sum()            if "_remaining_days" in df.columns else 0
stn_count    = df["STN No"].notna().sum() if "STN No" in df.columns else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card blue">
        <div class="kpi-lbl">Total Available Qty</div>
        <div class="kpi-num">{total_qty:,.0f}</div>
        <div class="kpi-cap">{len(df):,} records shown</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-lbl">Expiring in 30 Days</div>
        <div class="kpi-num">{expiring_qty:,.0f}</div>
        <div class="kpi-cap">Requires immediate attention</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-lbl">Expired · Qty</div>
        <div class="kpi-num">{expired_qty:,.0f}</div>
        <div class="kpi-cap">Past expiry date</div>
    </div>
    <div class="kpi-card teal">
        <div class="kpi-lbl">Items with STN</div>
        <div class="kpi-num">{stn_count:,}</div>
        <div class="kpi-cap">Transfer records linked</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">FG Records + STN Transfer</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 FG Inventory · STN Combined</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.drop(columns=["_remaining_days"], errors="ignore").to_excel(w, index=False, sheet_name="FG Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "FG_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_row(row):
        rem = row.get("_remaining_days", 999)
        if isinstance(rem, (int, float)):
            if rem < 0:  return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
            if rem <= 30: return ["background-color:#2d1f00; color:#fde68a"] * len(row)
        return [""] * len(row)

    display_df = df.drop(columns=["_remaining_days"], errors="ignore").copy()

    # Format dates
    for dc in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if dc in display_df.columns:
            display_df[dc] = display_df[dc].dt.strftime("%d-%b-%Y").fillna("")
    if "STN Date" in display_df.columns:
        display_df["STN Date"] = pd.to_datetime(display_df["STN Date"], errors="coerce").dt.strftime("%d-%b-%Y").fillna("")

    # Column order: FG cols first, then STN cols at end
    fg_cols  = [c for c in display_df.columns if not c.startswith("STN")]
    stn_cols = [c for c in display_df.columns if c.startswith("STN")]
    display_df = display_df[fg_cols + stn_cols]

    st.dataframe(
        display_df.style.apply(colour_row, axis=1),
        use_container_width=True, height=530, hide_index=True,
        column_config={
            "Qty Available":    st.column_config.NumberColumn("Qty Avail",    format="%.0f"),
            "Qty Inward":       st.column_config.NumberColumn("Inward",       format="%.0f"),
            "Qty (Issue / Hold)":st.column_config.NumberColumn("Issue/Hold",  format="%.0f"),
            "Value (Inc Tax)":  st.column_config.NumberColumn("Val (Inc)",    format="%.0f"),
            "Value (Ex Tax)":   st.column_config.NumberColumn("Val (Ex)",     format="%.0f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging (d)", format="%d"),
            "Shelf Life %":     st.column_config.ProgressColumn("Shelf Life %", min_value=0, max_value=100, format="%.1f%%"),
            "STN Qty":          st.column_config.NumberColumn("STN Qty",      format="%.0f"),
        }
    )

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · STN</div>', unsafe_allow_html=True)
