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
# RESPONSIVE ENTERPRISE CSS (Smaller Mobile Fonts)
# ─────────────────────────────────────────────
st.markdown("""
<style>

body {
    background-color: #f4f6f9;
}

/* Desktop */
.kpi-box {
    background: linear-gradient(135deg, #1A56DB, #2563EB);
    padding: 30px;
    border-radius: 16px;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.kpi-title {
    font-size: 18px;
    font-weight: 500;
}

.kpi-value {
    font-size: 38px;
    font-weight: 700;
    margin-top: 8px;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
}

/* 📱 MOBILE OPTIMIZED */
@media (max-width: 768px) {

    .main .block-container {
        padding: 0.8rem 0.8rem;
    }

    .kpi-box {
        padding: 16px;
        border-radius: 12px;
    }

    .kpi-title {
        font-size: 12px;
    }

    .kpi-value {
        font-size: 20px;
    }

    .section-title {
        font-size: 16px;
    }

    .stTextInput input {
        font-size: 13px !important;
    }

    .stSelectbox div {
        font-size: 13px !important;
    }

    .stDataFrame {
        font-size: 12px !important;
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
# FILTER SECTION
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input("🔎 Search Item / SKU")

with col2:
    selected_wh = st.selectbox(
        "🏢 Select Warehouse",
        ["All Warehouses"] + main_warehouses
    )

# ─────────────────────────────────────────────
# FILTER LOGIC
# ─────────────────────────────────────────────
filtered_df = df[df[WAREHOUSE_COL].isin(main_warehouses)]

if selected_wh != "All Warehouses":
    filtered_df = filtered_df[filtered_df[WAREHOUSE_COL] == selected_wh]

if search_text:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str)
            .str.contains(search_text, case=False)
            .any(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# KPI CALCULATION (Dynamic)
# ─────────────────────────────────────────────
total_stock = filtered_df[STOCK_COL].sum()

st.markdown(
    f"""
    <div class="kpi-box">
        <div class="kpi-title">Total Stock Available</div>
        <div class="kpi-value">{total_stock:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True
)

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
