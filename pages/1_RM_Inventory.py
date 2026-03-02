import streamlit as st
import pandas as pd
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦"
)

# ─────────────────────────────────────────────
# LOAD EXCEL FROM PROJECT ROOT (WORKS IN ONEDRIVE)
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():

    # Get current file location (inside pages folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Move one level up (project root)
    project_root = os.path.dirname(base_dir)

    file_path = os.path.join(project_root, "Inventory Data1.xlsx")

    if not os.path.exists(file_path):
        st.error(f"Excel file not found at: {file_path}")
        st.stop()

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    return df


df = load_data()

# ─────────────────────────────────────────────
# MOBILE MODE
# ─────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📦 RM Inventory")
st.markdown("Live raw material stock")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# SEARCH & FILTER
# ─────────────────────────────────────────────
st.markdown("### 🔎 Search & Filter")

if mobile_mode:
    search = st.text_input("Search item, SKU, batch...")
    warehouse = st.selectbox(
        "Warehouse",
        ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique().tolist())
    )
    stock_status = st.selectbox(
        "Stock Status",
        ["All", "In Stock", "Low Stock", "Out of Stock"]
    )
else:
    c1, c2, c3 = st.columns([3,2,2])
    with c1:
        search = st.text_input("Search item, SKU, batch...")
    with c2:
        warehouse = st.selectbox(
            "Warehouse",
            ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique().tolist())
        )
    with c3:
        stock_status = st.selectbox(
            "Stock Status",
            ["All", "In Stock", "Low Stock", "Out of Stock"]
        )

# ─────────────────────────────────────────────
# APPLY FILTERS SAFELY
# ─────────────────────────────────────────────
filtered_df = df.copy()

# Search across all columns
if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

# Warehouse filter
if warehouse != "All Warehouses":
    filtered_df = filtered_df[filtered_df["Warehouse"] == warehouse]

# Stock status filter
if stock_status == "In Stock":
    filtered_df = filtered_df[filtered_df["Stock"] > 0]

elif stock_status == "Out of Stock":
    filtered_df = filtered_df[filtered_df["Stock"] == 0]

elif stock_status == "Low Stock":
    filtered_df = filtered_df[
        (filtered_df["Stock"] > 0) &
        (filtered_df["Stock"] < 500)
    ]

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_qty = filtered_df["Stock"].sum()
total_records = len(filtered_df)
in_stock = len(filtered_df[filtered_df["Stock"] > 0])
low_or_out = len(filtered_df[filtered_df["Stock"] <= 500])

# ─────────────────────────────────────────────
# KPI DISPLAY
# ─────────────────────────────────────────────
st.markdown("### 📊 Summary")

if mobile_mode:
    st.metric("Total Qty Available", f"{total_qty:,.0f}")
    st.metric("Items In Stock", in_stock)
    st.metric("Low / Out of Stock", low_or_out)
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Qty Available", f"{total_qty:,.0f}", f"{total_records} records")
    with c2:
        st.metric("Items In Stock", in_stock)
    with c3:
        st.metric("Low / Out of Stock", low_or_out)

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Inventory Records")

if filtered_df.empty:
    st.warning("No records found.")
else:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
