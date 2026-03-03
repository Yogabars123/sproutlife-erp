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
# ENTERPRISE STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #f4f6f9; }

.kpi-box {
    background: linear-gradient(135deg, #1A56DB, #2563EB);
    padding: 25px;
    border-radius: 16px;
    color: white;
    font-size: 22px;
    font-weight: 600;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

.kpi-value {
    font-size: 40px;
    font-weight: 700;
    margin-top: 10px;
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

WAREHOUSE_COL = "Warehouse"
STOCK_COL = "Qty Available"

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
# FILTER SECTION
# ─────────────────────────────────────────────
st.markdown("## 📦 Raw Material Inventory Overview")

col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input("🔎 Search Item / SKU")

with col2:
    selected_wh = st.selectbox(
        "🏢 Select Warehouse",
        ["All Warehouses"] + main_warehouses
    )

# Apply base warehouse restriction (only main warehouses allowed)
filtered_df = df[df[WAREHOUSE_COL].isin(main_warehouses)]

# Apply warehouse dropdown filter
if selected_wh != "All Warehouses":
    filtered_df = filtered_df[filtered_df[WAREHOUSE_COL] == selected_wh]

# Apply search filter
if search_text:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search_text, case=False).any(),
            axis=1
        )
    ]

# ─────────────────────────────────────────────
# KPI CALCULATION (AFTER FILTERING)
# ─────────────────────────────────────────────
total_stock = filtered_df[STOCK_COL].sum()

st.markdown(
    f"""
    <div class="kpi-box">
        Total Stock Available
        <div class="kpi-value">{total_stock:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown("### 📋 Inventory Records")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
