import streamlit as st
import pandas as pd
import io
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
  --bg:      #05070f;
  --bg1:     #080b14;
  --bg2:     #0c1020;
  --bg3:     #111827;
  --border:  #161d2e;
  --border2: #1e2840;
  --text:    #e2e8f0;
  --muted:   #64748b;
  --dim:     #2d3a50;
  --actual:  #06b6d4;
  --expect:  #1e2d45;
  --over:    #ef4444;
  --under:   #22c55e;
  --ontrack: #3b82f6;
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
.block-container { padding: 1rem 1.4rem 4rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── HEADER ─────────────────────────────────────────────────────────────── */
.app-header { display:flex; align-items:center; justify-content:space-between; padding-bottom:14px; border-bottom:1px solid var(--border); margin-bottom:16px; }
.hdr-left   { display:flex; align-items:center; gap:10px; }
.hdr-logo   { width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg,#0c1a10,#122418); border:1px solid #14532d; display:flex; align-items:center; justify-content:center; font-size:20px; }
.hdr-title  { font-size:17px; font-weight:800; color:#f1f5f9; }
.hdr-sub    { font-size:11px; color:var(--muted); margin-top:1px; }
.live-pill  { display:inline-flex; align-items:center; gap:6px; background:#041208; border:1px solid #155e2e; border-radius:20px; padding:5px 13px; font-size:10px; font-weight:700; color:#22c55e; letter-spacing:1.2px; font-family:'JetBrains Mono',monospace; }
.live-dot   { width:6px; height:6px; background:#22c55e; border-radius:50%; animation:blink 1.8s infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 6px #22c55e} 50%{opacity:.2;box-shadow:none} }

/* ── BUTTONS ─────────────────────────────────────────────────────────────── */
.stButton > button { background:var(--bg1) !important; border:1px solid var(--border2) !important; border-radius:9px !important; color:var(--muted) !important; font-size:12px !important; font-weight:600 !important; width:100% !important; padding:9px !important; margin-bottom:8px !important; transition:all .2s !important; }
.stButton > button:hover { border-color:var(--actual) !important; color:var(--actual) !important; }
.stDownloadButton > button { background:linear-gradient(135deg,#0f172a,#1e1b4b) !important; border:1.5px solid #4338ca !important; border-radius:9px !important; color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; width:100% !important; padding:10px !important; }

/* ── FILTERS ─────────────────────────────────────────────────────────────── */
.filter-wrap { background:var(--bg1); border:1px solid var(--border); border-radius:14px; padding:12px 14px; margin-bottom:16px; }
.filter-title { font-size:10px; font-weight:700; color:var(--dim); text-transform:uppercase; letter-spacing:1.3px; margin-bottom:10px; display:flex; align-items:center; gap:6px; }
.filter-title::after { content:''; flex:1; height:1px; background:var(--border); }
[data-testid="stTextInput"] > div > div { background:var(--bg3) !important; border:1.5px solid var(--border2) !important; border-radius:9px !important; }
[data-testid="stTextInput"] > div > div:focus-within { border-color:var(--actual) !important; }
[data-testid="stTextInput"] input { background:transparent !important; color:var(--text) !important; font-size:13px !important; padding:9px 12px !important; border:none !important; }
[data-testid="stTextInput"] input::placeholder { color:var(--dim) !important; }
[data-testid="stSelectbox"] > div > div { background:var(--bg3) !important; border:1.5px solid var(--border2) !important; border-radius:9px !important; color:var(--text) !important; font-size:12.5px !important; }
[data-testid="stWidgetLabel"] { display:none !important; }

/* ── KPI CARDS ───────────────────────────────────────────────────────────── */
.kpi-row { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:20px; }
.kpi-box { border-radius:14px; padding:16px; border:1px solid var(--border); background:var(--bg1); position:relative; overflow:hidden; transition:transform .18s; }
.kpi-box:hover { transform:translateY(-2px); }
.kpi-box::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.m0::before{background:#06b6d4;} .m1::before{background:#a855f7;}
.m2::before{background:#f59e0b;} .m3::before{background:#ec4899;}
.m4::before{background:#22c55e;}
.kpi-mth  { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.3px; margin-bottom:5px; }
.m0 .kpi-mth{color:#06b6d4;} .m1 .kpi-mth{color:#a855f7;}
.m2 .kpi-mth{color:#f59e0b;} .m3 .kpi-mth{color:#ec4899;}
.m4 .kpi-mth{color:#22c55e;}
.kpi-num  { font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:700; color:var(--text); line-height:1; letter-spacing:-1px; }
.kpi-meta { font-size:10px; color:var(--muted); margin-top:5px; }
.kpi-exp  { font-size:10px; color:var(--muted); margin-top:3px; font-family:'JetBrains Mono',monospace; }
.var-badge { display:inline-block; font-size:9px; font-weight:700; padding:2px 8px; border-radius:20px; margin-top:6px; font-family:'JetBrains Mono',monospace; }
.var-badge.over   { background:#2d0a0a; color:#f87171; border:1px solid #7f1d1d; }
.var-badge.under  { background:#061a0a; color:#4ade80; border:1px solid #14532d; }
.var-badge.ok     { background:#0a1628; color:#60a5fa; border:1px solid #1e3a5f; }

/* ── SECTION ─────────────────────────────────────────────────────────────── */
.sec { font-size:10px; font-weight:700; color:var(--dim); text-transform:uppercase; letter-spacing:1.4px; padding:14px 0 10px; display:flex; align-items:center; gap:8px; }
.sec::after { content:''; flex:1; height:1px; background:var(--border); }

/* ── CHART WRAP ──────────────────────────────────────────────────────────── */
.chart-wrap { background:var(--bg1); border:1px solid var(--border); border-radius:16px; padding:18px 20px; margin-bottom:20px; }
.chart-hdr  { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.chart-title { font-size:12px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1.2px; }
.chart-legend { display:flex; gap:16px; align-items:center; }
.legend-item  { display:flex; align-items:center; gap:6px; font-size:11px; color:var(--muted); }
.legend-dot   { width:10px; height:10px; border-radius:50%; flex-shrink:0; }

/* ── TABLE ───────────────────────────────────────────────────────────────── */
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid var(--border) !important; }
.tbl-hdr   { display:flex; align-items:center; justify-content:space-between; padding:6px 0; }
.tbl-lbl   { font-size:10px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge { background:var(--bg2); border:1px solid var(--border2); color:#818cf8; font-size:11px; font-weight:700; padding:3px 11px; border-radius:20px; font-family:'JetBrains Mono',monospace; }

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.footer { margin-top:3rem; padding-top:12px; border-top:1px solid var(--border); text-align:center; font-size:10px; font-weight:600; color:var(--dim); letter-spacing:2px; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MONTH CONFIG — last 5 months
# ══════════════════════════════════════════════════════════════════════════════
now = datetime.now()
MONTHS = []
for i in range(4, -1, -1):
    t = pd.Timestamp(now.year, now.month, 1) - pd.DateOffset(months=i)
    d = (pd.Timestamp(t.year, t.month, 1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).day
    MONTHS.append({"month": t.month, "year": t.year, "label": t.strftime("%b %Y"), "short": t.strftime("%b"), "days": d})

MONTH_COLORS = ["#06b6d4", "#a855f7", "#f59e0b", "#ec4899", "#22c55e"]
MONTH_CSS    = ["m0", "m1", "m2", "m3", "m4"]

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_all_months():
    df_con = load_sheet("Consumption")
    df_fc  = load_sheet("Forecast")
    if df_con.empty or df_fc.empty:
        return pd.DataFrame()

    df_con.columns = df_con.columns.str.strip()
    df_fc.columns  = df_fc.columns.str.strip()

    # Date
    date_col = next((c for c in df_con.columns if "date" in c.lower()), None)
    if date_col:
        df_con[date_col] = pd.to_datetime(df_con[date_col], errors="coerce")
        df_con["_month"] = df_con[date_col].dt.month
        df_con["_year"]  = df_con[date_col].dt.year

    # Columns
    con_col  = next((c for c in df_con.columns if "consumed" in c.lower()), None)
    mat_col  = next((c for c in df_con.columns if ("material" in c.lower() and ("code" in c.lower() or "sku" in c.lower()))), None)
    if not mat_col: mat_col = next((c for c in df_con.columns if "sku" in c.lower()), None)
    name_col = next((c for c in df_con.columns if "material name" in c.lower()), mat_col)
    cat_col  = next((c for c in df_con.columns if "category" in c.lower()), None)

    if not mat_col or not con_col: return pd.DataFrame()

    df_con[mat_col] = df_con[mat_col].astype(str).str.strip().str.upper()
    df_con[con_col] = pd.to_numeric(df_con[con_col], errors="coerce").fillna(0)

    # Forecast
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    df_fc["Forecast"] = pd.to_numeric(df_fc.get("Forecast", 0), errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]
    ic_col = next((c for c in df_fc.columns if "item" in c.lower() and "code" in c.lower()), None)
    if not ic_col: return pd.DataFrame()
    df_fc[ic_col] = df_fc[ic_col].astype(str).str.strip().str.upper()
    fc_agg = df_fc.groupby(ic_col)["Forecast"].sum().reset_index()
    fc_agg.columns = ["_key", "Forecast"]

    frames = []
    for minfo in MONTHS:
        if "_month" not in df_con.columns: continue
        mdf = df_con[(df_con["_month"] == minfo["month"]) & (df_con["_year"] == minfo["year"])].copy()
        if mdf.empty: continue

        agg_dict = {con_col: "sum"}
        if name_col and name_col != mat_col: agg_dict[name_col] = "first"
        if cat_col: agg_dict[cat_col] = "first"

        agg = mdf.groupby(mat_col).agg(agg_dict).reset_index()
        cols = ["Material SKU", "Actual"] + \
               (["Material Name"] if name_col and name_col != mat_col else []) + \
               (["Category"] if cat_col else [])
        agg.columns = cols

        agg["Month"] = minfo["label"]
        agg["_key"]  = agg["Material SKU"]
        agg = agg.merge(fc_agg, on="_key", how="left").drop(columns=["_key"])
        agg["Forecast"]  = agg["Forecast"].fillna(0)
        agg["Per Day"]   = (agg["Forecast"] / 24).round(2)
        agg["Expected"]  = (agg["Per Day"] * minfo["days"]).round(0)
        agg["Variance"]  = agg["Actual"] - agg["Expected"]
        agg["Var %"]     = agg.apply(lambda r: round((r["Actual"]/r["Expected"]*100-100), 1) if r["Expected"] > 0 else 0, axis=1)
        agg["Status"]    = agg["Variance"].apply(lambda v: "Over" if v > 0 else ("Under" if v < 0 else "On Track"))
        # Only keep rows with actual consumption > 0
        agg = agg[agg["Actual"] > 0]
        frames.append(agg)

    if not frames: return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

df_full = load_all_months()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="app-header">
  <div class="hdr-left">
    <div class="hdr-logo">📈</div>
    <div>
      <div class="hdr-title">Consumption vs Forecast</div>
      <div class="hdr-sub">YogaBar · 5-Month Actual vs Expected Comparison</div>
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

if df_full.empty:
    st.error("⚠️ No consumption data found. Check your Consumption sheet has a date column.")
    st.stop()

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
    type_opts = ["All Types", "RM (Raw Material)", "PM (Packaging Material)"]
    sel_type  = st.selectbox("t", type_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Apply
df = df_full.copy()
if search:    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_month != "All Months":  df = df[df["Month"] == sel_month]
if sel_type == "RM (Raw Material)":         df = df[~df["Material SKU"].str.startswith("PM")]
elif sel_type == "PM (Packaging Material)": df = df[df["Material SKU"].str.startswith("PM")]

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS — one per month
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📅 Monthly Summary</div>', unsafe_allow_html=True)
html = '<div class="kpi-row">'
for i, minfo in enumerate(MONTHS):
    mdf     = df[df["Month"] == minfo["label"]]
    actual  = mdf["Actual"].sum()
    exp     = mdf["Expected"].sum()
    n       = mdf["Material SKU"].nunique()
    var_pct = round((actual / exp * 100 - 100), 1) if exp > 0 else 0
    cls     = "over" if var_pct > 5 else ("under" if var_pct < -5 else "ok")
    lbl     = f"+{var_pct:.1f}%" if var_pct > 0 else f"{var_pct:.1f}%"
    html += f"""
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
# CHART 1 — Monthly Actual vs Expected (overlapping bars + variance line)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📊 Monthly Comparison — Actual vs Expected</div>', unsafe_allow_html=True)

month_totals = (
    df.groupby("Month")
    .agg(Actual=("Actual","sum"), Expected=("Expected","sum"))
    .reindex([m["label"] for m in MONTHS])
    .reset_index().fillna(0)
)
variance_vals = [round(a - e, 0) for a, e in zip(month_totals["Actual"], month_totals["Expected"])]

fig1 = go.Figure()

# Expected bar (background)
fig1.add_trace(go.Bar(
    x=month_totals["Month"], y=month_totals["Expected"],
    name="Expected", marker_color="#1e2d45", marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>Expected: <b>%{y:,.0f}</b><extra></extra>"
))

# Actual bar (foreground, cyan)
fig1.add_trace(go.Bar(
    x=month_totals["Month"], y=month_totals["Actual"],
    name="Actual Consumed", marker_color="#06b6d4", marker_line_width=0, opacity=0.9,
    hovertemplate="<b>%{x}</b><br>Actual: <b>%{y:,.0f}</b><extra></extra>"
))

# Variance line on second axis
var_colors = ["#ef4444" if v < 0 else "#22c55e" for v in variance_vals]
fig1.add_trace(go.Scatter(
    x=month_totals["Month"], y=variance_vals,
    name="Variance", mode="lines+markers+text",
    yaxis="y2",
    line=dict(color="#f59e0b", width=2.5),
    marker=dict(size=9, color=var_colors, line=dict(color="#f59e0b", width=2)),
    text=[f"{'+' if v>0 else ''}{v:,.0f}" for v in variance_vals],
    textposition="top center",
    textfont=dict(size=10, color="#f59e0b", family="JetBrains Mono"),
    hovertemplate="<b>%{x}</b><br>Variance: <b>%{y:+,.0f}</b><extra></extra>"
))

fig1.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="Inter", color="#94a3b8", size=11),
    barmode="overlay", height=340,
    margin=dict(l=10, r=60, t=10, b=30),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(0,0,0,0)", font=dict(size=12),
        itemclick=False, itemdoubleclick=False
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=13, color="#94a3b8"), linecolor="#161d2e"),
    yaxis=dict(showgrid=True, gridcolor="#0c1020", zeroline=False, tickfont=dict(size=10, color="#64748b"), tickformat=",", title=dict(text="Qty", font=dict(size=10, color="#475569"))),
    yaxis2=dict(showgrid=False, zeroline=True, zerolinecolor="#2d3a50", overlaying="y", side="right", tickfont=dict(size=9, color="#f59e0b"), title=dict(text="Variance", font=dict(size=10, color="#f59e0b"))),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0", size=12)),
)

st.markdown("""
<div class="chart-wrap">
  <div class="chart-hdr">
    <div class="chart-title">Total Actual vs Expected — All 5 Months</div>
    <div class="chart-legend">
      <div class="legend-item"><div class="legend-dot" style="background:#06b6d4"></div>Actual</div>
      <div class="legend-item"><div class="legend-dot" style="background:#1e2d45"></div>Expected</div>
      <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>Variance</div>
    </div>
  </div>
""", unsafe_allow_html=True)
st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Top 10 SKUs: Actual vs Expected (horizontal bars, color = status)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">🏆 Top 10 SKUs by Consumption — Actual vs Expected</div>', unsafe_allow_html=True)

top10 = (
    df.groupby("Material SKU")
    .agg(Actual=("Actual","sum"), Expected=("Expected","sum"))
    .reset_index()
)
top10 = top10[top10["Actual"] > 0].nlargest(10, "Actual").copy()
top10["Var %"]  = top10.apply(lambda r: round((r["Actual"]/r["Expected"]*100-100),1) if r["Expected"]>0 else 0, axis=1)
top10["Status"] = top10["Var %"].apply(lambda v: "Over" if v > 5 else ("Under" if v < -5 else "On Track"))
top10["Color"]  = top10["Status"].map({"Over":"#ef4444","Under":"#22c55e","On Track":"#3b82f6"})
top10["Label"]  = top10.apply(lambda r: f"{'+' if r['Var %']>0 else ''}{r['Var %']:.1f}%  {'▲ Over' if r['Status']=='Over' else ('▼ Under' if r['Status']=='Under' else '● On Track')}", axis=1)

fig2 = go.Figure()

# Expected (grey background bar)
fig2.add_trace(go.Bar(
    y=top10["Material SKU"], x=top10["Expected"],
    name="Expected", orientation="h",
    marker_color="#1e2840", marker_line_width=0,
    hovertemplate="<b>%{y}</b><br>Expected: <b>%{x:,.0f}</b><extra></extra>"
))

# Actual (colored by status)
fig2.add_trace(go.Bar(
    y=top10["Material SKU"], x=top10["Actual"],
    name="Actual", orientation="h",
    marker_color=top10["Color"].tolist(),
    marker_line_width=0, opacity=0.9,
    text=top10["Label"].tolist(),
    textposition="outside",
    textfont=dict(size=10, color="#94a3b8", family="JetBrains Mono"),
    hovertemplate="<b>%{y}</b><br>Actual: <b>%{x:,.0f}</b><br>%{text}<extra></extra>"
))

fig2.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="Inter", color="#94a3b8", size=11),
    barmode="overlay", height=max(380, len(top10) * 38 + 80),
    margin=dict(l=10, r=160, t=10, b=20),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(0,0,0,0)", font=dict(size=12),
        itemclick=False, itemdoubleclick=False
    ),
    xaxis=dict(showgrid=True, gridcolor="#0c1020", zeroline=False, tickfont=dict(size=10, color="#64748b"), tickformat=","),
    yaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94a3b8"), autorange="reversed"),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0", size=12)),
)

st.markdown("""
<div class="chart-wrap">
  <div class="chart-hdr">
    <div class="chart-title">Top 10 SKUs — Actual vs Expected</div>
    <div class="chart-legend">
      <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div>Over Consumed</div>
      <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div>Under Consumed</div>
      <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div>On Track</div>
      <div class="legend-item"><div class="legend-dot" style="background:#1e2840"></div>Expected</div>
    </div>
  </div>
""", unsafe_allow_html=True)
st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Top 10 SKU trend lines across 5 months
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📉 Top 10 SKUs — Consumption Trend Over 5 Months</div>', unsafe_allow_html=True)

top10_skus = top10["Material SKU"].tolist()
trend_pivot = (
    df[df["Material SKU"].isin(top10_skus)]
    .pivot_table(index="Material SKU", columns="Month", values="Actual", aggfunc="sum")
    .reindex(columns=[m["label"] for m in MONTHS])
    .fillna(0)
)

fig3 = go.Figure()
line_colors = ["#06b6d4","#a855f7","#f59e0b","#ec4899","#22c55e","#f87171","#60a5fa","#4ade80","#fb923c","#e879f9"]
for idx, (sku, row) in enumerate(trend_pivot.iterrows()):
    clr = line_colors[idx % len(line_colors)]
    fig3.add_trace(go.Scatter(
        x=[m["short"] for m in MONTHS],
        y=row.values.tolist(),
        name=sku, mode="lines+markers",
        line=dict(color=clr, width=2),
        marker=dict(size=7, color=clr, line=dict(color="#080b14", width=1.5)),
        hovertemplate=f"<b>{sku}</b><br>%{{x}}: <b>%{{y:,.0f}}</b><extra></extra>"
    ))

fig3.update_layout(
    paper_bgcolor="#080b14", plot_bgcolor="#080b14",
    font=dict(family="Inter", color="#94a3b8", size=11),
    height=320,
    margin=dict(l=10, r=160, t=10, b=20),
    legend=dict(
        yanchor="middle", y=0.5, xanchor="left", x=1.01,
        bgcolor="rgba(0,0,0,0)", font=dict(size=9, family="JetBrains Mono"),
        itemclick="toggleothers"
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12, color="#94a3b8"), linecolor="#161d2e"),
    yaxis=dict(showgrid=True, gridcolor="#0c1020", zeroline=False, tickfont=dict(size=10, color="#64748b"), tickformat=","),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0", size=12)),
)

st.markdown("""
<div class="chart-wrap">
  <div class="chart-hdr">
    <div class="chart-title">5-Month Trend — Click legend to isolate a SKU</div>
    <div style="font-size:10px;color:#334155;font-family:'JetBrains Mono',monospace;">Click a SKU in the legend to isolate it</div>
  </div>
""", unsafe_allow_html=True)
st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DETAILED TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📋 Detailed Records</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="tbl-hdr">'
    f'<span class="tbl-lbl">5-Month Consumption vs Expected · Active SKUs Only</span>'
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
        if s == "Over":     return ["background-color:#1a0608;color:#fca5a5"] * len(row)
        if s == "Under":    return ["background-color:#061a0a;color:#bbf7d0"] * len(row)
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

st.markdown('<div class="footer">YOGABAR · CONSUMPTION VS FORECAST · 5-MONTH COMPARISON</div>', unsafe_allow_html=True)
