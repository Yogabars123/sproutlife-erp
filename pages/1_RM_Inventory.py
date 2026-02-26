import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="RM Inventory", layout="wide")

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
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

df_raw = load_rm()

# ---------------------------------------------------
# ALLOWED WAREHOUSES
# ---------------------------------------------------
allowed_warehouses = [
    "Central",
    "Central Production -Bar Line",
    "Central Production - Oats Line",
    "Central Production - Peanut Line",
    "Central Production - Muesli Line",
    "RM Warehouse Tumkur",
    "Central Production -Dry Fruits Line",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Central Production -Packing",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)"
]
allowed_warehouses = [w.strip() for w in allowed_warehouses]
df_raw = df_raw[df_raw["Warehouse"].isin(allowed_warehouses)]

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("📦 RM Inventory")
st.caption("Live view of raw material stock across all warehouses")

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ---------------------------------------------------
# KPI METRICS - ONLY TOTAL QTY AVAILABLE
# ---------------------------------------------------
total_qty = df_raw["Qty Available"].sum() if "Qty Available" in df_raw.columns else 0

k1, _, _ = st.columns(3)
with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Qty Available</div>
        <div class="value">{total_qty:,.0f}</div>
        <div class="sub">Across all warehouses</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

with f1:
    search = st.text_input("Search (Item Name / SKU / Batch)", placeholder="Type to search...")

with f2:
    warehouse_options = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    selected_warehouse = st.selectbox("Warehouse", warehouse_options)

with f3:
    if "Category" in df_raw.columns:
        cat_options = ["All Categories"] + sorted(df_raw["Category"].dropna().astype(str).unique().tolist())
        selected_category = st.selectbox("Category", cat_options)
    else:
        selected_category = "All Categories"

with f4:
    stock_filter = st.selectbox("Stock Status", ["All", "Available Only", "Zero / Negative Stock"])

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
df = df_raw.copy()

if search:
    mask = df.astype(str).apply(
        lambda x: x.str.contains(search, case=False, na=False)
    ).any(axis=1)
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
# RESULTS COUNT + DOWNLOAD
# ---------------------------------------------------
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="RM Inventory")
    st.download_button(
        label="⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="RM_Inventory_Filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ---------------------------------------------------
# DISPLAY TABLE
# ---------------------------------------------------
if df.empty:
    st.warning("No records match your current filters.")
else:
    priority_cols = [
        "Item Name", "Item SKU", "Category", "Primary Category",
        "Warehouse", "UoM", "Qty Available", "Qty Inward",
        "Qty (Issue / Hold)", "Value (Inc Tax)", "Value (Ex Tax)",
        "Batch No", "MFG Date", "Expiry Date", "Current Aging (Days)",
        "Inventory Date", "Item Type"
    ]
    display_cols = [c for c in priority_cols if c in df.columns]
    remaining = [c for c in df.columns if c not in display_cols]
    display_cols += remaining

    df_display = df[display_cols].copy()

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
            "Qty Available": st.column_config.NumberColumn("Qty Available", format="%.2f"),
            "Qty Inward": st.column_config.NumberColumn("Qty Inward", format="%.2f"),
            "Qty (Issue / Hold)": st.column_config.NumberColumn("Qty (Issue / Hold)", format="%.2f"),
            "Current Aging (Days)": st.column_config.NumberColumn("Aging (Days)", format="%d"),
        }
    )
