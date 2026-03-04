import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory · Sproutlife", layout="centered", page_icon="📦")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
    background: #0f1117 !important;
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 1.2rem 1rem 2rem 1rem !important;
    max-width: 100% !important;
}

[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ── TOPBAR ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    flex-wrap: nowrap;
}
.topbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}
.topbar-icon {
    width: 36px; height: 36px;
    min-width: 36px;
    background: linear-gradient(135deg, #22c55e22, #16a34a44);
    border: 1px solid #22c55e55;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
}
.topbar-text { min-width: 0; }
.topbar-title {
    font-size: 16px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
    margin: 0;
    line-height: 1.1;
    white-space: nowrap;
}
.topbar-sub {
    font-size: 11px;
    color: #64748b;
    margin: 2px 0 0 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #0d2218;
    border: 1px solid #166534;
    color: #4ade80;
    font-size: 10px;
    font-weight: 600;
    padding: 4px 9px;
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.5px;
    white-space: nowrap;
    flex-shrink: 0;
}
.live-dot {
    width: 6px; height: 6px;
    min-width: 6px;
    border-radius: 50%;
    background: #4ade80;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── SINGLE KPI CARD ── */
.kpi-card {
    background: linear-gradient(135deg, #0d2218 0%, #111827 100%);
    border: 1px solid #166534;
    border-left: 3px solid #22c55e;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.kpi-label {
    font-size: 10px;
    font-weight: 600;
    color: #4ade80;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -1px;
    line-height: 1;
    font-family: 'DM Mono', monospace;
}
.kpi-sub {
    font-size: 11px;
    color: #475569;
    margin-top: 4px;
}
.kpi-icon-wrap {
    width: 48px; height: 48px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}

/* ── FILTER LABELS ── */
.filter-label {
    font-size: 10.5px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin: 0.9rem 0 0.4rem 0;
}

/* ── FILTERED RESULT BANNER ── */
.filter-result {
    background: linear-gradient(135deg, #0d2218, #0a1f2e);
    border: 1px solid #166534;
    border-left: 3px solid #22c55e;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 0.75rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.fr-tag {
    font-size: 10px;
    font-weight: 600;
    color: #4ade80;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 3px;
}
.fr-val {
    font-size: 26px;
    font-weight: 700;
    color: #f1f5f9;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.8px;
    line-height: 1;
}
.fr-right { text-align: right; }
.fr-count {
    font-size: 20px;
    font-weight: 700;
    color: #60a5fa;
    font-family: 'DM Mono', monospace;
}
.fr-count-label { font-size: 10px; color: #475569; }

/* ── TABLE ROW HEADER ── */
.tbl-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0.5rem 0;
}
.tbl-badge {
    background: #1e293b;
    border: 1px solid rgba(255,255,255,0.08);
    color: #60a5fa;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
}

/* ── Widget overrides ── */
[data-testid="stTextInput"] input {
    background: #161b27 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #475569 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #161b27 !important;
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
    padding: 9px 16px !important;
    transition: all 0.2s !important;
    width: 100% !important;
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
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    color: #fff !important;
}

[data-testid="stWidgetLabel"] p {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

[data-testid="stAlert"] {
    background: #1c1a10 !important;
    border: 1px solid #854d0e !important;
    border-radius: 10px !important;
    color: #fbbf24 !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; margin: 0.5rem 0 !important; }
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
st.markdown("""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-icon">📦</div>
        <div class="topbar-text">
            <p class="topbar-title">RM Inventory</p>
            <p class="topbar-sub">Sproutlife Foods · Raw Material</p>
        </div>
    </div>
    <div class="live-badge">
        <span class="live-dot"></span>LIVE
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("⟳  Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.markdown("<div style='margin-bottom:0.75rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------
# SINGLE KPI — Total SOH
# ---------------------------------------------------
total_soh = df_raw[df_raw["Warehouse"].isin(soh_warehouses)]["Qty Available"].sum()

st.markdown(f"""
<div class="kpi-card">
    <div>
        <div class="kpi-label">Total Stock on Hand</div>
        <div class="kpi-value">{total_soh:,.0f}</div>
        <div class="kpi-sub">Across all storage warehouses</div>
    </div>
    <div class="kpi-icon-wrap">📦</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FILTERS — stacked vertically for mobile
# ---------------------------------------------------
st.markdown('<div class="filter-label">🔍 Search</div>', unsafe_allow_html=True)
search = st.text_input("Search", placeholder="Item name, SKU or batch…", label_visibility="collapsed")

st.markdown('<div class="filter-label">🏭 Warehouse</div>', unsafe_allow_html=True)
wh_opts = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
selected_wh = st.selectbox("Warehouse", wh_opts, label_visibility="collapsed")

st.markdown('<div class="filter-label">🗂 Category</div>', unsafe_allow_html=True)
cat_opts = (["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
            if "Category" in df_raw.columns else ["All Categories"])
selected_cat = st.selectbox("Category", cat_opts, label_visibility="collapsed")

st.markdown('<div class="filter-label">📊 Stock Status</div>', unsafe_allow_html=True)
stock_filter = st.selectbox("Stock Status",
                             ["All", "Available Only", "Zero / Negative Stock"],
                             label_visibility="collapsed")

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

# ── Filtered result banner
is_filtered = (search or selected_wh != "All Warehouses"
               or selected_cat != "All Categories" or stock_filter != "All")
if is_filtered:
    filtered_qty = df[df["Warehouse"].isin(soh_warehouses)]["Qty Available"].sum()
    if search:
        ctx = f'"{search}"'
    elif selected_wh != "All Warehouses":
        ctx = selected_wh
    elif selected_cat != "All Categories":
        ctx = selected_cat
    else:
        ctx = stock_filter

    st.markdown(f"""
    <div class="filter-result">
        <div>
            <div class="fr-tag">Filtered · {ctx}</div>
            <div class="fr-val">{filtered_qty:,.0f}</div>
        </div>
        <div class="fr-right">
            <div class="fr-count">{len(df):,}</div>
            <div class="fr-count-label">records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------
st.markdown(f"""
<div class="tbl-row">
    <span style="font-size:11px;font-weight:600;color:#64748b;
                 text-transform:uppercase;letter-spacing:0.9px;">📋 Records</span>
    <span class="tbl-badge">{len(df):,}</span>
</div>
""", unsafe_allow_html=True)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as w:
    df.to_excel(w, index=False, sheet_name="RM")
st.download_button(
    "⬇  Export to Excel", buf.getvalue(), "RM_Inventory.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.markdown("<div style='margin-bottom:0.4rem'></div>", unsafe_allow_html=True)

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
        height=460,
        hide_index=True,
        column_config={
            "Qty Available":        st.column_config.NumberColumn("Qty Avail",  format="%.0f"),
            "Forecast":             st.column_config.NumberColumn("Forecast",   format="%.0f"),
            "Days of Stock":        st.column_config.NumberColumn("DoS",        format="%.1f"),
            "Qty Inward":           st.column_config.NumberColumn("Inward",     format="%.0f"),
            "Qty (Issue / Hold)":   st.column_config.NumberColumn("Issue/Hold", format="%.0f"),
            "Value (Inc Tax)":      st.column_config.NumberColumn("Value",      format="₹%.0f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging (d)",  format="%d"),
        }
    )

# ── Footer
st.markdown("""
<div style="margin-top:2rem;padding-top:1rem;
            border-top:1px solid rgba(255,255,255,0.06);
            text-align:center;">
    <span style="font-size:10px;color:#334155;font-family:'DM Mono',monospace;letter-spacing:0.5px;">
        SPROUTLIFE FOODS · RM INVENTORY
    </span>
</div>
""", unsafe_allow_html=True)
