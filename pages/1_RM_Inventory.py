import streamlit as st
import pandas as pd
import io
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email               import encoders

st.set_page_config(page_title="RM Inventory · YogaBar", layout="wide", page_icon="📦", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("RM Inventory")

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
.app-header { display:flex; align-items:center; justify-content:space-between; padding-bottom:14px; border-bottom:1px solid #161d2e; margin-bottom:16px; }
.hdr-left { display:flex; align-items:center; gap:10px; }
.hdr-logo { width:42px; height:42px; min-width:42px; background:#0f2e1a; border:1px solid #1a5c30; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px; }
.hdr-title { font-size:17px; font-weight:800; color:#f1f5f9; }
.hdr-sub { font-size:11px; color:#94a3b8; }
.live-pill { display:inline-flex; align-items:center; gap:5px; background:#071a0f; border:1px solid #166534; border-radius:20px; padding:5px 12px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1px; font-family:JetBrains Mono,monospace; }
.live-dot { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 6px #22c55e;} 50%{opacity:.2;box-shadow:none;} }
.kpi-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:18px; }
.kpi-card { border-radius:18px; padding:22px 26px; position:relative; overflow:hidden; border:1px solid; min-height:130px; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:18px 18px 0 0; }
.kpi-card.violet { background:linear-gradient(135deg,#130a2a,#1e0f40); border-color:#3b1f6e; }
.kpi-card.violet::before { background:linear-gradient(90deg,#a855f7,#818cf8); }
.kpi-card.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before   { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-card.amber  { background:linear-gradient(135deg,#1a1000,#2a1800); border-color:#78350f; }
.kpi-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-inner { display:flex; align-items:flex-start; justify-content:space-between; }
.kpi-lbl { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:8px; }
.kpi-num { font-size:36px; font-weight:800; line-height:1; font-family:JetBrains Mono,monospace; letter-spacing:-1.5px; }
.kpi-cap { font-size:11px; margin-top:7px; } .kpi-ico { font-size:30px; opacity:.6; margin-top:2px; }
.kpi-sub { font-size:10px; margin-top:4px; font-family:JetBrains Mono,monospace; }
.kpi-card.violet .kpi-lbl{color:#c084fc;} .kpi-card.violet .kpi-num{color:#e9d5ff;} .kpi-card.violet .kpi-cap{color:#9d6fe8;} .kpi-card.violet .kpi-sub{color:#6d3aad;}
.kpi-card.teal   .kpi-lbl{color:#5bc8c0;} .kpi-card.teal   .kpi-num{color:#99f6e4;} .kpi-card.teal   .kpi-cap{color:#0d9488;} .kpi-card.teal   .kpi-sub{color:#0f5e59;}
.kpi-card.amber  .kpi-lbl{color:#fbbf24;} .kpi-card.amber  .kpi-num{color:#fde68a;} .kpi-card.amber  .kpi-cap{color:#d97706;} .kpi-card.amber  .kpi-sub{color:#92510b;}
.dos-critical{color:#f87171!important;font-weight:800;} .dos-low{color:#fbbf24!important;font-weight:800;} .dos-healthy{color:#6ee7b7!important;font-weight:800;}
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }
[data-testid="stTextInput"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:#a855f7 !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:#f1f5f9 !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div { background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }
.stButton > button { width:100% !important; background:#0d1117 !important; border:1.5px solid #1e2535 !important; border-radius:9px !important; color:#64748b !important; font-size:13px !important; font-weight:600 !important; padding:9px !important; transition:all .2s !important; margin-bottom:6px !important; }
.stButton > button:hover { border-color:#a855f7 !important; color:#c084fc !important; background:#130a2a !important; }
.stDownloadButton > button { width:100% !important; background:linear-gradient(135deg,#0f172a,#1e1b4b) !important; border:1.5px solid #4338ca !important; border-radius:9px !important; color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; padding:10px !important; }
.sec-div { font-size:10px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:1.2px; padding:12px 0 8px; display:flex; align-items:center; gap:7px; }
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:6px 0; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:#0f172a; border:1px solid #1e2d45; color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:JetBrains Mono,monospace; }
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.legend-bar { display:flex; gap:16px; align-items:center; background:#0d1117; border:1px solid #1e2535; border-radius:10px; padding:8px 14px; margin-bottom:8px; font-size:11px; }
.ldot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:4px; }
.app-footer { margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e; text-align:center; font-size:10px; font-weight:600; color:#334155; letter-spacing:1.5px; font-family:JetBrains Mono,monospace; }

/* ── Notification button styles ──────────────────────────────────────────── */
.notif-btn-tg > button {
    background: linear-gradient(135deg,#0a1628,#0d2040) !important;
    border: 1.5px solid #2563eb !important; color: #93c5fd !important;
    font-size: 13px !important; font-weight: 700 !important;
    border-radius: 9px !important; padding: 9px !important;
    width: 100% !important; transition: all .2s !important;
}
.notif-btn-tg > button:hover { border-color:#60a5fa !important; color:#bfdbfe !important; background:#0f2350 !important; }
.notif-btn-email > button {
    background: linear-gradient(135deg,#0a1a0a,#0d2d12) !important;
    border: 1.5px solid #16a34a !important; color: #86efac !important;
    font-size: 13px !important; font-weight: 700 !important;
    border-radius: 9px !important; padding: 9px !important;
    width: 100% !important; transition: all .2s !important;
}
.notif-btn-email > button:hover { border-color:#4ade80 !important; color:#bbf7d0 !important; background:#0d3518 !important; }
</style>
""", unsafe_allow_html=True)

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
# NOTIFICATION CONFIGURATION
# Add to .streamlit/secrets.toml:
#
# [telegram]
# bot_token = "123456:ABC-DEF..."
# chat_id   = "-1001234567890"   # group (negative) or personal user ID
#
# [email]
# smtp_host  = "smtp.gmail.com"
# smtp_port  = 587
# sender     = "yourapp@gmail.com"
# password   = "xxxx xxxx xxxx xxxx"   # Gmail App Password
# recipients = ["ops@yogabar.com", "supply@yogabar.com"]
# ══════════════════════════════════════════════════════════════════════════════

def _tg_cfg():
    try:
        return st.secrets["telegram"]["bot_token"], str(st.secrets["telegram"]["chat_id"])
    except Exception:
        return "", ""

def _email_cfg():
    try:
        return {
            "host":       st.secrets["email"]["smtp_host"],
            "port":       int(st.secrets["email"]["smtp_port"]),
            "sender":     st.secrets["email"]["sender"],
            "password":   st.secrets["email"]["password"],
            "recipients": st.secrets["email"]["recipients"],
        }
    except Exception:
        return None


# ── TELEGRAM: Critical SKUs only ─────────────────────────────────────────────
def build_telegram_critical(n_crit, n_zero, critical_skus):
    def esc(t):
        for ch in r"_*[]()~`>#+-=|{}.!":
            t = t.replace(ch, f"\\{ch}")
        return t

    lines = [
        "🚨 *YogaBar · Critical RM Stock Alert*",
        "",
        f"⛔ Stockout Today: *{n_zero}* SKUs",
        f"🟠 Critical \\(\\<7 days\\): *{n_crit}* SKUs",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "*SKU  ·  Days Left  ·  SOH  ·  Per Day*",
        "",
    ]
    for _, r in critical_skus.iterrows():
        sku  = esc(str(r["Item SKU"]))
        dos  = float(r["Days of Stock"])
        soh  = float(r["SOH"])
        pdr  = float(r["Per Day Req"])
        name = esc(str(r.get("Item Name", "")))[:28]
        icon = "⛔" if dos <= 1 else ("🔴" if dos <= 3 else "🟠")
        lines.append(f"{icon} `{sku}` — *{dos:.1f}d*")
        if name:
            lines.append(f"   _{name}_")
        lines.append(f"   SOH `{soh:,.0f}` · Per day `{pdr:.1f}`")
        lines.append("")
    if len(critical_skus) > 15:
        lines.append(f"_\\.\\.\\. and {len(critical_skus) - 15} more SKUs_")
    lines += ["━━━━━━━━━━━━━━━━━━━━", "_YogaBar RM Inventory Dashboard_"]
    return "\n".join(lines)


def send_telegram(message: str) -> tuple[bool, str]:
    bot_token, chat_id = _tg_cfg()
    if not bot_token or not chat_id:
        return False, "Telegram not configured — add [telegram] bot_token & chat_id to secrets.toml"
    url     = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "MarkdownV2"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return True, "✅ Telegram alert sent!"
        return False, f"Telegram API error {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, f"Telegram send failed: {e}"


# ── EMAIL: Critical SKUs table only ──────────────────────────────────────────
def build_email_critical_html(n_crit, n_zero, critical_skus):
    if critical_skus.empty:
        table_body = '<tr><td colspan="5" style="padding:20px;text-align:center;color:#475569;">✅ No critical SKUs at this time.</td></tr>'
    else:
        table_body = ""
        for _, r in critical_skus.iterrows():
            sku  = str(r["Item SKU"])
            name = str(r.get("Item Name", ""))[:35]
            dos  = float(r["Days of Stock"])
            soh  = float(r["SOH"])
            pdr  = float(r["Per Day Req"])
            cat  = str(r.get("Category", "—"))[:14]
            if dos <= 1:
                bb, bt, bl, rb = "#7f1d1d", "#fca5a5", "STOCKOUT", "#1f0406"
            elif dos <= 3:
                bb, bt, bl, rb = "#450a0a", "#fca5a5", f"{dos:.1f}d", "#1a0608"
            else:
                bb, bt, bl, rb = "#431407", "#fed7aa", f"{dos:.1f}d", "#180b02"
            table_body += f"""
            <tr style="border-bottom:1px solid #2d0a0a;background:{rb};">
              <td style="padding:10px 12px;">
                <div style="font-family:monospace;font-size:12px;font-weight:700;color:#fca5a5;">{sku}</div>
                <div style="font-size:11px;color:#64748b;margin-top:2px;">{name}</div>
              </td>
              <td style="padding:10px 12px;text-align:center;">
                <span style="background:{bb};border:1px solid #7f1d1d;border-radius:6px;padding:3px 10px;
                             font-family:monospace;font-size:12px;font-weight:800;color:{bt};">{bl}</span>
              </td>
              <td style="padding:10px 12px;text-align:right;font-family:monospace;font-size:12px;color:#94a3b8;">{soh:,.0f}</td>
              <td style="padding:10px 12px;text-align:right;font-family:monospace;font-size:12px;color:#94a3b8;">{pdr:.1f}</td>
              <td style="padding:10px 12px;text-align:center;font-size:11px;color:#64748b;">{cat}</td>
            </tr>"""

    return f"""<!DOCTYPE html>
<html><body style="background:#080b12;color:#e2e8f0;font-family:Inter,sans-serif;padding:0;margin:0;">
<div style="max-width:680px;margin:0 auto;padding:28px 20px;">

  <div style="background:linear-gradient(135deg,#1a0608,#2d0a0a);border:1px solid #7f1d1d;
              border-radius:16px;padding:20px 28px;margin-bottom:22px;">
    <div style="font-size:22px;font-weight:800;color:#f1f5f9;">🚨 Critical RM Stock Alert</div>
    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">YogaBar · Raw Material Inventory · Immediate Action Required</div>
  </div>

  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:22px;">
    <tr>
      <td width="50%" style="padding-right:8px;">
        <div style="background:#1a0608;border:1.5px solid #7f1d1d;border-radius:12px;padding:14px 18px;text-align:center;">
          <div style="font-size:9px;color:#ef4444;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">⛔ Stockout Today</div>
          <div style="font-size:32px;font-weight:800;color:#fca5a5;font-family:monospace;line-height:1;">{n_zero}</div>
          <div style="font-size:10px;color:#7f1d1d;margin-top:3px;">SKUs at ≤ 1 day</div>
        </div>
      </td>
      <td width="50%" style="padding-left:8px;">
        <div style="background:#160a00;border:1.5px solid #92400e;border-radius:12px;padding:14px 18px;text-align:center;">
          <div style="font-size:9px;color:#f97316;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🟠 Critical &lt; 7d</div>
          <div style="font-size:32px;font-weight:800;color:#fed7aa;font-family:monospace;line-height:1;">{n_crit}</div>
          <div style="font-size:10px;color:#78350f;margin-top:3px;">SKUs need reorder</div>
        </div>
      </td>
    </tr>
  </table>

  <div style="font-size:10px;font-weight:700;color:#ef4444;text-transform:uppercase;
              letter-spacing:1.2px;margin-bottom:10px;">🚨 Critical SKUs — Runs Out in &lt; 7 Days</div>
  <table width="100%" cellpadding="0" cellspacing="0"
         style="border-collapse:collapse;background:#140608;border:1.5px solid #7f1d1d;border-radius:10px;overflow:hidden;">
    <thead>
      <tr style="background:#2d0a0a;">
        <th style="padding:10px 12px;text-align:left;color:#ef4444;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;">SKU / Name</th>
        <th style="padding:10px 12px;text-align:center;color:#ef4444;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;">Days Left</th>
        <th style="padding:10px 12px;text-align:right;color:#ef4444;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;">SOH</th>
        <th style="padding:10px 12px;text-align:right;color:#ef4444;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;">Per Day</th>
        <th style="padding:10px 12px;text-align:center;color:#ef4444;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;">Category</th>
      </tr>
    </thead>
    <tbody>{table_body}</tbody>
  </table>

  <div style="margin-top:28px;padding-top:12px;border-top:1px solid #161d2e;
              text-align:center;font-size:10px;color:#334155;font-family:monospace;letter-spacing:1.5px;">
    YOGABAR · RM INVENTORY DASHBOARD · AUTO-GENERATED ALERT
  </div>
</div>
</body></html>"""


def send_email(subject: str, html_body: str) -> tuple[bool, str]:
    cfg = _email_cfg()
    if not cfg:
        return False, "Email not configured — add [email] block to secrets.toml"
    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg["sender"]
        recipients     = cfg["recipients"] if isinstance(cfg["recipients"], list) else [cfg["recipients"]]
        msg["To"]      = ", ".join(recipients)
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(cfg["host"], cfg["port"]) as srv:
            srv.starttls()
            srv.login(cfg["sender"], cfg["password"])
            srv.sendmail(cfg["sender"], recipients, msg.as_string())
        return True, f"✅ Email sent to {', '.join(recipients)}"
    except Exception as e:
        return False, f"Email send failed: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING (unchanged)
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
# HEADER + REFRESH
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
    Forecast     =("Forecast",     "first"),
    Per_Day_Req  =("Per Day Req",  "first"),
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
if kpi_avg_dos < 7:     dos_cls, dos_label = "dos-critical","⚠ Critical — reorder now"
elif kpi_avg_dos <= 14: dos_cls, dos_label = "dos-low",     "⚡ Low — reorder soon"
else:                   dos_cls, dos_label = "dos-healthy",  "✅ Healthy stock level"
if kpi_avg_dos == 0:    dos_cls, dos_label = "",             "No forecast data"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card violet"><div class="kpi-inner"><div>
    <div class="kpi-lbl">Stock on Hand (SOH)</div><div class="kpi-num">{kpi_soh:,.0f}</div>
    <div class="kpi-cap">Central · Tumkur · Cold Storage · Snowman</div>
    <div class="kpi-sub">{total_skus:,} unique SKUs in current filter</div>
  </div><div class="kpi-ico">📦</div></div></div>
  <div class="kpi-card teal"><div class="kpi-inner"><div>
    <div class="kpi-lbl">Forecast Qty</div><div class="kpi-num">{kpi_forecast:,.0f}</div>
    <div class="kpi-cap">Plant forecast · {forecast_skus:,} SKUs with demand plan</div>
    <div class="kpi-sub">Per day req: {per_day_total:,.1f} units / day</div>
  </div><div class="kpi-ico">📈</div></div></div>
  <div class="kpi-card amber"><div class="kpi-inner"><div>
    <div class="kpi-lbl">Avg Days of Stock</div><div class="kpi-num">{kpi_avg_dos:.1f}</div>
    <div class="kpi-cap"><span class="{dos_cls}">{dos_label}</span></div>
    <div class="kpi-sub">SOH ÷ (Forecast ÷ 24) · {forecast_skus:,} SKUs</div>
  </div><div class="kpi-ico">⏱</div></div></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BUILD CRITICAL / REORDER LISTS  (needed for buttons below KPIs)
# ══════════════════════════════════════════════════════════════════════════════
soh_full = soh_sku.copy() if not soh_sku.empty else pd.DataFrame()
if not soh_full.empty and "Item SKU" in df_raw.columns and "Category" in df_raw.columns:
    cat_map = df_raw.drop_duplicates("Item SKU").set_index("Item SKU")["Category"].to_dict()
    soh_full["Category"] = soh_full["Item SKU"].map(cat_map).fillna("Unknown")

critical_skus = pd.DataFrame()
reorder_skus  = pd.DataFrame()
if not soh_full.empty and "Days of Stock" in soh_full.columns:
    has_fc = soh_full[soh_full["Per Day Req"] > 0].copy()
    if "Item SKU" in df_raw.columns and "Item Name" in df_raw.columns:
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
# 🔔 NOTIFICATION BUTTONS — placed immediately below KPI cards
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="background:#0d1117;border:1px solid #1e2535;border-radius:12px;'
    'padding:12px 16px;margin-bottom:16px;">'
    '<div style="font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;'
    'letter-spacing:1.2px;margin-bottom:10px;">'
    '🔔 Send Alerts'
    '<span style="display:inline-block;flex:1;height:1px;background:#1e2535;'
    'margin-left:8px;vertical-align:middle;width:calc(100% - 90px);"></span>'
    '</div>',
    unsafe_allow_html=True
)

nb1, nb2 = st.columns(2)
with nb1:
    st.markdown('<div class="notif-btn-tg">', unsafe_allow_html=True)
    send_tg_clicked = st.button(
        f"✈️  Telegram  ·  {n_crit} Critical SKUs",
        key="btn_tg", use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
with nb2:
    st.markdown('<div class="notif-btn-email">', unsafe_allow_html=True)
    send_email_clicked = st.button(
        f"📧  Email Critical Table  ·  {n_crit} SKUs",
        key="btn_email", use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)   # close alert bar

# ── Handle clicks ─────────────────────────────────────────────────────────────
if send_tg_clicked:
    if n_crit == 0:
        st.info("ℹ️ No critical SKUs right now — nothing to send.")
    else:
        msg = build_telegram_critical(n_crit, n_zero, critical_skus)
        ok, info = send_telegram(msg)
        st.success(info) if ok else st.error(info)

if send_email_clicked:
    if n_crit == 0:
        st.info("ℹ️ No critical SKUs right now — nothing to send.")
    else:
        subject   = f"[🚨 YogaBar RM Alert] {n_crit} Critical SKUs · {n_zero} Stockout Today"
        html_body = build_email_critical_html(n_crit, n_zero, critical_skus)
        ok, info  = send_email(subject, html_body)
        st.success(info) if ok else st.error(info)

# ══════════════════════════════════════════════════════════════════════════════
# INTELLIGENCE PANELS (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)
st.markdown('<div class="sec-div">🔍 Inventory Intelligence</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;">'

    f'<div style="background:#1a0608;border:1.5px solid #7f1d1d;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#ef4444;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🔴 Stockout Today</div>'
    f'<div style="font-size:28px;font-weight:800;color:#fca5a5;font-family:JetBrains Mono,monospace;line-height:1;">{n_zero}</div>'
    f'<div style="font-size:10px;color:#7f1d1d;margin-top:3px;">SKUs at ≤ 1 day</div>'
    f'</div>'

    f'<div style="background:#160a00;border:1.5px solid #92400e;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#f97316;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🟠 Critical &lt; 7d</div>'
    f'<div style="font-size:28px;font-weight:800;color:#fed7aa;font-family:JetBrains Mono,monospace;line-height:1;">{n_crit}</div>'
    f'<div style="font-size:10px;color:#78350f;margin-top:3px;">SKUs need reorder</div>'
    f'</div>'

    f'<div style="background:#0f0d02;border:1.5px solid #78350f;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#f59e0b;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🟡 Low 7–14d</div>'
    f'<div style="font-size:28px;font-weight:800;color:#fde68a;font-family:JetBrains Mono,monospace;line-height:1;">{n_low}</div>'
    f'<div style="font-size:10px;color:#713f12;margin-top:3px;">SKUs watch closely</div>'
    f'</div>'

    f'<div style="background:#061a0a;border:1.5px solid #14532d;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">✅ Healthy &gt; 14d</div>'
    f'<div style="font-size:28px;font-weight:800;color:#bbf7d0;font-family:JetBrains Mono,monospace;line-height:1;">{n_ok}</div>'
    f'<div style="font-size:10px;color:#14532d;margin-top:3px;">SKUs well stocked</div>'
    f'</div>'

    '</div>',
    unsafe_allow_html=True
)

col_alert, col_reorder = st.columns(2, gap="medium")

with col_alert:
    st.markdown(
        '<div style="background:#140608;border:1.5px solid #7f1d1d;border-radius:14px;padding:14px 16px;margin-bottom:12px;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
        '<div style="font-size:10px;font-weight:700;color:#ef4444;text-transform:uppercase;letter-spacing:1.2px;">🚨 Critical — Runs Out &lt; 7 Days</div>'
        f'<div style="background:#2d0a0a;border:1px solid #7f1d1d;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800;color:#fca5a5;font-family:JetBrains Mono,monospace;">{n_crit} SKUs</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if critical_skus.empty:
        st.markdown('<div style="color:#334155;font-size:12px;padding:8px 0;text-align:center;">✅ No critical SKUs right now</div>', unsafe_allow_html=True)
    else:
        for _, r in critical_skus.iterrows():
            dos   = float(r["Days of Stock"])
            soh_v = float(r["SOH"])
            pdr   = float(r["Per Day Req"])
            sku   = str(r["Item SKU"])
            name  = str(r.get("Item Name", ""))
            cat   = str(r.get("Category", ""))
            if dos <= 1:
                bar_c,txt_c,bg_c,bdr_c,badge = "#dc2626","#fca5a5","#1f0406","#7f1d1d","STOCKOUT"
            elif dos <= 3:
                bar_c,txt_c,bg_c,bdr_c,badge = "#ef4444","#fca5a5","#1a0608","#450a0a",f"{dos:.1f}d left"
            else:
                bar_c,txt_c,bg_c,bdr_c,badge = "#f97316","#fed7aa","#180b02","#431407",f"{dos:.1f}d left"
            bar_w = min(int(dos / 7 * 100), 100)
            urgency = "⛔ Stocking out NOW" if dos <= 1 else (f"🔴 Gone in ~{int(dos)}d" if dos <= 3 else f"🟠 ~{dos:.1f} days remaining")
            st.markdown(
                f'<div style="background:{bg_c};border:1px solid {bdr_c};border-radius:10px;padding:10px 14px;margin-bottom:7px;">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="font-size:11px;font-weight:700;color:{txt_c};font-family:JetBrains Mono,monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sku}</div>'
                f'<div style="font-size:10px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">{name}</div>'
                f'</div><div style="margin-left:10px;flex-shrink:0;">'
                f'<div style="background:#2d0a0a;border:1px solid {bdr_c};border-radius:6px;padding:3px 8px;font-size:11px;font-weight:800;color:{txt_c};font-family:JetBrains Mono,monospace;text-align:center;">{badge}</div>'
                f'</div></div>'
                f'<div style="font-size:10px;color:#f87171;margin-bottom:5px;font-weight:600;">{urgency}</div>'
                f'<div style="background:#2d0a0a;border-radius:4px;height:5px;margin-bottom:6px;">'
                f'<div style="width:{bar_w}%;background:{bar_c};height:5px;border-radius:4px;"></div></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;">'
                f'<div style="background:#0d0204;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">SOH</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{soh_v:,.0f}</div></div>'
                f'<div style="background:#0d0204;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Per Day</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{pdr:.1f}</div></div>'
                f'<div style="background:#0d0204;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Category</div>'
                f'<div style="font-size:10px;font-weight:600;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{cat[:12] if cat else "—"}</div>'
                f'</div></div></div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

with col_reorder:
    st.markdown(
        '<div style="background:#0f0d02;border:1.5px solid #78350f;border-radius:14px;padding:14px 16px;margin-bottom:12px;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
        '<div style="font-size:10px;font-weight:700;color:#f59e0b;text-transform:uppercase;letter-spacing:1.2px;">⚡ Reorder Watchlist — 7 to 14 Days</div>'
        f'<div style="background:#2d1f00;border:1px solid #78350f;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800;color:#fde68a;font-family:JetBrains Mono,monospace;">{n_low} SKUs</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if reorder_skus.empty:
        st.markdown('<div style="color:#334155;font-size:12px;padding:8px 0;text-align:center;">✅ No SKUs in watchlist</div>', unsafe_allow_html=True)
    else:
        for _, r in reorder_skus.iterrows():
            dos   = float(r["Days of Stock"])
            soh_v = float(r["SOH"])
            pdr   = float(r["Per Day Req"])
            sku   = str(r["Item SKU"])
            name  = str(r.get("Item Name",""))
            cat   = str(r.get("Category",""))
            bar_w = min(int((dos - 7) / 7 * 100), 100)
            st.markdown(
                f'<div style="background:#120d00;border:1px solid #451a03;border-radius:10px;padding:10px 14px;margin-bottom:7px;">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="font-size:11px;font-weight:700;color:#fde68a;font-family:JetBrains Mono,monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sku}</div>'
                f'<div style="font-size:10px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">{name}</div>'
                f'</div><div style="margin-left:10px;flex-shrink:0;">'
                f'<div style="background:#2d1f00;border:1px solid #78350f;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:800;color:#fde68a;font-family:JetBrains Mono,monospace;">{dos:.1f}d</div>'
                f'</div></div>'
                f'<div style="background:#2d1f00;border-radius:4px;height:5px;margin-bottom:6px;">'
                f'<div style="width:{bar_w}%;background:#f59e0b;height:5px;border-radius:4px;"></div></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;">'
                f'<div style="background:#0a0800;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">SOH</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{soh_v:,.0f}</div></div>'
                f'<div style="background:#0a0800;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Per Day</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{pdr:.1f}</div></div>'
                f'<div style="background:#0a0800;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Category</div>'
                f'<div style="font-size:10px;font-weight:600;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{cat[:12] if cat else "—"}</div>'
                f'</div></div></div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DETAILED TABLE (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr style="border:none;border-top:1px solid #161d2e;margin:14px 0;">', unsafe_allow_html=True)
st.markdown('<div class="sec-div">Detailed Records</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="tbl-hdr"><span class="tbl-lbl">📋 RM Inventory · Forecast · Days of Stock</span>'
    f'<span class="tbl-badge">{len(df_m):,} rows</span></div>',
    unsafe_allow_html=True
)
st.markdown("""
<div class="legend-bar">
    <span><span class="ldot" style="background:#ef4444"></span><span style="color:#f87171">Critical &lt; 7 days</span></span>
    <span><span class="ldot" style="background:#f59e0b"></span><span style="color:#fbbf24">Low 7–14 days</span></span>
    <span><span class="ldot" style="background:#5bc8c0"></span><span style="color:#99f6e4">Healthy &gt; 14 days</span></span>
    <span style="color:#475569;margin-left:auto;font-size:10px;font-family:JetBrains Mono,monospace;">DoS = SOH ÷ (Forecast ÷ 24)</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df_m.to_excel(w, index=False, sheet_name="RM Inventory")
st.download_button("⬇  Export to Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df_m.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_row(row):
        dos = row.get("Days of Stock", None)
        if pd.isna(dos) or dos is None: return [""] * len(row)
        if dos < 7:   return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
        if dos <= 14: return ["background-color:#2d1f00; color:#fde68a"] * len(row)
        return ["background-color:#061410; color:#99f6e4"] * len(row)

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

    st.dataframe(df_show.style.apply(colour_row, axis=1),
        use_container_width=True, height=520, hide_index=True,
        column_config={
            "Qty Available":      st.column_config.NumberColumn("Qty Avail",       format="%.0f"),
            "Forecast":           st.column_config.NumberColumn("Forecast",        format="%.0f"),
            "Per Day Req":        st.column_config.NumberColumn("Per Day Req",     format="%.2f"),
            "Days of Stock":      st.column_config.NumberColumn("Days of Stock ⏱", format="%.1f"),
            "Qty Inward":         st.column_config.NumberColumn("Inward",          format="%.0f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Issue/Hold",      format="%.0f"),
            "Value (Inc Tax)":    st.column_config.NumberColumn("Val (Inc)",       format="%.0f"),
            "Value (Ex Tax)":     st.column_config.NumberColumn("Val (Ex)",        format="%.0f"),
        })

st.markdown('<div class="app-footer">YOGABAR · RM INVENTORY</div>', unsafe_allow_html=True)
