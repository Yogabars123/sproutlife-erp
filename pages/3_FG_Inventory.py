import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="FG Inventory · YogaBar", layout="wide", page_icon="📦", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("FG Inventory")

def _tg_send(token: str, chat_id: str, text: str) -> tuple[bool, str]:
    import requests as _req
    url    = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            r = _req.post(url, json={"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"}, timeout=15)
            if r.status_code != 200:
                return False, r.json().get("description", r.text)
        except Exception as e:
            return False, str(e)
    return True, ""

def build_cfa_telegram(merged: "pd.DataFrame", central_stock: dict) -> str:
    import pytz
    NL  = chr(10)
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    shortfall = merged[merged["Diff"] < 0].copy().sort_values("Diff")
    total     = len(shortfall)
    lines = ["📦 <b>YogaBar · CFA FG Shortfall</b>", "🕐 " + now, "━━━━━━━━━━━━━━━━━━━━━━━━"]
    if total == 0:
        lines.append("✅ All CFAs fully stocked — no shortfall!")
    else:
        lines.append("⚠️ <b>" + str(total) + " shortfall SKU(s) across " + str(shortfall["CFA Warehouse"].nunique()) + " CFA(s)</b>")
        lines.append("")
        for cfa in shortfall["CFA Warehouse"].unique():
            rows = shortfall[shortfall["CFA Warehouse"] == cfa]
            n    = len(rows); net = float(rows["Diff"].sum())
            lines.append("🏭 <b>" + cfa + "</b>  [" + str(n) + " SKU" + ("s" if n > 1 else "") + "  |  Net: " + f"{net:+,.0f}" + "]")
            n_ok = n_pt = n_no = 0
            for _, r in rows.iterrows():
                sku = str(r["Item SKU"]).strip(); cen = float(central_stock.get(sku, 0)); diff_abs = abs(float(r["Diff"]))
                if cen >= diff_abs:  icon = "✅"; n_ok += 1
                elif cen > 0:        icon = "⚠️"; n_pt += 1
                else:                icon = "❌"; n_no += 1
                name = str(r.get("Item Name", sku))[:38]
                lines.append("  • <code>" + sku + "</code>  " + name + NL + "    Stock: <b>" + f"{r['FG Stock']:,.0f}" + "</b>  PO: " + f"{r['Open PO Qty']:,.0f}" + "  Diff: <b>" + f"{r['Diff']:+,.0f}" + "</b>  " + icon + " STN")
            parts = []
            if n_ok: parts.append("✅ " + str(n_ok) + " possible")
            if n_pt: parts.append("⚠️ " + str(n_pt) + " partial")
            if n_no: parts.append("❌ " + str(n_no) + " no stock")
            if parts: lines.append("  └ " + " · ".join(parts))
            lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 <i>Sent from YogaBar ERP Dashboard</i>")
    return NL.join(lines)

_DEFAULT_TG_TOKEN   = "8368375473:AAERuMSZGrdrvYKiGGQl9HIrdNzh-6a8eZQ"
_DEFAULT_TG_CHAT_ID = "5667118823"
if not st.session_state.get("tg_token"):    st.session_state["tg_token"]   = _DEFAULT_TG_TOKEN
if not st.session_state.get("tg_chat_id"): st.session_state["tg_chat_id"] = _DEFAULT_TG_CHAT_ID

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"],.main{
  background:#080b12!important;font-family:'Inter',sans-serif!important;color:#e2e8f0!important;}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;}
.block-container{padding:1rem 1.2rem 3rem!important;max-width:100%!important;}
[data-testid="stVerticalBlock"]>div{gap:0!important;}
.app-header{display:flex;align-items:center;justify-content:space-between;padding-bottom:14px;border-bottom:1px solid #161d2e;margin-bottom:14px;}
.hdr-left{display:flex;align-items:center;gap:10px;}
.hdr-logo{width:40px;height:40px;min-width:40px;background:#0f1f3a;border:1px solid #1a3a5c;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:19px;}
.hdr-title{font-size:16px;font-weight:800;color:#f1f5f9;}
.hdr-sub{font-size:11px;color:#94a3b8;}
.live-pill{display:inline-flex;align-items:center;gap:5px;background:#071a0f;border:1px solid #166534;border-radius:20px;padding:5px 11px;font-size:10px;font-weight:700;color:#22c55e;letter-spacing:1px;font-family:'JetBrains Mono',monospace;}
.live-dot{width:6px;height:6px;background:#22c55e;border-radius:50%;animation:blink 1.8s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;}50%{opacity:.2;box-shadow:none;}}
.kpi-row{display:grid;grid-template-columns:repeat(5,1fr);gap:11px;margin-bottom:16px;}
.kpi-row-2{display:grid;grid-template-columns:repeat(2,1fr);gap:11px;margin-bottom:16px;}
.kpi-box{border-radius:15px;padding:16px 18px;border:1px solid;position:relative;overflow:hidden;}
.kpi-box::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:15px 15px 0 0;}
.kpi-box.teal{background:linear-gradient(135deg,#061413,#0a2825);border-color:#134e4a;}
.kpi-box.teal::before{background:linear-gradient(90deg,#5bc8c0,#2dd4bf);}
.kpi-box.violet{background:linear-gradient(135deg,#130a2a,#1e0f40);border-color:#3b1f6e;}
.kpi-box.violet::before{background:linear-gradient(90deg,#a855f7,#818cf8);}
.kpi-box.blue{background:linear-gradient(135deg,#060e1a,#0a1a2e);border-color:#1e3a5f;}
.kpi-box.blue::before{background:linear-gradient(90deg,#3b82f6,#60a5fa);}
.kpi-box.amber{background:linear-gradient(135deg,#1a1000,#2a1800);border-color:#78350f;}
.kpi-box.amber::before{background:linear-gradient(90deg,#f59e0b,#fbbf24);}
.kpi-box.green{background:linear-gradient(135deg,#061a0a,#0a2e12);border-color:#14532d;}
.kpi-box.green::before{background:linear-gradient(90deg,#22c55e,#4ade80);}
.kpi-box.red{background:linear-gradient(135deg,#1a0000,#2a0808);border-color:#7f1d1d;}
.kpi-box.red::before{background:linear-gradient(90deg,#ef4444,#f87171);}
.kpi-inner{display:flex;align-items:flex-start;justify-content:space-between;}
.kpi-label{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px;}
.kpi-value{font-size:26px;font-weight:800;line-height:1;font-family:'JetBrains Mono',monospace;letter-spacing:-1px;}
.kpi-sub{font-size:10.5px;margin-top:5px;}
.kpi-ico{font-size:22px;opacity:.6;margin-top:2px;}
.kpi-box.teal .kpi-label{color:#5bc8c0;}.kpi-box.teal .kpi-value{color:#99f6e4;}.kpi-box.teal .kpi-sub{color:#0d9488;}
.kpi-box.violet .kpi-label{color:#c084fc;}.kpi-box.violet .kpi-value{color:#e9d5ff;}.kpi-box.violet .kpi-sub{color:#7c3aed;}
.kpi-box.blue .kpi-label{color:#60a5fa;}.kpi-box.blue .kpi-value{color:#bfdbfe;}.kpi-box.blue .kpi-sub{color:#2563eb;}
.kpi-box.amber .kpi-label{color:#fbbf24;}.kpi-box.amber .kpi-value{color:#fde68a;}.kpi-box.amber .kpi-sub{color:#d97706;}
.kpi-box.green .kpi-label{color:#4ade80;}.kpi-box.green .kpi-value{color:#bbf7d0;}.kpi-box.green .kpi-sub{color:#16a34a;}
.kpi-box.red .kpi-label{color:#f87171;}.kpi-box.red .kpi-value{color:#fecaca;}.kpi-box.red .kpi-sub{color:#dc2626;}
.filter-wrap{background:#0d1117;border:1px solid #1e2535;border-radius:14px;padding:12px 14px;margin-bottom:14px;}
.filter-title{font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;display:flex;align-items:center;gap:6px;}
.filter-title::after{content:'';flex:1;height:1px;background:#1e2535;}
[data-testid="stTextInput"]>div>div{background:#111827!important;border:1.5px solid #1e2d45!important;border-radius:9px!important;}
[data-testid="stTextInput"]>div>div:focus-within{border-color:#5bc8c0!important;}
[data-testid="stTextInput"] input{background:transparent!important;color:#f1f5f9!important;font-size:13px!important;padding:9px 12px!important;border:none!important;}
[data-testid="stTextInput"] input::placeholder{color:#334155!important;}
[data-testid="stSelectbox"]>div>div{background:#111827!important;border:1.5px solid #1e2d45!important;border-radius:9px!important;color:#e2e8f0!important;font-size:12.5px!important;}
[data-testid="stWidgetLabel"]{display:none!important;}
.stDownloadButton>button{width:100%!important;background:linear-gradient(135deg,#0f172a,#1e1b4b)!important;border:1.5px solid #4338ca!important;border-radius:9px!important;color:#a5b4fc!important;font-size:13px!important;font-weight:700!important;padding:10px!important;}
.stButton>button{width:100%!important;background:#0d1117!important;border:1.5px solid #1e2535!important;border-radius:9px!important;color:#64748b!important;font-size:13px!important;font-weight:600!important;padding:9px!important;transition:all .2s!important;margin-bottom:6px!important;}
.stButton>button:hover{border-color:#5bc8c0!important;color:#5bc8c0!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:#0d1117!important;border-radius:12px 12px 0 0!important;border:1px solid #1e2535!important;border-bottom:none!important;padding:6px 8px 0!important;gap:4px!important;}
[data-testid="stTabs"] [data-baseweb="tab"]{background:transparent!important;border-radius:8px 8px 0 0!important;color:#475569!important;font-size:12px!important;font-weight:700!important;padding:8px 18px!important;border:none!important;}
[data-testid="stTabs"] [aria-selected="true"]{background:#111827!important;color:#5bc8c0!important;border-bottom:2px solid #5bc8c0!important;}
[data-testid="stTabs"] [data-baseweb="tab-panel"]{background:#0d1117!important;border:1px solid #1e2535!important;border-radius:0 0 12px 12px!important;padding:14px!important;}
.tbl-hdr{display:flex;align-items:center;justify-content:space-between;padding:8px 0 6px;}
.tbl-lbl{font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1.2px;}
.tbl-badge{background:#0f172a;border:1px solid #1e2d45;color:#818cf8;font-size:11px;font-weight:700;padding:3px 11px;border-radius:20px;font-family:'JetBrains Mono',monospace;}
div[data-testid="stDataFrame"]{border-radius:10px!important;overflow:hidden!important;border:1px solid #1e2535!important;}
.sec-div{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1.2px;padding:10px 0 6px;display:flex;align-items:center;gap:7px;}
.sec-div::after{content:'';flex:1;height:1px;background:#161d2e;}
.formula-bar{background:#0a0f1a;border:1px solid #1e2d45;border-radius:10px;padding:10px 16px;margin-bottom:12px;font-size:11px;font-family:'JetBrains Mono',monospace;color:#64748b;display:flex;gap:24px;flex-wrap:wrap;}
.formula-bar span{color:#94a3b8;}.formula-bar b{color:#5bc8c0;}
.app-footer{margin-top:2rem;padding-top:12px;border-top:1px solid #161d2e;text-align:center;font-size:10px;font-weight:600;color:#334155;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;}
/* ── Channel "All" summary bar ─────────────────────────────────────────────── */
.ch-all-bar{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-bottom:16px;}
.ch-all-card{background:#0d1117;border:1px solid #1e2535;border-radius:12px;padding:12px 14px;position:relative;overflow:hidden;}
.ch-all-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.ch-all-card.red-c::before{background:linear-gradient(90deg,#ef4444,#f87171);}
.ch-all-card.amber-c::before{background:linear-gradient(90deg,#f59e0b,#fbbf24);}
.ch-all-card.green-c::before{background:linear-gradient(90deg,#22c55e,#4ade80);}
.ch-all-card .ch-lbl{font-size:9px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;}
.ch-all-card .ch-val{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace;line-height:1;}
.ch-all-card .ch-sub{font-size:10px;color:#475569;margin-top:3px;}
</style>
""", unsafe_allow_html=True)

CLOSED_STATUSES   = {"cancelled", "closed"}
STN_OPEN_STATUSES = {"raised", "approved", "in transit", "intransit", "in-transit", "pending"}

CFA_WAREHOUSES = [
    "Mumbai CFA", "Chennai CFA", "Kerala CFA", "Delhi -CFA GHEVRA",
    "Ahmedabad CFA", "Kolkata CFA", "Pune CFA", "Mithra Associates", "BENGALURU CFA",
]
def is_cfa(warehouse_name: str) -> bool:
    return str(warehouse_name).strip() in CFA_WAREHOUSES

CHANNEL_STOCK_WAREHOUSES = ["Tumkur New Warehouse", "YB FG Warehouse"]

@st.cache_data(ttl=300)
def load_fg():
    df = load_sheet("FG-Inventory")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    for col in ["Qty Available","Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)"]:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    today = pd.Timestamp(datetime.today().date())
    for col in ["Expiry Date","MFG Date","Inventory Date"]:
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors="coerce")
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
    if "Date" in df.columns: df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if "Qty"  in df.columns: df["Qty"]  = pd.to_numeric(df["Qty"],  errors="coerce").fillna(0)
    return df

@st.cache_data(ttl=300)
def load_sos():
    df = load_sheet("SOS")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    for col in ["Order Qty","Dispatch Qty","Rate","Order Value","Total Amount","GST"]:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["Order Date","PO Date","Invoice Date","Last Dispatch Date"]:
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

@st.cache_data(ttl=300)
def load_mapper():
    df = load_sheet("Mapper")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(ttl=300)
def load_reorder():
    df = load_sheet("Reorder")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if any(k in col.lower() for k in ["qty","stock","min","max","reorder"]):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df_fg      = load_fg()
df_stn     = load_stn()
df_sos     = load_sos()
df_mapper  = load_mapper()
df_reorder = load_reorder()

# ── HEADER ──────────────────────────────────────────────────────────────────────
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
    st.cache_data.clear(); st.rerun()

if df_fg.empty:
    st.error("⚠️ No FG Inventory data found."); st.stop()

all_fg_wh = sorted(df_fg["Warehouse"].dropna().astype(str).unique().tolist()) if "Warehouse" in df_fg.columns else []
cfa_warehouses = sorted([w for w in CFA_WAREHOUSES if w in all_fg_wh])

_all_channels_filt = []
if not df_mapper.empty:
    _cust_col_m    = next((c for c in df_mapper.columns if "customer" in c.lower() or "party" in c.lower()), None)
    _channel_col_m = next((c for c in df_mapper.columns if "channel" in c.lower()), None)
    if _cust_col_m and _channel_col_m:
        _all_channels_filt = sorted(df_mapper[_channel_col_m].dropna().astype(str).str.strip().unique().tolist())

st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2, 1.8, 1.8, 1.8, 1.8])
with c1: search      = st.text_input("s", placeholder="🔍 Search SKU / product name…", label_visibility="collapsed")
with c2: sel_fg_wh   = st.selectbox("fg_wh", ["All Warehouses"] + all_fg_wh, label_visibility="collapsed")
with c3: sel_cfa     = st.selectbox("cfa",   ["All CFAs"] + cfa_warehouses,  label_visibility="collapsed")
with c4: sel_channel = st.selectbox("ch_filt", ["All Channels"] + _all_channels_filt, label_visibility="collapsed")
with c5: sel_shelf   = st.selectbox("sh",    ["All Shelf Life","Below 90%","Below 80%","Below 70%","Below 50%"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

df = df_fg.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_fg_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_fg_wh]
shelf_map = {"Below 90%": 90, "Below 80%": 80, "Below 70%": 70, "Below 50%": 50}
if sel_shelf in shelf_map and "Shelf Life %" in df.columns:
    df = df[df["Shelf Life %"] < shelf_map[sel_shelf]]

# ── GLOBAL KPIs — only Total FG Stock shown here; CFA/STN/PO/Diff moved to Tab 2 ──
total_fg = df["Qty Available"].sum() if "Qty Available" in df.columns else 0

# Pre-compute CFA values (used in Tab 2)
cfa_fg = df[df["Warehouse"].astype(str).apply(is_cfa)]["Qty Available"].sum() if "Warehouse" in df.columns else 0
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
diff_global     = total_available - open_so_qty

# Only Total FG Stock in global bar (1 wide card)
st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr;gap:11px;margin-bottom:16px;">
  <div class="kpi-box teal"><div class="kpi-inner"><div>
    <div class="kpi-label">Total FG Stock — All Warehouses</div>
    <div class="kpi-value">{total_fg:,.0f}</div>
    <div class="kpi-sub">Across all warehouses · use tabs below for CFA / Channel breakdown</div>
  </div><div class="kpi-ico">📦</div></div></div>
</div>
""", unsafe_allow_html=True)

# ── TABS ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📦  FG Inventory", "📊  CFA Stock vs Open Orders", "🏪  Channel Analysis", "🔁  Reorder & Alerts"])

# ═══ TAB 1 ══════════════════════════════════════════════════════════════════════
with tab1:
    _fg3 = df_fg[df_fg["Warehouse"].astype(str).isin(CHANNEL_STOCK_WAREHOUSES)].copy() if "Warehouse" in df_fg.columns else pd.DataFrame()
    if not _fg3.empty and "Item SKU" in _fg3.columns:
        _fg3_agg = _fg3.groupby("Item SKU").agg(Item_Name=("Item Name","first"), Category=("Category","first"), FG_Stock=("Qty Available","sum")).reset_index()
        _fg3_agg.columns = ["Item SKU","Item Name","Category","FG Stock"]
    else:
        _fg3_agg = pd.DataFrame(columns=["Item SKU","Item Name","Category","FG Stock"])

    _t1_sos = pd.DataFrame()
    if not df_sos.empty:
        _sku_c  = next((c for c in df_sos.columns if "product sku"  in c.lower()), None)
        _cust_c = next((c for c in df_sos.columns if "customer" in c.lower() or "party" in c.lower()), None)
        _qty_c  = next((c for c in df_sos.columns if "order qty"    in c.lower()), None)
        if _sku_c and _qty_c:
            _t1_open = df_sos[~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)].copy() if "SO Status" in df_sos.columns else df_sos.copy()
            _t1_open["_sku"]      = _t1_open[_sku_c].astype(str).str.strip()
            _t1_open["_customer"] = _t1_open[_cust_c].astype(str).str.strip() if _cust_c else "Unknown"
            _t1_open["_po_qty"]   = pd.to_numeric(_t1_open[_qty_c], errors="coerce").fillna(0)
            _t1_cust_map = {}
            if not df_mapper.empty:
                _mc = next((c for c in df_mapper.columns if "customer" in c.lower() or "party" in c.lower()), None)
                _ch = next((c for c in df_mapper.columns if "channel"  in c.lower()), None)
                if _mc and _ch:
                    _t1_cust_map = dict(zip(df_mapper[_mc].astype(str).str.strip(), df_mapper[_ch].astype(str).str.strip()))
            _t1_open["_channel"] = _t1_open["_customer"].map(_t1_cust_map).fillna("Unknown")
            _t1_sos = _t1_open.groupby(["_sku","_customer","_channel"]).agg(PO_Qty=("_po_qty","sum"), Orders=("_po_qty","count")).reset_index()
            _t1_sos.columns = ["Item SKU","Customer Name","Channel","PO Quantity","# Orders"]

    if not _t1_sos.empty and not _fg3_agg.empty:
        _t1_merged = _t1_sos.merge(_fg3_agg, on="Item SKU", how="left")
    elif not _fg3_agg.empty:
        _t1_merged = _fg3_agg.copy(); _t1_merged["Customer Name"] = ""; _t1_merged["Channel"] = ""; _t1_merged["PO Quantity"] = 0; _t1_merged["# Orders"] = 0
    else:
        _t1_merged = pd.DataFrame(columns=["Item Name","Item SKU","Category","FG Stock","Customer Name","PO Quantity","Diff","Channel"])

    if not _t1_merged.empty:
        _t1_merged["Item Name"]   = _t1_merged["Item Name"].fillna(_t1_merged["Item SKU"])
        _t1_merged["Category"]    = _t1_merged.get("Category", pd.Series("")).fillna("")
        _t1_merged["FG Stock"]    = _t1_merged.get("FG Stock", pd.Series(0)).fillna(0)
        _t1_merged["PO Quantity"] = _t1_merged.get("PO Quantity", pd.Series(0)).fillna(0)
        _t1_merged["Diff"]        = _t1_merged["FG Stock"] - _t1_merged["PO Quantity"]

    _t1_view = _t1_merged.copy() if not _t1_merged.empty else pd.DataFrame()
    if not _t1_view.empty:
        if search:
            _t1_view = _t1_view[_t1_view.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
        if sel_channel != "All Channels" and "Channel" in _t1_view.columns:
            _t1_view = _t1_view[_t1_view["Channel"].astype(str) == sel_channel]

    _t1_cols = ["Item Name","Item SKU","Category","FG Stock","Customer Name","PO Quantity","Diff","Channel"]
    _t1_cols = [c for c in _t1_cols if c in (_t1_view.columns if not _t1_view.empty else [])]

    def _colour_t1(row):
        d = row.get("Diff", 0)
        if pd.isna(d): return [""] * len(row)
        if d < 0:      return ["background-color:#2d0a0a;color:#fca5a5"] * len(row)
        tot = row.get("FG Stock", 1)
        if tot > 0 and d / max(tot,1) < 0.15: return ["background-color:#2d1f00;color:#fde68a"] * len(row)
        return ["background-color:#061410;color:#d1fae5"] * len(row)

    buf1 = io.BytesIO()
    with pd.ExcelWriter(buf1, engine="openpyxl") as w:
        (_t1_view[_t1_cols] if not _t1_view.empty else pd.DataFrame(columns=_t1_cols)).to_excel(w, index=False, sheet_name="FG Inventory")
    hdr1, hdr2 = st.columns([4,1])
    with hdr1: st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📋 FG Inventory vs Open Orders</span><span class="tbl-badge">{len(_t1_view):,} rows</span></div>', unsafe_allow_html=True)
    with hdr2: st.download_button("⬇  Export", buf1.getvalue(), "FG_Inventory.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
    if _t1_view.empty or not _t1_cols:
        st.warning("⚠️ No records match the current filters.")
    else:
        st.dataframe(_t1_view[_t1_cols].style.apply(_colour_t1, axis=1), use_container_width=True, height=560, hide_index=True,
            column_config={"FG Stock": st.column_config.NumberColumn("FG Stock", format="%.0f", help="Tumkur New + YB FG"),
                           "PO Quantity": st.column_config.NumberColumn("PO Quantity", format="%.0f"),
                           "Diff": st.column_config.NumberColumn("Diff", format="%.0f"),
                           "# Orders": st.column_config.NumberColumn("# Orders", format="%d")})

# ═══ TAB 2 ══════════════════════════════════════════════════════════════════════
with tab2:
    # ── CFA KPIs shown ONLY here ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-box violet"><div class="kpi-inner"><div>
        <div class="kpi-label">CFA FG Stock</div><div class="kpi-value">{cfa_fg:,.0f}</div>
        <div class="kpi-sub">At CFA warehouses</div></div><div class="kpi-ico">🏭</div></div></div>
      <div class="kpi-box blue"><div class="kpi-inner"><div>
        <div class="kpi-label">STN In-Transit to CFA</div><div class="kpi-value">{stn_cfa_qty:,.0f}</div>
        <div class="kpi-sub">Raised / Approved STNs → CFA</div></div><div class="kpi-ico">🚚</div></div></div>
      <div class="kpi-box amber"><div class="kpi-inner"><div>
        <div class="kpi-label">Open PO Qty</div><div class="kpi-value">{open_so_qty:,.0f}</div>
        <div class="kpi-sub">Excl. Cancelled &amp; Closed</div></div><div class="kpi-ico">📋</div></div></div>
      <div class="kpi-box {'green' if diff_global>=0 else 'red'}"><div class="kpi-inner"><div>
        <div class="kpi-label">Diff (FG+STN−PO)</div><div class="kpi-value">{diff_global:,.0f}</div>
        <div class="kpi-sub">{'Surplus ✅' if diff_global>=0 else 'Shortfall ⚠️'}</div></div>
        <div class="kpi-ico">{'✅' if diff_global>=0 else '⚠️'}</div></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-bar">
        <span>📐 Formula:</span>
        <b>FG Stock</b> <span>= Qty at CFA warehouse</span> <span>+</span>
        <b>STN In-Transit</b> <span>= Raised/Approved STNs → CFA</span> <span>−</span>
        <b>Open PO Qty</b> <span>= Order Qty (excl. Cancelled &amp; Closed)</span> <span>=</span> <b>Diff</b>
    </div>
    """, unsafe_allow_html=True)

    df_cfa = df_fg[df_fg["Warehouse"].astype(str).apply(is_cfa)].copy() if "Warehouse" in df_fg.columns else pd.DataFrame()
    if sel_cfa != "All CFAs" and not df_cfa.empty:
        df_cfa = df_cfa[df_cfa["Warehouse"].astype(str) == sel_cfa]
    if search and not df_cfa.empty:
        df_cfa = df_cfa[df_cfa.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]

    if not df_cfa.empty and "Item SKU" in df_cfa.columns:
        fg_agg = df_cfa.groupby(["Item SKU","Warehouse"]).agg(Item_Name=("Item Name","first"), Category=("Category","first"), FG_Stock=("Qty Available","sum"), Shelf_Life=("Shelf Life %","mean")).reset_index()
        fg_agg.columns = ["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"]
        fg_agg["Shelf Life %"] = fg_agg["Shelf Life %"].round(1)
    else:
        fg_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"])

    stn_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","STN In-Transit","STN Transfers"])
    if not df_stn.empty:
        fg_code_col = next((c for c in df_stn.columns if "fg code" in c.lower()), None) or next((c for c in df_stn.columns if "code" in c.lower() or "sku" in c.lower()), None)
        to_wh_col   = next((c for c in df_stn.columns if "to warehouse" in c.lower()), None)
        stat_col    = next((c for c in df_stn.columns if c.lower() == "status"), None)
        qty_col     = next((c for c in df_stn.columns if c.lower() == "qty"), None)
        if fg_code_col and to_wh_col and stat_col and qty_col:
            stn_filt = df_stn[df_stn[to_wh_col].astype(str).apply(is_cfa) & df_stn[stat_col].astype(str).str.strip().str.lower().isin(STN_OPEN_STATUSES)].copy()
            if sel_cfa != "All CFAs": stn_filt = stn_filt[stn_filt[to_wh_col].astype(str) == sel_cfa]
            if search: stn_filt = stn_filt[stn_filt.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            if not stn_filt.empty:
                stn_filt["_sku"] = stn_filt[fg_code_col].astype(str).str.strip()
                stn_filt["_wh"]  = stn_filt[to_wh_col].astype(str).str.strip()
                stn_agg = stn_filt.groupby(["_sku","_wh"]).agg(STN_In_Transit=(qty_col,"sum"), STN_Transfers=(qty_col,"count")).reset_index()
                stn_agg.columns = ["Item SKU","CFA Warehouse","STN In-Transit","STN Transfers"]

    so_agg = pd.DataFrame(columns=["Item SKU","CFA Warehouse","Open PO Qty","Open Orders"])
    if not df_sos.empty and "SO Status" in df_sos.columns:
        sku_col_so = next((c for c in df_sos.columns if "product sku" in c.lower()), None)
        wh_col_so  = next((c for c in df_sos.columns if c.lower() == "warehouse"), None)
        qty_col_so = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
        val_col_so = next((c for c in df_sos.columns if "total amount" in c.lower()), None)
        if sku_col_so and wh_col_so and qty_col_so:
            sos_open = df_sos[~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)].copy()
            sos_open = sos_open[sos_open[wh_col_so].astype(str).apply(is_cfa)]
            if sel_cfa != "All CFAs": sos_open = sos_open[sos_open[wh_col_so].astype(str) == sel_cfa]
            if search: sos_open = sos_open[sos_open.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            if not sos_open.empty:
                sos_open["_sku"] = sos_open[sku_col_so].astype(str).str.strip()
                sos_open["_wh"]  = sos_open[wh_col_so].astype(str).str.strip()
                agg_dict = {"Open PO Qty": (qty_col_so,"sum"), "Open Orders": (qty_col_so,"count")}
                if val_col_so: agg_dict["Open PO Value (₹)"] = (val_col_so,"sum")
                so_agg = sos_open.groupby(["_sku","_wh"]).agg(**agg_dict).reset_index()
                so_agg.columns = ["Item SKU","CFA Warehouse"] + list(agg_dict.keys())

    merged = fg_agg.copy() if not fg_agg.empty else pd.DataFrame(columns=["Item SKU","CFA Warehouse","Item Name","Category","FG Stock","Shelf Life %"])
    if not stn_agg.empty: merged = merged.merge(stn_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    else: merged["STN In-Transit"] = 0; merged["STN Transfers"] = 0
    if not so_agg.empty: merged = merged.merge(so_agg, on=["Item SKU","CFA Warehouse"], how="outer")
    else: merged["Open PO Qty"] = 0; merged["Open Orders"] = 0

    if merged.empty:
        st.warning("⚠️ No CFA data found.")
    else:
        merged["FG Stock"]       = merged["FG Stock"].fillna(0)
        merged["STN In-Transit"] = merged["STN In-Transit"].fillna(0)
        merged["STN Transfers"]  = merged["STN Transfers"].fillna(0).astype(int)
        merged["Open PO Qty"]    = merged["Open PO Qty"].fillna(0)
        merged["Open Orders"]    = merged["Open Orders"].fillna(0).astype(int)
        merged["Shelf Life %"]   = merged["Shelf Life %"].fillna(0.0).round(1)
        if "Open PO Value (₹)" in merged.columns: merged["Open PO Value (₹)"] = merged["Open PO Value (₹)"].fillna(0)
        merged = merged[merged["CFA Warehouse"].astype(str).apply(is_cfa)]
        merged["Total Available"] = merged["FG Stock"] + merged["STN In-Transit"]
        merged["Diff"]            = merged["Total Available"] - merged["Open PO Qty"]
        fg_name_map = df_fg.drop_duplicates("Item SKU").set_index("Item SKU")[["Item Name","Category"]].to_dict("index") if "Item SKU" in df_fg.columns else {}
        def fill_name(row):
            if pd.isna(row.get("Item Name")) or str(row.get("Item Name","")) == "":
                info = fg_name_map.get(str(row["Item SKU"]).strip(), {})
                row["Item Name"] = info.get("Item Name", row["Item SKU"]); row["Category"] = info.get("Category", "")
            return row
        merged = merged.apply(fill_name, axis=1)
        merged = merged.sort_values("Diff", ascending=True)

        t_fg   = merged["FG Stock"].sum(); t_stn  = merged["STN In-Transit"].sum()
        t_po   = merged["Open PO Qty"].sum(); t_diff = merged["Diff"].sum()
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("CFA FG Stock",    f"{t_fg:,.0f}")
        s2.metric("STN In-Transit",  f"{t_stn:,.0f}")
        s3.metric("Total Available", f"{(t_fg+t_stn):,.0f}", help="FG + STN")
        s4.metric("Open PO Qty",     f"{t_po:,.0f}")
        s5.metric("Net Diff",        f"{t_diff:,.0f}", delta=f"{'Surplus' if t_diff>=0 else 'Shortfall'}: {abs(t_diff):,.0f}", delta_color="normal" if t_diff>=0 else "inverse")
        st.markdown("<div style='margin-bottom:14px'></div>", unsafe_allow_html=True)

        today_ts = pd.Timestamp(datetime.today().date())
        fill_rows = []
        for cfa_wh in sorted(merged["CFA Warehouse"].dropna().astype(str).unique()):
            cfa_m = merged[merged["CFA Warehouse"] == cfa_wh]
            total_po = cfa_m["Open PO Qty"].sum()
            fulfillable = cfa_m.apply(lambda r: min(r["Total Available"], r["Open PO Qty"]), axis=1).sum()
            fill_pct = min((fulfillable / total_po * 100) if total_po > 0 else 100.0, 100.0)
            fill_rows.append({"CFA": cfa_wh, "Fill Rate %": round(fill_pct,1), "Total Available": cfa_m["Total Available"].sum(), "Open PO Qty": total_po, "Shortfall SKUs": int((cfa_m["Diff"] < 0).sum())})
        fill_df = pd.DataFrame(fill_rows).sort_values("Fill Rate %", ascending=True) if fill_rows else pd.DataFrame()

        expiry_rows = []
        if not df_cfa.empty and "Expiry Date" in df_cfa.columns:
            exp_data = df_cfa[["Warehouse","Qty Available","Expiry Date"]].copy()
            exp_data["Expiry Date"] = pd.to_datetime(exp_data["Expiry Date"], errors="coerce")
            exp_data["days_to_exp"] = (exp_data["Expiry Date"] - today_ts).dt.days
            for cfa_wh in sorted(exp_data["Warehouse"].dropna().astype(str).unique()):
                cfa_e = exp_data[exp_data["Warehouse"] == cfa_wh]
                expiry_rows.append({"CFA": cfa_wh, "Expired": cfa_e[cfa_e["days_to_exp"] < 0]["Qty Available"].sum(), "< 30 days": cfa_e[cfa_e["days_to_exp"].between(0,30, inclusive="both")]["Qty Available"].sum(), "31–60 days": cfa_e[cfa_e["days_to_exp"].between(31,60, inclusive="both")]["Qty Available"].sum(), "61–90 days": cfa_e[cfa_e["days_to_exp"].between(61,90, inclusive="both")]["Qty Available"].sum(), "> 90 days": cfa_e[cfa_e["days_to_exp"] > 90]["Qty Available"].sum()})
        expiry_df = pd.DataFrame(expiry_rows) if expiry_rows else pd.DataFrame()

        col_fill, col_exp = st.columns([1, 1.6], gap="medium")
        with col_fill:
            st.markdown('<div class="sec-div">📊 Fill Rate by CFA</div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-size:10px;color:#475569;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">Fill Rate = % of open PO demand fulfillable with FG + STN stock</div>""", unsafe_allow_html=True)
            if fill_df.empty:
                st.info("No open PO data for CFA warehouses.")
            else:
                for _, fr in fill_df.iterrows():
                    pct = float(fr["Fill Rate %"]); avl = float(fr["Total Available"]); po = float(fr["Open PO Qty"]); short = int(fr["Shortfall SKUs"])
                    bar_c = "#22c55e" if pct>=90 else "#f59e0b" if pct>=60 else "#ef4444"
                    txt_c = "#bbf7d0" if pct>=90 else "#fde68a" if pct>=60 else "#fca5a5"
                    bdg_bg = "#061a0a" if pct>=90 else "#2d1f00" if pct>=60 else "#2d0a0a"
                    bdg_b  = "#14532d" if pct>=90 else "#78350f" if pct>=60 else "#7f1d1d"
                    short_html = f'<span style="font-size:10px;color:#f87171;margin-left:6px;">⚠️ {short} SKU{"s" if short!=1 else ""}</span>' if short > 0 else ""
                    st.markdown(f'<div style="background:#0d1117;border:1px solid #1e2535;border-radius:11px;padding:11px 14px;margin-bottom:8px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;"><span style="font-size:12px;font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px;">{fr["CFA"]}</span><div style="display:flex;align-items:center;gap:6px;">{short_html}<span style="background:{bdg_bg};border:1px solid {bdg_b};border-radius:20px;padding:2px 10px;font-size:12px;font-weight:800;color:{txt_c};font-family:JetBrains Mono,monospace;">{pct:.1f}%</span></div></div><div style="background:#1e2535;border-radius:5px;height:8px;margin-bottom:5px;"><div style="width:{min(pct,100):.1f}%;background:{bar_c};height:8px;border-radius:5px;"></div></div><div style="display:flex;justify-content:space-between;font-size:10px;font-family:JetBrains Mono,monospace;"><span style="color:#475569;">Available: <b style="color:#94a3b8;">{avl:,.0f}</b></span><span style="color:#475569;">Open PO: <b style="color:#94a3b8;">{po:,.0f}</b></span></div></div>', unsafe_allow_html=True)

        with col_exp:
            st.markdown('<div class="sec-div">🔥 Expiry Heatmap by CFA</div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-size:10px;color:#475569;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">Qty expiring within each window · cell intensity = urgency</div>""", unsafe_allow_html=True)
            if expiry_df.empty:
                st.info("No expiry data — ensure FG Inventory has an Expiry Date column.")
            else:
                buckets  = ["Expired","< 30 days","31–60 days","61–90 days","> 90 days"]
                bkt_cols = ["#7f1d1d","#b91c1c","#d97706","#ca8a04","#15803d"]
                bkt_bg   = ["#1a0000","#2d0a0a","#2d1800","#2d2200","#061a0a"]
                bkt_bdr  = ["#450a0a","#7f1d1d","#78350f","#713f12","#14532d"]
                max_vals = {b: max(expiry_df[b].max(), 1) for b in buckets}
                hdr = '<div style="display:grid;grid-template-columns:150px repeat(5,1fr);gap:4px;margin-bottom:6px;"><div style="font-size:10px;color:#334155;font-weight:700;font-family:JetBrains Mono,monospace;">CFA</div>'
                for b, bc in zip(buckets, bkt_cols): hdr += f'<div style="font-size:9px;color:{bc};font-weight:700;text-align:center;font-family:JetBrains Mono,monospace;line-height:1.3;">{b}</div>'
                hdr += '</div>'; st.markdown(hdr, unsafe_allow_html=True)
                for _, er in expiry_df.sort_values("< 30 days", ascending=False).iterrows():
                    row = f'<div style="display:grid;grid-template-columns:150px repeat(5,1fr);gap:4px;margin-bottom:5px;align-items:center;"><div style="font-size:11px;font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{er["CFA"]}</div>'
                    for b, bc, bbg, bbdr in zip(buckets, bkt_cols, bkt_bg, bkt_bdr):
                        val = float(er[b]); intensity = val / max_vals[b] if max_vals[b] > 0 else 0; opacity = min(0.4 + max(0.08, intensity), 1.0)
                        row += f'<div style="background:{bbg};border:1px solid {bbdr};border-radius:7px;padding:5px 4px;text-align:center;opacity:{opacity:.2f};"><div style="font-size:11px;font-weight:800;color:{"" if val>0 else "#1e2535"};font-family:JetBrains Mono,monospace;line-height:1;">{f"{val:,.0f}" if val>0 else "—"}</div></div>'
                    row += '</div>'; st.markdown(row, unsafe_allow_html=True)
                tot = '<div style="display:grid;grid-template-columns:150px repeat(5,1fr);gap:4px;margin-top:8px;padding-top:8px;border-top:1px solid #1e2535;"><div style="font-size:10px;font-weight:700;color:#475569;font-family:JetBrains Mono,monospace;">TOTAL</div>'
                for b, bc in zip(buckets, bkt_cols): tot += f'<div style="text-align:center;font-size:11px;font-weight:800;color:{bc};font-family:JetBrains Mono,monospace;">{expiry_df[b].sum():,.0f}</div>'
                tot += '</div>'; st.markdown(tot, unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid #161d2e;margin:14px 0;">', unsafe_allow_html=True)

        if not fill_df.empty:
            fill_rate_map = dict(zip(fill_df["CFA"], fill_df["Fill Rate %"]))
            merged["Fill Rate %"] = merged["CFA Warehouse"].map(fill_rate_map).fillna(0.0)
        else:
            merged["Fill Rate %"] = 0.0

        batch_lookup = {}
        if not df_cfa.empty and "Item SKU" in df_cfa.columns:
            for (sku, wh), grp in df_cfa.groupby(["Item SKU","Warehouse"]):
                batches = []
                for _, r in grp.iterrows():
                    exp = r.get("Expiry Date", None)
                    batches.append({"Batch No": str(r.get("Batch No","—")) if "Batch No" in r.index else "—", "Qty": float(r.get("Qty Available",0)), "Shelf Life %": round(float(r.get("Shelf Life %",0)),1), "Expiry Date": exp.strftime("%d-%b-%Y") if pd.notna(exp) else "—"})
                batch_lookup[(str(sku).strip(), str(wh).strip())] = batches

        def shelf_label(row):
            key = (str(row["Item SKU"]).strip(), str(row["CFA Warehouse"]).strip())
            n   = len(batch_lookup.get(key, [])); avg = row.get("Shelf Life %", 0)
            return f"{avg:.1f}% · {n} batch{'es' if n>1 else ''}" if n else f"{avg:.1f}%"
        merged["Shelf Life"] = merged.apply(shelf_label, axis=1)

        disp_cols = ["Item Name","Item SKU","Category","CFA Warehouse","FG Stock","STN In-Transit","STN Transfers","Shelf Life","Fill Rate %","Open PO Qty","Open Orders","Total Available","Diff"]
        if "Open PO Value (₹)" in merged.columns: disp_cols.insert(disp_cols.index("Diff"), "Open PO Value (₹)")
        disp_cols = [c for c in disp_cols if c in merged.columns]
        df_disp   = merged[disp_cols].copy()

        df_export = merged[["Item Name","Item SKU","Category","CFA Warehouse","FG Stock","STN In-Transit","STN Transfers","Shelf Life %","Fill Rate %","Open PO Qty","Open Orders","Total Available","Diff"] + (["Open PO Value (₹)"] if "Open PO Value (₹)" in merged.columns else [])].copy()
        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as w: df_export.to_excel(w, index=False, sheet_name="CFA Analysis")

        def colour_row(row):
            d = row.get("Diff", 0)
            if pd.isna(d): return [""] * len(row)
            if d < 0: return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
            tot = row.get("Total Available", 1)
            if tot > 0 and d / tot < 0.15: return ["background-color:#2d1f00; color:#fde68a"] * len(row)
            return ["background-color:#061410; color:#d1fae5"] * len(row)

        col_cfg = {"FG Stock": st.column_config.NumberColumn("FG Stock", format="%.0f"), "STN In-Transit": st.column_config.NumberColumn("STN In-Transit 🚚", format="%.0f"), "STN Transfers": st.column_config.NumberColumn("# STNs", format="%d"), "Shelf Life": st.column_config.TextColumn("Shelf Life 📦", help="avg · N batches"), "Fill Rate %": st.column_config.ProgressColumn("Fill Rate % 🎯", min_value=0, max_value=100, format="%.1f%%"), "Open PO Qty": st.column_config.NumberColumn("Open PO Qty", format="%.0f"), "Open Orders": st.column_config.NumberColumn("# Orders", format="%d"), "Total Available": st.column_config.NumberColumn("Total Available", format="%.0f"), "Diff": st.column_config.NumberColumn("Diff ✅", format="%.0f")}
        if "Open PO Value (₹)" in df_disp.columns: col_cfg["Open PO Value (₹)"] = st.column_config.NumberColumn("PO Value (₹)", format="%.0f")

        if "batch_sel_tab2" not in st.session_state: st.session_state["batch_sel_tab2"] = None
        sel_key      = st.session_state.get("batch_sel_tab2")
        lookup_key   = (sel_key[0], sel_key[2]) if sel_key and len(sel_key)==3 else None
        batches_show = batch_lookup.get(lookup_key, []) if lookup_key else []

        if sel_key and batches_show:
            batch_df = pd.DataFrame(batches_show).sort_values("Shelf Life %", ascending=True)
            batch_rows_html = ""
            for _, b in batch_df.iterrows():
                pct = float(b["Shelf Life %"]); bar_w = max(2, int(pct))
                batch_rows_html += f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:7px;"><span style="min-width:130px;max-width:130px;color:#94a3b8;font-family:JetBrains Mono,monospace;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{b["Batch No"]}</span><div style="flex:1;background:#1e2535;border-radius:5px;height:12px;max-width:280px;"><div style="width:{bar_w}%;background:#5bc8c0;height:12px;border-radius:5px;"></div></div><span style="min-width:48px;text-align:right;color:#e2e8f0;font-weight:800;font-family:JetBrains Mono,monospace;font-size:12px;">{pct:.1f}%</span><span style="min-width:88px;text-align:right;color:#64748b;font-family:JetBrains Mono,monospace;font-size:11px;">{b["Qty"]:,.0f} units</span><span style="min-width:96px;color:#475569;font-size:11px;">Exp: {b["Expiry Date"]}</span></div>'
            n_batches = len(batch_df); wh_display = sel_key[2] if len(sel_key) > 2 else ""; sku_display = sel_key[0]
            st.markdown(f'<div style="background:#060d18;border:1.5px solid #5bc8c0;border-radius:14px;padding:16px 20px;margin-bottom:12px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;"><div><div style="font-size:10px;color:#5bc8c0;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:3px;">📦 Batch Shelf Life Breakdown</div><div style="font-size:13px;color:#f1f5f9;font-weight:700;">{wh_display}<span style="color:#818cf8;font-family:JetBrains Mono,monospace;font-size:12px;margin-left:8px;">{sku_display}</span></div></div><div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:6px 14px;font-size:11px;color:#60a5fa;font-family:JetBrains Mono,monospace;font-weight:700;">{n_batches} batch{"es" if n_batches>1 else ""}</div></div>{batch_rows_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#060d18;border:1px dashed #1e2535;border-radius:14px;padding:14px 20px;margin-bottom:12px;text-align:center;color:#334155;font-size:11px;font-family:\'JetBrains Mono\',monospace;">👆 Select a row below to see batch-level shelf life &amp; expiry breakdown</div>', unsafe_allow_html=True)

        hc1, hc2 = st.columns([3, 1])
        with hc1: st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📊 SKU · CFA · FG + STN vs Open PO</span><span class="tbl-badge">{len(df_disp):,} SKUs</span></div>', unsafe_allow_html=True)
        with hc2: st.download_button("⬇  Export", buf2.getvalue(), "CFA_Stock_Analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

        event = st.dataframe(df_disp.style.apply(colour_row, axis=1), use_container_width=True, height=480, hide_index=False, column_config=col_cfg, on_select="rerun", selection_mode="single-row", key="cfa_table")
        selected_rows = event.selection.get("rows", []) if hasattr(event, "selection") else []
        if selected_rows:
            r = df_disp.iloc[selected_rows[0]]
            new_key = (str(r["Item SKU"]).strip(), str(r.get("Item Name","")).strip(), str(r["CFA Warehouse"]).strip())
            if st.session_state.get("batch_sel_tab2") != new_key:
                st.session_state["batch_sel_tab2"] = new_key; st.rerun()

        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-div">Breakdown by CFA Warehouse</div>', unsafe_allow_html=True)
        for cfa_wh in sorted(df_disp["CFA Warehouse"].dropna().astype(str).unique()):
            cfa_data = df_disp[df_disp["CFA Warehouse"] == cfa_wh]
            c_fg = cfa_data["FG Stock"].sum(); c_stn = cfa_data["STN In-Transit"].sum(); c_po = cfa_data["Open PO Qty"].sum(); c_diff = cfa_data["Diff"].sum(); c_short = int((cfa_data["Diff"] < 0).sum())
            label = f"🏭  {cfa_wh}   |   FG: {c_fg:,.0f}  +  STN: {c_stn:,.0f}  −  PO: {c_po:,.0f}  =  Diff: {c_diff:,.0f}   {'⚠️ '+str(c_short)+' shortfall' if c_short else '✅ Healthy'}"
            with st.expander(label, expanded=False):
                st.dataframe(cfa_data.style.apply(colour_row, axis=1), use_container_width=True, height=min(60 + len(cfa_data)*36, 420), hide_index=True, column_config=col_cfg)

        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec-div">📬 Send CFA Report to Telegram</div>', unsafe_allow_html=True)
        _tok = st.session_state.get("tg_token", ""); _cid = st.session_state.get("tg_chat_id", "")
        if not _tok or not _cid:
            st.warning("⚠️ Enter Bot Token and Chat ID in the sidebar to enable Telegram sending.")
        else:
            if st.button("📬  Send CFA Shortfall Report to Telegram", use_container_width=True, key="tg_cfa_btn"):
                _central = {}
                if not df_fg.empty and "Warehouse" in df_fg.columns:
                    _c_rows = df_fg[df_fg["Warehouse"].astype(str).str.strip() == "Central"].copy()
                    if not _c_rows.empty: _central = _c_rows.groupby("Item SKU")["Qty Available"].sum().to_dict()
                _msg = build_cfa_telegram(merged, _central); _ok, _err = _tg_send(_tok, _cid, _msg)
                if _ok: st.success("✅ CFA Shortfall report sent to Telegram!")
                else:   st.error(f"❌ Failed to send: {_err}")

# ═══ TAB 3 — CHANNEL ANALYSIS ════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="formula-bar">
        <span>📐 Formula:</span>
        <b>Stock</b> <span>= Tumkur New Warehouse + YB FG Warehouse</span> <span>−</span>
        <b>Open PO Qty</b> <span>= per Channel (Mapper → Customer Name)</span> <span>=</span> <b>Diff</b>
    </div>
    """, unsafe_allow_html=True)

    if df_mapper.empty:
        st.error("⚠️ Mapper sheet not found or empty.")
    elif df_sos.empty:
        st.error("⚠️ SOS sheet not found or empty.")
    elif df_fg.empty:
        st.error("⚠️ FG Inventory sheet not found or empty.")
    else:
        stock_base = df_fg[df_fg["Warehouse"].astype(str).isin(CHANNEL_STOCK_WAREHOUSES)].copy() if "Warehouse" in df_fg.columns else pd.DataFrame()
        if not stock_base.empty and "Item SKU" in stock_base.columns:
            sku_stock = stock_base.groupby("Item SKU").agg(Item_Name=("Item Name","first"), Category=("Category","first"), Stock_Avail=("Qty Available","sum")).reset_index()
            sku_stock.columns = ["Item SKU","Item Name","Category","Stock Available"]
        else:
            sku_stock = pd.DataFrame(columns=["Item SKU","Item Name","Category","Stock Available"])

        cust_col_m    = next((c for c in df_mapper.columns if "customer" in c.lower() or "party" in c.lower()), None)
        channel_col_m = next((c for c in df_mapper.columns if "channel" in c.lower()), None)
        if not cust_col_m or not channel_col_m:
            st.error(f"⚠️ Mapper must have Customer Name + Channel columns. Found: {list(df_mapper.columns)}"); st.stop()

        mapper_clean = df_mapper[[cust_col_m, channel_col_m]].copy()
        mapper_clean.columns = ["Customer Name","Channel"]
        mapper_clean["Customer Name"] = mapper_clean["Customer Name"].astype(str).str.strip()
        mapper_clean["Channel"]       = mapper_clean["Channel"].astype(str).str.strip()
        customer_channel_map          = dict(zip(mapper_clean["Customer Name"], mapper_clean["Channel"]))

        sku_col_so  = next((c for c in df_sos.columns if "product sku"  in c.lower()), None)
        cust_col_so = next((c for c in df_sos.columns if "customer" in c.lower() or "party" in c.lower()), None)
        qty_col_so  = next((c for c in df_sos.columns if "order qty"    in c.lower()), None)
        dsp_col_so  = next((c for c in df_sos.columns if "dispatch qty" in c.lower()), None)
        nm_col_so   = next((c for c in df_sos.columns if "item name"    in c.lower() or "product name" in c.lower()), None)
        if not sku_col_so or not qty_col_so:
            st.error(f"⚠️ SOS missing Product SKU / Order Qty. Found: {list(df_sos.columns)}"); st.stop()

        open_sos = df_sos[~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)].copy() if "SO Status" in df_sos.columns else df_sos.copy()
        open_sos["_sku"]       = open_sos[sku_col_so].astype(str).str.strip()
        open_sos["_customer"]  = open_sos[cust_col_so].astype(str).str.strip() if cust_col_so else ""
        open_sos["_channel"]   = open_sos["_customer"].map(customer_channel_map).fillna("Unknown")
        open_sos["_order_qty"] = pd.to_numeric(open_sos[qty_col_so], errors="coerce").fillna(0)
        open_sos["_dispatch"]  = pd.to_numeric(open_sos[dsp_col_so], errors="coerce").fillna(0) if dsp_col_so else 0
        open_sos["_item_name"] = open_sos[nm_col_so].astype(str).str.strip() if nm_col_so else open_sos["_sku"]

        all_channels = sorted([c for c in open_sos["_channel"].unique() if c not in ("Unknown", "Offline")])
        if "Unknown" in open_sos["_channel"].values: all_channels.append("Unknown")

        if not all_channels:
            st.warning("⚠️ No channel data found. Check Mapper customer names match SOS.")
        else:
            # ── Per-channel overview cards ─────────────────────────────────────
            _ch_cards_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:11px;margin-bottom:16px;">'
            for _ch in all_channels:
                _ch_d = open_sos[open_sos["_channel"] == _ch]
                _ch_skus = _ch_d.groupby("_sku").agg(po=("_order_qty","sum")).reset_index()
                _ch_skus = _ch_skus.merge(sku_stock[["Item SKU","Stock Available"]].rename(columns={"Item SKU":"_sku"}), on="_sku", how="left")
                _ch_skus["Stock Available"] = _ch_skus["Stock Available"].fillna(0)
                _ch_skus["diff"] = _ch_skus["Stock Available"] - _ch_skus["po"]
                _ch_po = float(_ch_skus["po"].sum()); _ch_stock = float(_ch_skus["Stock Available"].sum())
                _ch_diff = _ch_stock - _ch_po; _ch_short_n = int((_ch_skus["diff"] < 0).sum()); _ch_cust_n = int(_ch_d["_customer"].nunique())
                if _ch_short_n > 0:
                    _dot="🔴"; _border="#7f1d1d"; _bg="linear-gradient(135deg,#1a0000,#2a0808)"; _dcolor="#fca5a5"; _dlabel="color:#f87171"
                elif _ch_diff / max(_ch_stock,1) < 0.15:
                    _dot="🟡"; _border="#78350f"; _bg="linear-gradient(135deg,#1a1000,#2a1800)"; _dcolor="#fde68a"; _dlabel="color:#f59e0b"
                else:
                    _dot="🟢"; _border="#14532d"; _bg="linear-gradient(135deg,#061a0a,#0a2e12)"; _dcolor="#bbf7d0"; _dlabel="color:#22c55e"
                _bar_bg = "linear-gradient(90deg,#ef4444,#f87171)" if _ch_short_n>0 else "linear-gradient(90deg,#f59e0b,#fbbf24)" if _ch_diff/max(_ch_stock,1)<0.15 else "linear-gradient(90deg,#22c55e,#4ade80)"
                _ch_cards_html += f'<div style="background:{_bg};border:1px solid {_border};border-radius:14px;padding:14px 16px;position:relative;overflow:hidden;"><div style="position:absolute;top:0;left:0;right:0;height:3px;background:{_bar_bg};border-radius:14px 14px 0 0;"></div><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"><span style="font-size:11px;font-weight:800;color:#f1f5f9;">{_dot} {_ch}</span><span style="font-size:10px;{_dlabel};font-weight:700;font-family:\'JetBrains Mono\',monospace;">{_ch_short_n} short</span></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;"><div><div style="font-size:9px;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Stock</div><div style="font-size:15px;font-weight:800;color:#e2e8f0;font-family:\'JetBrains Mono\',monospace;line-height:1.2;">{_ch_stock:,.0f}</div></div><div><div style="font-size:9px;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Open PO</div><div style="font-size:15px;font-weight:800;color:#e2e8f0;font-family:\'JetBrains Mono\',monospace;line-height:1.2;">{_ch_po:,.0f}</div></div><div><div style="font-size:9px;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Diff</div><div style="font-size:14px;font-weight:800;color:{_dcolor};font-family:\'JetBrains Mono\',monospace;line-height:1.2;">{_ch_diff:+,.0f}</div></div><div><div style="font-size:9px;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Customers</div><div style="font-size:14px;font-weight:800;color:#94a3b8;font-family:\'JetBrains Mono\',monospace;line-height:1.2;">{_ch_cust_n}</div></div></div></div>'
            _ch_cards_html += '</div>'
            st.markdown(_ch_cards_html, unsafe_allow_html=True)

            show_shortfall_only = st.toggle("⚠️ Show shortfall SKUs only", value=False, key="ch_shortfall_toggle")

            # ── Channel tabs — "All" is FIRST ───────────────────────────────────
            def _ch_status_dot(ch):
                _ch_d = open_sos[open_sos['_channel'] == ch].copy()
                _ch_skus = _ch_d.groupby('_sku').agg(po=('_order_qty','sum')).reset_index()
                _ch_skus = _ch_skus.merge(sku_stock[['Item SKU','Stock Available']].rename(columns={'Item SKU':'_sku'}), on='_sku', how='left')
                _ch_skus['Stock Available'] = _ch_skus['Stock Available'].fillna(0)
                _ch_skus['diff'] = _ch_skus['Stock Available'] - _ch_skus['po']
                n_short = (_ch_skus['diff'] < 0).sum(); n_tight = ((_ch_skus['diff'] >= 0) & (_ch_skus['diff'] / _ch_skus['Stock Available'].clip(lower=1) < 0.15)).sum()
                if n_short > 0:  return f'🔴  {ch}  ({n_short} short)'
                if n_tight > 0:  return f'🟡  {ch}  ({n_tight} tight)'
                return f'🟢  {ch}'

            ch_tab_labels = ["🌐  All Channels"] + [_ch_status_dot(ch) for ch in all_channels]
            ch_tabs = st.tabs(ch_tab_labels)

            # ── HELPER: render one channel's content ──────────────────────────
            def render_channel_tab(channel, ch_sos):
                if ch_sos.empty:
                    st.info(f"No open orders found for channel: {channel}"); return

                ch_sku_agg = ch_sos.groupby("_sku").agg(Item_Name=("_item_name","first"), Open_PO=("_order_qty","sum"), Dispatched=("_dispatch","sum"), Num_Orders=("_order_qty","count"), Num_Custs=("_customer","nunique"), Customers=("_customer", lambda x: ", ".join(sorted(x.unique())))).reset_index()
                ch_sku_agg.columns = ["Item SKU","Item Name","Open PO Qty","Dispatch Qty","# Orders","# Customers","Customer Names"]
                ch_sku_agg = ch_sku_agg.merge(sku_stock[["Item SKU","Category","Stock Available"]], on="Item SKU", how="left")
                ch_sku_agg["Stock Available"] = ch_sku_agg["Stock Available"].fillna(0)
                ch_sku_agg["Diff (Stock−PO)"] = ch_sku_agg["Stock Available"] - ch_sku_agg["Open PO Qty"]
                ch_sku_agg["Days of Stock"]   = ch_sku_agg.apply(lambda r: round(r["Stock Available"] / (r["Open PO Qty"] / 26), 1) if r["Open PO Qty"] > 0 else 0.0, axis=1)
                ch_sku_agg = ch_sku_agg.sort_values("Diff (Stock−PO)", ascending=True)
                if show_shortfall_only: ch_sku_agg = ch_sku_agg[ch_sku_agg["Diff (Stock−PO)"] < 0]

                c_stock = ch_sku_agg["Stock Available"].sum(); c_po = ch_sku_agg["Open PO Qty"].sum()
                c_diff  = ch_sku_agg["Diff (Stock−PO)"].sum(); c_short_n = int((ch_sku_agg["Diff (Stock−PO)"] < 0).sum()); c_cust_n = ch_sos["_customer"].nunique()
                k1,k2,k3,k4,k5 = st.columns(5)
                k1.metric("Stock Available", f"{c_stock:,.0f}"); k2.metric("Open PO Qty", f"{c_po:,.0f}")
                k3.metric("Net Diff", f"{c_diff:,.0f}", delta=f"{'Surplus' if c_diff>=0 else 'Shortfall'}: {abs(c_diff):,.0f}", delta_color="normal" if c_diff>=0 else "inverse")
                k4.metric("Shortfall SKUs", f"{c_short_n}"); k5.metric("Customers", f"{c_cust_n}")
                st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

                if ch_sku_agg.empty:
                    st.info("No shortfall SKUs." if show_shortfall_only else "No SKUs found."); return

                ch_search_key = f"ch_search_{channel}"
                ch_search = st.text_input("sku_search", placeholder="🔍 Search SKU / item name…", label_visibility="collapsed", key=ch_search_key)
                if ch_search:
                    ch_sku_agg = ch_sku_agg[ch_sku_agg["Item Name"].str.contains(ch_search, case=False, na=False) | ch_sku_agg["Item SKU"].str.contains(ch_search, case=False, na=False)]

                def _colour(row, diff_col="Diff (Stock−PO)"):
                    d = row.get(diff_col, 0)
                    if pd.isna(d): return [""] * len(row)
                    if d < 0: return ["background-color:#2d0a0a;color:#fca5a5"] * len(row)
                    tot = row.get("Stock Available", 1)
                    if tot > 0 and d / max(tot,1) < 0.15: return ["background-color:#2d1f00;color:#fde68a"] * len(row)
                    return ["background-color:#061410;color:#d1fae5"] * len(row)

                sku_col_cfg = {"Open PO Qty": st.column_config.NumberColumn("Open PO Qty", format="%.0f"), "Dispatch Qty": st.column_config.NumberColumn("Dispatch Qty", format="%.0f"), "Stock Available": st.column_config.NumberColumn("Stock Available", format="%.0f"), "Diff (Stock−PO)": st.column_config.NumberColumn("Diff (Stock−PO)", format="%.0f"), "Days of Stock": st.column_config.NumberColumn("Days of Stock", format="%.1f"), "# Orders": st.column_config.NumberColumn("# Orders", format="%d"), "# Customers": st.column_config.NumberColumn("# Customers", format="%d"), "Customer Names": st.column_config.TextColumn("Customers")}

                disp_sku = ch_sku_agg[["Item Name","Item SKU","Category","Open PO Qty","Dispatch Qty","Stock Available","Diff (Stock−PO)","Days of Stock","# Orders","# Customers","Customer Names"]].copy()

                cust_detail = ch_sos.groupby(["_sku","_customer"]).agg(Item_Name=("_item_name","first"), Open_PO=("_order_qty","sum"), Dispatched=("_dispatch","sum"), Num_Orders=("_order_qty","count")).reset_index()
                cust_detail.columns = ["Item SKU","Customer Name","Item Name","Open PO Qty","Dispatch Qty","# Orders"]
                cust_detail = cust_detail.merge(sku_stock[["Item SKU","Category","Stock Available"]], on="Item SKU", how="left")
                cust_detail["Stock Available"] = cust_detail["Stock Available"].fillna(0)
                cust_detail["Diff (Stock−PO)"] = cust_detail["Stock Available"] - cust_detail["Open PO Qty"]
                cust_detail["Channel"]         = channel
                cust_detail = cust_detail.sort_values(["Diff (Stock−PO)","Item SKU"], ascending=[True,True])
                cust_disp_all   = cust_detail[["Item Name","Item SKU","Category","Customer Name","Channel","Open PO Qty","Dispatch Qty","Stock Available","Diff (Stock−PO)","# Orders"]].copy()
                cust_disp_short = cust_disp_all[cust_disp_all["Diff (Stock−PO)"] < 0].copy()
                cust_col_cfg = {"Open PO Qty": st.column_config.NumberColumn("Open PO Qty", format="%.0f"), "Dispatch Qty": st.column_config.NumberColumn("Dispatch Qty", format="%.0f"), "Stock Available": st.column_config.NumberColumn("Stock Available", format="%.0f"), "Diff (Stock−PO)": st.column_config.NumberColumn("Diff (Stock−PO)", format="%.0f"), "# Orders": st.column_config.NumberColumn("# Orders", format="%d")}

                _central_stock_df = df_fg[df_fg["Warehouse"].astype(str).isin(["Central"])].copy() if "Warehouse" in df_fg.columns else pd.DataFrame()
                if not _central_stock_df.empty and "Item SKU" in _central_stock_df.columns:
                    _central_agg = _central_stock_df.groupby("Item SKU")["Qty Available"].sum().reset_index(); _central_agg.columns = ["Item SKU","Central Stock"]
                else:
                    _central_agg = pd.DataFrame(columns=["Item SKU","Central Stock"])

                _short_sku_agg = cust_disp_short.groupby(["Item SKU","Item Name","Category"]).agg(Total_PO=("Open PO Qty","sum"), Total_Stock=("Stock Available","first"), Total_Short=("Diff (Stock−PO)","sum"), Customers=("Customer Name", lambda x: ", ".join(sorted(x.unique())))).reset_index() if not cust_disp_short.empty else pd.DataFrame()

                if not _short_sku_agg.empty:
                    _short_sku_agg["Shortfall Qty"] = _short_sku_agg["Total_Short"].abs()
                    _short_sku_agg = _short_sku_agg.merge(_central_agg, on="Item SKU", how="left"); _short_sku_agg["Central Stock"] = _short_sku_agg["Central Stock"].fillna(0)
                    def _stn_status(row):
                        c = row["Central Stock"]; s = row["Shortfall Qty"]
                        if c <= 0: return "❌ Not Possible"
                        if c >= s: return "✅ STN Possible"
                        return f"⚠️ Partial ({c:,.0f} of {s:,.0f})"
                    _short_sku_agg["STN Status"]    = _short_sku_agg.apply(_stn_status, axis=1)
                    _short_sku_agg["STN Qty"]       = _short_sku_agg.apply(lambda r: min(r["Central Stock"], r["Shortfall Qty"]), axis=1)
                    _short_sku_agg["Remaining Gap"] = (_short_sku_agg["Shortfall Qty"] - _short_sku_agg["STN Qty"]).clip(lower=0)
                    stn_disp = _short_sku_agg[["Item Name","Item SKU","Category","Total_Stock","Total_PO","Shortfall Qty","Central Stock","STN Qty","Remaining Gap","STN Status","Customers"]].copy()
                    stn_disp.columns = ["Item Name","Item SKU","Category","Tumkur+YB Stock","Open PO Qty","Shortfall Qty","Central Stock","STN Qty","Remaining Gap","STN Status","Customers"]
                    stn_disp = stn_disp.sort_values("STN Status", ascending=True)
                else:
                    stn_disp = pd.DataFrame()

                buf_ch = io.BytesIO(); buf_short = io.BytesIO()

                try:
                    import plotly.graph_objects as go
                    bar_data = ch_sku_agg[ch_sku_agg["Diff (Stock−PO)"] < 0].nsmallest(15, "Diff (Stock−PO)")
                    if not bar_data.empty:
                        vc1, vc2 = st.columns([2, 1])
                        with vc1:
                            fig_bar = go.Figure()
                            fig_bar.add_bar(x=bar_data["Item SKU"].tolist(), y=bar_data["Stock Available"], name="Stock", marker_color="#2dd4bf", opacity=0.85)
                            fig_bar.add_bar(x=bar_data["Item SKU"].tolist(), y=bar_data["Open PO Qty"], name="Open PO", marker_color="#f87171", opacity=0.85)
                            fig_bar.update_layout(barmode="group", height=260, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8",size=10), legend=dict(orientation="h",y=1.1,font=dict(size=10)), margin=dict(l=10,r=10,t=30,b=60), title=dict(text="📊 Top Shortfall SKUs — Stock vs Open PO", font=dict(size=11,color="#e2e8f0"),x=0), xaxis=dict(tickangle=-35,gridcolor="#1e2535"), yaxis=dict(gridcolor="#1e2535"))
                            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})
                        with vc2:
                            stn_donut_placeholder = st.empty()
                    else:
                        stn_donut_placeholder = None
                except Exception:
                    stn_donut_placeholder = None

                hch1, hch2 = st.columns([4, 1])
                with hch1: st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📊 {channel} — SKU Summary</span><span class="tbl-badge">{len(disp_sku):,} SKUs</span></div>', unsafe_allow_html=True)
                with hch2: full_dl_placeholder = st.empty()

                sku_event = st.dataframe(disp_sku.style.apply(_colour, axis=1), use_container_width=True, height=360, hide_index=False, column_config=sku_col_cfg, on_select="rerun", selection_mode="single-row", key=f"sku_tbl_{channel}")

                sel_sku_rows = sku_event.selection.get("rows", []) if hasattr(sku_event,"selection") else []
                if sel_sku_rows:
                    sel_sku_row = disp_sku.iloc[sel_sku_rows[0]]; sel_sku_code = sel_sku_row["Item SKU"]
                    sel_sku_stock = float(sel_sku_row["Stock Available"]); sel_sku_po = float(sel_sku_row["Open PO Qty"]); sel_sku_diff = float(sel_sku_row["Diff (Stock−PO)"])
                    sku_cust_rows = cust_disp_all[cust_disp_all["Item SKU"] == sel_sku_code].copy()
                    _cen_sel = df_fg[df_fg["Warehouse"].astype(str).isin(["Central"]) & (df_fg["Item SKU"].astype(str) == sel_sku_code)]["Qty Available"].sum() if "Warehouse" in df_fg.columns else 0
                    stn_txt = "✅ STN Possible" if _cen_sel >= abs(sel_sku_diff) else f"⚠️ Partial ({_cen_sel:,.0f} available)" if _cen_sel > 0 else "❌ Not Possible"
                    stn_color = "#22c55e" if _cen_sel >= abs(sel_sku_diff) else "#f59e0b" if _cen_sel > 0 else "#ef4444"
                    status_icon = "🔴" if sel_sku_diff < 0 else "🟡" if sel_sku_diff / max(sel_sku_stock,1) < 0.15 else "🟢"
                    st.markdown(f"""<div style="background:#060d18;border:1.5px solid #5bc8c0;border-radius:14px;padding:16px 20px;margin:12px 0;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;"><div><div style="font-size:10px;color:#5bc8c0;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:3px;">{status_icon} Selected SKU</div><div style="font-size:14px;color:#f1f5f9;font-weight:800;">{sel_sku_row["Item Name"]}</div><div style="font-size:11px;color:#818cf8;font-family:'JetBrains Mono',monospace;margin-top:2px;">{sel_sku_code}</div></div><div style="display:flex;gap:12px;flex-wrap:wrap;"><div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:10px;padding:8px 14px;text-align:center;"><div style="font-size:9px;color:#60a5fa;font-weight:700;text-transform:uppercase;">Stock</div><div style="font-size:16px;font-weight:800;color:#bfdbfe;font-family:'JetBrains Mono',monospace;">{sel_sku_stock:,.0f}</div></div><div style="background:#1a0a00;border:1px solid #78350f;border-radius:10px;padding:8px 14px;text-align:center;"><div style="font-size:9px;color:#fbbf24;font-weight:700;text-transform:uppercase;">Open PO</div><div style="font-size:16px;font-weight:800;color:#fde68a;font-family:'JetBrains Mono',monospace;">{sel_sku_po:,.0f}</div></div><div style="background:{"#2d0a0a" if sel_sku_diff<0 else "#061a0a"};border:1px solid {"#7f1d1d" if sel_sku_diff<0 else "#14532d"};border-radius:10px;padding:8px 14px;text-align:center;"><div style="font-size:9px;color:{"#f87171" if sel_sku_diff<0 else "#4ade80"};font-weight:700;text-transform:uppercase;">Diff</div><div style="font-size:16px;font-weight:800;color:{"#fca5a5" if sel_sku_diff<0 else "#bbf7d0"};font-family:'JetBrains Mono',monospace;">{sel_sku_diff:,.0f}</div></div><div style="background:#060d18;border:1px solid #1e3a5f;border-radius:10px;padding:8px 14px;text-align:center;"><div style="font-size:9px;color:#94a3b8;font-weight:700;text-transform:uppercase;">Central WH</div><div style="font-size:14px;font-weight:800;color:#e2e8f0;font-family:'JetBrains Mono',monospace;">{_cen_sel:,.0f}</div><div style="font-size:10px;font-weight:700;color:{stn_color};margin-top:2px;">{stn_txt}</div></div></div></div></div>""", unsafe_allow_html=True)
                    p1, p2 = st.columns([1,1])
                    with p1:
                        st.markdown('<div class="sec-div">👤 Customers for this SKU</div>', unsafe_allow_html=True)
                        st.dataframe(sku_cust_rows[["Customer Name","Open PO Qty","Dispatch Qty","Stock Available","Diff (Stock−PO)","# Orders"]].style.apply(_colour, axis=1), use_container_width=True, height=min(60+len(sku_cust_rows)*36,280), hide_index=True, column_config=cust_col_cfg)
                    with p2:
                        try:
                            import plotly.graph_objects as go
                            fig_cust = go.Figure(go.Bar(x=sku_cust_rows["Customer Name"].tolist(), y=sku_cust_rows["Open PO Qty"].tolist(), marker_color=["#f87171" if d<0 else "#2dd4bf" for d in sku_cust_rows["Diff (Stock−PO)"]], text=sku_cust_rows["Open PO Qty"].apply(lambda v: f"{v:,.0f}"), textposition="outside"))
                            fig_cust.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8",size=10), margin=dict(l=10,r=10,t=30,b=60), title=dict(text="Open PO by Customer", font=dict(size=11,color="#e2e8f0"),x=0), xaxis=dict(tickangle=-30,gridcolor="#1e2535"), yaxis=dict(gridcolor="#1e2535"))
                            st.plotly_chart(fig_cust, use_container_width=True, config={"displayModeBar":False})
                        except Exception: pass

                st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
                n_short_rows = len(cust_disp_short)
                short_badge_color = "#7f1d1d" if n_short_rows > 0 else "#14532d"; short_badge_text = "#fca5a5" if n_short_rows > 0 else "#bbf7d0"
                sh1, sh2 = st.columns([4, 1])
                with sh1: st.markdown(f'<div style="display:flex;align-items:center;gap:8px;padding:8px 0 6px;"><span style="font-size:10px;font-weight:700;color:#ef4444;text-transform:uppercase;letter-spacing:1.2px;">⚠️ Shortfall SKUs — Customer Detail</span><span style="background:{short_badge_color};border:1px solid {short_badge_text}33;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800;color:{short_badge_text};font-family:\'JetBrains Mono\',monospace;">{n_short_rows} rows</span></div>', unsafe_allow_html=True)
                with sh2: short_dl_placeholder = st.empty()

                if cust_disp_short.empty:
                    st.markdown('<div style="background:#061a0a;border:1px solid #14532d;border-radius:10px;padding:14px 18px;text-align:center;color:#4ade80;font-size:12px;font-weight:700;">✅ No shortfall SKUs for this channel</div>', unsafe_allow_html=True)
                else:
                    st.dataframe(cust_disp_short.style.apply(_colour, axis=1), use_container_width=True, height=min(80 + len(cust_disp_short) * 36, 420), hide_index=True, column_config=cust_col_cfg)

                st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
                def _stn_colour(row):
                    s = str(row.get("STN Status",""))
                    if s.startswith("✅"): return ["background-color:#061a0a;color:#d1fae5"] * len(row)
                    if s.startswith("⚠️"): return ["background-color:#2d1f00;color:#fde68a"] * len(row)
                    return ["background-color:#2d0a0a;color:#fca5a5"] * len(row)

                if stn_disp.empty:
                    st.markdown('<div style="background:#061a0a;border:1px solid #14532d;border-radius:10px;padding:14px 18px;text-align:center;color:#4ade80;font-size:12px;font-weight:700;">✅ No shortfall — STN check not required</div>', unsafe_allow_html=True)
                else:
                    n_possible = int((stn_disp["STN Status"].str.startswith("✅")).sum()); n_partial = int((stn_disp["STN Status"].str.startswith("⚠️")).sum()); n_not = int((stn_disp["STN Status"].str.startswith("❌")).sum())
                    st.markdown(f'<div style="background:#060d18;border:1.5px solid #1e3a5f;border-radius:14px;padding:14px 18px;margin-bottom:12px;"><div style="font-size:10px;font-weight:700;color:#60a5fa;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">🚚 STN Feasibility — Can Central WH cover the shortfall?</div><div style="display:flex;gap:18px;flex-wrap:wrap;"><span style="background:#061a0a;border:1px solid #14532d;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:800;color:#4ade80;">✅ Possible: {n_possible}</span><span style="background:#2d1f00;border:1px solid #78350f;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:800;color:#fde68a;">⚠️ Partial: {n_partial}</span><span style="background:#2d0a0a;border:1px solid #7f1d1d;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:800;color:#fca5a5;">❌ Not Possible: {n_not}</span></div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">🏭 Central WH → STN Feasibility</span><span class="tbl-badge">{len(stn_disp):,} SKUs</span></div>', unsafe_allow_html=True)
                    st.dataframe(stn_disp.style.apply(_stn_colour, axis=1), use_container_width=True, height=min(80 + len(stn_disp) * 36, 460), hide_index=True, column_config={"Tumkur+YB Stock": st.column_config.NumberColumn("Tumkur+YB Stock", format="%.0f"), "Open PO Qty": st.column_config.NumberColumn("Open PO Qty", format="%.0f"), "Shortfall Qty": st.column_config.NumberColumn("Shortfall Qty", format="%.0f"), "Central Stock": st.column_config.NumberColumn("Central Stock", format="%.0f"), "STN Qty": st.column_config.NumberColumn("STN Qty", format="%.0f"), "Remaining Gap": st.column_config.NumberColumn("Remaining Gap", format="%.0f"), "STN Status": st.column_config.TextColumn("STN Status"), "Customers": st.column_config.TextColumn("Customers")})

                if stn_donut_placeholder is not None and not stn_disp.empty:
                    try:
                        import plotly.graph_objects as go
                        _n_pos = int((stn_disp["STN Status"].str.startswith("✅")).sum()); _n_part = int((stn_disp["STN Status"].str.startswith("⚠️")).sum()); _n_no = int((stn_disp["STN Status"].str.startswith("❌")).sum())
                        fig_donut = go.Figure(go.Pie(labels=["✅ Possible","⚠️ Partial","❌ Not Possible"], values=[_n_pos, _n_part, _n_no], hole=0.6, marker_colors=["#22c55e","#f59e0b","#ef4444"], textinfo="label+value", textfont=dict(size=10, color="#e2e8f0")))
                        fig_donut.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(l=10,r=10,t=30,b=10), title=dict(text="🚚 STN Coverage", font=dict(size=11,color="#e2e8f0"),x=0.5,xanchor="center"), annotations=[dict(text=f"{_n_pos+_n_part+_n_no}<br>SKUs", x=0.5, y=0.5, font_size=13, font_color="#e2e8f0", showarrow=False)])
                        with stn_donut_placeholder: st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar":False})
                    except Exception: pass

                with pd.ExcelWriter(buf_ch, engine="openpyxl") as wx:
                    disp_sku.to_excel(wx, index=False, sheet_name="SKU Summary")
                    cust_disp_short.to_excel(wx, index=False, sheet_name="Shortfall Detail")
                    (stn_disp if not stn_disp.empty else pd.DataFrame()).to_excel(wx, index=False, sheet_name="STN Feasibility")
                    cust_disp_all.to_excel(wx, index=False, sheet_name="All Customer Detail")
                with pd.ExcelWriter(buf_short, engine="openpyxl") as wx:
                    cust_disp_short.to_excel(wx, index=False, sheet_name="Shortfall SKUs")
                    (stn_disp if not stn_disp.empty else pd.DataFrame()).to_excel(wx, index=False, sheet_name="STN Feasibility")

                with full_dl_placeholder: st.download_button("⬇ Full Export", buf_ch.getvalue(), f"Channel_{channel}_Full.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, help="4 sheets: SKU Summary · Shortfall · STN · All Customers", key=f"full_dl_{channel}")
                with short_dl_placeholder: st.download_button("⬇ Shortfall", buf_short.getvalue(), f"Shortfall_{channel}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, help="Shortfall SKUs + STN Feasibility", key=f"short_dl_{channel}")

                st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
                with st.expander(f"📋 View all {len(cust_disp_all):,} customer rows ({channel})", expanded=False):
                    st.dataframe(cust_disp_all.style.apply(_colour, axis=1), use_container_width=True, height=min(80 + len(cust_disp_all) * 36, 520), hide_index=True, column_config=cust_col_cfg)

            # ── ALL CHANNELS tab ──────────────────────────────────────────────
            with ch_tabs[0]:
                all_sos = open_sos.copy()
                all_sos["_channel_label"] = all_sos["_channel"]  # keep channel info visible
                render_channel_tab("All Channels", all_sos)

            # ── Individual channel tabs ───────────────────────────────────────
            for ch_tab, channel in zip(ch_tabs[1:], all_channels):
                with ch_tab:
                    ch_sos = open_sos[open_sos["_channel"] == channel].copy()
                    render_channel_tab(channel, ch_sos)

# ═══ TAB 4 ═══════════════════════════════════════════════════════════════════
with tab4:
    import urllib.request, urllib.parse, json as _json

    st.markdown("""
    <div class="formula-bar">
        <span>📐 Logic:</span>
        <b>Reorder Needed</b> <span>= Current Stock &lt; Min Stock (from Reorder sheet)</span>
        <span> · </span>
        <b>Suggest Qty</b> <span>= Reorder Qty − Current Stock</span>
    </div>
    """, unsafe_allow_html=True)

    def send_telegram(token, chat_id, text):
        try:
            url  = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
            req  = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=10)
            return True, "✅ Sent!"
        except Exception as e:
            return False, f"❌ Failed: {e}"

    if not df_fg.empty and "Item SKU" in df_fg.columns:
        curr_stock = df_fg.groupby("Item SKU").agg(Item_Name=("Item Name","first"), Category=("Category","first"), Curr_Stock=("Qty Available","sum")).reset_index()
        curr_stock.columns = ["Item SKU","Item Name","Category","Current Stock"]
    else:
        curr_stock = pd.DataFrame(columns=["Item SKU","Item Name","Category","Current Stock"])

    if df_reorder.empty:
        st.warning("⚠️ No **Reorder** sheet found. Create a sheet named **Reorder** with columns: Item SKU, Min Stock, Reorder Qty.")
    else:
        sku_col_r = next((c for c in df_reorder.columns if "sku" in c.lower() or "item" in c.lower()), None)
        min_col_r = next((c for c in df_reorder.columns if "min" in c.lower()), None)
        req_col_r = next((c for c in df_reorder.columns if "reorder" in c.lower() or "suggest" in c.lower() or "qty" in c.lower()), None)
        if not sku_col_r:
            st.error(f"⚠️ Reorder sheet must have an Item SKU column. Found: {list(df_reorder.columns)}")
        else:
            reorder_clean = df_reorder.copy()
            reorder_clean = reorder_clean.rename(columns={sku_col_r: "Item SKU", **({"Min Stock": min_col_r} if min_col_r else {}), **({"Reorder Qty": req_col_r} if req_col_r else {})})
            if min_col_r and min_col_r != "Min Stock":     reorder_clean = reorder_clean.rename(columns={min_col_r: "Min Stock"})
            if req_col_r and req_col_r != "Reorder Qty":   reorder_clean = reorder_clean.rename(columns={req_col_r: "Reorder Qty"})
            reorder_clean["Item SKU"] = reorder_clean["Item SKU"].astype(str).str.strip()
            if "Min Stock"   not in reorder_clean.columns: reorder_clean["Min Stock"]   = 0
            if "Reorder Qty" not in reorder_clean.columns: reorder_clean["Reorder Qty"] = 0

            merged_ro = reorder_clean.merge(curr_stock[["Item SKU","Item Name","Category","Current Stock"]], on="Item SKU", how="left")
            merged_ro["Current Stock"] = merged_ro["Current Stock"].fillna(0)
            merged_ro["Gap"]           = merged_ro["Current Stock"] - merged_ro["Min Stock"]
            merged_ro["Suggest Qty"]   = (merged_ro["Reorder Qty"] - merged_ro["Current Stock"]).clip(lower=0)
            merged_ro["Status"]        = merged_ro["Gap"].apply(lambda g: "🔴 Reorder Now" if g < 0 else "🟡 Getting Low" if g < merged_ro["Min Stock"].median() * 0.2 else "🟢 OK")

            n_critical = int((merged_ro["Status"] == "🔴 Reorder Now").sum()); n_low = int((merged_ro["Status"] == "🟡 Getting Low").sum()); n_ok = int((merged_ro["Status"] == "🟢 OK").sum()); total_suggest = merged_ro["Suggest Qty"].sum()
            st.markdown(f"""
            <div class="kpi-row" style="grid-template-columns:repeat(4,1fr);">
              <div class="kpi-box red"><div class="kpi-inner"><div><div class="kpi-label">Reorder Now</div><div class="kpi-value">{n_critical}</div><div class="kpi-sub">Below Min Stock</div></div><div class="kpi-ico">🔴</div></div></div>
              <div class="kpi-box amber"><div class="kpi-inner"><div><div class="kpi-label">Getting Low</div><div class="kpi-value">{n_low}</div><div class="kpi-sub">Near threshold</div></div><div class="kpi-ico">🟡</div></div></div>
              <div class="kpi-box green"><div class="kpi-inner"><div><div class="kpi-label">Stock OK</div><div class="kpi-value">{n_ok}</div><div class="kpi-sub">Above Min Stock</div></div><div class="kpi-ico">🟢</div></div></div>
              <div class="kpi-box blue"><div class="kpi-inner"><div><div class="kpi-label">Total Suggest Qty</div><div class="kpi-value">{total_suggest:,.0f}</div><div class="kpi-sub">Units to produce/order</div></div><div class="kpi-ico">📋</div></div></div>
            </div>
            """, unsafe_allow_html=True)

            ro_filter = st.radio("Show:", ["All SKUs","🔴 Reorder Now only","🔴+🟡 Needs attention"], horizontal=True, key="ro_filter")
            if ro_filter == "🔴 Reorder Now only":     merged_ro = merged_ro[merged_ro["Status"] == "🔴 Reorder Now"]
            elif ro_filter == "🔴+🟡 Needs attention": merged_ro = merged_ro[merged_ro["Status"].isin(["🔴 Reorder Now","🟡 Getting Low"])]
            merged_ro = merged_ro.sort_values("Gap", ascending=True)

            def _ro_colour(row):
                s = str(row.get("Status",""))
                if "🔴" in s: return ["background-color:#2d0a0a;color:#fca5a5"] * len(row)
                if "🟡" in s: return ["background-color:#2d1f00;color:#fde68a"] * len(row)
                return ["background-color:#061410;color:#d1fae5"] * len(row)

            ro_disp_cols = ["Item Name","Item SKU","Category","Current Stock","Min Stock","Reorder Qty","Gap","Suggest Qty","Status"]
            ro_disp_cols = [c for c in ro_disp_cols if c in merged_ro.columns]

            buf_ro = io.BytesIO()
            with pd.ExcelWriter(buf_ro, engine="openpyxl") as wx: merged_ro[ro_disp_cols].to_excel(wx, index=False, sheet_name="Reorder Suggestions")

            stn_rows = []
            if not df_sos.empty:
                _sku_c2 = next((c for c in df_sos.columns if "product sku" in c.lower()), None); _qty_c2 = next((c for c in df_sos.columns if "order qty" in c.lower()), None)
                if _sku_c2 and _qty_c2:
                    _open2 = df_sos[~df_sos["SO Status"].astype(str).str.strip().str.lower().isin(CLOSED_STATUSES)].copy() if "SO Status" in df_sos.columns else df_sos.copy()
                    _open2["_sku"] = _open2[_sku_c2].astype(str).str.strip(); _open2["_po"] = pd.to_numeric(_open2[_qty_c2], errors="coerce").fillna(0)
                    _sku_po = _open2.groupby("_sku")["_po"].sum().reset_index(); _sku_po.columns = ["Item SKU","Open PO Qty"]
                    stn_base = curr_stock.merge(_sku_po, on="Item SKU", how="inner"); stn_base["Shortfall"] = stn_base["Current Stock"] - stn_base["Open PO Qty"]
                    stn_short = stn_base[stn_base["Shortfall"] < 0].copy()
                    _cen2 = df_fg[df_fg["Warehouse"].astype(str) == "Central"].groupby("Item SKU")["Qty Available"].sum().reset_index(); _cen2.columns = ["Item SKU","Central Stock"]
                    stn_short = stn_short.merge(_cen2, on="Item SKU", how="left"); stn_short["Central Stock"] = stn_short["Central Stock"].fillna(0)
                    stn_short["STN Suggest Qty"] = stn_short[["Shortfall","Central Stock"]].apply(lambda r: min(abs(r["Shortfall"]), r["Central Stock"]), axis=1)
                    stn_short["STN Feasible"] = stn_short.apply(lambda r: "✅ Yes" if r["Central Stock"] >= abs(r["Shortfall"]) else "⚠️ Partial" if r["Central Stock"] > 0 else "❌ No", axis=1)
                    stn_short["From Warehouse"] = "Central"; stn_short["To Warehouse"] = "Tumkur New Warehouse / YB FG Warehouse"
                    stn_short["Date"] = datetime.today().strftime("%d-%b-%Y"); stn_short["Raised By"] = ""; stn_short["Remarks"] = ""
                    stn_rows = stn_short[["Item Name","Item SKU","Category","Current Stock","Open PO Qty","Shortfall","Central Stock","STN Suggest Qty","STN Feasible","From Warehouse","To Warehouse","Date","Raised By","Remarks"]].sort_values("Shortfall", ascending=True)

            buf_stn = io.BytesIO()
            with pd.ExcelWriter(buf_stn, engine="openpyxl") as wx:
                (stn_rows if len(stn_rows) else pd.DataFrame(columns=["Item SKU","STN Suggest Qty"])).to_excel(wx, index=False, sheet_name="STN Template")

            st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)
            ab1, ab2, ab3 = st.columns(3)
            with ab1: st.download_button("⬇ Download Reorder Suggestions", buf_ro.getvalue(), "Reorder_Suggestions.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with ab2: st.download_button("📋 Download STN Template", buf_stn.getvalue(), f"STN_Template_{datetime.today().strftime('%d%b%Y')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with ab3:
                tg_tok = st.session_state.get("tg_token",""); tg_cid = st.session_state.get("tg_chat_id","")
                if st.button("📬 Send Telegram Digest", use_container_width=True, disabled=(not tg_tok or not tg_cid)):
                    _crit = merged_ro[merged_ro["Status"] == "🔴 Reorder Now"]
                    lines = [f"<b>📦 YogaBar · Daily Reorder Digest</b>", f"<i>{datetime.today().strftime('%d %b %Y')}</i>", ""]
                    if _crit.empty: lines.append("✅ No SKUs below Min Stock today!")
                    else:
                        lines.append(f"🔴 <b>{len(_crit)} SKUs need reorder:</b>")
                        for _, r in _crit.iterrows(): lines.append(f"• <code>{r['Item SKU']}</code> — Stock: <b>{r['Current Stock']:,.0f}</b> | Min: {r['Min Stock']:,.0f} | Suggest: <b>{r['Suggest Qty']:,.0f}</b>")
                    if not df_sos.empty and len(stn_rows):
                        _s_crit = stn_rows[stn_rows["STN Feasible"] == "❌ No"] if len(stn_rows) else pd.DataFrame()
                        if len(_s_crit):
                            lines += ["", f"❌ <b>{len(_s_crit)} SKUs — No Central stock for STN:</b>"]
                            for _, r in _s_crit.head(10).iterrows(): lines.append(f"• <code>{r['Item SKU']}</code> — Shortfall: <b>{abs(r['Shortfall']):,.0f}</b>")
                    ok, resp_msg = send_telegram(tg_tok, tg_cid, chr(10).join(lines))
                    if ok: st.success(resp_msg)
                    else:  st.error(resp_msg)
                elif not tg_tok or not tg_cid: st.caption("⚙️ Add Bot Token + Chat ID in sidebar to enable")

            st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
            st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">🔁 Reorder Suggestions</span><span class="tbl-badge">{len(merged_ro):,} SKUs</span></div>', unsafe_allow_html=True)
            st.dataframe(merged_ro[ro_disp_cols].style.apply(_ro_colour, axis=1), use_container_width=True, height=460, hide_index=True, column_config={"Current Stock": st.column_config.NumberColumn("Current Stock", format="%.0f"), "Min Stock": st.column_config.NumberColumn("Min Stock", format="%.0f"), "Reorder Qty": st.column_config.NumberColumn("Reorder Qty", format="%.0f"), "Gap": st.column_config.NumberColumn("Gap", format="%.0f"), "Suggest Qty": st.column_config.NumberColumn("Suggest Qty", format="%.0f"), "Status": st.column_config.TextColumn("Status")})

            if len(stn_rows):
                st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
                st.markdown(f'<div class="tbl-hdr"><span class="tbl-lbl">📋 STN Template Preview</span><span class="tbl-badge">{len(stn_rows):,} SKUs</span></div>', unsafe_allow_html=True)
                st.markdown("""<div style="font-size:10px;color:#475569;margin-bottom:8px;font-family:'JetBrains Mono',monospace;">Pre-filled from Central WH → Tumkur New / YB FG · Fill in Raised By + Remarks before submitting</div>""", unsafe_allow_html=True)
                def _stn_t_colour(row):
                    s = str(row.get("STN Feasible",""))
                    if "Yes"     in s: return ["background-color:#061410;color:#d1fae5"] * len(row)
                    if "Partial" in s: return ["background-color:#2d1f00;color:#fde68a"] * len(row)
                    return ["background-color:#2d0a0a;color:#fca5a5"] * len(row)
                st.dataframe(stn_rows.style.apply(_stn_t_colour, axis=1), use_container_width=True, height=min(80 + len(stn_rows)*36, 440), hide_index=True, column_config={"Current Stock": st.column_config.NumberColumn(format="%.0f"), "Open PO Qty": st.column_config.NumberColumn(format="%.0f"), "Shortfall": st.column_config.NumberColumn(format="%.0f"), "Central Stock": st.column_config.NumberColumn(format="%.0f"), "STN Suggest Qty": st.column_config.NumberColumn("STN Qty", format="%.0f"), "STN Feasible": st.column_config.TextColumn("Feasible")})

st.markdown('<div class="app-footer">YOGABAR · FG INVENTORY · CFA ANALYSIS</div>', unsafe_allow_html=True)
