import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦"
)

mobile_mode = st.toggle("📱 Mobile View", value=False)

# ─────────────────────────────────────────────
# LOAD YOUR REAL DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    file_path = "Inventory Data1.xlsx"  # 🔥 CHANGE THIS
    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df

df = load_data()

# ─────────────────────────────────────────────
# SEARCH & FILTER
# ─────────────────────────────────────────────
st.markdown("### 🔎 Search & Filter")

if mobile_mode:
    search = st.text_input("", placeholder="Search item, SKU, batch...")
    warehouse = st.selectbox("Warehouse",
                             ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique()))
    stock_status = st.selectbox("Stock Status",
                                ["All", "In Stock", "Low Stock", "Out of Stock"])
else:
    c1, c2, c3 = st.columns([3,2,2])
    with c1:
        search = st.text_input("", placeholder="Search item, SKU, batch...")
    with c2:
        warehouse = st.selectbox("Warehouse",
                                 ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique()))
    with c3:
        stock_status = st.selectbox("Stock Status",
                                    ["All", "In Stock", "Low Stock", "Out of Stock"])

filtered_df = df.copy()

# 🔥 SMART SEARCH (ALL COLUMNS SAFE)
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

# Stock status filter (CHANGE column name if needed)
if stock_status == "In Stock":
    filtered_df = filtered_df[filtered_df["Stock"] > 0]
elif stock_status == "Out of Stock":
    filtered_df = filtered_df[filtered_df["Stock"] == 0]
elif stock_status == "Low Stock":
    filtered_df = filtered_df[(filtered_df["Stock"] > 0) & (filtered_df["Stock"] < 500)]

# ─────────────────────────────────────────────
# KPI BASED ON FILTERED DATA
# ─────────────────────────────────────────────
total_qty = filtered_df["Stock"].sum()
total_records = len(filtered_df)
in_stock = len(filtered_df[filtered_df["Stock"] > 0])
low_or_out = len(filtered_df[filtered_df["Stock"] <= 500])

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total QTY Available", f"{total_qty:,.0f}", f"{total_records} records")

with c2:
    st.metric("Items In Stock", f"{in_stock}")

with c3:
    st.metric("Low / Out of Stock", f"{low_or_out}")

st.markdown("---")
st.markdown("### 📋 Inventory Records")

if filtered_df.empty:
    st.warning("No records found.")
else:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
