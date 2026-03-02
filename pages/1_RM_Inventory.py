import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory",
    layout="wide",
    page_icon="📦"
)

# ─────────────────────────────────────────────
# LOAD EXCEL FROM ONEDRIVE (CLOUD SAFE)
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)  # refresh every 10 minutes
def load_data():

    # 🔥 PASTE YOUR ONEDRIVE DIRECT DOWNLOAD LINK BELOW
    file_url = "https://sproutlife01-my.sharepoint.com/:x:/r/personal/abinaya_m_yogabars_in/_layouts/15/Doc.aspx?sourcedoc=%7BE2429A27-4C87-4F4F-8B1E-B57704B0311C%7D&file=Sproutlife%20Inventory.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1"

    response = requests.get(file_url)

    if response.status_code != 200:
        st.error("Failed to fetch Excel file from OneDrive.")
        st.stop()

    df = pd.read_excel(BytesIO(response.content))
    df.columns = df.columns.str.strip()

    return df


df = load_data()

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

st.markdown("## 📦 RM Inventory")
st.markdown("Live raw material stock")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")
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

# KPI calculations
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
