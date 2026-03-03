import streamlit as st
import pandas as pd

# PAGE CONFIG
st.set_page_config(
    page_title="RM Inventory | ERP",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL ERP CSS
st.markdown("""
<style>

/* Reduce top spacing */
.block-container {
    padding-top: 0.5rem !important;
}

/* Professional background */
body {
    background-color: #f4f6f9;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #1f2937;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Header */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
}

/* KPI Card */
.kpi-box {
    background: linear-gradient(135deg, #1A56DB, #2563EB);
    padding: 20px;
    border-radius: 14px;
    color: white;
    margin-bottom: 15px;
}

.kpi-title {
    font-size: 14px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
}

/* Mobile optimization */
@media (max-width: 768px) {
    .kpi-title { font-size: 12px; }
    .kpi-value { font-size: 20px; }
    .section-title { font-size: 16px; }
}

</style>
""", unsafe_allow_html=True)

# LOAD DATA
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_excel(
        "Sproutlife Inventory.xlsx",
        sheet_name="RM-Inventory"
    )
    df.columns = df.columns.str.strip()
    return df

df = load_data()

WAREHOUSE_COL = "Warehouse"
STOCK_COL = "Qty Available"
ITEM_COL = "Item code"

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

# ───────── SIDEBAR FILTERS (Professional ERP Style)
st.sidebar.title("📊 Filters")

search_text = st.sidebar.text_input("🔎 Item Code")
selected_wh = st.sidebar.selectbox(
    "🏢 Warehouse",
    ["All Warehouses"] + main_warehouses
)

# MAIN HEADER
st.markdown(
    '<div class="section-title">📦 Raw Material Inventory</div>',
    unsafe_allow_html=True
)

# FILTER LOGIC
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

# KPI
total_stock = filtered_df[STOCK_COL].sum()

st.markdown(f"""
<div class="kpi-box">
    <div class="kpi-title">Total Stock Available</div>
    <div class="kpi-value">{total_stock:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# TABLE
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)
