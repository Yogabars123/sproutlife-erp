import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500;700&family=Bebas+Neue&display=swap');

:root {
  --bg:      #05070f;
  --bg1:     #080b14;
  --bg2:     #0c1020;
  --bg3:     #111827;
  --border:  #161d2e;
  --border2: #1e2840;
  --text:    #e2e8f0;
  --muted:   #64748b;
  --dim:     #2d3a50;
  /* month palette — 5 distinct accent colours */
  --m0: #06b6d4;   /* cyan    */
  --m1: #a855f7;   /* violet  */
  --m2: #f59e0b;   /* amber   */
  --m3: #ec4899;   /* pink    */
  --m4: #22c55e;   /* green   */
  --forecast: #334155;
}

*, *::before, *::after { box-sizing: border-box; }
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"], .main {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1rem 1.4rem 4rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── TOP BAR ─────────────────────────────────────────────────────────────── */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 16px; border-bottom: 1px solid var(--border); margin-bottom: 18px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: linear-gradient(135deg,#0c1a10,#122418);
  border: 1px solid #14532d;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.brand-title { font-size: 17px; font-weight: 700; color: #f1f5f9; letter-spacing: -.2px; }
.brand-sub   { font-size: 11px; color: var(--muted); margin-top: 1px; }
.live-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: #041208; border: 1px solid #155e2e;
  border-radius: 20px; padding: 5px 13px;
  font-size: 10px; font-weight: 700; color: #22c55e;
  letter-spacing: 1.2px; font-family: 'DM Mono', monospace;
}
.live-dot {
  width: 6px; height: 6px; background: #22c55e; border-radius: 50%;
  animation: pulse 1.8s ease-in-out infinite; box-shadow: 0 0 6px #22c55e;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.2;transform:scale(.8)} }

/* ── BUTTONS ─────────────────────────────────────────────────────────────── */
.stButton > button {
  background: var(--bg1) !important; border: 1px solid var(--border2) !important;
  border-radius: 9px !important; color: var(--muted) !important;
  font-size: 12px !important; font-weight: 600 !important;
  width: 100% !important; padding: 9px !important;
  margin-bottom: 6px !important; transition: all .2s !important;
}
.stButton > button:hover { border-color: #06b6d4 !important; color: #06b6d4 !important; }
.stDownloadButton > button {
  background: linear-gradient(135deg,#0f172a,#1e1b4b) !important;
  border: 1.5px solid #4338ca !important; border-radius: 9px !important;
  color: #a5b4fc !important; font-size: 13px !important; font-weight: 700 !important;
  width: 100% !important; padding: 10px !important;
}

/* ── FILTER BAR ─────────────────────────────────────────────────────────────*/
.filter-wrap { background: var(--bg1); border: 1px solid var(--border); border-radius: 14px; padding: 12px 14px; margin-bottom: 16px; }
.filter-title { font-size: 10px; font-weight: 700; color: var(--dim); text-transform: uppercase; letter-spacing: 1.3px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.filter-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }
[data-testid="stTextInput"] > div > div { background: var(--bg3) !important; border: 1.5px solid var(--border2) !important; border-radius: 9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color: #06b6d4 !important; }
[data-testid="stTextInput"] input { background: transparent !important; color: var(--text) !important; font-size: 13px !important; padding: 9px 12px !important; border: none !important; }
[data-testid="stTextInput"] input::placeholder { color: var(--dim) !important; }
[data-testid="stSelectbox"] > div > div { background: var(--bg3) !important; border: 1.5px solid var(--border2) !important; border-radius: 9px !important; color: var(--text) !important; font-size: 12.5px !important; }
[data-testid="stWidgetLabel"] { display: none !important; }

/* ── KPI SUMMARY ROW ─────────────────────────────────────────────────────── */
.kpi-row { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; margin-bottom: 20px; }
.kpi-box {
  border-radius: 14px; padding: 14px 16px; border: 1px solid var(--border);
  background: var(--bg1); position: relative; overflow: hidden;
  transition: transform .18s;
}
.kpi-box:hover { transform: translateY(-2px); }
.kpi-box::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-box.m0::before { background: var(--m0); }
.kpi-box.m1::before { background: var(--m1); }
.kpi-box.m2::before { background: var(--m2); }
.kpi-box.m3::before { background: var(--m3); }
.kpi-box.m4::before { background: var(--m4); }
.kpi-month { font-family: 'Bebas Neue', sans-serif; font-size: 13px; letter-spacing: 1.5px; margin-bottom: 6px; }
.kpi-box.m0 .kpi-month { color: var(--m0); }
.kpi-box.m1 .kpi-month { color: var(--m1); }
.kpi-box.m2 .kpi-month { color: var(--m2); }
.kpi-box.m3 .kpi-month { color: var(--m3); }
.kpi-box.m4 .kpi-month { color: var(--m4); }
.kpi-big { font-family: 'DM Mono', monospace; font-size: 22px; font-weight: 700; color: var(--text); line-height: 1; letter-spacing: -1px; }
.kpi-sub { font-size: 10px; color: var(--muted); margin-top: 5px; }
.kpi-vs  { font-size: 10px; color: var(--muted); margin-top: 4px; font-family: 'DM Mono', monospace; }
.kpi-pill{
  display: inline-block; font-size: 9px; font-weight: 700; padding: 2px 8px;
  border-radius: 20px; margin-top: 5px; font-family: 'DM Mono', monospace;
}
.kpi-pill.over  { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
.kpi-pill.under { background: #061a0a; color: #4ade80; border: 1px solid #14532d; }
.kpi-pill.ok    { background: #0a1628; color: #60a5fa; border: 1px solid #1e3a5f; }

/* ── SECTION HEADER ──────────────────────────────────────────────────────── */
.sec { font-size: 10px; font-weight: 700; color: var(--dim); text-transform: uppercase; letter-spacing: 1.4px; padding: 14px 0 10px; display: flex; align-items: center; gap: 8px; }
.sec::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* ── HEATMAP GRID ────────────────────────────────────────────────────────── */
.heat-wrap { background: var(--bg1); border: 1px solid var(--border); border-radius: 16px; padding: 18px; margin-bottom: 18px; overflow-x: auto; }
.heat-title { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1.3px; margin-bottom: 14px; }

/* ── TREND CHART CONTAINER ───────────────────────────────────────────────── */
.chart-wrap { background: var(--bg1); border: 1px solid var(--border); border-radius: 16px; padding: 16px 18px; margin-bottom: 18px; }
.chart-title { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1.3px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.chart-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* ── TABLE ───────────────────────────────────────────────────────────────── */
div[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid var(--border) !important; }
.tbl-hdr { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; }
.tbl-lbl { font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1.2px; }
.tbl-badge { background: var(--bg2); border: 1px solid var(--border2); color: #818cf8; font-size: 11px; font-weight: 700; padding: 3px 11px; border-radius: 20px; font-family: 'DM Mono', monospace; }

/* ── MONTH LEGEND STRIP ──────────────────────────────────────────────────── */
.month-strip { display: flex; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.month-chip {
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: 8px; padding: 5px 12px;
  font-size: 11px; font-weight: 600;
}
.month-dot { width: 8px; height: 8px; border-radius: 50%; }

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.footer { margin-top: 3rem; padding-top: 12px; border-top: 1px solid var(--border); text-align: center; font-size: 10px; font-weight: 600; color: var(--dim); letter-spacing: 2px; font-family: 'DM Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MONTH CONFIG — last 5 months ending at current month
# ══════════════════════════════════════════════════════════════════════════════
now = datetime.now()
MONTHS = []
for i in range(4, -1, -1):   # 4 months back → current
    m = (now.month - i - 1) % 12 + 1
    y = now.year - ((now.month - i - 1) // 12 + (1 if (now.month - i - 1) < 0 else 0))
    if (now.month - i - 1) < 0:
        y = now.year - 1
    else:
        y = now.year
    # simpler
    target = pd.Timestamp(now.year, now.month, 1) - pd.DateOffset(months=i)
    MONTHS.append({
        "month": target.month,
        "year":  target.year,
        "label": target.strftime("%b %Y"),
        "short": target.strftime("%b"),
        "days":  (pd.Timestamp(target.year, target.month, 1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).day,
    })

MONTH_COLORS = ["#06b6d4","#a855f7","#f59e0b","#ec4899","#22c55e"]
MONTH_CSS    = ["m0","m1","m2","m3","m4"]

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_all_months():
    df_con = load_sheet("Consumption")
    df_fc  = load_sheet("Forecast")

    if df_con.empty or df_fc.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_con.columns = df_con.columns.str.strip()
    df_fc.columns  = df_fc.columns.str.strip()

    # Parse date
    date_col = next((c for c in df_con.columns if "date" in c.lower()), None)
    if date_col:
        df_con[date_col] = pd.to_datetime(df_con[date_col], errors="coerce")
        df_con["_month"] = df_con[date_col].dt.month
        df_con["_year"]  = df_con[date_col].dt.year

    # Consumed qty column
    con_col = next((c for c in df_con.columns if "consumed" in c.lower()), None)
    if con_col:
        df_con[con_col] = pd.to_numeric(df_con[con_col], errors="coerce").fillna(0)

    # Material SKU column
    mat_col = next((c for c in df_con.columns
                    if ("material" in c.lower() and ("code" in c.lower() or "sku" in c.lower()))
                    or c.lower() == "sku"), None)
    if not mat_col:
        mat_col = next((c for c in df_con.columns if "sku" in c.lower()), None)

    # Material name column
    name_col = next((c for c in df_con.columns if "material name" in c.lower()), mat_col)
    cat_col  = next((c for c in df_con.columns if "category" in c.lower()), None)

    if not mat_col or not con_col:
        return pd.DataFrame(), pd.DataFrame()

    df_con[mat_col] = df_con[mat_col].astype(str).str.strip().str.upper()

    # ── Forecast (plant, all) ──────────────────────────────────────────────
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    df_fc["Forecast"] = pd.to_numeric(df_fc.get("Forecast", 0), errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]
    ic_col = next((c for c in df_fc.columns if "item" in c.lower() and "code" in c.lower()), None)
    if not ic_col:
        return pd.DataFrame(), pd.DataFrame()
    df_fc[ic_col] = df_fc[ic_col].astype(str).str.strip().str.upper()
    fc_agg = df_fc.groupby(ic_col)["Forecast"].sum().reset_index()
    fc_agg.columns = ["_key","Forecast"]

    # ── Per-month aggregation ─────────────────────────────────────────────
    month_frames = []
    for minfo in MONTHS:
        mdf = df_con[
            (df_con["_month"] == minfo["month"]) & (df_con["_year"] == minfo["year"])
        ].copy() if "_month" in df_con.columns else pd.DataFrame()

        if mdf.empty:
            continue

        agg_dict = {con_col: "sum"}
        if name_col and name_col != mat_col:
            agg_dict[name_col] = "first"
        if cat_col:
            agg_dict[cat_col] = "first"

        agg = mdf.groupby(mat_col).agg(agg_dict).reset_index()
        agg.columns = (["Material SKU","Actual"] +
                       (["Material Name"] if name_col and name_col != mat_col else []) +
                       (["Category"] if cat_col else []))
        agg["Month"]    = minfo["label"]
        agg["MonthNum"] = minfo["month"]
        agg["Year"]     = minfo["year"]
        agg["Days"]     = minfo["days"]
        agg["_key"]     = agg["Material SKU"]
        agg = agg.merge(fc_agg, on="_key", how="left").drop(columns=["_key"])
        agg["Forecast"]    = agg["Forecast"].fillna(0)
        agg["Per Day Req"] = (agg["Forecast"] / 24).round(2)
        agg["Exp_Month"]   = (agg["Per Day Req"] * agg["Days"]).round(0)
        agg["Variance"]    = agg["Actual"] - agg["Exp_Month"]
        agg["Var %"]       = agg.apply(
            lambda r: round((r["Actual"] / r["Exp_Month"] * 100 - 100), 1) if r["Exp_Month"] > 0 else 0, axis=1)
        agg["Status"]      = agg["Variance"].apply(
            lambda v: "Over" if v > 0 else ("Under" if v < 0 else "On Track"))
        month_frames.append(agg)

    if not month_frames:
        return pd.DataFrame(), fc_agg

    full = pd.concat(month_frames, ignore_index=True)
    return full, fc_agg

df_full, fc_agg = load_all_months()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="top-bar">
  <div class="brand">
    <div class="brand-icon">📈</div>
    <div>
      <div class="brand-title">Consumption vs Forecast</div>
      <div class="brand-sub">YogaBar · 5-Month Trend · Raw & Packaging Materials</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#475569;">{now.strftime('%d %b %Y')}</div>
    <div class="live-badge"><span class="live-dot"></span>LIVE</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear(); st.rerun()

if df_full.empty:
    st.error("⚠️ No consumption data found for the last 5 months. Check your Consumption sheet has a date column and data.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns([2.8, 1.8, 1.8, 1.8])
with fc1:
    search = st.text_input("s", placeholder="🔍 Search SKU / material name…", label_visibility="collapsed")
with fc2:
    month_opts = ["All Months"] + [m["label"] for m in MONTHS]
    sel_month  = st.selectbox("m", month_opts, label_visibility="collapsed")
with fc3:
    var_opts = ["All Status","🔴 Over Consumed","🟢 Under Consumed","🔵 On Track"]
    sel_var  = st.selectbox("v", var_opts, label_visibility="collapsed")
with fc4:
    type_opts = ["All Types","RM (Raw Material)","PM (Packaging Material)"]
    sel_type  = st.selectbox("t", type_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════════
df = df_full.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_month != "All Months":
    df = df[df["Month"] == sel_month]
if sel_var == "🔴 Over Consumed":  df = df[df["Status"] == "Over"]
elif sel_var == "🟢 Under Consumed": df = df[df["Status"] == "Under"]
elif sel_var == "🔵 On Track":      df = df[df["Status"] == "On Track"]
if sel_type == "RM (Raw Material)":
    df = df[~df["Material SKU"].str.startswith("PM")]
elif sel_type == "PM (Packaging Material)":
    df = df[df["Material SKU"].str.startswith("PM")]

# ══════════════════════════════════════════════════════════════════════════════
# ── KPI CARDS — one per month ─────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📅 Monthly Snapshot</div>', unsafe_allow_html=True)

present_months = [m for m in MONTHS if m["label"] in df["Month"].unique()]
kpi_html = '<div class="kpi-row">'
for i, minfo in enumerate(MONTHS):
    mdf     = df[df["Month"] == minfo["label"]]
    actual  = mdf["Actual"].sum()
    exp     = mdf["Exp_Month"].sum()
    over    = (mdf["Status"] == "Over").sum()
    under   = (mdf["Status"] == "Under").sum()
    n_skus  = mdf["Material SKU"].nunique()
    var_pct = round((actual / exp * 100 - 100), 1) if exp > 0 else 0
    pill_cls= "over" if var_pct > 5 else ("under" if var_pct < -5 else "ok")
    pill_lbl= f"+{var_pct:.1f}%" if var_pct > 0 else f"{var_pct:.1f}%"
    css = MONTH_CSS[i]
    clr = MONTH_COLORS[i]

    kpi_html += f"""
    <div class="kpi-box {css}">
      <div class="kpi-month">{minfo['label']}</div>
      <div class="kpi-big">{actual:,.0f}</div>
      <div class="kpi-sub">{n_skus} materials</div>
      <div class="kpi-vs">Exp: {exp:,.0f}</div>
      <div><span class="kpi-pill {pill_cls}">{pill_lbl} vs forecast</span></div>
      <div style="margin-top:8px;display:flex;gap:8px;">
        <span style="font-size:9px;color:#f87171;font-family:'DM Mono',monospace;">⬆ {over} over</span>
        <span style="font-size:9px;color:#4ade80;font-family:'DM Mono',monospace;">⬇ {under} under</span>
      </div>
    </div>"""

kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── CHART 1: Stacked area — total consumption by month ───────────────────────
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📊 5-Month Consumption Trend</div>', unsafe_allow_html=True)

month_totals = (
    df.groupby("Month")
    .agg(Actual=("Actual","sum"), Expected=("Exp_Month","sum"))
    .reindex([m["label"] for m in MONTHS])
    .reset_index()
)

fig_trend = go.Figure()

# Forecast expected line (dashed)
fig_trend.add_trace(go.Scatter(
    x=month_totals["Month"], y=month_totals["Expected"],
    name="Expected (Forecast)", mode="lines",
    line=dict(color="#334155", width=2, dash="dot"),
    hovertemplate="<b>%{x}</b><br>Expected: %{y:,.0f}<extra></extra>"
))

# Actual consumption — filled area
fig_trend.add_trace(go.Scatter(
    x=month_totals["Month"], y=month_totals["Actual"],
    name="Actual Consumption", mode="lines+markers",
    line=dict(color="#06b6d4", width=3),
    marker=dict(size=8, color="#06b6d4", line=dict(color="#05070f", width=2)),
    fill="tozeroy",
    fillgradient=dict(colorscale=[[0,"rgba(6,182,212,0.25)"],[1,"rgba(6,182,212,0.0)"]]),
    hovertemplate="<b>%{x}</b><br>Actual: %{y:,.0f}<extra></extra>"
))

fig_trend.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="DM Sans", color="#94a3b8", size=11),
    height=280, margin=dict(l=10, r=10, t=10, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#64748b"), linecolor="#161d2e"),
    yaxis=dict(showgrid=True, gridcolor="#0c1020", zeroline=False, tickfont=dict(size=10, color="#64748b"), tickformat=","),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0")),
)
st.markdown('<div class="chart-wrap"><div class="chart-title">📈 Total Consumption vs Expected — All Months</div>', unsafe_allow_html=True)
st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── CHART 2: Top 10 SKUs — grouped bar across 5 months ───────────────────────
# ══════════════════════════════════════════════════════════════════════════════
top_skus = (
    df.groupby("Material SKU")["Actual"].sum()
    .nlargest(10).index.tolist()
)

sku_pivot = (
    df[df["Material SKU"].isin(top_skus)]
    .pivot_table(index="Material SKU", columns="Month", values="Actual", aggfunc="sum")
    .reindex(columns=[m["label"] for m in MONTHS])
    .fillna(0)
)

fig_bar = go.Figure()
for i, minfo in enumerate(MONTHS):
    col = minfo["label"]
    if col in sku_pivot.columns:
        fig_bar.add_trace(go.Bar(
            name=minfo["short"],
            x=sku_pivot.index.tolist(),
            y=sku_pivot[col].tolist(),
            marker_color=MONTH_COLORS[i],
            marker_line_width=0,
            opacity=0.85,
            hovertemplate=f"<b>%{{x}}</b><br>{col}: %{{y:,.0f}}<extra></extra>"
        ))

fig_bar.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="DM Sans", color="#94a3b8", size=11),
    barmode="group", bargap=0.18, bargroupgap=0.04,
    height=320, margin=dict(l=10, r=10, t=10, b=70),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=9, color="#64748b"),
               linecolor="#161d2e", tickangle=-35),
    yaxis=dict(showgrid=True, gridcolor="#0c1020", zeroline=False,
               tickfont=dict(size=10, color="#64748b"), tickformat=","),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0")),
)
st.markdown('<div class="chart-wrap"><div class="chart-title">🏆 Top 10 SKUs — Consumption Across 5 Months</div>', unsafe_allow_html=True)
st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── CHART 3: Variance heatmap — top 20 SKUs × 5 months ───────────────────────
# ══════════════════════════════════════════════════════════════════════════════
top20 = (
    df.groupby("Material SKU")["Actual"].sum()
    .nlargest(20).index.tolist()
)

heat_pivot = (
    df[df["Material SKU"].isin(top20)]
    .pivot_table(index="Material SKU", columns="Month", values="Var %", aggfunc="mean")
    .reindex(columns=[m["label"] for m in MONTHS])
    .fillna(0)
)

fig_heat = go.Figure(go.Heatmap(
    z=heat_pivot.values.tolist(),
    x=[m["short"] for m in MONTHS],
    y=heat_pivot.index.tolist(),
    colorscale=[
        [0.0,  "#1a0608"],
        [0.35, "#7f1d1d"],
        [0.45, "#1e2535"],
        [0.55, "#1e2535"],
        [0.65, "#14532d"],
        [1.0,  "#061a0a"],
    ],
    zmid=0,
    text=[[f"{v:+.0f}%" for v in row] for row in heat_pivot.values.tolist()],
    texttemplate="%{text}",
    textfont=dict(size=10, color="#e2e8f0"),
    hovertemplate="<b>%{y}</b><br>%{x}: <b>%{z:+.1f}%</b> vs forecast<extra></extra>",
    showscale=True,
    colorbar=dict(
        tickfont=dict(color="#64748b", size=9),
        outlinecolor="#161d2e", outlinewidth=1,
        len=0.8, thickness=12,
        title=dict(text="Var %", font=dict(color="#64748b", size=9))
    )
))

fig_heat.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="DM Sans", color="#94a3b8", size=11),
    height=max(300, len(top20) * 26 + 60),
    margin=dict(l=10, r=60, t=10, b=40),
    xaxis=dict(side="top", tickfont=dict(size=11, color="#94a3b8"), linecolor="#161d2e"),
    yaxis=dict(tickfont=dict(size=9, color="#64748b"), autorange="reversed"),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0")),
)
st.markdown('<div class="chart-wrap"><div class="chart-title">🌡️ Variance Heatmap — Actual vs Expected (%) · Top 20 SKUs</div>', unsafe_allow_html=True)
st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── CHART 4: Over vs Under count per month — stacked horizontal bar ───────────
# ══════════════════════════════════════════════════════════════════════════════
over_counts  = []
under_counts = []
track_counts = []
for minfo in MONTHS:
    mdf = df[df["Month"] == minfo["label"]]
    over_counts.append((mdf["Status"] == "Over").sum())
    under_counts.append((mdf["Status"] == "Under").sum())
    track_counts.append((mdf["Status"] == "On Track").sum())

month_labels = [m["short"] for m in MONTHS]

fig_status = go.Figure()
fig_status.add_trace(go.Bar(
    name="Over", y=month_labels, x=over_counts,
    orientation="h", marker_color="#ef4444", opacity=0.85, marker_line_width=0,
    hovertemplate="<b>%{y}</b> — Over: %{x}<extra></extra>"
))
fig_status.add_trace(go.Bar(
    name="Under", y=month_labels, x=under_counts,
    orientation="h", marker_color="#22c55e", opacity=0.85, marker_line_width=0,
    hovertemplate="<b>%{y}</b> — Under: %{x}<extra></extra>"
))
fig_status.add_trace(go.Bar(
    name="On Track", y=month_labels, x=track_counts,
    orientation="h", marker_color="#334155", opacity=0.85, marker_line_width=0,
    hovertemplate="<b>%{y}</b> — On Track: %{x}<extra></extra>"
))
fig_status.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="DM Sans", color="#94a3b8", size=11),
    barmode="stack", height=220,
    margin=dict(l=10, r=10, t=10, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    xaxis=dict(showgrid=True, gridcolor="#0c1020", zeroline=False, tickfont=dict(size=10, color="#64748b")),
    yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#94a3b8")),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0")),
)

col_a, col_b = st.columns([3, 2], gap="large")
with col_a:
    st.markdown('<div class="chart-wrap"><div class="chart-title">⚖️ Over vs Under vs On Track — Per Month</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    # ── Top 5 most consistently over-consuming SKUs ────────────────────────
    over_freq = (
        df[df["Status"] == "Over"]
        .groupby("Material SKU").size()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    over_freq.columns = ["SKU", "Months Over"]
    over_freq["Name"] = over_freq["SKU"].map(
        df.drop_duplicates("Material SKU").set_index("Material SKU").get(
            "Material Name", pd.Series(dtype=str)
        )
    ).fillna("") if "Material Name" in df.columns else ""

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🚨 Consistently Over-Consuming SKUs</div>', unsafe_allow_html=True)
    if over_freq.empty:
        st.markdown('<div style="color:#334155;text-align:center;padding:20px;font-size:12px;">✅ No SKUs consistently over-consuming</div>', unsafe_allow_html=True)
    else:
        for _, row in over_freq.iterrows():
            bar_w = int(row["Months Over"] / 5 * 100)
            name  = str(row["Name"])[:35] if row["Name"] else ""
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-family:'DM Mono',monospace;font-size:11px;color:#fca5a5;">{row['SKU']}</span>
                <span style="font-size:10px;background:#2d0a0a;color:#f87171;border:1px solid #7f1d1d;border-radius:20px;padding:1px 8px;font-family:'DM Mono',monospace;">{int(row['Months Over'])}/5 months</span>
              </div>
              <div style="font-size:10px;color:#475569;margin-bottom:5px;">{name}</div>
              <div style="background:rgba(255,255,255,.06);border-radius:4px;height:5px;overflow:hidden;">
                <div style="width:{bar_w}%;height:5px;background:#ef4444;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── DETAILED TABLE ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📋 Detailed Records</div>', unsafe_allow_html=True)

# Month legend strip
strip_html = '<div class="month-strip">'
for i, minfo in enumerate(MONTHS):
    strip_html += f'<div class="month-chip"><span class="month-dot" style="background:{MONTH_COLORS[i]};"></span><span style="color:#e2e8f0;">{minfo["label"]}</span></div>'
strip_html += '</div>'
st.markdown(strip_html, unsafe_allow_html=True)

st.markdown(
    f'<div class="tbl-hdr">'
    f'<span class="tbl-lbl">📋 5-Month Consumption vs Expected</span>'
    f'<span class="tbl-badge">{len(df):,} rows</span></div>',
    unsafe_allow_html=True
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="5-Month Consumption")
    # Pivot summary sheet
    if not sku_pivot.empty:
        sku_pivot.to_excel(w, sheet_name="SKU Pivot")
st.download_button(
    "⬇  Export to Excel (5 months + pivot)",
    buf.getvalue(), "Consumption_5Month.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)
st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No records match the current filters.")
else:
    def colour_row(row):
        s = row.get("Status","")
        if s == "Over":     return ["background-color:#1a0608;color:#fca5a5"] * len(row)
        if s == "Under":    return ["background-color:#061a0a;color:#bbf7d0"] * len(row)
        return ["background-color:#0a1628;color:#bfdbfe"] * len(row)

    col_order = ["Month","Material SKU"]
    if "Material Name" in df.columns: col_order.append("Material Name")
    if "Category"      in df.columns: col_order.append("Category")
    col_order += ["Actual","Exp_Month","Variance","Var %","Status"]
    col_order = [c for c in col_order if c in df.columns]

    col_cfg = {
        "Actual":    st.column_config.NumberColumn("Actual",    format="%.0f"),
        "Exp_Month": st.column_config.NumberColumn("Expected",  format="%.0f"),
        "Variance":  st.column_config.NumberColumn("Variance",  format="%.0f"),
        "Var %":     st.column_config.NumberColumn("Var %",     format="%.1f%%"),
        "Status":    st.column_config.TextColumn("Status"),
    }

    st.dataframe(
        df[col_order].style.apply(colour_row, axis=1),
        use_container_width=True, height=540, hide_index=True,
        column_config=col_cfg
    )

st.markdown('<div class="footer">YOGABAR · CONSUMPTION VS FORECAST · 5-MONTH TREND</div>', unsafe_allow_html=True)
