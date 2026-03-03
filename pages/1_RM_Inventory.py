import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RM Inventory Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# POWER BI WEB STYLE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
body {
    background-color: #f3f2f1;
}
.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e1dfdd;
}
.dashboard-title {
    font-size: 24px;
    font-weight: 600;
    color: #323130;
}
.dashboard-subtitle {
    font-size: 14px;
    color: #605e5c;
    margin-bottom: 20px;
}
.kpi-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border-left: 5px solid #0078D4;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.kpi-label {
    font-size: 13px;
    color: #605e5c;
}
.kpi-number {
    font-size: 24px;
    font-weight: 600;
    color: #323130;
}
.section-title {
    font-size: 16px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #323130;
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

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.markdown("### Filters")

search_text = st.sidebar.text_input("Search Item Code")

selected_wh = st.sidebar.selectbox(
    "Select Warehouse",
    ["All Warehouses"] + main_warehouses
)

low_stock_threshold = st.sidebar.number_input(
    "Low Stock Threshold",
    min_value=0,
    value=100
)

# ─────────────────────────────────────────────
# FILTER LOGIC
# ─────────────────────────────────────────────
filtered_df = df[df[WAREHOUSE_COL].isin(main_warehouses)].copy()

if selected_wh != "All Warehouses":
    filtered_df = filtered_df[
        filtered_df[WAREHOUSE_COL] == selected_wh
    ]

if search_text:
    filtered_df = filtered_df[
        filtered_df[ITEM_COL].astype(str)
        .str.contains(search_text, case=False, na=False)
    ]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="dashboard-title">Raw Material Inventory Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Enterprise Warehouse Monitoring System</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_stock = filtered_df[STOCK_COL].sum()
total_skus = filtered_df[ITEM_COL].nunique()
warehouse_count = filtered_df[WAREHOUSE_COL].nunique()
low_stock_items = filtered_df[filtered_df[STOCK_COL] <= low_stock_threshold].shape[0]

# ─────────────────────────────────────────────
# KPI ROW (Like Power BI)
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Stock</div>
        <div class="kpi-number">{total_stock:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total SKUs</div>
        <div class="kpi-number">{total_skus}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Warehouses Covered</div>
        <div class="kpi-number">{warehouse_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Low Stock Items</div>
        <div class="kpi-number">{low_stock_items}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# WAREHOUSE STOCK CHART
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Warehouse Stock Distribution</div>', unsafe_allow_html=True)

warehouse_summary = (
    filtered_df
    .groupby(WAREHOUSE_COL)[STOCK_COL]
    .sum()
    .reset_index()
)

fig = px.bar(
    warehouse_summary,
    x=WAREHOUSE_COL,
    y=STOCK_COL,
    title=None
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# LOW STOCK ALERT TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Low Stock Items</div>', unsafe_allow_html=True)

low_stock_df = filtered_df[
    filtered_df[STOCK_COL] <= low_stock_threshold
]

st.dataframe(
    low_stock_df,
    use_container_width=True,
    hide_index=True
)

# ─────────────────────────────────────────────
# FULL DATA TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Inventory Details</div>', unsafe_allow_html=True)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)
