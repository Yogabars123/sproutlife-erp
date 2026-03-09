import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="GRN Data · YogaBar", page_icon="📥", layout="wide", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("GRN Data")

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
.hdr-logo { width:40px; height:40px; min-width:40px; background:#0c1f3a; border:1px solid #1e3a5f; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:19px; }
.hdr-title { font-size:16px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 11px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.kpi-card { border-radius:16px; padding:16px 18px; position:relative; overflow:hidden; border:1px solid; min-height:100px; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.kpi-card.blue   { background:linear-gradient(135deg,#0c1f3a,#0f2d5e); border-color:#1e3a5f; }
.kpi-card.blue::before   { background:linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-card.green  { background:linear-gradient(135deg,#052e16,#064e3b); border-color:#166534; }
.kpi-card.green::before  { background:linear-gradient(90deg,#22c55e,#4ade80); }
.kpi-card.amber  { background:linear-gradient(135deg,#1c1500,#2d1f00); border-color:#854d0e; }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.red    { background:linear-gradient(135deg,#1f0707,#3b0a0a); border-color:#991b1b; }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-lbl { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:8px; }
.kpi-card.blue  .kpi-lbl { color:#60a5fa; } .kpi-card.green .kpi-lbl { color:#4ade80; }
.kpi-card.amber .kpi-lbl { color:#fbbf24; } .kpi-card.red   .kpi-lbl { color:#f87171; }
.kpi-num { font-size:26px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-card.blue  .kpi-num { color:#bfdbfe; } .kpi-card.green .kpi-num { color:#bbf7d0; }
.kpi-card.amber .kpi-num { color:#fde68a; } .kpi-card.red   .kpi-num { color:#fecaca; }
.kpi-cap { font-size:11px; margin-top:5px; }
.kpi-card.blue  .kpi-cap { color:#1e3a5f; } .kpi-card.green .kpi-cap { color:#166534; }
.kpi-card.amber .kpi-cap { color:#854d0e; } .kpi-card.red   .kpi-cap { color:#991b1b; }
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }
[data-testid="stTextInput"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:#3b82f6 !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:#f1f5f9 !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }
.stDownloadButton > button { width:100% !important; background:linear-gradient(135deg,#0f172a,#1e1b4b) !important; border:1.5px solid #4338ca !important; border-radius:9px !important; color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; padding:10px !important; }
.stButton > button { width:100% !important; background:#0d1117 !important; border:1.5px solid #1e2535 !important; border-radius:9px !important; color:#64748b !important; font-size:13px !important; font-weight:600 !important; padding:9px !important; transition:all .2s !important; margin-bottom:6px !important; }
.stButton > button:hover { border-color:#3b82f6 !important; color:#60a5fa !important; }
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:12px 0 8px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:6px 0; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#60a5fa; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    df = load_sheet("GRN-Data")
    if df.empty:
        return pd.DataFrame()
    df.columns = df.columns.str.strip()
    for col in ["QuantityOrdered", "QuantityReceived", "QuantityRejected"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    # Parse date column — try GRN Date or Date
    # Use existing GRN Month column if present
    if "GRN Month" in df.columns:
        df["_month"] = df["GRN Month"].astype(str).str.strip()
    else:
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        if date_col:
            df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
            df["_month"] = df["_date"].dt.strftime("%b-%Y")
    return df

df_all = load_data()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📥</div>
        <div>
            <div class="hdr-title">GRN Data</div>
            <div class="hdr-sub">YogaBar · Goods Received Notes</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if df_all.empty:
    st.error("⚠️ No GRN data found. Check Excel file.")
    st.stop()

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([2.5, 1.8, 1.8, 1.8, 1.8])

with c1:
    search = st.text_input("s", placeholder="🔍 GRN No / Item Code / Item Name / PO No…", label_visibility="collapsed")

with c2:
    # Vendor dropdown
    vendor_col = "Vendor Name" if "Vendor Name" in df_all.columns else next((c for c in df_all.columns if "vendor" in c.lower() or "supplier" in c.lower()), None)
    if vendor_col:
        vendors = ["All Vendors"] + sorted(df_all[vendor_col].dropna().astype(str).str.strip().unique().tolist())
    else:
        vendors = ["All Vendors"]
    sel_vendor = st.selectbox("v", vendors, label_visibility="collapsed")

with c3:
    # Month dropdown
    if "_month" in df_all.columns:
        raw_months = df_all["_month"].dropna().astype(str).str.strip().unique().tolist()
        # Sort by month order: Jan, Feb, Mar... 
        month_order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        sorted_months = sorted(raw_months, key=lambda x: month_order.index(x) if x in month_order else 99)
        months = ["All Months"] + sorted_months
    else:
        months = ["All Months"]
    sel_month = st.selectbox("m", months, label_visibility="collapsed")

with c4:
    # Warehouse dropdown
    if "Warehouse" in df_all.columns:
        wh_opts = ["All Warehouses"] + sorted(df_all["Warehouse"].dropna().astype(str).unique().tolist())
    else:
        wh_opts = ["All Warehouses"]
    sel_wh = st.selectbox("w", wh_opts, label_visibility="collapsed")

with c5:
    # PO filter - valid PO only toggle
    po_opts = ["All Records", "Valid PO Only"]
    sel_po = st.selectbox("p", po_opts, label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_all.copy()

if sel_po == "Valid PO Only" and "PO No" in df.columns:
    df = df[df["PO No"].notna() & (df["PO No"].astype(str).str.strip() != "") & (df["PO No"].astype(str).str.strip() != "-")]

if search:
    s = search.lower()
    df = df[df.apply(lambda row:
        s in str(row.get("GRN No","")).lower() or
        s in str(row.get("Item Code","")).lower() or
        s in str(row.get("Item Name","")).lower() or
        s in str(row.get("PO No","")).lower(), axis=1)]

if vendor_col and sel_vendor != "All Vendors":
    df = df[df[vendor_col].astype(str) == sel_vendor]

if sel_month != "All Months" and "_month" in df.columns:
    df = df[df["_month"] == sel_month]

if sel_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_wh]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
# Ordered Qty — deduplicate by PO No + Item Code to avoid double counting
if "QuantityOrdered" in df.columns and "PO No" in df.columns and "Item Code" in df.columns:
    total_ordered = df.drop_duplicates(subset=["PO No", "Item Code"])["QuantityOrdered"].sum()
elif "QuantityOrdered" in df.columns:
    total_ordered = df["QuantityOrdered"].sum()
else:
    total_ordered = 0

total_received = df["QuantityReceived"].sum() if "QuantityReceived" in df.columns else 0
total_rejected = df["QuantityRejected"].sum() if "QuantityRejected" in df.columns else 0
pending_qty    = total_ordered - total_received

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card blue">
        <div class="kpi-lbl">Ordered Quantity</div>
        <div class="kpi-num">{total_ordered:,.0f}</div>
        <div class="kpi-cap">Total PO qty raised</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-lbl">Received Quantity</div>
        <div class="kpi-num">{total_received:,.0f}</div>
        <div class="kpi-cap">Total GRN qty received</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-lbl">Pending Quantity</div>
        <div class="kpi-num">{pending_qty:,.0f}</div>
        <div class="kpi-cap">Ordered − Received</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-lbl">Rejected Quantity</div>
        <div class="kpi-num">{total_rejected:,.0f}</div>
        <div class="kpi-cap">Quality rejections</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">GRN Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 All Columns</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

# Export
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.drop(columns=["_date","_month"], errors="ignore").to_excel(w, index=False, sheet_name="GRN Data")
st.download_button("⬇  Export to Excel", buf.getvalue(), "GRN_Data.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

disp = df.drop(columns=["_date","_month"], errors="ignore")
st.dataframe(disp, use_container_width=True, height=520, hide_index=True,
    column_config={
        "QuantityOrdered":  st.column_config.NumberColumn("Qty Ordered",  format="%.0f"),
        "QuantityReceived": st.column_config.NumberColumn("Qty Received", format="%.0f"),
        "QuantityRejected": st.column_config.NumberColumn("Qty Rejected", format="%.0f"),
    }
)

st.markdown('<div class="app-footer">YOGABAR · GRN DATA</div>', unsafe_allow_html=True)
