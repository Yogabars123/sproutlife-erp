import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory", layout="wide")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .metric-card .label {
        font-size: 13px;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .metric-card .sub {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 4px;
    }
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 0 8px 0;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
    /* Mobile responsive */
    @media (max-width: 768px) {
        .metric-card .value { font-size: 22px; }
        .metric-card .label { font-size: 11px; }
        .metric-card { padding: 14px 16px; }
        [data-testid="stHorizontalBlock"] > div { min-width: 0 !important; }
    }
    /* Hide sidebar toggle on mobile for cleaner look */
    section[data-testid="stSidebar"] { min-width: 0 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")

    # --- RM Inventory ---
    df_rm = pd.read_excel(file_path, sheet_name="RM-Inventory")
    df_rm.columns = df_rm.columns.str.strip()
    df_rm["Warehouse"] = df_rm["Warehouse"].astype(str).str.strip()
    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df_rm.columns:
            df_rm[col] = pd.to_datetime(df_rm[col], errors="coerce")
    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)"]:
        if col in df_rm.columns:
            df_rm[col] = pd.to_numeric(df_rm[col], errors="coerce").fillna(0)

    # --- Forecast ---
    xl = pd.ExcelFile(file_path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "forecast"), None)
    df_fc = pd.DataFrame()
    if sheet:
        df_fc = pd.read_excel(file_path, sheet_name=sheet)
        df_fc.columns = df_fc.columns.str.strip()
        # Filter Plant only
        if "Location" in df_fc.columns:
            df_fc = df_fc[df_fc["Location"].astype(str).str.strip().str.lower() == "plant"]
        # Numeric
        if "Forecast" in df_fc.columns:
            df_fc["Forecast"] = pd.to_numeric(df_fc["Forecast"], errors="coerce").fillna(0)
            df_fc = df_fc[df_fc["Forecast"] > 0]
        # Find item code column (case-insensitive)
        item_col = next((c for c in df_fc.columns if c.lower().replace(" ","") == "itemcode"), None)
        if item_col:
            df_fc = df_fc.rename(columns={item_col: "Item code"})
            df_fc["Item code"] = df_fc["Item code"].astype(str).str.strip().str.upper()
            df_fc = df_fc[["Item code", "Forecast"]].drop_duplicates(subset="Item code")

    return df_rm, df_fc

df_raw, df_forecast = load_all()

# Allowed warehouses for display
allowed_warehouses = [
    "Central", "Central Production -Bar Line", "Central Production - Oats Line",
    "Central Production - Peanut Line", "Central Production - Muesli Line",
    "RM Warehouse Tumkur", "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM", "Tumkur Warehouse",
    "Central Production -Packing", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
df_raw = df_raw[df_raw["Warehouse"].isin(allowed_warehouses)]

# SOH warehouses for Days of Stock
soh_warehouses = [
    "Central", "RM Warehouse Tumkur", "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse", "Tumkur New Warehouse",
    "HF Factory FG Warehouse", "Sproutlife Foods Private Ltd (SNOWMAN)"
]
df_soh = df_raw[df_raw["Warehouse"].isin(soh_warehouses)].copy()
df_soh["_key"] = df_soh["Item SKU"].astype(str).str.strip().str.upper()
soh_by_sku = df_soh.groupby("_key")["Qty Available"].sum().reset_index()
soh_by_sku.columns = ["_key", "SOH"]

# Merge forecast into SOH
if not df_forecast.empty:
    soh_by_sku = soh_by_sku.merge(df_forecast, left_on="_key", right_on="Item code", how="left")
else:
    soh_by_sku["Forecast"] = 0

soh_by_sku["Forecast"] = soh_by_sku["Forecast"].fillna(0)
soh_by_sku["Days of Stock"] = soh_by_sku.apply(
    lambda r: round(r["SOH"] / (r["Forecast"] / 26), 1) if r["Forecast"] > 0 else None,
    axis=1
)

# Add _key to df_raw for merging later
df_raw["_key"] = df_raw["Item SKU"].astype(str).str.strip().str.upper()

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
    <span style="font-size:28px;">📦</span>
    <span style="font-size:24px; font-weight:700;">RM Inventory</span>
</div>
<p style="color:#888; font-size:13px; margin:0 0 8px 0;">Live view of raw material stock</p>
""", unsafe_allow_html=True)

if st.button("🔄 Refresh", use_container_width=False):
    st.cache_data.clear()
    st.rerun()

st.divider()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)
search = st.text_input("🔍 Search (Item Name / SKU / Batch)", placeholder="Type to search...")

f1, f2 = st.columns(2)
with f1:
    warehouse_options = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    selected_warehouse = st.selectbox("Warehouse", warehouse_options)
with f2:
    if "Category" in df_raw.columns:
        cat_options = ["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
        selected_category = st.selectbox("Category", cat_options)
    else:
        selected_category = "All Categories"

stock_filter = st.selectbox("Stock Status", ["All", "Available Only", "Zero / Negative Stock"])

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
df = df_raw.copy()

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
    df = df[mask]
if selected_warehouse != "All Warehouses":
    df = df[df["Warehouse"] == selected_warehouse]
if selected_category != "All Categories" and "Category" in df.columns:
    df = df[df["Category"].astype(str) == selected_category]
if stock_filter == "Available Only":
    df = df[df["Qty Available"] > 0]
elif stock_filter == "Zero / Negative Stock":
    df = df[df["Qty Available"] <= 0]

# ---------------------------------------------------
# KPI — based on filtered SKUs
# ---------------------------------------------------
st.divider()

filtered_keys = df["_key"].unique().tolist()
filtered_soh  = soh_by_sku[soh_by_sku["_key"].isin(filtered_keys)]

total_qty      = df["Qty Available"].sum()
total_forecast = filtered_soh["Forecast"].sum()
dos_valid      = filtered_soh[filtered_soh["Days of Stock"].notna()]["Days of Stock"]
avg_dos        = round(dos_valid.mean(), 1) if len(dos_valid) > 0 else 0
low_dos        = (filtered_soh["Days of Stock"] < 7).sum()

if selected_warehouse != "All Warehouses":
    card_label = f"Qty Available — {selected_warehouse}"
elif search:
    card_label = f"Qty Available — '{search}'"
elif selected_category != "All Categories":
    card_label = f"Qty Available — {selected_category}"
else:
    card_label = "Total Qty Available"

k1, _, _ = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">{card_label}</div>
        <div class="value">{total_qty:,.0f}</div>
        <div class="sub">{len(df):,} records matching filters</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# DOWNLOAD + TABLE
# ---------------------------------------------------
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.drop(columns=["_key"], errors="ignore").to_excel(writer, index=False, sheet_name="RM Inventory")
    st.download_button(
        label="⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="RM_Inventory_Filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

if df.empty:
    st.warning("No records match your current filters.")
else:
    # Merge Forecast + Days of Stock into display
    df_display = df.merge(
        soh_by_sku[["_key", "Forecast", "Days of Stock"]],
        on="_key", how="left"
    ).drop(columns=["_key"], errors="ignore")

    priority_cols = [
        "Item Name", "Item SKU", "Category", "Primary Category",
        "Warehouse", "UoM", "Qty Available", "Forecast", "Days of Stock",
        "Qty Inward", "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)",
        "Batch No", "MFG Date", "Expiry Date", "Current Aging (Days)",
        "Inventory Date", "Item Type"
    ]
    display_cols = [c for c in priority_cols if c in df_display.columns]
    display_cols += [c for c in df_display.columns if c not in display_cols]
    df_display = df_display[display_cols].copy()

    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].dt.strftime("%d-%b-%Y").fillna("")
    for col in ["Value (Inc Tax)", "Value (Ex Tax)"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"₹{x:,.2f}" if x else "")

    st.dataframe(
        df_display,
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config={
            "Qty Available":        st.column_config.NumberColumn("Qty Available", format="%.2f"),
            "Forecast":             st.column_config.NumberColumn("Forecast", format="%.0f"),
            "Days of Stock":        st.column_config.NumberColumn("Days of Stock", format="%.1f"),
            "Qty Inward":           st.column_config.NumberColumn("Qty Inward", format="%.2f"),
            "Qty (Issue / Hold)":   st.column_config.NumberColumn("Qty (Issue / Hold)", format="%.2f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging (Days)", format="%d"),
        }
    )
