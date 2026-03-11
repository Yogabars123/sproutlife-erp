import streamlit as st
import pandas as pd
import io

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

# ── FILTERS ───────────────────────────────────────────────────────────────────
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

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
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

# ── KPIs ──────────────────────────────────────────────────────────────────────
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
# INTELLIGENCE PANELS
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

cat_dos = pd.DataFrame()
if not soh_full.empty and "Category" in soh_full.columns:
    cat_dos = (soh_full[soh_full["Per Day Req"] > 0]
               .groupby("Category").agg(Avg_DoS=("Days of Stock","mean"), SKUs=("Item SKU","count"), SOH=("SOH","sum"))
               .reset_index().sort_values("Avg_DoS", ascending=True))

wh_dist = pd.DataFrame()
if not df_raw.empty:
    wh_dist = (df_raw[df_raw["Warehouse"].isin(SOH_WH)]
               .groupby("Warehouse")["Qty Available"].sum().reset_index()
               .sort_values("Qty Available", ascending=False))
    wh_dist = wh_dist[wh_dist["Qty Available"] > 0]

st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)
st.markdown('<div class="sec-div">🔍 Inventory Intelligence</div>', unsafe_allow_html=True)

# ── Summary strip: 3 urgency counts ──────────────────────────────────────────
n_crit  = len(critical_skus)
n_low   = len(reorder_skus)
n_zero  = len(critical_skus[critical_skus["Days of Stock"] <= 1]) if not critical_skus.empty else 0
if not soh_full.empty and "Days of Stock" in soh_full.columns:
    n_ok = int((soh_full["Days of Stock"].fillna(0) > 14).sum())
else:
    n_ok = 0

st.markdown(
    '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;">'

    # Stockout today
    f'<div style="background:#1a0608;border:1.5px solid #7f1d1d;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#ef4444;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🔴 Stockout Today</div>'
    f'<div style="font-size:28px;font-weight:800;color:#fca5a5;font-family:JetBrains Mono,monospace;line-height:1;">{n_zero}</div>'
    f'<div style="font-size:10px;color:#7f1d1d;margin-top:3px;">SKUs at ≤ 1 day</div>'
    f'</div>'

    # Critical < 7d
    f'<div style="background:#160a00;border:1.5px solid #92400e;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#f97316;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🟠 Critical &lt; 7d</div>'
    f'<div style="font-size:28px;font-weight:800;color:#fed7aa;font-family:JetBrains Mono,monospace;line-height:1;">{n_crit}</div>'
    f'<div style="font-size:10px;color:#78350f;margin-top:3px;">SKUs need reorder</div>'
    f'</div>'

    # Low 7-14d
    f'<div style="background:#0f0d02;border:1.5px solid #78350f;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#f59e0b;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">🟡 Low 7–14d</div>'
    f'<div style="font-size:28px;font-weight:800;color:#fde68a;font-family:JetBrains Mono,monospace;line-height:1;">{n_low}</div>'
    f'<div style="font-size:10px;color:#713f12;margin-top:3px;">SKUs watch closely</div>'
    f'</div>'

    # Healthy
    f'<div style="background:#061a0a;border:1.5px solid #14532d;border-radius:12px;padding:12px 16px;text-align:center;">'
    f'<div style="font-size:9px;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;">✅ Healthy &gt; 14d</div>'
    f'<div style="font-size:28px;font-weight:800;color:#bbf7d0;font-family:JetBrains Mono,monospace;line-height:1;">{n_ok}</div>'
    f'<div style="font-size:10px;color:#14532d;margin-top:3px;">SKUs well stocked</div>'
    f'</div>'

    '</div>',
    unsafe_allow_html=True
)

# ── Row 1: Critical Alerts + Reorder Watchlist ────────────────────────────────
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
            dos      = float(r["Days of Stock"])
            soh_v    = float(r["SOH"])
            pdr      = float(r["Per Day Req"])
            sku      = str(r["Item SKU"])
            name     = str(r.get("Item Name", ""))
            cat      = str(r.get("Category", ""))
            # Colour tiers: ≤1d = deep red, 1-3d = red, 3-7d = orange
            if dos <= 1:
                bar_c = "#dc2626"; txt_c = "#fca5a5"; bg_c = "#1f0406"; bdr_c = "#7f1d1d"
                badge = "STOCKOUT"
            elif dos <= 3:
                bar_c = "#ef4444"; txt_c = "#fca5a5"; bg_c = "#1a0608"; bdr_c = "#450a0a"
                badge = f"{dos:.1f}d left"
            else:
                bar_c = "#f97316"; txt_c = "#fed7aa"; bg_c = "#180b02"; bdr_c = "#431407"
                badge = f"{dos:.1f}d left"
            bar_w    = min(int(dos / 7 * 100), 100)
            soh_f    = f"{soh_v:,.0f}"
            pdr_f    = f"{pdr:,.1f}"
            # Days remaining as human label
            if dos <= 1:   urgency = "⛔ Stocking out NOW"
            elif dos <= 3: urgency = f"🔴 Gone in ~{int(dos)}d"
            else:          urgency = f"🟠 ~{dos:.1f} days remaining"
            st.markdown(
                f'<div style="background:{bg_c};border:1px solid {bdr_c};border-radius:10px;padding:10px 14px;margin-bottom:7px;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="font-size:11px;font-weight:700;color:{txt_c};font-family:JetBrains Mono,monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sku}</div>'
                f'<div style="font-size:10px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">{name}</div>'
                f'</div>'
                f'<div style="margin-left:10px;flex-shrink:0;">'
                f'<div style="background:#2d0a0a;border:1px solid {bdr_c};border-radius:6px;padding:3px 8px;font-size:11px;font-weight:800;color:{txt_c};font-family:JetBrains Mono,monospace;text-align:center;">{badge}</div>'
                f'</div>'
                '</div>'
                f'<div style="font-size:10px;color:#f87171;margin-bottom:5px;font-weight:600;">{urgency}</div>'
                f'<div style="background:#2d0a0a;border-radius:4px;height:5px;margin-bottom:6px;">'
                f'<div style="width:{bar_w}%;background:{bar_c};height:5px;border-radius:4px;"></div>'
                f'</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;">'
                f'<div style="background:#0d0204;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">SOH</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{soh_f}</div>'
                f'</div>'
                f'<div style="background:#0d0204;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Per Day</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{pdr_f}</div>'
                f'</div>'
                f'<div style="background:#0d0204;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Category</div>'
                f'<div style="font-size:10px;font-weight:600;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{cat[:12] if cat else "—"}</div>'
                f'</div>'
                '</div></div>',
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
            soh_f = f"{soh_v:,.0f}"
            pdr_f = f"{pdr:,.1f}"
            dos_f = f"{dos:.1f}d"
            st.markdown(
                '<div style="background:#120d00;border:1px solid #451a03;border-radius:10px;padding:10px 14px;margin-bottom:7px;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">'
                '<div style="flex:1;min-width:0;">'
                f'<div style="font-size:11px;font-weight:700;color:#fde68a;font-family:JetBrains Mono,monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sku}</div>'
                f'<div style="font-size:10px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">{name}</div>'
                '</div>'
                '<div style="margin-left:10px;flex-shrink:0;">'
                f'<div style="background:#2d1f00;border:1px solid #78350f;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:800;color:#fde68a;font-family:JetBrains Mono,monospace;">{dos_f}</div>'
                '</div></div>'
                '<div style="background:#2d1f00;border-radius:4px;height:5px;margin-bottom:6px;">'
                f'<div style="width:{bar_w}%;background:#f59e0b;height:5px;border-radius:4px;"></div>'
                '</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;">'
                '<div style="background:#0a0800;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">SOH</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{soh_f}</div>'
                '</div>'
                '<div style="background:#0a0800;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Per Day</div>'
                f'<div style="font-size:11px;font-weight:700;color:#94a3b8;font-family:JetBrains Mono,monospace;">{pdr_f}</div>'
                '</div>'
                '<div style="background:#0a0800;border-radius:6px;padding:4px 8px;text-align:center;">'
                f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.8px;">Category</div>'
                f'<div style="font-size:10px;font-weight:600;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{cat[:12] if cat else "—"}</div>'
                '</div>'
                '</div></div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 2: Category DoS bars + Warehouse Distribution ────────────────────────
col_cat, col_wh = st.columns([1.4, 1], gap="medium")

with col_cat:
    st.markdown('<div class="sec-div">📊 Days of Stock by Category</div>', unsafe_allow_html=True)
    if cat_dos.empty:
        st.info("No category data available.")
    else:
        max_dos = min(float(cat_dos["Avg_DoS"].max()), 60.0)
        for _, row in cat_dos.iterrows():
            dos_v  = float(row["Avg_DoS"]) if pd.notna(row["Avg_DoS"]) else 0
            skus_n = int(row["SKUs"])
            soh_v  = float(row["SOH"])
            cat_n  = str(row["Category"])
            bar_w  = min(int(dos_v / max(max_dos, 1) * 100), 100)
            bar_c  = "#ef4444" if dos_v < 7 else "#f59e0b" if dos_v <= 14 else "#22c55e"
            txt_c  = "#fca5a5" if dos_v < 7 else "#fde68a" if dos_v <= 14 else "#bbf7d0"
            bg_c   = "#140608" if dos_v < 7 else "#0f0d02" if dos_v <= 14 else "#061a0a"
            bdr_c  = "#450a0a" if dos_v < 7 else "#451a03" if dos_v <= 14 else "#14532d"
            dos_f  = f"{dos_v:.1f}d"
            soh_f  = f"{soh_v:,.0f}"
            st.markdown(
                f'<div style="background:{bg_c};border:1px solid {bdr_c};border-radius:10px;padding:10px 14px;margin-bottom:7px;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">'
                f'<span style="font-size:12px;font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;">{cat_n}</span>'
                '<div style="display:flex;align-items:center;gap:8px;">'
                f'<span style="font-size:10px;color:#475569;font-family:JetBrains Mono,monospace;">{skus_n} SKUs</span>'
                f'<span style="font-size:13px;font-weight:800;color:{txt_c};font-family:JetBrains Mono,monospace;">{dos_f}</span>'
                '</div></div>'
                '<div style="background:#1e2535;border-radius:4px;height:7px;margin-bottom:5px;">'
                f'<div style="width:{bar_w}%;background:{bar_c};height:7px;border-radius:4px;"></div>'
                '</div>'
                f'<div style="font-size:10px;color:#475569;font-family:JetBrains Mono,monospace;">SOH: <b style="color:#64748b;">{soh_f}</b></div>'
                '</div>',
                unsafe_allow_html=True
            )

with col_wh:
    st.markdown('<div class="sec-div">🏭 Stock by Warehouse</div>', unsafe_allow_html=True)
    if wh_dist.empty:
        st.info("No warehouse data.")
    else:
        total_wh = float(wh_dist["Qty Available"].sum())
        max_wh   = float(wh_dist["Qty Available"].max())
        wh_short = {
            "Central": "Central",
            "RM Warehouse Tumkur": "RM Tumkur",
            "Central Warehouse - Cold Storage RM": "Cold Storage",
            "Tumkur Warehouse": "Tumkur",
            "Tumkur New Warehouse": "Tumkur New",
            "HF Factory FG Warehouse": "HF Factory",
            "Sproutlife Foods Private Ltd (SNOWMAN)": "SNOWMAN",
        }
        wh_colors = ["#5bc8c0","#818cf8","#60a5fa","#34d399","#f59e0b","#f472b6","#a78bfa"]
        for i, (_, row) in enumerate(wh_dist.iterrows()):
            wh_n  = str(row["Warehouse"])
            qty   = float(row["Qty Available"])
            bar_w = int(qty / max(max_wh, 1) * 100)
            pct   = qty / total_wh * 100 if total_wh > 0 else 0
            color = wh_colors[i % len(wh_colors)]
            short = wh_short.get(wh_n, wh_n[:18])
            qty_f = f"{qty:,.0f}"
            pct_f = f"{pct:.1f}%"
            st.markdown(
                '<div style="background:#0d1117;border:1px solid #1e2535;border-radius:10px;padding:10px 14px;margin-bottom:7px;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">'
                f'<span style="font-size:12px;font-weight:700;color:#e2e8f0;">{short}</span>'
                '<div style="display:flex;align-items:center;gap:8px;">'
                f'<span style="font-size:10px;color:#475569;font-family:JetBrains Mono,monospace;">{pct_f}</span>'
                f'<span style="font-size:12px;font-weight:800;color:{color};font-family:JetBrains Mono,monospace;">{qty_f}</span>'
                '</div></div>'
                '<div style="background:#1e2535;border-radius:4px;height:7px;">'
                f'<div style="width:{bar_w}%;background:{color};height:7px;border-radius:4px;"></div>'
                '</div></div>',
                unsafe_allow_html=True
            )
        total_f = f"{total_wh:,.0f}"
        st.markdown(
            '<div style="background:#0a0f1a;border:1px solid #1e3a5f;border-radius:10px;padding:8px 14px;margin-top:4px;">'
            '<div style="display:flex;justify-content:space-between;font-size:11px;font-family:JetBrains Mono,monospace;">'
            '<span style="color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Total SOH</span>'
            f'<span style="color:#60a5fa;font-weight:800;">{total_f}</span>'
            '</div></div>',
            unsafe_allow_html=True
        )

# ── TABLE ─────────────────────────────────────────────────────────────────────
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
