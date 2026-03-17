import streamlit as st
import pandas as pd
import io
import requests as _requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Consumption vs Forecast · YogaBar",
    layout="wide", page_icon="📈",
    initial_sidebar_state="expanded"
)

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("Consumption vs Forecast")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

:root {
  --bg:#05070f; --bg1:#080b14; --bg2:#0c1020; --bg3:#111827;
  --border:#161d2e; --border2:#1e2840;
  --text:#e2e8f0; --muted:#64748b; --dim:#2d3a50;
  --actual:#06b6d4; --expect:#1e2d45;
  --over:#ef4444; --under:#22c55e; --ontrack:#3b82f6;
}
*,*::before,*::after{box-sizing:border-box;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.main{
  background:var(--bg)!important;font-family:'Inter',sans-serif!important;color:var(--text)!important;
}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;}
.block-container{padding:1rem 1.4rem 4rem!important;max-width:100%!important;}
[data-testid="stVerticalBlock"]>div{gap:0!important;}

.app-header{display:flex;align-items:center;justify-content:space-between;padding-bottom:14px;border-bottom:1px solid var(--border);margin-bottom:16px;}
.hdr-left{display:flex;align-items:center;gap:10px;}
.hdr-logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#0c1a10,#122418);border:1px solid #14532d;display:flex;align-items:center;justify-content:center;font-size:20px;}
.hdr-title{font-size:17px;font-weight:800;color:#f1f5f9;}
.hdr-sub{font-size:11px;color:var(--muted);margin-top:1px;}
.live-pill{display:inline-flex;align-items:center;gap:6px;background:#041208;border:1px solid #155e2e;border-radius:20px;padding:5px 13px;font-size:10px;font-weight:700;color:#22c55e;letter-spacing:1.2px;font-family:'JetBrains Mono',monospace;}
.live-dot{width:6px;height:6px;background:#22c55e;border-radius:50%;animation:blink 1.8s infinite;}
@keyframes blink{0%,100%{opacity:1;box-shadow:0 0 6px #22c55e}50%{opacity:.2;box-shadow:none}}

.stButton>button{background:var(--bg1)!important;border:1px solid var(--border2)!important;border-radius:9px!important;color:var(--muted)!important;font-size:12px!important;font-weight:600!important;width:100%!important;padding:9px!important;margin-bottom:8px!important;transition:all .2s!important;}
.stButton>button:hover{border-color:var(--actual)!important;color:var(--actual)!important;}
.stDownloadButton>button{background:linear-gradient(135deg,#0f172a,#1e1b4b)!important;border:1.5px solid #4338ca!important;border-radius:9px!important;color:#a5b4fc!important;font-size:13px!important;font-weight:700!important;width:100%!important;padding:10px!important;}

.filter-wrap{background:var(--bg1);border:1px solid var(--border);border-radius:14px;padding:12px 14px;margin-bottom:16px;}
.filter-title{font-size:10px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:1.3px;margin-bottom:10px;display:flex;align-items:center;gap:6px;}
.filter-title::after{content:'';flex:1;height:1px;background:var(--border);}
[data-testid="stTextInput"]>div>div{background:var(--bg3)!important;border:1.5px solid var(--border2)!important;border-radius:9px!important;}
[data-testid="stTextInput"]>div>div:focus-within{border-color:var(--actual)!important;}
[data-testid="stTextInput"] input{background:transparent!important;color:var(--text)!important;font-size:13px!important;padding:9px 12px!important;border:none!important;}
[data-testid="stTextInput"] input::placeholder{color:var(--dim)!important;}
[data-testid="stSelectbox"]>div>div{background:var(--bg3)!important;border:1.5px solid var(--border2)!important;border-radius:9px!important;color:var(--text)!important;font-size:12.5px!important;}
[data-testid="stWidgetLabel"]{display:none!important;}

.kpi-row{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:20px;}
.kpi-box{border-radius:14px;padding:16px;border:1px solid var(--border);background:var(--bg1);position:relative;overflow:hidden;transition:transform .18s;}
.kpi-box:hover{transform:translateY(-2px);}
.kpi-box::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.m0::before{background:#06b6d4;} .m1::before{background:#a855f7;}
.m2::before{background:#f59e0b;} .m3::before{background:#ec4899;}
.m4::before{background:#22c55e;}
.kpi-mth{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.3px;margin-bottom:5px;}
.m0 .kpi-mth{color:#06b6d4;} .m1 .kpi-mth{color:#a855f7;}
.m2 .kpi-mth{color:#f59e0b;} .m3 .kpi-mth{color:#ec4899;}
.m4 .kpi-mth{color:#22c55e;}
.kpi-num{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;color:var(--text);line-height:1;letter-spacing:-1px;}
.kpi-meta{font-size:10px;color:var(--muted);margin-top:5px;}
.kpi-exp{font-size:10px;color:var(--muted);margin-top:3px;font-family:'JetBrains Mono',monospace;}
.var-badge{display:inline-block;font-size:9px;font-weight:700;padding:2px 8px;border-radius:20px;margin-top:6px;font-family:'JetBrains Mono',monospace;}
.var-badge.over{background:#2d0a0a;color:#f87171;border:1px solid #7f1d1d;}
.var-badge.under{background:#061a0a;color:#4ade80;border:1px solid #14532d;}
.var-badge.ok{background:#0a1628;color:#60a5fa;border:1px solid #1e3a5f;}

.sec{font-size:10px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:1.4px;padding:14px 0 10px;display:flex;align-items:center;gap:8px;}
.sec::after{content:'';flex:1;height:1px;background:var(--border);}

.chart-wrap{background:var(--bg1);border:1px solid var(--border);border-radius:16px;padding:18px 20px;margin-bottom:20px;}

/* ── Trend chart: premium gradient background ─────────────────────────────── */
.trend-wrap{
  position:relative; border-radius:20px; padding:22px 22px 10px;
  margin-bottom:20px; overflow:hidden; border:1px solid #1e2840;
  background:
    radial-gradient(ellipse at 15% 80%, rgba(6,182,212,0.07)  0%, transparent 55%),
    radial-gradient(ellipse at 85% 20%, rgba(168,85,247,0.07) 0%, transparent 55%),
    radial-gradient(ellipse at 50% 50%, rgba(30,40,64,0.4)    0%, transparent 70%),
    linear-gradient(160deg, #080d1a 0%, #060911 60%, #080d1a 100%);
}
.trend-wrap::before{
  content:''; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg, transparent, rgba(6,182,212,0.4), rgba(168,85,247,0.4), transparent);
}

/* ── SKU drill-down panel ─────────────────────────────────────────────────── */
.drill-panel{
  border-radius:16px; padding:18px 20px; margin-bottom:18px;
  border:1.5px solid #1e3a5f;
  background:linear-gradient(135deg,#060d1a,#080e1f);
  position:relative; overflow:hidden;
}
.drill-panel::before{
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,#06b6d4,#a855f7);
}
.drill-sku{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700;color:#06b6d4;}
.drill-name{font-size:11px;color:#475569;margin-top:3px;}
.drill-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:14px;}
.drill-month{border-radius:10px;padding:12px;border:1px solid var(--border2);background:rgba(0,0,0,.3);text-align:center;}
.drill-month-lbl{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}
.drill-actual{font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;line-height:1;}
.drill-exp{font-size:10px;color:var(--muted);margin-top:3px;}
.drill-var{font-size:10px;font-weight:700;font-family:'JetBrains Mono',monospace;margin-top:4px;}

/* ── AI Summary panel ─────────────────────────────────────────────────────── */
.ai-panel{
  border-radius:16px; padding:18px 20px; margin-bottom:18px;
  border:1.5px solid #2d1f50;
  background:linear-gradient(135deg,#0a0618,#0d0a20);
}
.ai-header{display:flex;align-items:center;gap:10px;margin-bottom:14px;}
.ai-icon{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#4c1d95,#5b21b6);display:flex;align-items:center;justify-content:center;font-size:14px;}
.ai-title{font-size:12px;font-weight:700;color:#c084fc;text-transform:uppercase;letter-spacing:1.2px;}
.ai-body{font-size:13px;line-height:1.8;color:#d1d5db;}
.ai-body b{color:#e2e8f0;}

/* ── Toggle buttons ───────────────────────────────────────────────────────── */
.toggle-row{display:flex;gap:8px;margin-bottom:12px;}
.t-btn{padding:6px 16px;border-radius:8px;font-size:11px;font-weight:700;cursor:pointer;border:1px solid var(--border2);background:var(--bg2);color:var(--muted);transition:all .15s;}
.t-btn.active{background:#0a1628;border-color:#06b6d4;color:#06b6d4;}

.chart-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px;}
.chart-title{font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1.2px;}
.info-box{background:#0a1628;border:1px solid #1e3a5f;border-radius:10px;padding:12px 16px;margin-bottom:14px;font-size:11px;color:#60a5fa;font-family:'JetBrains Mono',monospace;line-height:1.7;}
.info-box b{color:#93c5fd;}
div[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden!important;border:1px solid var(--border)!important;}
.tbl-hdr{display:flex;align-items:center;justify-content:space-between;padding:6px 0;}
.tbl-lbl{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px;}
.tbl-badge{background:var(--bg2);border:1px solid var(--border2);color:#818cf8;font-size:11px;font-weight:700;padding:3px 11px;border-radius:20px;font-family:'JetBrains Mono',monospace;}
.footer{margin-top:3rem;padding-top:12px;border-top:1px solid var(--border);text-align:center;font-size:10px;font-weight:600;color:var(--dim);letter-spacing:2px;font-family:'JetBrains Mono',monospace;}

/* ai button */
.ai-btn>button{
  background:linear-gradient(135deg,#0a0618,#130a2a)!important;
  border:1.5px solid #7c3aed!important;color:#c084fc!important;
  font-size:13px!important;font-weight:700!important;
  border-radius:10px!important;padding:11px!important;
  width:100%!important;transition:all .2s!important;
}
.ai-btn>button:hover{border-color:#a855f7!important;color:#e9d5ff!important;box-shadow:0 0 20px rgba(124,58,237,.15)!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MONTH CONFIG
# ══════════════════════════════════════════════════════════════════════════════
now = datetime.now()
MONTHS = []
for i in range(4, -1, -1):
    t = pd.Timestamp(now.year, now.month, 1) - pd.DateOffset(months=i)
    d = (pd.Timestamp(t.year, t.month, 1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).day
    MONTHS.append({
        "month": t.month, "year": t.year,
        "label": t.strftime("%b %Y"),
        "short": t.strftime("%b"),
        "days":  d,
        "full":  t.strftime("%B"),
    })

MONTH_COLORS = ["#06b6d4","#a855f7","#f59e0b","#ec4899","#22c55e"]
MONTH_CSS    = ["m0","m1","m2","m3","m4"]
LINE_COLORS  = ["#06b6d4","#a855f7","#f59e0b","#ec4899","#22c55e",
                "#f87171","#60a5fa","#4ade80","#fb923c","#e879f9"]
FILL_COLORS  = [c.replace("#","rgba(").replace(")","") + ",0.06)" if c.startswith("#") else c
                for c in ["rgba(6,182,212","rgba(168,85,247","rgba(245,158,11",
                           "rgba(236,72,153","rgba(34,197,94","rgba(248,113,113",
                           "rgba(96,165,250","rgba(74,222,128","rgba(251,146,60",
                           "rgba(232,121,249"]]

# ══════════════════════════════════════════════════════════════════════════════
# FORECAST LOADER
# ══════════════════════════════════════════════════════════════════════════════
MONTH_ABBR = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
MONTH_FULL = ["january","february","march","april","may","june",
              "july","august","september","october","november","december"]

def col_to_month_num(col_name: str):
    import re
    s = col_name.strip().lower().replace("forecast","").replace("qty","").strip(" -_")
    for i, full in enumerate(MONTH_FULL):
        if full in s or s == full:
            return i + 1
    for i, abbr in enumerate(MONTH_ABBR):
        if re.search(r'\b' + abbr + r'\b', s):
            return i + 1
    return None

@st.cache_data(ttl=300)
def load_forecast_by_month():
    df_fc = load_sheet("Forecast")
    if df_fc.empty: return {}, [], "empty"
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    ic_col = next((c for c in df_fc.columns if "item" in c.lower() and "code" in c.lower()), None)
    if not ic_col: ic_col = next((c for c in df_fc.columns if "sku" in c.lower()), None)
    if not ic_col: return {}, [], "no_item_col"
    df_fc[ic_col] = df_fc[ic_col].astype(str).str.strip().str.upper()
    fc_cols = {}
    detected_cols = []
    for col in df_fc.columns:
        if "forecast" in col.lower():
            m = col_to_month_num(col)
            if m:
                fc_cols[m] = col
                detected_cols.append(f"{col} → Month {m}")
    if not fc_cols: return {}, [], "no_forecast_cols"
    result = {}
    for month_int, col in fc_cols.items():
        df_fc[col] = pd.to_numeric(df_fc[col], errors="coerce").fillna(0)
        sub = df_fc[df_fc[col] > 0][[ic_col, col]].copy()
        sub.columns = ["_key","Forecast"]
        result[month_int] = sub.groupby("_key")["Forecast"].sum().reset_index()
    return result, detected_cols, "wide"

@st.cache_data(ttl=300)
def load_consumption():
    df_con = load_sheet("Consumption")
    if df_con.empty: return pd.DataFrame(), None, None, None, None
    df_con.columns = df_con.columns.str.strip()
    date_col = next((c for c in df_con.columns if "date" in c.lower()), None)
    if date_col:
        df_con[date_col] = pd.to_datetime(df_con[date_col], errors="coerce")
        df_con["_month"] = df_con[date_col].dt.month
        df_con["_year"]  = df_con[date_col].dt.year
    con_col  = next((c for c in df_con.columns if "consumed" in c.lower()), None)
    mat_col  = next((c for c in df_con.columns if "material" in c.lower() and ("code" in c.lower() or "sku" in c.lower())), None)
    if not mat_col: mat_col = next((c for c in df_con.columns if "sku" in c.lower()), None)
    name_col = next((c for c in df_con.columns if "material name" in c.lower()), mat_col)
    cat_col  = next((c for c in df_con.columns if "category" in c.lower()), None)
    if mat_col: df_con[mat_col] = df_con[mat_col].astype(str).str.strip().str.upper()
    if con_col: df_con[con_col] = pd.to_numeric(df_con[con_col], errors="coerce").fillna(0)
    return df_con, mat_col, con_col, name_col, cat_col

@st.cache_data(ttl=300)
def build_data():
    fc_dict, detected_cols, fc_fmt = load_forecast_by_month()
    raw = load_consumption()
    if isinstance(raw[0], pd.DataFrame) and raw[0].empty:
        return pd.DataFrame(), fc_fmt, detected_cols
    df_con, mat_col, con_col, name_col, cat_col = raw
    if not mat_col or not con_col: return pd.DataFrame(), fc_fmt, detected_cols
    frames = []
    for minfo in MONTHS:
        if "_month" not in df_con.columns: continue
        mdf = df_con[(df_con["_month"] == minfo["month"]) & (df_con["_year"] == minfo["year"])].copy()
        if mdf.empty: continue
        agg_dict = {con_col: "sum"}
        if name_col and name_col != mat_col: agg_dict[name_col] = "first"
        if cat_col: agg_dict[cat_col] = "first"
        agg = mdf.groupby(mat_col).agg(agg_dict).reset_index()
        cols = ["Material SKU","Actual"] + \
               (["Material Name"] if name_col and name_col != mat_col else []) + \
               (["Category"] if cat_col else [])
        agg.columns = cols
        agg["Month"]    = minfo["label"]
        agg["MonthNum"] = minfo["month"]
        agg["_key"]     = agg["Material SKU"]
        fc_month = fc_dict.get(minfo["month"], pd.DataFrame(columns=["_key","Forecast"]))
        agg = agg.merge(fc_month, on="_key", how="left").drop(columns=["_key"])
        agg["Forecast"]  = agg["Forecast"].fillna(0)
        agg["Expected"]  = agg["Forecast"].round(0)
        agg["Per Day"]   = (agg["Forecast"] / minfo["days"]).round(2)
        agg["Variance"]  = agg["Actual"] - agg["Expected"]
        agg["Var %"]     = agg.apply(lambda r: round((r["Actual"]/r["Expected"]*100-100),1) if r["Expected"]>0 else 0, axis=1)
        agg["Status"]    = agg["Variance"].apply(lambda v: "Over" if v>0 else ("Under" if v<0 else "On Track"))
        agg = agg[agg["Actual"] > 0]
        frames.append(agg)
    if not frames: return pd.DataFrame(), fc_fmt, detected_cols
    return pd.concat(frames, ignore_index=True), fc_fmt, detected_cols

df_full, fc_fmt, detected_cols = build_data()

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "chart_mode"    not in st.session_state: st.session_state["chart_mode"]    = "Actual Qty"
if "selected_sku"  not in st.session_state: st.session_state["selected_sku"]  = None
if "ai_summary"    not in st.session_state: st.session_state["ai_summary"]    = ""
if "ai_loading"    not in st.session_state: st.session_state["ai_loading"]    = False

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="app-header">
  <div class="hdr-left">
    <div class="hdr-logo">📈</div>
    <div>
      <div class="hdr-title">Consumption vs Forecast</div>
      <div class="hdr-sub">YogaBar · 5-Month Actual vs Expected · Month-Matched Forecast</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#475569;">{now.strftime('%d %b %Y')}</div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear(); st.rerun()

# Info box
if detected_cols:
    st.markdown(
        f'<div class="info-box">✅ Forecast columns detected: <b>{" · ".join(detected_cols)}</b></div>',
        unsafe_allow_html=True
    )

if df_full.empty:
    st.error("⚠️ No consumption data found for the last 5 months."); st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns([3, 2, 2])
with f1: search = st.text_input("s", placeholder="🔍 Search SKU / material name…", label_visibility="collapsed")
with f2:
    month_opts = ["All Months"] + [m["label"] for m in MONTHS]
    sel_month  = st.selectbox("m", month_opts, label_visibility="collapsed")
with f3:
    type_opts = ["All Types","RM (Raw Material)","PM (Packaging Material)"]
    sel_type  = st.selectbox("t", type_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

df = df_full.copy()
if search:    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_month != "All Months":  df = df[df["Month"] == sel_month]
if sel_type == "RM (Raw Material)":         df = df[~df["Material SKU"].str.startswith("PM")]
elif sel_type == "PM (Packaging Material)": df = df[df["Material SKU"].str.startswith("PM")]

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📅 Monthly Summary</div>', unsafe_allow_html=True)
html = '<div class="kpi-row">'
for i, minfo in enumerate(MONTHS):
    mdf    = df[df["Month"] == minfo["label"]]
    actual = mdf["Actual"].sum()
    exp    = mdf["Expected"].sum()
    n      = mdf["Material SKU"].nunique()
    var_pct= round((actual/exp*100-100),1) if exp>0 else 0
    cls    = "over" if var_pct>5 else ("under" if var_pct<-5 else "ok")
    lbl    = f"+{var_pct:.1f}%" if var_pct>0 else f"{var_pct:.1f}%"
    html  += f"""
    <div class="kpi-box {MONTH_CSS[i]}">
      <div class="kpi-mth">{minfo['label']}</div>
      <div class="kpi-num">{actual:,.0f}</div>
      <div class="kpi-meta">{n} materials</div>
      <div class="kpi-exp">Exp: {exp:,.0f}</div>
      <span class="var-badge {cls}">{lbl}</span>
    </div>"""
html += '</div>'
st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TOP 10 SKUS
# ══════════════════════════════════════════════════════════════════════════════
top10 = (
    df.groupby("Material SKU")
    .agg(Actual=("Actual","sum"), Expected=("Expected","sum"))
    .reset_index()
)
top10 = top10[top10["Actual"]>0].nlargest(10,"Actual").copy()
top10_skus = top10["Material SKU"].tolist()

trend_pivot = (
    df[df["Material SKU"].isin(top10_skus)]
    .pivot_table(index="Material SKU", columns="Month", values="Actual", aggfunc="sum")
    .reindex(columns=[m["label"] for m in MONTHS])
    .fillna(0)
)
var_pivot = (
    df[df["Material SKU"].isin(top10_skus)]
    .pivot_table(index="Material SKU", columns="Month", values="Var %", aggfunc="mean")
    .reindex(columns=[m["label"] for m in MONTHS])
    .fillna(0)
)

month_labels_short = [m["short"] for m in MONTHS]

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 1: VARIANCE TOGGLE + TREND CHART
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📉 5-Month Consumption Trend</div>', unsafe_allow_html=True)

# Toggle buttons
t_col1, t_col2, t_col3 = st.columns([2, 2, 6])
with t_col1:
    if st.button("📊  Actual Qty", key="btn_actual",
                 type="primary" if st.session_state["chart_mode"]=="Actual Qty" else "secondary"):
        st.session_state["chart_mode"] = "Actual Qty"
        st.rerun()
with t_col2:
    if st.button("📈  Variance %", key="btn_variance",
                 type="primary" if st.session_state["chart_mode"]=="Variance %" else "secondary"):
        st.session_state["chart_mode"] = "Variance %"
        st.rerun()

# Build chart based on mode
mode      = st.session_state["chart_mode"]
use_var   = (mode == "Variance %")
pivot_use = var_pivot if use_var else trend_pivot
y_format  = "+.1f%" if use_var else ","
y_title   = "Variance %" if use_var else "Qty"

fig_trend = go.Figure()
shapes = [dict(type="line", xref="x", yref="paper", x0=m, x1=m, y0=0, y1=1,
               line=dict(color="rgba(255,255,255,0.03)", width=1))
          for m in month_labels_short[1:]]

# Zero line for variance mode
if use_var:
    shapes.append(dict(type="line", xref="paper", yref="y", x0=0, x1=1, y0=0, y1=0,
                       line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot")))

for idx, (sku, row) in enumerate(pivot_use.iterrows()):
    clr  = LINE_COLORS[idx % len(LINE_COLORS)]
    fill = FILL_COLORS[idx % len(FILL_COLORS)]
    vals = row.values.tolist()
    # In variance mode: color markers red/green based on value
    marker_colors = [clr] * len(vals)
    if use_var:
        marker_colors = ["#ef4444" if v < -10 else ("#22c55e" if v > 10 else "#f59e0b") for v in vals]

    fig_trend.add_trace(go.Scatter(
        x=month_labels_short, y=vals,
        name=sku, mode="lines+markers",
        line=dict(color=clr, width=2.5, shape="spline", smoothing=0.7),
        marker=dict(size=9, color=marker_colors,
                    line=dict(color="#080d1a", width=2), symbol="circle"),
        fill="tozeroy" if not use_var else None,
        fillcolor=fill if not use_var else None,
        hovertemplate=(
            f"<b>{sku}</b><br>%{{x}}: <b>%{{y:,.1f}}{'%' if use_var else ' units'}</b><extra></extra>"
        )
    ))

fig_trend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,14,26,0.7)",
    font=dict(family="Inter", color="#94a3b8", size=11),
    height=440, shapes=shapes,
    margin=dict(l=14, r=190, t=20, b=44),
    legend=dict(
        yanchor="middle", y=0.5, xanchor="left", x=1.01,
        bgcolor="rgba(8,13,26,0.9)", bordercolor="#1e2840", borderwidth=1,
        font=dict(size=10, family="JetBrains Mono"),
        itemclick="toggleothers", itemdoubleclick="toggle",
    ),
    xaxis=dict(showgrid=False, zeroline=False,
               tickfont=dict(size=14, color="#94a3b8"), linecolor="#1e2840",
               ticklen=7, tickcolor="#1e2840"),
    yaxis=dict(showgrid=True, gridcolor="rgba(30,40,64,0.5)", zeroline=False,
               tickfont=dict(size=10, color="#475569"),
               tickformat="+.1f%" if use_var else ",",
               title=dict(text=y_title, font=dict(size=10, color="#475569"))),
    hoverlabel=dict(bgcolor="#0c1020", bordercolor="#1e2840",
                    font=dict(color="#e2e8f0", size=12)),
    hovermode="x unified",
)

hint = ("🔴 Red dot = under >10% · 🟡 Amber = within ±10% · 🟢 Green = over >10%"
        if use_var else "Click a SKU in legend to isolate · Double-click to reset")

st.markdown(f"""
<div class="trend-wrap">
  <div class="chart-hdr">
    <div class="chart-title">{'📈 Variance % vs Forecast' if use_var else '📉 Actual Consumption Qty'} — Top 10 SKUs</div>
    <div style="font-size:10px;color:#2d3a50;font-family:'JetBrains Mono',monospace;">{hint}</div>
  </div>
""", unsafe_allow_html=True)

# FEATURE 2: Click on chart → drill-down (using plotly click event)
event = st.plotly_chart(
    fig_trend, use_container_width=True,
    config={"displayModeBar": False},
    on_select="rerun", selection_mode="points",
    key="trend_chart"
)
st.markdown('</div>', unsafe_allow_html=True)

# Handle point click — extract SKU from curve number
if hasattr(event, "selection") and event.selection:
    pts = event.selection.get("points", [])
    if pts:
        curve_idx = pts[0].get("curve_number", 0)
        if curve_idx < len(pivot_use.index):
            clicked_sku = pivot_use.index[curve_idx]
            st.session_state["selected_sku"] = clicked_sku

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 2: SKU DRILL-DOWN PANEL
# ══════════════════════════════════════════════════════════════════════════════
sel_sku = st.session_state.get("selected_sku")

if sel_sku:
    sku_df = df_full[df_full["Material SKU"] == sel_sku].copy()
    sku_name = sku_df["Material Name"].iloc[0] if "Material Name" in sku_df.columns and not sku_df.empty else ""

    # Build month-by-month breakdown
    month_data = []
    for minfo in MONTHS:
        mrow = sku_df[sku_df["Month"] == minfo["label"]]
        if mrow.empty:
            month_data.append({"label": minfo["label"], "short": minfo["short"],
                                "actual": 0, "expected": 0, "var_pct": 0, "status": "—"})
        else:
            r = mrow.iloc[0]
            month_data.append({
                "label": minfo["label"], "short": minfo["short"],
                "actual": float(r["Actual"]), "expected": float(r["Expected"]),
                "var_pct": float(r["Var %"]), "status": str(r["Status"])
            })

    # Drill panel HTML
    drill_months_html = ""
    for j, md in enumerate(month_data):
        clr   = MONTH_COLORS[j]
        v     = md["var_pct"]
        v_clr = "#f87171" if v < -5 else ("#4ade80" if v > 5 else "#60a5fa")
        v_lbl = f"+{v:.1f}%" if v > 0 else f"{v:.1f}%"
        drill_months_html += f"""
        <div class="drill-month">
          <div class="drill-month-lbl" style="color:{clr};">{md['short']}</div>
          <div class="drill-actual" style="color:{clr};">{md['actual']:,.0f}</div>
          <div class="drill-exp">Exp: {md['expected']:,.0f}</div>
          <div class="drill-var" style="color:{v_clr};">{v_lbl}</div>
        </div>"""

    st.markdown(f"""
    <div class="drill-panel">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
        <div>
          <div class="drill-sku">🔍 {sel_sku}</div>
          <div class="drill-name">{sku_name[:60] if sku_name else ''}</div>
        </div>
        <div style="font-size:10px;color:#334155;font-family:'JetBrains Mono',monospace;">
          Click another SKU on the chart to switch · Click away to close
        </div>
      </div>
      <div class="drill-grid">{drill_months_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # Mini bar chart inside drill-down
    fig_drill = go.Figure()
    drill_months_labels = [md["short"] for md in month_data]
    fig_drill.add_trace(go.Bar(
        x=drill_months_labels,
        y=[md["expected"] for md in month_data],
        name="Expected", marker_color="#1e2d45", marker_line_width=0,
        hovertemplate="%{x}: Expected <b>%{y:,.0f}</b><extra></extra>"
    ))
    fig_drill.add_trace(go.Bar(
        x=drill_months_labels,
        y=[md["actual"] for md in month_data],
        name="Actual",
        marker_color=["#ef4444" if md["var_pct"]<-5 else ("#22c55e" if md["var_pct"]>5 else "#06b6d4")
                      for md in month_data],
        marker_line_width=0, opacity=0.9,
        text=[f"{md['var_pct']:+.1f}%" for md in month_data],
        textposition="outside",
        textfont=dict(size=10, color="#94a3b8", family="JetBrains Mono"),
        hovertemplate="%{x}: Actual <b>%{y:,.0f}</b><extra></extra>"
    ))
    fig_drill.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        barmode="overlay", height=220,
        margin=dict(l=10, r=10, t=30, b=20),
        font=dict(family="Inter", color="#94a3b8", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#94a3b8")),
        yaxis=dict(showgrid=True, gridcolor="rgba(30,40,64,0.4)", tickformat=",",
                   tickfont=dict(size=10, color="#475569")),
        title=dict(text=f"{sel_sku} — Actual vs Expected per Month",
                   font=dict(size=11, color="#94a3b8"), x=0),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535",
                        font=dict(color="#e2e8f0", size=12)),
    )
    st.plotly_chart(fig_drill, use_container_width=True, config={"displayModeBar": False})

    if st.button("✕  Close drill-down", key="close_drill"):
        st.session_state["selected_sku"] = None
        st.rerun()

else:
    st.markdown("""
    <div style="background:#080b14;border:1px dashed #1e2535;border-radius:14px;
                padding:14px 20px;margin-bottom:18px;text-align:center;
                color:#2d3a50;font-size:11px;font-family:'JetBrains Mono',monospace;">
      👆 Click any point on the trend chart above to drill into that SKU's 5-month breakdown
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 3: AI SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">🤖 AI Monthly Summary</div>', unsafe_allow_html=True)

# Build context for AI
def build_ai_context(df_data):
    latest_month = MONTHS[-1]["label"]
    latest_df = df_data[df_data["Month"] == latest_month]
    total_actual   = latest_df["Actual"].sum()
    total_expected = latest_df["Expected"].sum()
    total_var_pct  = round((total_actual/total_expected*100-100),1) if total_expected>0 else 0
    over_skus  = latest_df[latest_df["Var %"] > 20].nlargest(5, "Var %")
    under_skus = latest_df[latest_df["Var %"] < -20].nsmallest(5, "Var %")
    over_list  = "; ".join([f"{r['Material SKU']} (+{r['Var %']:.1f}%)" for _, r in over_skus.iterrows()])
    under_list = "; ".join([f"{r['Material SKU']} ({r['Var %']:.1f}%)" for _, r in under_skus.iterrows()])
    # 5-month trend
    trend_summary = []
    for minfo in MONTHS:
        mdf = df_data[df_data["Month"] == minfo["label"]]
        a = mdf["Actual"].sum(); e = mdf["Expected"].sum()
        v = round((a/e*100-100),1) if e>0 else 0
        trend_summary.append(f"{minfo['short']}: actual={a:,.0f}, expected={e:,.0f}, var={v:+.1f}%")
    return f"""
YogaBar Raw Material Consumption Analysis — {now.strftime('%B %Y')}

5-Month Trend:
{chr(10).join(trend_summary)}

Latest Month ({latest_month}):
- Total actual consumption: {total_actual:,.0f}
- Total expected (from forecast): {total_expected:,.0f}
- Overall variance: {total_var_pct:+.1f}%
- Materials over-consumed >20%: {over_list if over_list else 'None'}
- Materials under-consumed >20%: {under_list if under_list else 'None'}
- Total SKUs tracked: {latest_df['Material SKU'].nunique()}

Write a concise, professional 4-sentence summary of:
1. Overall consumption vs forecast performance this month
2. The most notable over-consuming materials and what that might mean for procurement
3. The most notable under-consuming materials and what that might mean
4. A one-line trend observation from the 5-month data (is overall consumption rising, falling, or stable vs forecast?)

Be specific with numbers. Write in plain business English. No bullet points — just flowing sentences.
"""

ai_col1, ai_col2 = st.columns([3, 1])
with ai_col2:
    st.markdown('<div class="ai-btn">', unsafe_allow_html=True)
    gen_ai = st.button("✨  Generate AI Summary", key="btn_ai", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state["ai_summary"]:
        if st.button("🗑  Clear", key="btn_clear_ai", use_container_width=True):
            st.session_state["ai_summary"] = ""
            st.rerun()

if gen_ai:
    context = build_ai_context(df)
    with st.spinner("✨ Generating AI summary…"):
        try:
            resp = _requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": context}]
                },
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                summary = "".join(
                    b.get("text","") for b in data.get("content",[]) if b.get("type")=="text"
                ).strip()
                st.session_state["ai_summary"] = summary
            else:
                st.session_state["ai_summary"] = f"⚠️ API error {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            st.session_state["ai_summary"] = f"⚠️ Request failed: {e}"
    st.rerun()

if st.session_state["ai_summary"]:
    summary_text = st.session_state["ai_summary"]
    if not summary_text.startswith("⚠️"):
        # Format: bold the first sentence of each "insight"
        st.markdown(f"""
        <div class="ai-panel">
          <div class="ai-header">
            <div class="ai-icon">✨</div>
            <div class="ai-title">AI Consumption Analysis — {now.strftime('%B %Y')}</div>
          </div>
          <div class="ai-body">{summary_text.replace(chr(10),'<br>')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(summary_text)
else:
    st.markdown("""
    <div style="background:#0a0618;border:1px dashed #2d1f50;border-radius:14px;
                padding:14px 20px;margin-bottom:18px;text-align:center;
                color:#2d3a50;font-size:11px;font-family:'JetBrains Mono',monospace;">
      ✨ Click "Generate AI Summary" to get a plain-English analysis of this month's consumption vs forecast
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DETAILED TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📋 Detailed Records</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="tbl-hdr">'
    f'<span class="tbl-lbl">5-Month Consumption vs Expected · Month-Matched Forecast</span>'
    f'<span class="tbl-badge">{len(df):,} rows</span></div>',
    unsafe_allow_html=True
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="5-Month Detail")
    try:
        pv = df.pivot_table(index="Material SKU", columns="Month", values="Actual", aggfunc="sum").fillna(0)
        pv.to_excel(w, sheet_name="SKU Pivot")
    except Exception:
        pass
st.download_button("⬇  Export to Excel", buf.getvalue(), "Consumption_5Month.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_row(row):
        s = row.get("Status","")
        if s == "Over":  return ["background-color:#1a0608;color:#fca5a5"] * len(row)
        if s == "Under": return ["background-color:#061a0a;color:#bbf7d0"] * len(row)
        return ["background-color:#0a1628;color:#bfdbfe"] * len(row)

    col_order = ["Month","Material SKU"]
    if "Material Name" in df.columns: col_order.append("Material Name")
    if "Category"      in df.columns: col_order.append("Category")
    col_order += ["Actual","Expected","Variance","Var %","Status"]
    col_order  = [c for c in col_order if c in df.columns]

    st.dataframe(
        df[col_order].style.apply(colour_row, axis=1),
        use_container_width=True, height=540, hide_index=True,
        column_config={
            "Actual":   st.column_config.NumberColumn("Actual",   format="%.0f"),
            "Expected": st.column_config.NumberColumn("Expected", format="%.0f"),
            "Variance": st.column_config.NumberColumn("Variance", format="%.0f"),
            "Var %":    st.column_config.NumberColumn("Var %",    format="%.1f%%"),
            "Status":   st.column_config.TextColumn("Status"),
        }
    )

st.markdown(
    '<div class="footer">YOGABAR · CONSUMPTION VS FORECAST · MONTH-MATCHED</div>',
    unsafe_allow_html=True
)
