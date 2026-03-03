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
# CLEAN ENTERPRISE + MOBILE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #f4f6f9; }

/* KPI Card */
.kpi-box {
    background: linear-gradient(135deg, #1A56DB, #2563EB);
    padding: 24px;
    border-radius: 14px;
    color: white;
    margin-bottom: 20px;
}

.kpi-title { font-size: 16px; }
.kpi-value { font-size: 34px; font-weight: 700; }

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 15px;
}

/* MOBILE */
@media (max-width: 768px) {
    .kpi-title { font-size: 12px; }
    .kpi-value { font-size: 20px; }
    .section-title { font-size: 16px; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA (FAST)
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
ITEM_COL = "Item code"   # change if needed

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
st.markdown('<div class="section-title">📦 Raw Material Inventory Overview</div>', unsafe_allow_html=True)

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
# FAST FILTER LOGIC
# ─────────────────────────────────────────────

# Filter only main warehouses
filtered_df = df[df[WAREHOUSE_COL].isin(main_warehouses)].copy()

# Filter warehouse dropdown
if selected_wh != "All Warehouses":
    filtered_df = filtered_df[
        filtered_df[WAREHOUSE_COL] == selected_wh
    ]

# FAST SEARCH FILTER (NO APPLY)
if search_text and ITEM_COL in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df[ITEM_COL].astype(str)
        .str.contains(search_text, case=False, na=False)
    ]

# ─────────────────────────────────────────────
# KPI CALCULATION
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
st.markdown('<div class="section-title">📋 Inventory Records</div>', unsafe_allow_html=True)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)
