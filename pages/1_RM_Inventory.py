import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory · Sproutlife", layout="wide", page_icon="📦")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117 !important;
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }

[data-testid="stAppViewContainer"] {
    background: #0f1117 !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 1600px !important;
}

/* ── TOPBAR ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.topbar-left { display: flex; align-items: center; gap: 14px; }
.topbar-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #22c55e22, #16a34a44);
    border: 1px solid #22c55e55;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.topbar-title {
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.4px;
    margin: 0;
    line-height: 1;
}
.topbar-sub {
    font-size: 12px;
    color: #64748b;
    margin: 3px 0 0 0;
    font-weight: 400;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0d2218;
    border: 1px solid #166534;
    color: #4ade80;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.5px;
}
.live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #4ade80;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 1.75rem;
}
.kpi-card {
    background: #161b27;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.green::before { background: linear-gradient(90deg, #22c55e, #16a34a); }
.kpi-card.blue::before  { background: linear-gradient(90deg, #3b82f6, #1d4ed8); }
.kpi-card.amber::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
.kpi-card.rose::before  { background: linear-gradient(90deg, #f43f5e, #be123c); }

.kpi-label {
    font-size: 10.5px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.8px;
    line-height: 1;
    font-family: 'DM Mono', monospace;
}
.kpi-value.green { color: #4ade80; }
.kpi-value.blue  { color: #60a5fa; }
.kpi-value.amber { color: #fbbf24; }
.kpi-value.rose  { color: #fb7185; }
.kpi-sub {
    font-size: 11px;
    color: #475569;
    margin-top: 5px;
}

/* ── FILTER PANEL ── */
.filter-panel {
    background: #161b27;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 1.5rem;
}
.filter-title {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 12px;
}

/* ── Streamlit widget overrides ── */
[data-testid="stTextInput"] input {
    background: #0f1117 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #475569 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #0f1117 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    font-size: 13.5px !important;
}

.stButton > button {
    background: #161b27 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #3b82f6 !important;
    color: #60a5fa !important;
    background: #1e2d45 !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #1e3a5f, #1d4ed8) !important;
    border: 1px solid #3b82f6 !important;
    color: #bfdbfe !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 9px 18px !important;
    letter-spacing: 0.2px !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    color: #fff !important;
}

/* ── TABLE SECTION ── */
.table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.table-title {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.9px;
}
.record-badge {
    background: #1e293b;
    border: 1px solid rgba(255,255,255,0.08);
    color: #60a5fa;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
div[data-testid="stDataFrame"] table {
    background: #161b27 !important;
    font-size: 12.5px !important;
    font-family: 'DM Sans', sans-serif !important;
}
div[data-testid="stDataFrame"] thead tr th {
    background: #1e293b !important;
    color: #94a3b8 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600 !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
div[data-testid="stDataFrame"] tbody tr:hover td {
    background: #1e293b !important;
}

/* ── DIVIDER ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 0.6rem 0 !important; }

/* ── LABELS ── */
[data-testid="stWidgetLabel"] p {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── WARNING ── */
[data-testid="stAlert"] {
    background: #1c1a10 !important;
    border: 1px solid #854d0e !important;
    border-radius: 10px !important;
    color: #fbbf24 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
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

df_raw = load_rm()
df_forecast = load_forecast()

allowed_warehouses = [
    "Central", "Central Production -Bar Line", "Central Production - Oats Line",
    "Central Production - Peanut Line", "Central Production - Muesli Line",
    "RM Warehouse Tumkur", "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM", "Tumkur Warehouse",
    "Central Production -Packing", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
df_raw = df_raw[df_raw["Warehouse"].isin(allowed_warehouses)]

soh_warehouses = [
    "Central", "RM Warehouse Tumkur", "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
df_soh = df_raw[df_raw["Warehouse"].isin(soh_warehouses)]
soh_by_sku = df_soh.groupby("Item SKU")["Qty Available"].sum().reset_index()
soh_by_sku.columns = ["Item SKU", "SOH"]
soh_by_sku["_key"] = soh_by_sku["Item SKU"].astype(str).str.upper()
df_forecast["_key"] = df_forecast["Item code"].astype(str).str.upper()
soh_by_sku = soh_by_sku.merge(df_forecast[["_key", "Forecast"]], on="_key", how="left")
soh_by_sku["Forecast"] = soh_by_sku["Forecast"].fillna(0)
soh_by_sku["Days of Stock"] = soh_by_sku.apply(
    lambda r: round(r["SOH"] / (r["Forecast"] / 26), 1) if r["Forecast"] > 0 else None, axis=1
)
soh_by_sku = soh_by_sku.drop(columns=["_key"])

# ---------------------------------------------------
# TOPBAR
# ---------------------------------------------------
col_title, col_refresh = st.columns([6, 1])
with col_title:
    st.markdown("""
    <div class="topbar">
        <div class="topbar-left">
            <div class="topbar-icon">📦</div>
            <div>
                <p class="topbar-title">RM Inventory</p>
                <p class="topbar-sub">Sproutlife Foods · Raw Material Stock</p>
            </div>
        </div>
        <div class="live-badge">
            <span class="live-dot"></span>LIVE
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_refresh:
    st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
    if st.button("⟳  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ---------------------------------------------------
# GLOBAL KPI METRICS (before filters)
# ---------------------------------------------------
total_soh = df_raw[df_raw["Warehouse"].isin(soh_warehouses)]["Qty Available"].sum()
total_skus = df_raw["Item SKU"].nunique()
zero_stock = (df_soh.groupby("Item SKU")["Qty Available"].sum() <= 0).sum()
with_forecast = (soh_by_sku["Forecast"] > 0).sum()

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card green">
        <div class="kpi-label">Total SOH (Qty)</div>
        <div class="kpi-value green">{total_soh:,.0f}</div>
        <div class="kpi-sub">Across storage warehouses</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-label">Active SKUs</div>
        <div class="kpi-value blue">{total_skus:,}</div>
        <div class="kpi-sub">Unique raw materials</div>
    </div>
    <div class="kpi-card amber">
        <div class="kpi-label">With Forecast</div>
        <div class="kpi-value amber">{with_forecast:,}</div>
        <div class="kpi-sub">SKUs with DoS calculated</div>
    </div>
    <div class="kpi-card rose">
        <div class="kpi-label">Zero / Low Stock</div>
        <div class="kpi-value rose">{zero_stock:,}</div>
        <div class="kpi-sub">SKUs at or below zero</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔽 Filters</div>', unsafe_allow_html=True)

fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])
with fc1:
    search = st.text_input("Search", placeholder="Item name, SKU, or batch…", label_visibility="collapsed")
with fc2:
    wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    selected_wh = st.selectbox("Warehouse", wh_opts, label_visibility="visible")
with fc3:
    cat_opts = ["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist()) if "Category" in df_raw.columns else ["All Categories"]
    selected_cat = st.selectbox("Category", cat_opts, label_visibility="visible")
with fc4:
    stock_filter = st.selectbox("Stock Status", ["All", "Available Only", "Zero / Negative Stock"], label_visibility="visible")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
df = df_raw.copy()
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
if selected_wh != "All Warehouses":
    df = df[df["Warehouse"] == selected_wh]
if selected_cat != "All Categories" and "Category" in df_raw.columns:
    df = df[df["Category"].astype(str) == selected_cat]
if stock_filter == "Available Only":
    df = df[df["Qty Available"] > 0]
elif stock_filter == "Zero / Negative Stock":
    df = df[df["Qty Available"] <= 0]

# ── Contextual filtered KPI
filtered_qty = df[df["Warehouse"].isin(soh_warehouses)]["Qty Available"].sum()
if search or selected_wh != "All Warehouses" or selected_cat != "All Categories" or stock_filter != "All":
    if search:
        ctx_label = f"Filtered Qty · \"{search}\""
    elif selected_wh != "All Warehouses":
        ctx_label = f"Qty · {selected_wh}"
    elif selected_cat != "All Categories":
        ctx_label = f"Qty · {selected_cat}"
    else:
        ctx_label = f"Qty · {stock_filter}"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0d2218, #0a1f2e);
        border: 1px solid #166534;
        border-left: 3px solid #22c55e;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div>
            <div style="font-size:11px;font-weight:600;color:#4ade80;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">{ctx_label}</div>
            <div style="font-size:30px;font-weight:700;color:#f1f5f9;font-family:'DM Mono',monospace;letter-spacing:-1px;">{filtered_qty:,.0f}</div>
        </div>
        <div style="text-align:right">
            <div style="font-size:22px;font-weight:700;color:#60a5fa;font-family:'DM Mono',monospace;">{len(df):,}</div>
            <div style="font-size:11px;color:#475569;">records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------
tl, tr = st.columns([6, 2])
with tl:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <span style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.9px;">📋 Records</span>
        <span style="background:#1e293b;border:1px solid rgba(255,255,255,0.08);color:#60a5fa;
                     font-size:11px;font-weight:600;padding:3px 10px;border-radius:100px;
                     font-family:'DM Mono',monospace;">{len(df):,}</span>
    </div>
    """, unsafe_allow_html=True)
with tr:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="RM")
    st.download_button(
        "⬇ Export Excel", buf.getvalue(), "RM_Inventory.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

if df.empty:
    st.warning("⚠️  No records match the current filters.")
else:
    df_m = df.merge(soh_by_sku[["Item SKU", "Forecast", "Days of Stock"]], on="Item SKU", how="left")
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
        height=480,
        hide_index=True,
        column_config={
            "Qty Available":          st.column_config.NumberColumn("Qty Avail",   format="%.0f"),
            "Forecast":               st.column_config.NumberColumn("Forecast",    format="%.0f"),
            "Days of Stock":          st.column_config.NumberColumn("DoS",         format="%.1f"),
            "Qty Inward":             st.column_config.NumberColumn("Inward",      format="%.0f"),
            "Qty (Issue / Hold)":     st.column_config.NumberColumn("Issue/Hold",  format="%.0f"),
            "Value (Inc Tax)":        st.column_config.NumberColumn("Value",       format="₹%.0f"),
            "Current Aging (Days)":   st.column_config.NumberColumn("Aging (d)",   format="%d"),
        }
    )

# ── Footer
st.markdown("""
<div style="margin-top:2.5rem;padding-top:1.25rem;border-top:1px solid rgba(255,255,255,0.06);
            display:flex;align-items:center;justify-content:space-between;">
    <span style="font-size:11px;color:#334155;font-family:'DM Mono',monospace;">
        SPROUTLIFE FOODS · RM INVENTORY
    </span>
    <span style="font-size:11px;color:#334155;">
        Data refreshes on every page load
    </span>
</div>
""", unsafe_allow_html=True)
