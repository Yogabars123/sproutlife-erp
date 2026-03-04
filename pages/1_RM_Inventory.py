import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(
    page_title="RM Inventory · Sproutlife",
    layout="centered",
    page_icon="📦"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ═══════════════════════════════════════
   BASE RESET
═══════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section[data-testid="stSidebar"],
.main {
    background: #0a0d14 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }

.block-container {
    padding: 1rem 0.85rem 3rem 0.85rem !important;
    max-width: 100% !important;
}

[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ═══════════════════════════════════════
   HEADER
═══════════════════════════════════════ */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 14px 0;
    border-bottom: 1px solid #1e2535;
    margin-bottom: 14px;
}
.header-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.header-logo {
    width: 38px; height: 38px;
    min-width: 38px;
    background: #0f2e1a;
    border: 1px solid #1a4a28;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.header-brand-text {}
.header-title {
    font-size: 15px;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.1;
    white-space: nowrap;
}
.header-subtitle {
    font-size: 11px;
    color: #475569;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}
.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #071a0f;
    border: 1px solid #14532d;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 700;
    color: #22c55e;
    letter-spacing: 1px;
    font-family: 'JetBrains Mono', monospace;
    flex-shrink: 0;
}
.live-dot {
    width: 6px; height: 6px;
    min-width: 6px;
    background: #22c55e;
    border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 4px #22c55e; }
    50% { opacity: 0.25; box-shadow: none; }
}

/* ═══════════════════════════════════════
   KPI CARD
═══════════════════════════════════════ */
.kpi-wrap {
    background: #0d1929;
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.kpi-wrap::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    border-radius: 16px 16px 0 0;
}
.kpi-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.kpi-label {
    font-size: 10px;
    font-weight: 700;
    color: #60a5fa;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.kpi-number {
    font-size: 34px;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: -1.5px;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-caption {
    font-size: 11px;
    color: #475569;
    margin-top: 5px;
    font-weight: 400;
}
.kpi-icon {
    width: 52px; height: 52px;
    min-width: 52px;
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.15);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}

/* ═══════════════════════════════════════
   FILTER SECTION
═══════════════════════════════════════ */
.section-heading {
    font-size: 10px;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 14px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2535;
}

/* ═══════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
═══════════════════════════════════════ */
[data-testid="stTextInput"] > div > div {
    background: #111827 !important;
    border: 1.5px solid #1e2d45 !important;
    border-radius: 10px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
[data-testid="stTextInput"] input {
    background: transparent !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #334155 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #111827 !important;
    border: 1.5px solid #1e2d45 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    padding: 2px 6px !important;
}

[data-testid="stWidgetLabel"] {
    display: none !important;
}

/* Refresh button */
.stButton > button {
    width: 100% !important;
    background: #111827 !important;
    border: 1.5px solid #1e2d45 !important;
    border-radius: 10px !important;
    color: #64748b !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s !important;
    margin-bottom: 4px !important;
}
.stButton > button:hover {
    border-color: #3b82f6 !important;
    color: #93c5fd !important;
    background: #0f1e36 !important;
}

/* Download button */
.stDownloadButton > button {
    width: 100% !important;
    background: #0f2e5a !important;
    border: 1.5px solid #1d4ed8 !important;
    border-radius: 10px !important;
    color: #93c5fd !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 11px !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: #1e3a8a !important;
    color: #fff !important;
    border-color: #3b82f6 !important;
}

/* ═══════════════════════════════════════
   FILTER RESULT BANNER
═══════════════════════════════════════ */
.result-banner {
    background: #071a0f;
    border: 1px solid #14532d;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 8px 0 14px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.rb-label {
    font-size: 10px;
    font-weight: 700;
    color: #16a34a;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
}
.rb-value {
    font-size: 28px;
    font-weight: 800;
    color: #f0fdf4;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -1px;
    line-height: 1;
}
.rb-right { text-align: right; flex-shrink: 0; }
.rb-count {
    font-size: 22px;
    font-weight: 700;
    color: #4ade80;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.rb-count-sub { font-size: 10px; color: #166534; margin-top: 2px; }

/* ═══════════════════════════════════════
   TABLE CONTROLS
═══════════════════════════════════════ */
.table-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 6px 0;
}
.tc-label {
    font-size: 10px;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}
.tc-badge {
    background: #0f172a;
    border: 1px solid #1e2d45;
    color: #3b82f6;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
}

/* ═══════════════════════════════════════
   DATAFRAME
═══════════════════════════════════════ */
div[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #1e2535 !important;
}
div[data-testid="stDataFrame"] > div {
    background: #0d1117 !important;
}

/* ═══════════════════════════════════════
   ALERT
═══════════════════════════════════════ */
[data-testid="stAlert"] {
    background: #1a1200 !important;
    border: 1px solid #78350f !important;
    border-radius: 10px !important;
    color: #fbbf24 !important;
}

/* ═══════════════════════════════════════
   FOOTER
═══════════════════════════════════════ */
.app-footer {
    margin-top: 2rem;
    padding-top: 12px;
    border-top: 1px solid #1e2535;
    text-align: center;
    font-size: 10px;
    font-weight: 600;
    color: #1e2d45;
    letter-spacing: 1.5px;
    font-family: 'JetBrains Mono', monospace;
}

/* spacing helper */
.gap { margin-bottom: 10px; }
.gap-sm { margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────
@st.cache_data
def load_rm():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="RM-Inventory")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_forecast():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    xl = pd.ExcelFile(file_path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    if not sheet:
        return pd.DataFrame(columns=["Item code", "Forecast"])
    df = pd.read_excel(file_path, sheet_name=sheet)
    df.columns = df.columns.str.strip()
    if "Location" in df.columns:
        df = df[df["Location"].astype(str).str.strip().str.lower() == "plant"]
    if "Forecast" in df.columns:
        df["Forecast"] = pd.to_numeric(df["Forecast"], errors="coerce").fillna(0)
        df = df[df["Forecast"] > 0]
    ic = "Item code" if "Item code" in df.columns else "Item Code"
    df[ic] = df[ic].astype(str).str.strip()
    return df[[ic, "Forecast"]].rename(columns={ic: "Item code"}).drop_duplicates(subset="Item code")

df_raw   = load_rm()
df_fcast = load_forecast()

ALLOWED_WH = [
    "Central", "Central Production -Bar Line", "Central Production - Oats Line",
    "Central Production - Peanut Line", "Central Production - Muesli Line",
    "RM Warehouse Tumkur", "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM", "Tumkur Warehouse",
    "Central Production -Packing", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
SOH_WH = [
    "Central", "RM Warehouse Tumkur", "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]

df_raw = df_raw[df_raw["Warehouse"].isin(ALLOWED_WH)]
df_soh = df_raw[df_raw["Warehouse"].isin(SOH_WH)]

soh_sku = df_soh.groupby("Item SKU")["Qty Available"].sum().reset_index()
soh_sku.columns = ["Item SKU", "SOH"]
soh_sku["_k"] = soh_sku["Item SKU"].astype(str).str.upper()
df_fcast["_k"] = df_fcast["Item code"].astype(str).str.upper()
soh_sku = soh_sku.merge(df_fcast[["_k", "Forecast"]], on="_k", how="left")
soh_sku["Forecast"] = soh_sku["Forecast"].fillna(0)
soh_sku["Days of Stock"] = soh_sku.apply(
    lambda r: round(r["SOH"] / (r["Forecast"] / 26), 1) if r["Forecast"] > 0 else None, axis=1
)
soh_sku = soh_sku.drop(columns=["_k"])

# ─────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="header-brand">
        <div class="header-logo">📦</div>
        <div class="header-brand-text">
            <div class="header-title">RM Inventory</div>
            <div class="header-subtitle">Sproutlife Foods · Raw Material</div>
        </div>
    </div>
    <div class="live-pill">
        <span class="live-dot"></span>LIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# REFRESH
# ─────────────────────────────────────────────────
if st.button("↺  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ─────────────────────────────────────────────────
# KPI
# ─────────────────────────────────────────────────
total_soh = df_raw[df_raw["Warehouse"].isin(SOH_WH)]["Qty Available"].sum()

st.markdown(f"""
<div class="kpi-wrap">
    <div class="kpi-inner">
        <div>
            <div class="kpi-label">Total Stock on Hand</div>
            <div class="kpi-number">{total_soh:,.0f}</div>
            <div class="kpi-caption">Across all storage warehouses</div>
        </div>
        <div class="kpi-icon">📦</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────────
st.markdown('<div class="section-heading">Filters</div>', unsafe_allow_html=True)

search = st.text_input("_", placeholder="🔍  Search item name, SKU or batch…",
                        label_visibility="collapsed")
st.markdown('<div class="gap-sm"></div>', unsafe_allow_html=True)

wh_opts  = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
selected_wh = st.selectbox("_", wh_opts, label_visibility="collapsed")
st.markdown('<div class="gap-sm"></div>', unsafe_allow_html=True)

cat_opts = (["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
            if "Category" in df_raw.columns else ["All Categories"])
selected_cat = st.selectbox("__", cat_opts, label_visibility="collapsed")
st.markdown('<div class="gap-sm"></div>', unsafe_allow_html=True)

stock_filter = st.selectbox("___",
                             ["All Stock", "Available Only", "Zero / Negative Stock"],
                             label_visibility="collapsed")

# ─────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(
        lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if selected_wh != "All Warehouses":
    df = df[df["Warehouse"] == selected_wh]
if selected_cat != "All Categories" and "Category" in df_raw.columns:
    df = df[df["Category"].astype(str) == selected_cat]
if stock_filter == "Available Only":
    df = df[df["Qty Available"] > 0]
elif stock_filter == "Zero / Negative Stock":
    df = df[df["Qty Available"] <= 0]

# ── Filtered result banner
is_filtered = (bool(search) or selected_wh != "All Warehouses"
               or selected_cat != "All Categories" or stock_filter != "All Stock")
if is_filtered:
    f_qty = df[df["Warehouse"].isin(SOH_WH)]["Qty Available"].sum()
    if search:        ctx = f'"{search}"'
    elif selected_wh != "All Warehouses": ctx = selected_wh[:28]
    elif selected_cat != "All Categories": ctx = selected_cat[:28]
    else: ctx = stock_filter

    st.markdown(f"""
    <div class="result-banner">
        <div>
            <div class="rb-label">Filtered · {ctx}</div>
            <div class="rb-value">{f_qty:,.0f}</div>
        </div>
        <div class="rb-right">
            <div class="rb-count">{len(df):,}</div>
            <div class="rb-count-sub">records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────────
st.markdown('<div class="section-heading">Records</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="table-controls">
    <span class="tc-label">📋 Showing results</span>
    <span class="tc-badge">{len(df):,} rows</span>
</div>
""", unsafe_allow_html=True)

# Export button
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="RM Inventory")
st.download_button(
    "⬇  Export to Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.markdown('<div class="gap-sm"></div>', unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️  No records match the current filters.")
else:
    df_m = df.merge(soh_sku[["Item SKU", "Forecast", "Days of Stock"]], on="Item SKU", how="left")
    priority = [
        "Item Name", "Item SKU", "Category", "Warehouse", "UoM",
        "Qty Available", "Forecast", "Days of Stock",
        "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)",
        "Batch No", "MFG Date", "Expiry Date", "Current Aging (Days)"
    ]
    cols = [c for c in priority if c in df_m.columns]
    cols += [c for c in df_m.columns if c not in cols]
    df_show = df_m[cols].copy()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df_show.columns:
            df_show[col] = df_show[col].dt.strftime("%d-%b-%Y").fillna("")

    st.dataframe(
        df_show,
        use_container_width=True,
        height=460,
        hide_index=True,
        column_config={
            "Qty Available":        st.column_config.NumberColumn("Qty Avail",  format="%.0f"),
            "Forecast":             st.column_config.NumberColumn("Forecast",   format="%.0f"),
            "Days of Stock":        st.column_config.NumberColumn("DoS",        format="%.1f"),
            "Qty Inward":           st.column_config.NumberColumn("Inward",     format="%.0f"),
            "Qty (Issue / Hold)":   st.column_config.NumberColumn("Issue/Hold", format="%.0f"),
            "Value (Inc Tax)":      st.column_config.NumberColumn("Value ₹",    format="%.0f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging",      format="%d"),
        }
    )

# ─────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">SPROUTLIFE FOODS · RM INVENTORY</div>
""", unsafe_allow_html=True)
