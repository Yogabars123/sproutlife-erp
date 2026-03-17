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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --bg:         #05080f;
  --bg1:        #080d18;
  --bg2:        #0c1220;
  --bg3:        #111827;
  --border:     #1a2540;
  --border2:    #243050;
  --text:       #e2e8f0;
  --muted:      #64748b;
  --dim:        #334155;
  --red:        #ef4444;
  --red-soft:   #fca5a5;
  --red-bg:     #1a0608;
  --red-bdr:    #7f1d1d;
  --orange:     #f97316;
  --orange-soft:#fed7aa;
  --orange-bg:  #1c0a00;
  --orange-bdr: #92400e;
  --amber:      #f59e0b;
  --amber-soft: #fde68a;
  --amber-bg:   #120d00;
  --amber-bdr:  #78350f;
  --teal:       #14b8a6;
  --teal-soft:  #99f6e4;
  --teal-bg:    #042420;
  --teal-bdr:   #134e4a;
  --green:      #22c55e;
  --green-soft: #bbf7d0;
  --green-bg:   #051a0a;
  --green-bdr:  #14532d;
  --violet:     #a855f7;
  --violet-soft:#e9d5ff;
  --violet-bg:  #130a2a;
  --violet-bdr: #3b1f6e;
  --blue:       #3b82f6;
  --blue-soft:  #bfdbfe;
  --blue-bg:    #060e1a;
  --blue-bdr:   #1e3a5f;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"], .main {
  background: var(--bg) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  color: var(--text) !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1.2rem 1.4rem 4rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── TOP HEADER ─────────────────────────────────────────────────────────── */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 0 18px; border-bottom: 1px solid var(--border); margin-bottom: 20px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: linear-gradient(135deg,#0a2e1a,#0f4a28);
  border: 1px solid #1a5c30;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.brand-name { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800; color: #f1f5f9; letter-spacing: -.3px; }
.brand-sub  { font-size: 11px; color: var(--muted); margin-top: 1px; }
.live-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: #041208; border: 1px solid #155e2e;
  border-radius: 20px; padding: 6px 14px;
  font-size: 10px; font-weight: 700; color: var(--green);
  letter-spacing: 1.2px; font-family: 'JetBrains Mono', monospace;
}
.live-dot {
  width: 7px; height: 7px; background: var(--green); border-radius: 50%;
  animation: pulse 1.8s ease-in-out infinite;
  box-shadow: 0 0 8px var(--green);
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.3;transform:scale(.85)} }

/* ── REFRESH BUTTON ─────────────────────────────────────────────────────── */
.stButton > button {
  background: var(--bg2) !important; border: 1px solid var(--border2) !important;
  border-radius: 10px !important; color: var(--muted) !important;
  font-size: 12px !important; font-weight: 600 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  padding: 9px 18px !important; transition: all .2s !important;
  width: 100% !important; margin-bottom: 6px !important;
}
.stButton > button:hover {
  border-color: var(--teal) !important; color: var(--teal) !important;
  background: var(--teal-bg) !important;
}
.stDownloadButton > button {
  background: var(--bg2) !important; border: 1px solid var(--blue-bdr) !important;
  border-radius: 10px !important; color: var(--blue-soft) !important;
  font-size: 12px !important; font-weight: 700 !important;
  width: 100% !important; padding: 10px !important;
}

/* ── FILTER BAR ─────────────────────────────────────────────────────────── */
.filter-bar {
  background: var(--bg1); border: 1px solid var(--border);
  border-radius: 14px; padding: 14px 16px; margin-bottom: 18px;
  display: flex; align-items: center; gap: 10px;
}
.filter-label {
  font-size: 10px; font-weight: 700; color: var(--dim);
  text-transform: uppercase; letter-spacing: 1.4px;
  white-space: nowrap;
}
[data-testid="stTextInput"] > div > div {
  background: var(--bg3) !important; border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
}
[data-testid="stTextInput"] > div > div:focus-within { border-color: var(--teal) !important; box-shadow: 0 0 0 3px rgba(20,184,166,.12) !important; }
[data-testid="stTextInput"] input {
  background: transparent !important; color: var(--text) !important;
  font-size: 13px !important; padding: 9px 12px !important; border: none !important;
  font-family: 'Space Grotesk', sans-serif !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--dim) !important; }
[data-testid="stSelectbox"] > div > div {
  background: var(--bg3) !important; border: 1px solid var(--border2) !important;
  border-radius: 10px !important; color: var(--text) !important; font-size: 13px !important;
}
[data-testid="stWidgetLabel"] { display: none !important; }

/* ── KPI CARDS ──────────────────────────────────────────────────────────── */
.kpi-row {
  display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 20px;
}
.kpi {
  border-radius: 16px; padding: 22px 24px; border: 1px solid;
  position: relative; overflow: hidden; cursor: default;
  transition: transform .2s, box-shadow .2s;
}
.kpi:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,.4); }
.kpi::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at 80% 0%, rgba(255,255,255,.04), transparent 60%);
  pointer-events: none;
}
.kpi-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; }
.kpi-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.4px; margin-bottom: 12px;
}
.kpi-value {
  font-family: 'Syne', sans-serif; font-size: 38px; font-weight: 800;
  line-height: 1; letter-spacing: -2px;
}
.kpi-sub { font-size: 11px; margin-top: 8px; opacity: .7; }
.kpi-icon { font-size: 28px; opacity: .5; }
.kpi-bar { height: 3px; border-radius: 2px; margin-top: 14px; opacity: .5; }

.kpi.violet { background: linear-gradient(135deg,var(--violet-bg),#1a0f35); border-color: var(--violet-bdr); }
.kpi.violet .kpi-label { color: var(--violet); }
.kpi.violet .kpi-value { color: var(--violet-soft); }
.kpi.violet .kpi-bar   { background: linear-gradient(90deg,var(--violet),#818cf8); }

.kpi.teal { background: linear-gradient(135deg,var(--teal-bg),#071f1c); border-color: var(--teal-bdr); }
.kpi.teal .kpi-label { color: var(--teal); }
.kpi.teal .kpi-value { color: var(--teal-soft); }
.kpi.teal .kpi-bar   { background: linear-gradient(90deg,var(--teal),#2dd4bf); }

.kpi.amber { background: linear-gradient(135deg,var(--amber-bg),#1a1000); border-color: var(--amber-bdr); }
.kpi.amber .kpi-label { color: var(--amber); }
.kpi.amber .kpi-value { color: var(--amber-soft); }
.kpi.amber .kpi-bar   { background: linear-gradient(90deg,var(--amber),#fbbf24); }

/* ── URGENCY SCOREBOARD ──────────────────────────────────────────────────── */
.score-grid {
  display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 20px;
}
.score-card {
  border-radius: 14px; padding: 16px 18px; border: 1px solid;
  text-align: center; position: relative; overflow: hidden;
  transition: transform .18s, box-shadow .18s; cursor: default;
}
.score-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,.35); }
.score-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.score-icon { font-size: 18px; margin-bottom: 6px; }
.score-label {
  font-size: 9px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.3px; margin-bottom: 8px;
}
.score-num {
  font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800;
  line-height: 1; font-variant-numeric: tabular-nums;
}
.score-caption { font-size: 10px; margin-top: 5px; opacity: .6; }

.score-card.red    { background: var(--red-bg);    border-color: var(--red-bdr);    }
.score-card.red::before    { background: linear-gradient(90deg,var(--red),#f87171); }
.score-card.red    .score-label { color: var(--red); }
.score-card.red    .score-num   { color: var(--red-soft); }

.score-card.orange { background: var(--orange-bg); border-color: var(--orange-bdr); }
.score-card.orange::before { background: linear-gradient(90deg,var(--orange),#fb923c); }
.score-card.orange .score-label { color: var(--orange); }
.score-card.orange .score-num   { color: var(--orange-soft); }

.score-card.amber  { background: var(--amber-bg);  border-color: var(--amber-bdr);  }
.score-card.amber::before  { background: linear-gradient(90deg,var(--amber),#fbbf24); }
.score-card.amber  .score-label { color: var(--amber); }
.score-card.amber  .score-num   { color: var(--amber-soft); }

.score-card.green  { background: var(--green-bg);  border-color: var(--green-bdr);  }
.score-card.green::before  { background: linear-gradient(90deg,var(--green),#4ade80); }
.score-card.green  .score-label { color: var(--green); }
.score-card.green  .score-num   { color: var(--green-soft); }

/* ── SECTION DIVIDER ─────────────────────────────────────────────────────── */
.sec {
  display: flex; align-items: center; gap: 10px;
  margin: 20px 0 14px; font-size: 10px; font-weight: 700;
  color: var(--dim); text-transform: uppercase; letter-spacing: 1.4px;
}
.sec::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* ── SKU CARD ────────────────────────────────────────────────────────────── */
.sku-card {
  border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
  border: 1px solid; position: relative; overflow: hidden;
  transition: border-color .2s, box-shadow .2s; cursor: default;
}
.sku-card:hover { box-shadow: 0 4px 24px rgba(0,0,0,.3); }
.sku-card::before { content:''; position:absolute; left:0; top:0; bottom:0; width:3px; border-radius:3px 0 0 3px; }

.sku-card.stockout { background:linear-gradient(135deg,#1f0406,#150204); border-color:#7f1d1d; }
.sku-card.stockout::before { background:#dc2626; }
.sku-card.critical { background:linear-gradient(135deg,#1a0608,#110204); border-color:#450a0a; }
.sku-card.critical::before { background:#ef4444; }
.sku-card.warning  { background:linear-gradient(135deg,#1c0a00,#130600); border-color:#431407; }
.sku-card.warning::before  { background:#f97316; }
.sku-card.watchlist{ background:linear-gradient(135deg,#120d00,#0d0900); border-color:#451a03; }
.sku-card.watchlist::before{ background:#f59e0b; }

.sku-top { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:8px; }
.sku-code {
  font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700;
  letter-spacing:.5px;
}
.sku-name { font-size:11px; color:var(--muted); margin-top:3px; line-height:1.4; }
.sku-badge {
  font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:800;
  padding:4px 12px; border-radius:8px; white-space:nowrap; flex-shrink:0; margin-left:10px;
}

.sku-card.stockout .sku-code  { color:#fca5a5; }
.sku-card.stockout .sku-badge { background:#2d0a0a; color:#fca5a5; border:1px solid #7f1d1d; }
.sku-card.critical .sku-code  { color:#fca5a5; }
.sku-card.critical .sku-badge { background:#2d0a0a; color:#fca5a5; border:1px solid #7f1d1d; }
.sku-card.warning  .sku-code  { color:#fed7aa; }
.sku-card.warning  .sku-badge { background:#2d1400; color:#fed7aa; border:1px solid #78350f; }
.sku-card.watchlist.sku-code  { color:#fde68a; }
.sku-card.watchlist .sku-code { color:#fde68a; }
.sku-card.watchlist .sku-badge{ background:#2d1f00; color:#fde68a; border:1px solid #78350f; }

/* Progress bar */
.prog-wrap { background:rgba(255,255,255,.06); border-radius:4px; height:5px; margin:10px 0 12px; overflow:hidden; }
.prog-fill  { height:100%; border-radius:4px; transition:width .4s ease; }

/* Stat row */
.stat-row { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }
.stat-box {
  background:rgba(0,0,0,.3); border:1px solid rgba(255,255,255,.05);
  border-radius:8px; padding:7px 10px; text-align:center;
}
.stat-key { font-size:9px; color:var(--muted); text-transform:uppercase; letter-spacing:.8px; margin-bottom:3px; }
.stat-val { font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; color:#94a3b8; }

/* ── TELEGRAM BUTTON ─────────────────────────────────────────────────────── */
.tg-wrap {
  background:var(--bg1); border:1px solid var(--border); border-radius:14px;
  padding:16px 18px; margin-bottom:20px;
}
.tg-label {
  font-size:10px; font-weight:700; color:var(--dim); text-transform:uppercase;
  letter-spacing:1.3px; margin-bottom:12px; display:flex; align-items:center; gap:8px;
}
.tg-label::after { content:''; flex:1; height:1px; background:var(--border); }
.tg-btn > button {
  background: linear-gradient(135deg,#0a1628,#0d2040) !important;
  border: 1.5px solid #2563eb !important; color: #93c5fd !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 14px !important; font-weight: 700 !important;
  border-radius: 10px !important; padding: 12px !important;
  width: 100% !important; transition: all .2s !important;
  letter-spacing: .3px !important;
}
.tg-btn > button:hover {
  border-color: #60a5fa !important; color: #bfdbfe !important;
  background: linear-gradient(135deg,#0f2350,#122860) !important;
  box-shadow: 0 0 24px rgba(59,130,246,.2) !important;
}

/* ── TABLE ───────────────────────────────────────────────────────────────── */
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid var(--border) !important; }

.tbl-header { display:flex; align-items:center; justify-content:space-between; padding:8px 0 6px; }
.tbl-title  { font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:1.2px; }
.tbl-count  {
  background:var(--bg2); border:1px solid var(--border2);
  color:#818cf8; font-size:11px; font-weight:700;
  padding:3px 12px; border-radius:20px; font-family:'JetBrains Mono',monospace;
}

.legend-row {
  display:flex; gap:18px; align-items:center; flex-wrap:wrap;
  background:var(--bg1); border:1px solid var(--border); border-radius:10px;
  padding:9px 14px; margin-bottom:10px; font-size:11px;
}
.ldot { width:9px; height:9px; border-radius:50%; display:inline-block; margin-right:5px; flex-shrink:0; }
.legend-formula { margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--dim); }

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.footer {
  margin-top:3rem; padding-top:14px; border-top:1px solid var(--border);
  text-align:center; font-size:10px; font-weight:700; color:var(--dim);
  letter-spacing:2px; font-family:'JetBrains Mono',monospace;
}
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
            sku  = str(r["Item SKU"])[:22].ljust(22)
            dos  = f"{float(r['Days of Stock']):.1f}d".ljust(6)
            soh  = f"{float(r['SOH']):,.0f}".rjust(9)
            pdr  = f"{float(r['Per Day Req']):,.1f}".rjust(8)
            lines.append(f"<code>{sku} {dos} {soh} {pdr}</code>")
            lines.append(f"  <i>{str(r.get('Item Name',''))[:38]}</i>")
        lines.append("")
    near = critical_skus[critical_skus["Days of Stock"] > 1]
    if not near.empty:
        lines.append("🔴 <b>Critical — Reorder Now</b>")
        lines.append("<code>SKU                   DoS    SOH       /day</code>")
        lines.append("<code>─────────────────────────────────────────</code>")
        for _, r in near.iterrows():
            sku  = str(r["Item SKU"])[:22].ljust(22)
            dos  = f"{float(r['Days of Stock']):.1f}d".ljust(6)
            soh  = f"{float(r['SOH']):,.0f}".rjust(9)
            pdr  = f"{float(r['Per Day Req']):,.1f}".rjust(8)
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
    return True, "✅ Alert sent!"

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
st.markdown(f"""
<div class="top-bar">
  <div class="brand">
    <div class="brand-icon">📦</div>
    <div>
      <div class="brand-name">RM Inventory</div>
      <div class="brand-sub">YogaBar · Raw Materials · Forecast · Days of Stock</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#475569;">
      {datetime.now().strftime("%d %b %Y")}
    </div>
    <div class="live-badge"><span class="live-dot"></span>LIVE</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear(); st.rerun()

if df_raw.empty:
    st.error("⚠️ No RM Inventory data found."); st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
st.markdown('<span class="filter-label">🔽 Filters</span>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([2.8, 1.7, 1.7, 1.7, 1.7])
with c1: search  = st.text_input("s", placeholder="🔍  Search SKU / name / batch…", label_visibility="collapsed")
with c2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    sel_wh  = st.selectbox("w", wh_opts, label_visibility="collapsed")
with c3:
    cat_opts = (["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
                if "Category" in df_raw.columns else ["All Categories"])
    sel_cat = st.selectbox("c", cat_opts, label_visibility="collapsed")
with c4: sel_st = st.selectbox("st", ["All Stock","Available Only","Zero / Neg"], label_visibility="collapsed")
with c5:
    dos_opts = ["All DoS","🔴 Critical (<7d)","🟡 Low (7–14d)","✅ Healthy (>14d)","⚫ No Forecast"]
    sel_dos  = st.selectbox("d", dos_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════════
df = df_raw.copy()
if search:    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh  != "All Warehouses":  df = df[df["Warehouse"] == sel_wh]
if sel_cat != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == sel_cat]
if sel_st == "Available Only": df = df[df["Qty Available"] > 0]
elif sel_st == "Zero / Neg":   df = df[df["Qty Available"] <= 0]

df_m = df.merge(soh_sku[["Item SKU","Forecast","Per Day Req","Days of Stock"]], on="Item SKU", how="left")
if sel_dos == "🔴 Critical (<7d)":   df_m = df_m[df_m["Days of Stock"] < 7]
elif sel_dos == "🟡 Low (7–14d)":    df_m = df_m[(df_m["Days of Stock"] >= 7) & (df_m["Days of Stock"] <= 14)]
elif sel_dos == "✅ Healthy (>14d)":  df_m = df_m[df_m["Days of Stock"] > 14]
elif sel_dos == "⚫ No Forecast":      df_m = df_m[df_m["Days of Stock"].isna()]

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

if kpi_avg_dos < 7:     dos_status = "⚠️ Critical — Reorder Now"
elif kpi_avg_dos <= 14: dos_status = "⚡ Low — Reorder Soon"
else:                   dos_status = "✅ Healthy Stock Level"
if kpi_avg_dos == 0:    dos_status = "— No Forecast Data"

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi violet">
    <div class="kpi-top">
      <div>
        <div class="kpi-label">Stock on Hand</div>
        <div class="kpi-value">{kpi_soh:,.0f}</div>
        <div class="kpi-sub">Central · Tumkur · Cold Storage · Snowman</div>
        <div style="margin-top:6px;font-size:10px;color:#7c3aed;font-family:'JetBrains Mono',monospace;">{total_skus:,} unique SKUs</div>
      </div>
      <div class="kpi-icon">📦</div>
    </div>
    <div class="kpi-bar"></div>
  </div>
  <div class="kpi teal">
    <div class="kpi-top">
      <div>
        <div class="kpi-label">Forecast Qty</div>
        <div class="kpi-value">{kpi_forecast:,.0f}</div>
        <div class="kpi-sub">Plant forecast · {forecast_skus:,} SKUs with demand plan</div>
        <div style="margin-top:6px;font-size:10px;color:#0f766e;font-family:'JetBrains Mono',monospace;">{per_day_total:,.0f} units / day</div>
      </div>
      <div class="kpi-icon">📈</div>
    </div>
    <div class="kpi-bar"></div>
  </div>
  <div class="kpi amber">
    <div class="kpi-top">
      <div>
        <div class="kpi-label">Avg Days of Stock</div>
        <div class="kpi-value">{kpi_avg_dos:.1f}<span style="font-size:18px;opacity:.6;">d</span></div>
        <div class="kpi-sub">{dos_status}</div>
        <div style="margin-top:6px;font-size:10px;color:#b45309;font-family:'JetBrains Mono',monospace;">SOH ÷ (Forecast ÷ 24)</div>
      </div>
      <div class="kpi-icon">⏱</div>
    </div>
    <div class="kpi-bar"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BUILD CRITICAL/REORDER DATA
# ══════════════════════════════════════════════════════════════════════════════
soh_full = soh_sku.copy() if not soh_sku.empty else pd.DataFrame()
if not soh_full.empty and "Category" in df_raw.columns:
    cat_map  = df_raw.drop_duplicates("Item SKU").set_index("Item SKU")["Category"].to_dict()
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
st.markdown('<div class="tg-label">📬 Send Alert</div>', unsafe_allow_html=True)
st.markdown('<div class="tg-btn">', unsafe_allow_html=True)
send_tg = st.button(
    f"✈️  Send Telegram Alert  ·  {n_crit} Critical  ·  {n_zero} Stockout Today",
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
            f'<div style="background:{"#061a0a" if ok else "#1a0608"};border:1.5px solid {"#16a34a" if ok else "#dc2626"};'
            f'border-radius:10px;padding:12px 18px;font-size:13px;font-weight:700;'
            f'color:{"#4ade80" if ok else "#f87171"};margin-top:8px;">{info}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# URGENCY SCOREBOARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📊 Urgency Overview</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="score-grid">
  <div class="score-card red">
    <div class="score-icon">⛔</div>
    <div class="score-label">Stockout Today</div>
    <div class="score-num">{n_zero}</div>
    <div class="score-caption">SKUs at ≤ 1 day</div>
  </div>
  <div class="score-card orange">
    <div class="score-icon">🟠</div>
    <div class="score-label">Critical &lt; 7d</div>
    <div class="score-num">{n_crit}</div>
    <div class="score-caption">Reorder immediately</div>
  </div>
  <div class="score-card amber">
    <div class="score-icon">🟡</div>
    <div class="score-label">Low 7 – 14d</div>
    <div class="score-num">{n_low}</div>
    <div class="score-caption">Watch closely</div>
  </div>
  <div class="score-card green">
    <div class="score-icon">✅</div>
    <div class="score-label">Healthy &gt; 14d</div>
    <div class="score-num">{n_ok}</div>
    <div class="score-caption">Well stocked</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CRITICAL + REORDER PANELS
# ══════════════════════════════════════════════════════════════════════════════
col_l, col_r = st.columns(2, gap="large")

def render_sku_card(r, panel="critical"):
    dos   = float(r["Days of Stock"])
    soh_v = float(r["SOH"])
    pdr   = float(r["Per Day Req"])
    sku   = str(r["Item SKU"])
    name  = str(r.get("Item Name",""))
    cat   = str(r.get("Category","—"))

    if panel == "critical":
        if dos <= 1:
            cls, badge, bar_c, bar_w = "stockout", "STOCKOUT", "#dc2626", 2
        elif dos <= 3:
            cls, badge, bar_c = "critical", f"{dos:.1f}d left", "#ef4444"
            bar_w = max(int(dos / 7 * 100), 4)
        else:
            cls, badge, bar_c = "warning", f"{dos:.1f}d left", "#f97316"
            bar_w = int(dos / 7 * 100)
        urgency = "⛔ Stocking out NOW" if dos <= 1 else (f"🔴 Gone in ~{int(dos)}d" if dos <= 3 else f"🟠 ~{dos:.1f} days remaining")
        urgency_color = "#f87171" if dos <= 1 else ("#fca5a5" if dos <= 3 else "#fed7aa")
    else:
        cls, bar_c = "watchlist", "#f59e0b"
        badge = f"{dos:.1f}d"
        bar_w = min(int((dos - 7) / 7 * 100), 100)
        urgency = f"🟡 {dos:.1f} days remaining"
        urgency_color = "#fde68a"

    return f"""
    <div class="sku-card {cls}">
      <div class="sku-top">
        <div style="flex:1;min-width:0;">
          <div class="sku-code">{sku}</div>
          <div class="sku-name">{name[:50] if name else "—"}</div>
        </div>
        <div class="sku-badge">{badge}</div>
      </div>
      <div style="font-size:11px;font-weight:600;color:{urgency_color};margin-bottom:6px;">{urgency}</div>
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

with col_l:
    st.markdown(
        f'<div class="sec">🚨 Critical — Runs Out &lt; 7 Days'
        f'<span style="margin-left:auto;background:#2d0a0a;border:1px solid #7f1d1d;'
        f'border-radius:20px;padding:2px 12px;font-size:11px;font-weight:800;color:#fca5a5;'
        f'font-family:JetBrains Mono,monospace;">{n_crit} SKUs</span></div>',
        unsafe_allow_html=True
    )
    if critical_skus.empty:
        st.markdown('<div style="text-align:center;color:#334155;padding:24px;font-size:13px;">✅ No critical SKUs right now</div>', unsafe_allow_html=True)
    else:
        for _, r in critical_skus.iterrows():
            st.markdown(render_sku_card(r, "critical"), unsafe_allow_html=True)

with col_r:
    st.markdown(
        f'<div class="sec">⚡ Reorder Watchlist — 7 to 14 Days'
        f'<span style="margin-left:auto;background:#2d1f00;border:1px solid #78350f;'
        f'border-radius:20px;padding:2px 12px;font-size:11px;font-weight:800;color:#fde68a;'
        f'font-family:JetBrains Mono,monospace;">{n_low} SKUs</span></div>',
        unsafe_allow_html=True
    )
    if reorder_skus.empty:
        st.markdown('<div style="text-align:center;color:#334155;padding:24px;font-size:13px;">✅ No SKUs in watchlist</div>', unsafe_allow_html=True)
    else:
        for _, r in reorder_skus.iterrows():
            st.markdown(render_sku_card(r, "watchlist"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DETAILED TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr style="border:none;border-top:1px solid #1a2540;margin:24px 0 0;">', unsafe_allow_html=True)
st.markdown('<div class="sec">📋 Detailed Records</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="tbl-header">
  <span class="tbl-title">RM Inventory · Forecast · Days of Stock</span>
  <span class="tbl-count">{len(df_m):,} rows</span>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="legend-row">
  <span><span class="ldot" style="background:#ef4444;"></span><span style="color:#f87171;font-size:11px;">Critical &lt; 7 days</span></span>
  <span><span class="ldot" style="background:#f59e0b;"></span><span style="color:#fbbf24;font-size:11px;">Low 7–14 days</span></span>
  <span><span class="ldot" style="background:#14b8a6;"></span><span style="color:#99f6e4;font-size:11px;">Healthy &gt; 14 days</span></span>
  <span class="legend-formula">DoS = SOH ÷ (Forecast ÷ 24)</span>
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
        if dos < 7:   return ["background-color:#1a0608;color:#fca5a5"] * len(row)
        if dos <= 14: return ["background-color:#120d00;color:#fde68a"] * len(row)
        return ["background-color:#042420;color:#99f6e4"] * len(row)

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
        use_container_width=True, height=540, hide_index=True,
        column_config={
            "Qty Available":      st.column_config.NumberColumn("Qty Avail",        format="%.0f"),
            "Forecast":           st.column_config.NumberColumn("Forecast",         format="%.0f"),
            "Per Day Req":        st.column_config.NumberColumn("Per Day Req",      format="%.2f"),
            "Days of Stock":      st.column_config.NumberColumn("Days of Stock ⏱",  format="%.1f"),
            "Qty Inward":         st.column_config.NumberColumn("Inward",           format="%.0f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Issue / Hold",     format="%.0f"),
            "Value (Inc Tax)":    st.column_config.NumberColumn("Val (Inc Tax)",    format="%.0f"),
            "Value (Ex Tax)":     st.column_config.NumberColumn("Val (Ex Tax)",     format="%.0f"),
        }
    )

st.markdown('<div class="footer">YOGABAR · RM INVENTORY · SPROUTLIFE FOODS</div>', unsafe_allow_html=True)
