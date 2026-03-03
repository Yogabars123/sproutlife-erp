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
# ENTERPRISE STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #f4f6f9; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

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
# DEFINE MAIN WAREHOUSES FOR KPI
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

# Detect warehouse column
warehouse_col = None
for col in df.columns:
    if "location" in col.lower() or "warehouse" in col.lower():
        warehouse_col = col
        break

if warehouse_col is None:
    st.error("Warehouse column not found in Excel.")
    st.stop()

# Detect stock column (last numeric column)
stock_col = df.select_dtypes(include="number").columns[-1]

# ─────────────────────────────────────────────
# KPI CALCULATION (ONLY MAIN WAREHOUSES)
# ─────────────────────────────────────────────
kpi_df = df[df[warehouse_col].isin(main_warehouses)]
total_stock = kpi_df[stock_col].sum()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📦 Raw Material Inventory Overview</div>", unsafe_allow_html=True)

# KPI CARD
st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
st.metric("Total Stock Available (Main Warehouses)", f"{total_stock:,.0f}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTER SECTION
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>🔎 Search & Filter</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input("Search Item / SKU")

with col2:
    selected_wh = st.selectbox(
        "Select Warehouse",
        ["All Warehouses"] + main_warehouses
    )

filtered_df = df.copy()

# Apply warehouse filter
if selected_wh != "All Warehouses":
    filtered_df = filtered_df[filtered_df[warehouse_col] == selected_wh]

# Apply search filter
if search_text:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search_text, case=False).any(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# DATA TABLE
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📋 Inventory Records</div>", unsafe_allow_html=True)
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
