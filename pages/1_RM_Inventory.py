import streamlit as st
import pandas as pd
import io
import requests
from datetime import datetime

st.set_page_config(page_title="RM Inventory · YogaBar", layout="wide", page_icon="📦", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("RM Inventory")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

:root {
  --bg:       #080b12;
  --bg1:      #0d1117;
  --bg2:      #111827;
  --border:   #1e2535;
  --border2:  #243050;
  --text:     #e2e8f0;
  --muted:    #64748b;
  --dim:      #334155;
}

*, *::before, *::after { box-sizing: border-box; }
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"], .main {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1rem 1.2rem 3rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── HEADER ─────────────────────────────────────────────────────────────── */
.app-header {
  display:flex; align-items:center; justify-content:space-between;
  padding-bottom:14px; border-bottom:1px solid #161d2e; margin-bottom:16px;
}
.hdr-left { display:flex; align-items:center; gap:10px; }
.hdr-logo {
  width:42px; height:42px; min-width:42px;
  background:#0f2e1a; border:1px solid #1a5c30;
  border-radius:12px; display:flex; align-items:center;
  justify-content:center; font-size:20px;
}
.hdr-title { font-size:17px; font-weight:800; color:#f1f5f9; }
.hdr-sub   { font-size:11px; color:#94a3b8; }
.live-pill {
  display:inline-flex; align-items:center; gap:5px;
  background:#071a0f; border:1px solid #166534;
  border-radius:20px; padding:5px 12px;
  font-size:10px; font-weight:700; color:#22c55e;
  letter-spacing:1px; font-family:'JetBrains Mono',monospace;
}
.live-dot {
  width:6px; height:6px; background:#22c55e; border-radius:50%;
  animation:blink 1.8s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 6px #22c55e} 50%{opacity:.2;box-shadow:none} }

/* ── BUTTONS ─────────────────────────────────────────────────────────────── */
.stButton > button {
  width:100% !important; background:#0d1117 !important;
  border:1.5px solid #1e2535 !important; border-radius:9px !important;
  color:#64748b !important; font-size:13px !important; font-weight:600 !important;
  padding:9px !important; transition:all .2s !important; margin-bottom:6px !important;
}
.stButton > button:hover { border-color:#5bc8c0 !important; color:#5bc8c0 !important; }
.stDownloadButton > button {
  width:100% !important; background:linear-gradient(135deg,#0f172a,#1e1b4b) !important;
  border:1.5px solid #4338ca !important; border-radius:9px !important;
  color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; padding:10px !important;
}

/* ── FILTERS ─────────────────────────────────────────────────────────────── */
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title {
  font-size:10px; font-weight:700; color:#475569; text-transform:uppercase;
  letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px;
}
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }
[data-testid="stTextInput"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:#a855f7 !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:#f1f5f9 !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }

/* ── KPI CARDS ───────────────────────────────────────────────────────────── */
.kpi-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:18px; }
.kpi-card {
  border-radius:18px; padding:22px 26px;
  position:relative; overflow:hidden; border:1px solid; min-height:140px;
  transition: transform .18s, box-shadow .18s;
}
.kpi-card:hover { transform:translateY(-2px); box-shadow:0 8px 30px rgba(0,0,0,.35); }
.kpi-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:18px 18px 0 0;
}
/* violet */
.kpi-card.violet { background:linear-gradient(135deg,#130a2a,#1e0f40); border-color:#3b1f6e; }
.kpi-card.violet::before { background:linear-gradient(90deg,#a855f7,#818cf8); }
.kpi-card.violet .kpi-lbl  { color:#c084fc; }
.kpi-card.violet .kpi-num  { color:#e9d5ff; }
.kpi-card.violet .kpi-cap  { color:#9d6fe8; }
.kpi-card.violet .kpi-sub  { color:#6d3aad; }
/* teal */
.kpi-card.teal { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-card.teal .kpi-lbl  { color:#5bc8c0; }
.kpi-card.teal .kpi-num  { color:#99f6e4; }
.kpi-card.teal .kpi-cap  { color:#0d9488; }
.kpi-card.teal .kpi-sub  { color:#0f5e59; }
/* amber */
.kpi-card.amber { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-card.amber::before { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.amber .kpi-lbl  { color:#fbbf24; }
.kpi-card.amber .kpi-num  { color:#fde68a; }
.kpi-card.amber .kpi-cap  { color:#d97706; }
.kpi-card.amber .kpi-sub  { color:#92510b; }

.kpi-inner { display:flex; align-items:flex-start; justify-content:space-between; }
.kpi-lbl   { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:8px; }
.kpi-num   { font-size:36px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1.5px; }
.kpi-cap   { font-size:11px; margin-top:7px; }
.kpi-sub   { font-size:10px; margin-top:4px; font-family:'JetBrains Mono',monospace; }
.kpi-ico   { font-size:30px; opacity:.55; margin-top:2px; }
.dos-critical { color:#f87171 !important; font-weight:800; }
.dos-low      { color:#fbbf24 !important; font-weight:800; }
.dos-healthy  { color:#6ee7b7 !important; font-weight:800; }

/* ── SECTION DIVIDER ─────────────────────────────────────────────────────── */
.sec-div {
  font-size:10px; font-weight:700; color:#334155; text-transform:uppercase;
  letter-spacing:1.2px; padding:12px 0 8px; display:flex; align-items:center; gap:7px;
}
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }

/* ── URGENCY SCOREBOARD ──────────────────────────────────────────────────── */
.score-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.score-card {
  border-radius:14px; padding:14px 16px; border:1.5px solid;
  text-align:center; position:relative; overflow:hidden;
  transition:transform .18s, box-shadow .18s;
}
.score-card:hover { transform:translateY(-2px); box-shadow:0 6px 24px rgba(0,0,0,.3); }
.score-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.score-lbl  { font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:6px; }
.score-num  { font-size:32px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; }
.score-cap  { font-size:10px; margin-top:4px; opacity:.6; }

.score-card.s-red    { background:#1a0608; border-color:#7f1d1d; }
.score-card.s-red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.score-card.s-red    .score-lbl { color:#ef4444; }
.score-card.s-red    .score-num { color:#fca5a5; }
.score-card.s-orange { background:#1c0a00; border-color:#92400e; }
.score-card.s-orange::before { background:linear-gradient(90deg,#f97316,#fb923c); }
.score-card.s-orange .score-lbl { color:#f97316; }
.score-card.s-orange .score-num { color:#fed7aa; }
.score-card.s-amber  { background:#120d00; border-color:#78350f; }
.score-card.s-amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.score-card.s-amber  .score-lbl { color:#f59e0b; }
.score-card.s-amber  .score-num { color:#fde68a; }
.score-card.s-green  { background:#051a0a; border-color:#14532d; }
.score-card.s-green::before  { background:linear-gradient(90deg,#22c55e,#4ade80); }
.score-card.s-green  .score-lbl { color:#22c55e; }
.score-card.s-green  .score-num { color:#bbf7d0; }

/* ── SKU CARDS ───────────────────────────────────────────────────────────── */
.sku-card {
  border-radius:12px; padding:14px 16px; margin-bottom:9px; border:1px solid;
  position:relative; overflow:hidden; transition:box-shadow .2s, border-color .2s;
}
.sku-card:hover { box-shadow:0 4px 20px rgba(0,0,0,.3); }
.sku-card::before { content:''; position:absolute; left:0; top:0; bottom:0; width:3px; border-radius:2px 0 0 2px; }

.sku-card.stockout { background:linear-gradient(135deg,#1f0406,#150204); border-color:#7f1d1d; }
.sku-card.stockout::before { background:#dc2626; }
.sku-card.critical { background:linear-gradient(135deg,#1a0608,#110204); border-color:#450a0a; }
.sku-card.critical::before { background:#ef4444; }
.sku-card.warning  { background:linear-gradient(135deg,#1c0a00,#130600); border-color:#431407; }
.sku-card.warning::before  { background:#f97316; }
.sku-card.watchlist{ background:linear-gradient(135deg,#120d00,#0d0900); border-color:#451a03; }
.sku-card.watchlist::before{ background:#f59e0b; }

.sku-top  { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:6px; }
.sku-code { font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; letter-spacing:.4px; }
.sku-name { font-size:11px; color:#64748b; margin-top:3px; line-height:1.4; }
.sku-badge{ font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:800; padding:4px 11px; border-radius:7px; white-space:nowrap; flex-shrink:0; margin-left:10px; }

.sku-card.stockout .sku-code  { color:#fca5a5; }
.sku-card.stockout .sku-badge { background:#2d0a0a; color:#fca5a5; border:1px solid #7f1d1d; }
.sku-card.critical .sku-code  { color:#fca5a5; }
.sku-card.critical .sku-badge { background:#2d0a0a; color:#fca5a5; border:1px solid #450a0a; }
.sku-card.warning  .sku-code  { color:#fed7aa; }
.sku-card.warning  .sku-badge { background:#2d1400; color:#fed7aa; border:1px solid #78350f; }
.sku-card.watchlist .sku-code { color:#fde68a; }
.sku-card.watchlist .sku-badge{ background:#2d1f00; color:#fde68a; border:1px solid #78350f; }

.urgency-txt { font-size:11px; font-weight:600; margin-bottom:7px; }
.prog-wrap { background:rgba(255,255,255,.07); border-radius:4px; height:5px; margin-bottom:10px; overflow:hidden; }
.prog-fill  { height:100%; border-radius:4px; }
.stat-row   { display:grid; grid-template-columns:repeat(3,1fr); gap:5px; }
.stat-box   { background:rgba(0,0,0,.25); border:1px solid rgba(255,255,255,.05); border-radius:8px; padding:7px 8px; text-align:center; }
.stat-key   { font-size:9px; color:#475569; text-transform:uppercase; letter-spacing:.8px; margin-bottom:3px; }
.stat-val   { font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; color:#94a3b8; }

/* ── TELEGRAM BUTTON ─────────────────────────────────────────────────────── */
.tg-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:12px; padding:14px 16px; margin-bottom:16px; }
.tg-header { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.tg-header::after { content:''; flex:1; height:1px; background:#1e2535; }
.tg-btn > button {
  background:linear-gradient(135deg,#0a1628,#0d2040) !important;
  border:1.5px solid #2563eb !important; color:#93c5fd !important;
  font-size:14px !important; font-weight:700 !important;
  border-radius:10px !important; padding:12px !important;
  width:100% !important; transition:all .2s !important;
}
.tg-btn > button:hover {
  border-color:#60a5fa !important; color:#bfdbfe !important;
  background:linear-gradient(135deg,#0f2350,#122860) !important;
  box-shadow:0 0 20px rgba(59,130,246,.18) !important;
}

/* ── TABLE ───────────────────────────────────────────────────────────────── */
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:6px 0; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }
.legend-bar { display:flex; gap:16px; align-items:center; background:#0d1117; border:1px solid #1e2535; border-radius:10px; padding:8px 14px; margin-bottom:8px; font-size:11px; }
.ldot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:4px; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════════════════
# CREDENTIALS
# ══════════════════════════════════════════════════════════════════════════════
def _tg_cfg():
    return (
        "8368375473:AAERuMSZGrdrvYKiGGQl9HIrdNzh-6a8eZQ",
        "5667118823"
    )

# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM MESSAGE
# ══════════════════════════════════════════════════════════════════════════════
def build_telegram_msg(n_crit, n_zero, critical_skus):
    import pytz
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.now(IST).strftime("%d %b %Y  %I:%M %p IST")
    NL  = "\n"
    lines = [
        "🚨 <b>YogaBar · RM Critical Stock Alert</b>",
        f"🕐 {now}",
        "─────────────────────────────",
        f"⛔ Stockout Today : <b>{n_zero} SKUs</b>",
        f"🟠 Critical &lt;7d  : <b>{n_crit} SKUs</b>",
        "─────────────────────────────", "",
    ]
    stockout = critical_skus[critical_skus["Days of Stock"] <= 1]
    if not stockout.empty:
        lines.append("⛔ <b>STOCKOUT — Act Now</b>")
        lines.append("<code>SKU                   DoS    SOH       /day</code>")
        lines.append("<code>─────────────────────────────────────────</code>")
        for _, r in stockout.iterrows():
            sku = str(r["Item SKU"])[:22].ljust(22)
            dos = f"{float(r['Days of Stock']):.1f}d".ljust(6)
            soh = f"{float(r['SOH']):,.0f}".rjust(9)
            pdr = f"{float(r['Per Day Req']):,.1f}".rjust(8)
            lines.append(f"<code>{sku} {dos} {soh} {pdr}</code>")
            lines.append(f"  <i>{str(r.get('Item Name',''))[:38]}</i>")
        lines.append("")
    near = critical_skus[critical_skus["Days of Stock"] > 1]
    if not near.empty:
        lines.append("🔴 <b>Critical — Reorder Now</b>")
        lines.append("<code>SKU                   DoS    SOH       /day</code>")
        lines.append("<code>─────────────────────────────────────────</code>")
        for _, r in near.iterrows():
            sku = str(r["Item SKU"])[:22].ljust(22)
            dos = f"{float(r['Days of Stock']):.1f}d".ljust(6)
            soh = f"{float(r['SOH']):,.0f}".rjust(9)
            pdr = f"{float(r['Per Day Req']):,.1f}".rjust(8)
            lines.append(f"<code>{sku} {dos} {soh} {pdr}</code>")
            lines.append(f"  <i>{str(r.get('Item Name',''))[:38]}</i>")
        lines.append("")
    if len(critical_skus) > 20:
        lines.append(f"<i>... and {len(critical_skus)-20} more SKUs</i>")
        lines.append("")
    lines += ["─────────────────────────────", "🤖 <i>YogaBar RM Inventory Dashboard</i>"]
    return NL.join(lines)

def send_telegram(message: str) -> tuple[bool, str]:
    bot_token, chat_id = _tg_cfg()
    url    = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        try:
            resp = requests.post(url, json={"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"}, timeout=10)
            if resp.status_code != 200:
                return False, f"Telegram API error {resp.status_code}: {resp.text}"
        except Exception as e:
            return False, str(e)
    return True, "✅ Alert sent successfully!"

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
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
    if df_fc.empty: return pd.DataFrame(columns=["_k","Forecast","Per Day Req"])
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    if "Forecast" not in df_fc.columns:
        return pd.DataFrame(columns=["_k","Forecast","Per Day Req"])
    df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]
    ic = "Item code" if "Item code" in df_fc.columns else ("Item Code" if "Item Code" in df_fc.columns else None)
    if ic is None: return pd.DataFrame(columns=["_k","Forecast","Per Day Req"])
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
        soh["Forecast"] = 0.0; soh["Per Day Req"] = 0.0
    soh["Forecast"]    = soh["Forecast"].fillna(0)
    soh["Per Day Req"] = soh["Per Day Req"].fillna(0)
    soh["Days of Stock"] = soh.apply(
        lambda r: round(r["SOH"] / r["Per Day Req"], 1) if r["Per Day Req"] > 0 else None, axis=1)
    soh.drop(columns=["_k"], inplace=True)
    return soh

df_raw  = load_rm()
fc_agg  = load_forecast_agg()
soh_sku = build_soh_sku(df_raw, fc_agg) if not df_raw.empty else pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
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
    st.cache_data.clear(); st.rerun()

if df_raw.empty:
    st.error("⚠️ No RM Inventory data found."); st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2.5, 1.8, 1.8, 1.8, 1.8])
with c1: search = st.text_input("s", placeholder="🔍 Search SKU / name / batch…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    sel_wh  = st.selectbox("w", wh_opts, label_visibility="collapsed")
with c3:
    cat_opts = (["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
                if "Category" in df_raw.columns else ["All Categories"])
    sel_cat = st.selectbox("c", cat_opts, label_visibility="collapsed")
with c4: sel_st = st.selectbox("st", ["All Stock","Available Only","Zero / Neg"], label_visibility="collapsed")
with c5:
    dos_opts = ["All DoS","🔴 Critical (< 7d)","🟡 Low (7–14d)","✅ Healthy (> 14d)","⚫ No Forecast"]
    sel_dos  = st.selectbox("d", dos_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════════
df = df_raw.copy()
if search:    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh  != "All Warehouses": df = df[df["Warehouse"] == sel_wh]
if sel_cat != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == sel_cat]
if sel_st == "Available Only": df = df[df["Qty Available"] > 0]
elif sel_st == "Zero / Neg":   df = df[df["Qty Available"] <= 0]

df_m = df.merge(soh_sku[["Item SKU","Forecast","Per Day Req","Days of Stock"]], on="Item SKU", how="left")
if sel_dos == "🔴 Critical (< 7d)":   df_m = df_m[df_m["Days of Stock"] < 7]
elif sel_dos == "🟡 Low (7–14d)":     df_m = df_m[(df_m["Days of Stock"] >= 7) & (df_m["Days of Stock"] <= 14)]
elif sel_dos == "✅ Healthy (> 14d)":  df_m = df_m[df_m["Days of Stock"] > 14]
elif sel_dos == "⚫ No Forecast":       df_m = df_m[df_m["Days of Stock"].isna()]

# ══════════════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════════════
df_m_soh  = df_m[df_m["Warehouse"].isin(SOH_WH)]
sku_dedup = df_m_soh.groupby("Item SKU").agg(
    SOH_sum      =("Qty Available","sum"),
    Forecast     =("Forecast","first"),
    Per_Day_Req  =("Per Day Req","first"),
    Days_of_Stock=("Days of Stock","first"),
).reset_index()
kpi_soh       = sku_dedup["SOH_sum"].sum()
kpi_forecast  = sku_dedup["Forecast"].fillna(0).sum()
sku_with_fc   = sku_dedup[sku_dedup["Per_Day_Req"] > 0]
kpi_avg_dos   = sku_with_fc["Days_of_Stock"].dropna().mean()
kpi_avg_dos   = kpi_avg_dos if pd.notna(kpi_avg_dos) else 0
total_skus    = sku_dedup["Item SKU"].nunique()
forecast_skus = len(sku_with_fc)
per_day_total = sku_with_fc["Per_Day_Req"].sum()

if kpi_avg_dos < 7:     dos_cls, dos_label = "dos-critical", "⚠ Critical — reorder now"
elif kpi_avg_dos <= 14: dos_cls, dos_label = "dos-low",      "⚡ Low — reorder soon"
else:                   dos_cls, dos_label = "dos-healthy",   "✅ Healthy stock level"
if kpi_avg_dos == 0:    dos_cls, dos_label = "",              "No forecast data"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card violet">
    <div class="kpi-inner">
      <div>
        <div class="kpi-lbl">Stock on Hand (SOH)</div>
        <div class="kpi-num">{kpi_soh:,.0f}</div>
        <div class="kpi-cap">Central · Tumkur · Cold Storage · Snowman</div>
        <div class="kpi-sub">{total_skus:,} unique SKUs in current filter</div>
      </div>
      <div class="kpi-ico">📦</div>
    </div>
  </div>
  <div class="kpi-card teal">
    <div class="kpi-inner">
      <div>
        <div class="kpi-lbl">Forecast Qty</div>
        <div class="kpi-num">{kpi_forecast:,.0f}</div>
        <div class="kpi-cap">Plant forecast · {forecast_skus:,} SKUs with demand plan</div>
        <div class="kpi-sub">Per day req: {per_day_total:,.1f} units / day</div>
      </div>
      <div class="kpi-ico">📈</div>
    </div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-inner">
      <div>
        <div class="kpi-lbl">Avg Days of Stock</div>
        <div class="kpi-num">{kpi_avg_dos:.1f}</div>
        <div class="kpi-cap"><span class="{dos_cls}">{dos_label}</span></div>
        <div class="kpi-sub">SOH ÷ (Forecast ÷ 24) · {forecast_skus:,} SKUs</div>
      </div>
      <div class="kpi-ico">⏱</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BUILD CRITICAL / REORDER LISTS
# ══════════════════════════════════════════════════════════════════════════════
soh_full = soh_sku.copy() if not soh_sku.empty else pd.DataFrame()
if not soh_full.empty and "Category" in df_raw.columns:
    cat_map = df_raw.drop_duplicates("Item SKU").set_index("Item SKU")["Category"].to_dict()
    soh_full["Category"] = soh_full["Item SKU"].map(cat_map).fillna("Unknown")

critical_skus = pd.DataFrame()
reorder_skus  = pd.DataFrame()
if not soh_full.empty and "Days of Stock" in soh_full.columns:
    has_fc = soh_full[soh_full["Per Day Req"] > 0].copy()
    if "Item Name" in df_raw.columns:
        name_map = df_raw.drop_duplicates("Item SKU").set_index("Item SKU")["Item Name"].to_dict()
        has_fc["Item Name"] = has_fc["Item SKU"].map(name_map).fillna("")
    else:
        has_fc["Item Name"] = ""
    critical_skus = has_fc[has_fc["Days of Stock"] < 7].sort_values("Days of Stock")
    reorder_skus  = has_fc[(has_fc["Days of Stock"] >= 7) & (has_fc["Days of Stock"] <= 14)].sort_values("Days of Stock")

n_crit = len(critical_skus)
n_low  = len(reorder_skus)
n_zero = len(critical_skus[critical_skus["Days of Stock"] <= 1]) if not critical_skus.empty else 0
n_ok   = int((soh_full["Days of Stock"].fillna(0) > 14).sum()) if not soh_full.empty else 0

# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM BUTTON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="tg-wrap">', unsafe_allow_html=True)
st.markdown('<div class="tg-header">📬 Send Alert</div>', unsafe_allow_html=True)
st.markdown('<div class="tg-btn">', unsafe_allow_html=True)
send_tg = st.button(
    f"✈️  Send Telegram Alert  ·  {n_crit} Critical SKUs  ·  {n_zero} Stockout Today",
    key="btn_tg", use_container_width=True
)
st.markdown('</div>', unsafe_allow_html=True)
tg_result = st.empty()
if send_tg:
    if n_crit == 0:
        tg_result.info("ℹ️ No critical SKUs — nothing to send.")
    else:
        with st.spinner("Sending..."):
            msg = build_telegram_msg(n_crit, n_zero, critical_skus)
            ok, info = send_telegram(msg)
        tg_result.markdown(
            f'<div style="background:{"#061a0a" if ok else "#1a0608"};'
            f'border:1.5px solid {"#16a34a" if ok else "#dc2626"};'
            f'border-radius:10px;padding:12px 18px;font-size:13px;font-weight:700;'
            f'color:{"#4ade80" if ok else "#f87171"};margin-top:8px;">{info}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# URGENCY SCOREBOARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-div">📊 Inventory Intelligence</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="score-grid">
  <div class="score-card s-red">
    <div class="score-lbl">⛔ Stockout Today</div>
    <div class="score-num">{n_zero}</div>
    <div class="score-cap">SKUs at ≤ 1 day</div>
  </div>
  <div class="score-card s-orange">
    <div class="score-lbl">🟠 Critical &lt; 7d</div>
    <div class="score-num">{n_crit}</div>
    <div class="score-cap">SKUs need reorder</div>
  </div>
  <div class="score-card s-amber">
    <div class="score-lbl">🟡 Low 7–14d</div>
    <div class="score-num">{n_low}</div>
    <div class="score-cap">SKUs watch closely</div>
  </div>
  <div class="score-card s-green">
    <div class="score-lbl">✅ Healthy &gt; 14d</div>
    <div class="score-num">{n_ok}</div>
    <div class="score-cap">SKUs well stocked</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SKU PANELS
# ══════════════════════════════════════════════════════════════════════════════
def render_sku(r, panel="critical"):
    dos   = float(r["Days of Stock"])
    soh_v = float(r["SOH"])
    pdr   = float(r["Per Day Req"])
    sku   = str(r["Item SKU"])
    name  = str(r.get("Item Name",""))
    cat   = str(r.get("Category","—"))

    if panel == "critical":
        if dos <= 1:
            cls, badge, bar_c, bar_w = "stockout", "STOCKOUT", "#dc2626", 3
            urgency, urg_c = "⛔ Stocking out NOW", "#fca5a5"
        elif dos <= 3:
            cls, badge, bar_c = "critical", f"{dos:.1f}d left", "#ef4444"
            bar_w = max(int(dos / 7 * 100), 5)
            urgency, urg_c = f"🔴 Gone in ~{int(dos)}d", "#fca5a5"
        else:
            cls, badge, bar_c = "warning", f"{dos:.1f}d left", "#f97316"
            bar_w = int(dos / 7 * 100)
            urgency, urg_c = f"🟠 ~{dos:.1f} days remaining", "#fed7aa"
    else:
        cls, badge, bar_c = "watchlist", f"{dos:.1f}d", "#f59e0b"
        bar_w = min(int((dos - 7) / 7 * 100), 100)
        urgency, urg_c = f"🟡 {dos:.1f} days remaining", "#fde68a"

    return f"""
    <div class="sku-card {cls}">
      <div class="sku-top">
        <div style="flex:1;min-width:0;">
          <div class="sku-code">{sku}</div>
          <div class="sku-name">{name[:52] if name else "—"}</div>
        </div>
        <div class="sku-badge">{badge}</div>
      </div>
      <div class="urgency-txt" style="color:{urg_c};">{urgency}</div>
      <div class="prog-wrap">
        <div class="prog-fill" style="width:{bar_w}%;background:{bar_c};"></div>
      </div>
      <div class="stat-row">
        <div class="stat-box">
          <div class="stat-key">SOH</div>
          <div class="stat-val">{soh_v:,.0f}</div>
        </div>
        <div class="stat-box">
          <div class="stat-key">Per Day</div>
          <div class="stat-val">{pdr:.1f}</div>
        </div>
        <div class="stat-box">
          <div class="stat-key">Category</div>
          <div class="stat-val" style="font-size:10px;">{cat[:12] if cat else "—"}</div>
        </div>
      </div>
    </div>"""

col_l, col_r = st.columns(2, gap="medium")

with col_l:
    st.markdown(
        f'<div class="sec-div">🚨 Critical — Runs Out &lt; 7 Days'
        f'<span style="margin-left:6px;background:#2d0a0a;border:1px solid #7f1d1d;'
        f'border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800;'
        f'color:#fca5a5;font-family:JetBrains Mono,monospace;">{n_crit} SKUs</span></div>',
        unsafe_allow_html=True
    )
    if critical_skus.empty:
        st.markdown('<div style="text-align:center;color:#334155;padding:24px;font-size:13px;">✅ No critical SKUs right now</div>', unsafe_allow_html=True)
    else:
        for _, r in critical_skus.iterrows():
            st.markdown(render_sku(r, "critical"), unsafe_allow_html=True)

with col_r:
    st.markdown(
        f'<div class="sec-div">⚡ Reorder Watchlist — 7 to 14 Days'
        f'<span style="margin-left:6px;background:#2d1f00;border:1px solid #78350f;'
        f'border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800;'
        f'color:#fde68a;font-family:JetBrains Mono,monospace;">{n_low} SKUs</span></div>',
        unsafe_allow_html=True
    )
    if reorder_skus.empty:
        st.markdown('<div style="text-align:center;color:#334155;padding:24px;font-size:13px;">✅ No SKUs in watchlist</div>', unsafe_allow_html=True)
    else:
        for _, r in reorder_skus.iterrows():
            st.markdown(render_sku(r, "watchlist"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DETAILED TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr style="border:none;border-top:1px solid #161d2e;margin:20px 0 0;">', unsafe_allow_html=True)
st.markdown('<div class="sec-div">📋 Detailed Records</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="tbl-hdr"><span class="tbl-lbl">RM Inventory · Forecast · Days of Stock</span>'
    f'<span class="tbl-badge">{len(df_m):,} rows</span></div>',
    unsafe_allow_html=True
)
st.markdown("""
<div class="legend-bar">
  <span><span class="ldot" style="background:#ef4444;"></span><span style="color:#f87171;">Critical &lt; 7 days</span></span>
  <span><span class="ldot" style="background:#f59e0b;"></span><span style="color:#fbbf24;">Low 7–14 days</span></span>
  <span><span class="ldot" style="background:#5bc8c0;"></span><span style="color:#99f6e4;">Healthy &gt; 14 days</span></span>
  <span style="color:#334155;margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:10px;">DoS = SOH ÷ (Forecast ÷ 24)</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df_m.to_excel(w, index=False, sheet_name="RM Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

if df_m.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_row(row):
        dos = row.get("Days of Stock", None)
        if pd.isna(dos) or dos is None: return [""] * len(row)
        if dos < 7:   return ["background-color:#2d0a0a;color:#fca5a5"] * len(row)
        if dos <= 14: return ["background-color:#2d1f00;color:#fde68a"] * len(row)
        return ["background-color:#061410;color:#99f6e4"] * len(row)

    priority = ["Item Name","Item SKU","Category","Warehouse","UoM",
                "Qty Available","Forecast","Per Day Req","Days of Stock",
                "Qty Inward","Qty (Issue / Hold)","Value (Inc Tax)","Value (Ex Tax)",
                "Batch No","MFG Date","Expiry Date","Inventory Date"]
    cols  = [c for c in priority if c in df_m.columns]
    cols += [c for c in df_m.columns if c not in cols]
    df_show = df_m[cols].copy()
    for c in ["Inventory Date","Expiry Date","MFG Date"]:
        if c in df_show.columns:
            df_show[c] = df_show[c].dt.strftime("%d-%b-%Y").fillna("")

    st.dataframe(
        df_show.style.apply(colour_row, axis=1),
        use_container_width=True, height=530, hide_index=True,
        column_config={
            "Qty Available":      st.column_config.NumberColumn("Qty Avail",       format="%.0f"),
            "Forecast":           st.column_config.NumberColumn("Forecast",        format="%.0f"),
            "Per Day Req":        st.column_config.NumberColumn("Per Day Req",     format="%.2f"),
            "Days of Stock":      st.column_config.NumberColumn("Days of Stock ⏱", format="%.1f"),
            "Qty Inward":         st.column_config.NumberColumn("Inward",          format="%.0f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Issue/Hold",      format="%.0f"),
            "Value (Inc Tax)":    st.column_config.NumberColumn("Val (Inc)",       format="%.0f"),
            "Value (Ex Tax)":     st.column_config.NumberColumn("Val (Ex)",        format="%.0f"),
        }
    )

st.markdown('<div class="app-footer">YOGABAR · RM INVENTORY · SPROUTLIFE FOODS</div>', unsafe_allow_html=True)
