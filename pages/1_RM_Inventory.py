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
# CLEAN CSS (NO EXTRA TOP SPACE)
# ─────────────────────────────────────────────
st.markdown("""
<style>

/* Remove default Streamlit padding */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
}

/* Remove top margin */
.css-18e3th9 {
    padding-top: 0rem !important;
}

/* Background */
body {
    background-color: #f4f6f9;
}

/* Header */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 5px;
    margin-bottom: 10px;
}

/* KPI Card */
.kpi-box {
    background: linear-gradient(135deg, #1A56DB, #2563EB);
    padding: 22px;
    border-radius: 14px;
    color: white;
    margin-top: 10px;
    margin-bottom: 15px;
}

.kpi-title {
    font-size: 15px;
}

.kpi-value {
    font-size: 32px;
    font-weight: 700;
}

/* MOBILE OPTIMIZATION */
@media (max-width: 768px) {

    .block-container {
        padding-top: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .section-title {
        font-size: 16px;
        margin-top: 2px;
    }

    .kpi-title {
        font-size: 12px;
    }

    .kpi-value {
        font-size: 20px;
    }
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
# REQUIRED COLUMNS
# ─────────────────────────────────────────────
WAREHOUSE_COL = "Warehouse"
STOCK_COL = "Qty Available"
ITEM_COL = "Item code"

if WAREHOUSE_COL not in df.columns:
    st.error("Column 'Warehouse' not found.")
    st.stop()

if STOCK_COL not in df.columns:
    st.error("Column 'Qty Available' not found.")
    st.stop()

# ─────────────────────────────────────────────
# MAIN WAREHOUSES
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
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="section-title">📦 Raw Material Inventory Overview</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input("🔎 Search Item Code")

with col2:
    selected_wh = st.selectbox(
        "🏢 Select Warehouse",
        ["All Warehouses"] + main_warehouses
    )

# ─────────────────────────────────────────────
# FILTER LOGIC
# ─────────────────────────────────────────────
filtered_df = df[df[WAREHOUSE_COL].isin(main_warehouses)].copy()

if selected_wh != "All Warehouses":
    filtered_df = filtered_df[
        filtered_df[WAREHOUSE_COL] == selected_wh
    ]

if search_text and ITEM_COL in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df[ITEM_COL].astype(str)
        .str.contains(search_text, case=False, na=False)
    ]

# ─────────────────────────────────────────────
# KPI
# ─────────────────────────────────────────────
total_stock = filtered_df[STOCK_COL].sum()

st.markdown(f"""
<div class="kpi-box">
    <div class="kpi-title">Total Stock Available</div>
    <div class="kpi-value">{total_stock:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown(
    '<div class="section-title">📋 Inventory Records</div>',
    unsafe_allow_html=True
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)
