import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

st.set_page_config(page_title="Consumption vs Forecast · YogaBar", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

from pages.Sidebar_style import inject_sidebar
from pages.data_loader import load_sheet
inject_sidebar("Consumption vs Forecast")

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
.hdr-logo { width:40px; height:40px; min-width:40px; background:#0c1a10; border:1px solid #14532d; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:19px; }
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
.kpi-card.teal   { background:linear-gradient(135deg,#061413,#0a2825); border-color:#134e4a; }
.kpi-card.teal::before   { background:linear-gradient(90deg,#5bc8c0,#2dd4bf); }
.kpi-card.red    { background:linear-gradient(135deg,#1a0000,#2a0808); border-color:#7f1d1d; }
.kpi-card.red::before    { background:linear-gradient(90deg,#ef4444,#f87171); }
.kpi-card.green  { background:linear-gradient(135deg,#071a0f,#0f2d1a); border-color:#14532d; }
.kpi-card.green::before  { background:linear-gradient(90deg,#22c55e,#4ade80); }
.kpi-lbl { font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.kpi-card.blue  .kpi-lbl { color:#60a5fa; } .kpi-card.teal  .kpi-lbl { color:#5bc8c0; }
.kpi-card.red   .kpi-lbl { color:#f87171; } .kpi-card.green .kpi-lbl { color:#4ade80; }
.kpi-num { font-size:26px; font-weight:800; line-height:1; font-family:'JetBrains Mono',monospace; letter-spacing:-1px; }
.kpi-card.blue  .kpi-num { color:#bfdbfe; } .kpi-card.teal  .kpi-num { color:#99f6e4; }
.kpi-card.red   .kpi-num { color:#fecaca; } .kpi-card.green .kpi-num { color:#bbf7d0; }
.kpi-cap { font-size:11px; margin-top:5px; }
.kpi-card.blue  .kpi-cap { color:#1e3a6e; } .kpi-card.teal  .kpi-cap { color:#134e4a; }
.kpi-card.red   .kpi-cap { color:#7f1d1d; } .kpi-card.green .kpi-cap { color:#14532d; }
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
.chart-box { background:#0d1117; border:1px solid #1e2535; border-radius:16px; padding:16px 18px; margin-bottom:16px; }
.chart-title { font-size:12px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
.chart-title::after { content:''; flex:1; height:1px; background:#1e2535; }
.legend-bar { display:flex; gap:16px; align-items:center; background:#0d1117; border:1px solid #1e2535; border-radius:10px; padding:8px 14px; margin-bottom:12px; font-size:11px; }
.legend-dot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:5px; }
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
def load_data():
    # ── Consumption — March month only ───────────────────────────────────────
    df_con = load_sheet("Consumption")
    if df_con.empty:
        return pd.DataFrame()
    df_con.columns = df_con.columns.str.strip()

    if "Batch Date" in df_con.columns:
        df_con["Batch Date"] = pd.to_datetime(df_con["Batch Date"], errors="coerce")
        # Filter March (month=3) — any year
        df_con = df_con[df_con["Batch Date"].dt.month == 3].copy()

    # Consumed qty
    con_col = next((c for c in df_con.columns if "consumed" in c.lower()), None)
    if con_col:
        df_con[con_col] = pd.to_numeric(df_con[con_col], errors="coerce").fillna(0)

    # Find material code / SKU column in consumption
    mat_col = next((c for c in df_con.columns if "material" in c.lower() and ("code" in c.lower() or "sku" in c.lower())), None)
    if not mat_col:
        mat_col = next((c for c in df_con.columns if "sku" in c.lower()), None)

    if mat_col and con_col:
        df_con[mat_col] = df_con[mat_col].astype(str).str.strip().str.upper()
        actual = df_con.groupby(mat_col).agg(
            Actual_Consumed=(con_col, "sum"),
            Material_Name=(next((c for c in df_con.columns if "material name" in c.lower()), mat_col), "first"),
            Category=(next((c for c in df_con.columns if "category" in c.lower()), mat_col), "first") if any("category" in c.lower() for c in df_con.columns) else (mat_col, "first")
        ).reset_index().rename(columns={mat_col: "Material SKU"})
    else:
        return pd.DataFrame()

    # ── Forecast — Plant only ─────────────────────────────────────────────────
    df_fc = load_sheet("Forecast")
    if df_fc.empty:
        return pd.DataFrame()
    df_fc.columns = df_fc.columns.str.strip()
    if "Location" in df_fc.columns:
        df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"].copy()
    df_fc["Forecast"] = pd.to_numeric(df_fc.get("Forecast", 0), errors="coerce").fillna(0)
    df_fc = df_fc[df_fc["Forecast"] > 0]

    # Find item code column in forecast
    ic_col = next((c for c in df_fc.columns if "item" in c.lower() and "code" in c.lower()), None)
    if not ic_col:
        return pd.DataFrame()
    df_fc[ic_col] = df_fc[ic_col].astype(str).str.strip().str.upper()
    fc_agg = df_fc.groupby(ic_col)["Forecast"].sum().reset_index().rename(columns={ic_col: "_key"})

    # ── Merge actual consumption with forecast ────────────────────────────────
    actual["_key"] = actual["Material SKU"]
    merged = actual.merge(fc_agg, on="_key", how="inner").drop(columns=["_key"])

    # ── Per Day Req = Forecast / 24, Variance ────────────────────────────────
    merged["Per Day Req"]   = (merged["Forecast"] / 24).round(2)
    merged["Variance"]      = merged["Actual_Consumed"] - merged["Per Day Req"] * 31  # March has 31 days
    merged["Variance %"]    = ((merged["Actual_Consumed"] / (merged["Per Day Req"] * 31)) * 100).round(1)
    merged["Status"]        = merged["Variance"].apply(
        lambda v: "Over" if v > 0 else ("Under" if v < 0 else "On Track")
    )
    return merged.sort_values("Actual_Consumed", ascending=False)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="hdr-left">
        <div class="hdr-logo">📈</div>
        <div>
            <div class="hdr-title">Consumption vs Forecast</div>
            <div class="hdr-sub">YogaBar · March Actual vs Forecast · Plant Location</div>
        </div>
    </div>
    <div class="live-pill"><span class="live-dot"></span>LIVE</div>
</div>
""", unsafe_allow_html=True)

if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df_raw = load_data()

if df_raw.empty:
    st.error("⚠️ No data found. Ensure March consumption data exists and Forecast sheet is loaded.")
    st.stop()

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    search = st.text_input("s", placeholder="🔍 Search SKU / material name…", label_visibility="collapsed")
with c2:
    var_opts = ["All", "🔴 Over Consumed", "🟢 Under Consumed"]
    sel_var = st.selectbox("v", var_opts, label_visibility="collapsed")
with c3:
    type_opts = ["All", "RM (Raw Material)", "PM (Packaging Material)"]
    sel_type = st.selectbox("t", type_opts, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if sel_var == "🔴 Over Consumed":
    df = df[df["Status"] == "Over"]
elif sel_var == "🟢 Under Consumed":
    df = df[df["Status"] == "Under"]
if sel_type == "RM (Raw Material)":
    df = df[~df["Material SKU"].str.startswith("PM")]
elif sel_type == "PM (Packaging Material)":
    df = df[df["Material SKU"].str.startswith("PM")]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total_actual   = df["Actual_Consumed"].sum()
total_forecast = (df["Per Day Req"] * 31).sum()
over_count     = (df["Status"] == "Over").sum()
under_count    = (df["Status"] == "Under").sum()
variance_pct   = ((total_actual / total_forecast) * 100 - 100) if total_forecast > 0 else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card teal">
        <div class="kpi-lbl">March Actual Consumption</div>
        <div class="kpi-num">{total_actual:,.0f}</div>
        <div class="kpi-cap">{len(df):,} materials · March data</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-lbl">March Forecast (31 days)</div>
        <div class="kpi-num">{total_forecast:,.0f}</div>
        <div class="kpi-cap">Forecast ÷ 24 × 31 days</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-lbl">Over Consumed</div>
        <div class="kpi-num">{over_count:,}</div>
        <div class="kpi-cap">Actual &gt; Forecast</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-lbl">Under Consumed</div>
        <div class="kpi-num">{under_count:,}</div>
        <div class="kpi-cap">Actual &lt; Forecast</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CHART — Top 15 materials by consumption ───────────────────────────────────
top15 = df.nlargest(15, "Actual_Consumed").copy()
top15["Label"] = top15["Material SKU"]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=top15["Label"], y=top15["Actual_Consumed"],
    name="Actual (March)", marker_color="#5bc8c0", opacity=0.9, marker_line_width=0,
))
fig.add_trace(go.Bar(
    x=top15["Label"], y=top15["Per Day Req"] * 31,
    name="Forecast (31d)", marker_color="#818cf8", opacity=0.7, marker_line_width=0,
))
fig.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="Inter", color="#94a3b8", size=11),
    barmode="group", bargap=0.2, bargroupgap=0.05,
    height=320, margin=dict(l=10, r=10, t=10, b=60),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#94a3b8")),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=9, color="#64748b"),
               linecolor="#1e2535", tickangle=-35),
    yaxis=dict(showgrid=True, gridcolor="#111827", zeroline=False,
               tickfont=dict(size=10, color="#64748b"), tickformat=","),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2535", font=dict(color="#e2e8f0")),
)

st.markdown('<div class="chart-box"><div class="chart-title">📊 Top 15 Materials — March Actual vs Forecast</div>', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-div">Detailed Records</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="tbl-hdr">
    <span class="tbl-lbl">📋 March Consumption vs Forecast</span>
    <span class="tbl-badge">{len(df):,} materials</span>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="legend-bar">
    <span><span class="legend-dot" style="background:#ef4444"></span><span style="color:#f87171">Over Consumed (Actual &gt; Forecast)</span></span>
    <span><span class="legend-dot" style="background:#22c55e"></span><span style="color:#4ade80">Under Consumed (Actual &lt; Forecast)</span></span>
    <span style="color:#475569; margin-left:auto; font-size:10px; font-family:'JetBrains Mono',monospace;">Forecast for March = Per Day Req × 31 days</span>
</div>
""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="Cons vs Forecast")
st.download_button("⬇  Export to Excel", buf.getvalue(), "Consumption_vs_Forecast_March.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No records match the filters.")
else:
    def colour_row(row):
        s = row.get("Status", "")
        if s == "Over":   return ["background-color:#2d0a0a; color:#fca5a5"] * len(row)
        if s == "Under":  return ["background-color:#0a1f0a; color:#bbf7d0"] * len(row)
        return [""] * len(row)

    disp = df.rename(columns={
        "Actual_Consumed": "Actual (March)",
        "Material_Name":   "Material Name",
    }).copy()
    disp["Forecast (March)"] = (disp["Per Day Req"] * 31).round(0)

    col_order = ["Material SKU", "Material Name", "Category", "Actual (March)",
                 "Forecast (March)", "Per Day Req", "Variance", "Variance %", "Status"]
    col_order = [c for c in col_order if c in disp.columns]

    st.dataframe(
        disp[col_order].style.apply(colour_row, axis=1),
        use_container_width=True, hide_index=True, height=520,
        column_config={
            "Actual (March)":   st.column_config.NumberColumn("Actual (March)",   format="%.0f"),
            "Forecast (March)": st.column_config.NumberColumn("Forecast (March)", format="%.0f"),
            "Per Day Req":      st.column_config.NumberColumn("Per Day Req",       format="%.2f"),
            "Variance":         st.column_config.NumberColumn("Variance",          format="%.0f"),
            "Variance %":       st.column_config.NumberColumn("Variance %",        format="%.1f%%"),
        }
    )

st.markdown('<div class="app-footer">YOGABAR · CONSUMPTION VS FORECAST · MARCH</div>', unsafe_allow_html=True)
