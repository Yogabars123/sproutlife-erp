import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory | ERP",
    layout="wide",
    page_icon="📦"
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_excel(
        "Sproutlife Inventory.xlsx",
        sheet_name="RM-Inventory"
    )
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ─────────────────────────────────────────────
# REQUIRED COLUMNS
# ─────────────────────────────────────────────
WAREHOUSE_COL = "Warehouse"

# Try to detect stock column properly
possible_stock_cols = ["Current Stock", "Stock", "Available Qty", "Quantity"]

stock_col = None
for col in possible_stock_cols:
    if col in df.columns:
        stock_col = col
        break

# If not found, take last numeric column
if stock_col is None:
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) == 0:
        st.error("No stock column found.")
        st.stop()
    stock_col = numeric_cols[-1]

# Validate warehouse column
if WAREHOUSE_COL not in df.columns:
    st.error("Column 'Warehouse' not found.")
    st.write("Available columns:", df.columns)
    st.stop()

# ─────────────────────────────────────────────
# MAIN WAREHOUSES (FOR KPI)
# ─────────────────────────────────────────────
main_warehouses = [
    "Central",
    "RM Warehouse Tumkur",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)",
    "YB FG Warehouse"
]

# ─────────────────────────────────────────────
# KPI CALCULATION (STRICT FILTER)
# ─────────────────────────────────────────────
kpi_df = df[df[WAREHOUSE_COL].isin(main_warehouses)]

total_stock = kpi_df[stock_col].sum()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📦 Raw Material Inventory Overview")

# KPI DISPLAY
st.metric("Total Stock Available (Main Warehouses)", f"{total_stock:,.0f}")

st.markdown("---")

# ─────────────────────────────────────────────
# SEARCH + FILTER
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input("🔎 Search Item / SKU")

with col2:
    selected_wh = st.selectbox(
        "🏢 Select Warehouse",
        ["All Warehouses"] + main_warehouses
    )

filtered_df = df.copy()

# Warehouse filter
if selected_wh != "All Warehouses":
    filtered_df = filtered_df[filtered_df[WAREHOUSE_COL] == selected_wh]

# Search filter
if search_text:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search_text, case=False).any(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown("### 📋 Inventory Records")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
