import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(
    page_title="RM Inventory", layout="wide", page_icon="📦"
)

@st.cache_data(ttl=600)
def load_data():

    # Direct download link from SharePoint OneDrive
    file_url = "https://sproutlife01-my.sharepoint.com/:x:/g/personal/abinaya_m_yogabars_in/IQAnmkLih0xPT4setXcEsDEcAZCzWYYszE5oEFkQJrh_VZM?download=1"

    response = requests.get(file_url)

    # If the server returns something other than the file
    if response.status_code != 200:
        st.error("Unable to download file — check link & share permissions.")
        st.stop()

    try:
        df = pd.read_excel(BytesIO(response.content))
    except Exception as e:
        st.error("Downloaded file could not be read as Excel.")
        st.error(str(e))
        st.stop()

    df.columns = df.columns.str.strip()
    return df

# Load the spreadsheet
df = load_data()

# UI
mobile_mode = st.toggle("📱 Mobile View", value=False)

st.markdown("## 📦 RM Inventory")
st.markdown("Live raw material stock")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")
st.markdown("### 🔎 Search & Filter")

# Filters
if mobile_mode:
    search = st.text_input("Search item, SKU, batch…")
    warehouse = st.selectbox("Warehouse", ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique().tolist()))
    stock_status = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"])
else:
    c1, c2, c3 = st.columns([3,2,2])
    with c1:
        search = st.text_input("Search item, SKU, batch…")
    with c2:
        warehouse = st.selectbox("Warehouse", ["All Warehouses"] + sorted(df["Warehouse"].dropna().unique().tolist()))
    with c3:
        stock_status = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"])

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
