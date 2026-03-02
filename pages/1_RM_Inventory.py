import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦"
)

# ─────────────────────────────────────────────
# LOAD YOUR EXACT ONEDRIVE FILE
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():

    file_path = r"C:\Users\YOGA BAR\OneDrive - SPROUTLIFE FOODS PRIVATE LIMITED\Sproutlife Inventory.xlsx"

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    return df


df = load_data()

# ─────────────────────────────────────────────
# MOBILE MODE
# ─────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

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
    col1, col2, col3 = st.columns([3,2,2])
    with col1:
        search = st.text_input("Search item, SKU, batch...")
    with col2:
        warehouse = st.selectbox(
            "Warehouse",
            ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique().tolist())
        )
    with col3:
        stock_status = st.selectbox(
            "Stock Status",
            ["All", "In Stock", "Low Stock", "Out of Stock"]
        )

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

# Stock filter
if stock_status == "In Stock":
    filtered_df = filtered_df[filtered_df["Stock"] > 0]
elif stock_status == "Out of Stock":
    filtered_df = filtered_df[filtered_df["Stock"] == 0]
elif stock_status == "Low Stock":
    filtered_df = filtered_df[
        (filtered_df["Stock"] > 0) &
        (filtered_df["Stock"] < 500)
    ]

# KPIs
total_qty = filtered_df["Stock"].sum()
total_records = len(filtered_df)
in_stock = len(filtered_df[filtered_df["Stock"] > 0])
low_or_out = len(filtered_df[filtered_df["Stock"] <= 500])

st.markdown("### 📊 Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total Qty Available", f"{total_qty:,.0f}", f"{total_records} records")

with c2:
    st.metric("Items In Stock", in_stock)

with c3:
    st.metric("Low / Out of Stock", low_or_out)

st.markdown("---")
st.markdown("### 📋 Inventory Records")

if filtered_df.empty:
    st.warning("No records found.")
else:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
