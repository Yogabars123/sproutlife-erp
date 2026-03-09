import streamlit as st
import pandas as pd
import os
import io
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Consumption · YogaBar",
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="expanded"
)

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("Consumption")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"], .main {
    background: #080b12 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1rem 1.2rem 3rem 1.2rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── HEADER ── */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 14px; border-bottom: 1px solid #161d2e; margin-bottom: 14px;
}
.hdr-left { display: flex; align-items: center; gap: 10px; }
.hdr-logo {
    width: 40px; height: 40px; min-width: 40px;
    background: #1a0f2e; border: 1px solid #3b1a5c; border-radius: 11px;
    display: flex; align-items: center; justify-content: center; font-size: 19px;
}
.hdr-title { font-size: 16px; font-weight: 800; color: #f1f5f9; }
.hdr-sub   { font-size: 11px; color: #94a3b8; }
.live-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #071a0f; border: 1px solid #166534;
    border-radius: 20px; padding: 5px 11px;
    font-size: 10px; font-weight: 700; color: #22c55e;
    letter-spacing: 1px; font-family: 'JetBrains Mono', monospace;
}
.live-dot {
    width: 6px; height: 6px; background: #22c55e; border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 5px #22c55e;} 50%{opacity:.2;box-shadow:none;} }

/* ── KPI CARDS ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 16px; }
.kpi-card {
    border-radius: 16px; padding: 16px 18px;
    position: relative; overflow: hidden;
    border: 1px solid; min-height: 100px;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0;
}
.kpi-card.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before   { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-card.green  { background:linear-gradient(135deg,#071a0f,#0f2d1a); border-color:#14532d; }
.kpi-card.green::before  { background:linear-gradient(90deg,#22c55e,#4ade80); }
.kpi-card.purple { background:linear-gradient(135deg,#12082a,#1e1040); border-color:#3b1a5c; }
.kpi-card.purple::before { background:linear-gradient(90deg,#a855f7,#c084fc); }
.kpi-card.blue   { background:linear-gradient(135deg,#0c1a3a,#0f2460); border-color:#1a3a6e; }
.kpi-card.blue::before   { background:linear-gradient(90deg,#3b82f6,#60a5fa); }

.kpi-lbl { font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.kpi-card.teal   .kpi-lbl { color:#5bc8c0; }
.kpi-card.green  .kpi-lbl { color:#4ade80; }
.kpi-card.purple .kpi-lbl { color:#c084fc; }
.kpi-card.blue   .kpi-lbl { color:#60a5fa; }
.kpi-num { font-size:26px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-card.teal   .kpi-num { color:#99f6e4; }
.kpi-card.green  .kpi-num { color:#bbf7d0; }
.kpi-card.purple .kpi-num { color:#e9d5ff; }
.kpi-card.blue   .kpi-num { color:#bfdbfe; }
.kpi-cap { font-size:11px; margin-top:5px; }
.kpi-card.teal   .kpi-cap { color:#134e4a; }
.kpi-card.green  .kpi-cap { color:#14532d; }
.kpi-card.purple .kpi-cap { color:#3b1a5c; }
.kpi-card.blue   .kpi-cap { color:#1a3a6e; }

/* ── FILTER BOX ── */
.filter-wrap { background:#0d1117; border:1px solid #1e2535; border-radius:14px; padding:12px 14px; margin-bottom:14px; }
.filter-title {
    font-size:10px; font-weight:700; color:#475569;
    text-transform:uppercase; letter-spacing:1.2px;
    margin-bottom:10px; display:flex; align-items:center; gap:6px;
}
.filter-title::after { content:''; flex:1; height:1px; background:#1e2535; }

[data-testid="stTextInput"] > div > div {
    background:#111827 !important; border:1.5px solid #1e2d45 !important; border-radius:9px !important;
}
[data-testid="stTextInput"] > div > div:focus-within { border-color:#5bc8c0 !important; }
[data-testid="stTextInput"] input {
    background:transparent !important; color:#f1f5f9 !important;
    font-size:13px !important; padding:9px 12px !important; border:none !important;
}
[data-testid="stTextInput"] input::placeholder { color:#334155 !important; }
[data-testid="stSelectbox"] > div > div {
    background:#111827 !important; border:1.5px solid #1e2d45 !important;
    border-radius:9px !important; color:#e2e8f0 !important; font-size:12.5px !important;
}
[data-testid="stWidgetLabel"] { display:none !important; }

.stDownloadButton > button {
    width:100% !important; background:linear-gradient(135deg,#0f172a,#1e1b4b) !important;
    border:1.5px solid #4338ca !important; border-radius:9px !important;
    color:#a5b4fc !important; font-size:13px !important; font-weight:700 !important; padding:10px !important;
}
.stButton > button {
    width:100% !important; background:#0d1117 !important;
    border:1.5px solid #1e2535 !important; border-radius:9px !important;
    color:#64748b !important; font-size:13px !important; font-weight:600 !important;
    padding:9px !important; transition:all .2s !important; margin-bottom:6px !important;
}
.stButton > button:hover { border-color:#5bc8c0 !important; color:#5bc8c0 !important; }

/* ── CHART BOX ── */
.chart-box {
    background:#0d1117; border:1px solid #1e2535; border-radius:16px;
    padding:16px 18px; margin-bottom:16px;
}
.chart-title {
    font-size:12px; font-weight:700; color:#94a3b8;
    text-transform:uppercase; letter-spacing:1.2px; margin-bottom:12px;
    display:flex; align-items:center; gap:8px;
}
.chart-title::after { content:''; flex:1; height:1px; background:#1e2535; }

/* ── TABLE ── */
.tbl-hdr { display:flex; align-items:center; justify-content:space-between; padding:10px 0 6px; }
.tbl-lbl { font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; }
.tbl-badge {
    background:#0f172a; border:1px solid #1e2d45; color:#818cf8;
    font-size:11px; font-weight:700; padding:3px 11px;
    border-radius:20px; font-family:'JetBrains Mono',monospace;
}
.sec-div {
    font-size:10px; font-weight:700; color:#334155; text-transform:uppercase;
    letter-spacing:1.2px; padding:12px 0 8px; display:flex; align-items:center; gap:7px;
}
.sec-div::after { content:''; flex:1; height:1px; background:#161d2e; }
div[data-testid="stDataFrame"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #1e2535 !important; }
.app-footer {
    margin-top:2rem; padding-top:12px; border-top:1px solid #161d2e;
    text-align:center; font-size:10px; font-weight:600; color:#334155;
    letter-spacing:1.5px; font-family:'JetBrains Mono',monospace;
}
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_consumption():
    # Data loaded from OneDrive via data_loader
    df = load_sheet("Consumption")
    df.columns = df.columns.str.strip()
    if "Batch Date" in df.columns:
        df["Batch Date"] = pd.to_datetime(df["Batch Date"], errors="coerce")
    for col in ["Batch Qty", "Damage/Wastage", "Total Produced Qty", "Consumed (As per BOM)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df_raw = load_consumption()

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">🏭</div>
        <div>
            <div class="hdr-title">Consumption</div>
            <div class="hdr-sub">YogaBar · Material Consumption & Production</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ── FILTERS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([2.5, 2, 2, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search product / material / batch…", label_visibility="collapsed")
with c2:
    if "Warehouse" in df_raw.columns:
        wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().astype(str).unique().tolist())
    else:
        wh_opts = ["All Warehouses"]
    sel_wh = st.selectbox("w", wh_opts, label_visibility="collapsed")
with c3:
    if "Category Name" in df_raw.columns:
        cat_opts = ["All Categories"] + sorted(df_raw["Category Name"].dropna().astype(str).unique().tolist())
    else:
        cat_opts = ["All Categories"]
    sel_cat = st.selectbox("c", cat_opts, label_visibility="collapsed")
with c4:
    if "Batch Date" in df_raw.columns:
        months = ["All Months"] + sorted(df_raw["Batch Date"].dropna().dt.strftime("%b-%Y").unique().tolist(), reverse=True)
    else:
        months = ["All Months"]
    sel_month = st.selectbox("m", months, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == sel_wh]
if sel_cat != "All Categories" and "Category Name" in df.columns:
    df = df[df["Category Name"].astype(str) == sel_cat]
if sel_month != "All Months" and "Batch Date" in df.columns:
    df = df[df["Batch Date"].dt.strftime("%b-%Y") == sel_month]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_consumed   = df["Consumed (As per BOM)"].sum() if "Consumed (As per BOM)" in df.columns else 0
total_produced   = df["Total Produced Qty"].sum()    if "Total Produced Qty" in df.columns else 0
total_wastage    = df["Damage/Wastage"].sum()         if "Damage/Wastage" in df.columns else 0
unique_materials = df["Material Name"].nunique()      if "Material Name" in df.columns else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card teal">
        <div class="kpi-lbl">Total Consumption</div>
        <div class="kpi-num">{total_consumed:,.0f}</div>
        <div class="kpi-cap">{unique_materials:,} unique materials</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-lbl">Total Produced Qty</div>
        <div class="kpi-num">{total_produced:,.0f}</div>
        <div class="kpi-cap">{df["Product Name"].nunique() if "Product Name" in df.columns else 0:,} products</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-lbl">Damage / Wastage</div>
        <div class="kpi-num">{total_wastage:,.0f}</div>
        <div class="kpi-cap">Total loss quantity</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-lbl">Records</div>
        <div class="kpi-num">{len(df):,}</div>
        <div class="kpi-cap">Filtered rows shown</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CONSUMPTION TREND CHART (last 6 months) ───────────────────────────────────
if "Batch Date" in df_raw.columns and "Consumed (As per BOM)" in df_raw.columns:
    # Use last 6 months of ACTUAL data (not from today)
    max_date = df_raw["Batch Date"].max()
    cutoff = max_date - pd.DateOffset(months=6)
    df_trend = df_raw[df_raw["Batch Date"] >= cutoff].copy()
    df_trend["Month"] = df_trend["Batch Date"].dt.to_period("M").astype(str)
    monthly = df_trend.groupby("Month").agg(
        Consumed=("Consumed (As per BOM)", "sum"),
        Produced=("Total Produced Qty", "sum")
    ).reset_index().sort_values("Month")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly["Month"], y=monthly["Consumed"],
        name="Consumption",
        marker_color="#5bc8c0",
        marker_line_width=0,
        opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=monthly["Month"], y=monthly["Produced"],
        name="Produced",
        marker_color="#a855f7",
        marker_line_width=0,
        opacity=0.75,
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Consumed"],
        mode="lines+markers",
        name="Consumption trend",
        line=dict(color="#2dd4bf", width=2.5, dash="solid"),
        marker=dict(size=7, color="#2dd4bf", line=dict(width=2, color="#080b12")),
        showlegend=False,
    ))

    fig.update_layout(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(family="Inter", color="#94a3b8", size=12),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#94a3b8")
        ),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=11, color="#64748b"),
            linecolor="#1e2535",
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#111827", zeroline=False,
            tickfont=dict(size=11, color="#64748b"),
            tickformat=",",
        ),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0")),
    )

    st.markdown('<div class="chart-box"><div class="chart-title">📈 Consumption vs Production — Last 6 Months</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 Consumption Data</span>
    <span class="tbl-badge">{len(df):,} rows</span>
</div>""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="Consumption")
st.download_button("⬇  Export to Excel", buf.getvalue(), "Consumption.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️  No records match the current filters.")
else:
    disp = df.copy()
    if "Batch Date" in disp.columns:
        disp["Batch Date"] = disp["Batch Date"].dt.strftime("%d-%b-%Y").fillna("")
    st.dataframe(disp, use_container_width=True, height=500, hide_index=True,
        column_config={
            "Batch Qty":             st.column_config.NumberColumn("Batch Qty",    format="%.0f"),
            "Consumed (As per BOM)": st.column_config.NumberColumn("Consumed",     format="%.0f"),
            "Total Produced Qty":    st.column_config.NumberColumn("Produced Qty", format="%.0f"),
            "Damage/Wastage":        st.column_config.NumberColumn("Wastage",      format="%.0f"),
        })

st.markdown('<div class="app-footer">YOGABAR · CONSUMPTION</div>', unsafe_allow_html=True)
