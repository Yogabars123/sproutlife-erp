import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# CONFIG
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
# DEFINE ALLOWED WAREHOUSES
# ─────────────────────────────────────────────
allowed_warehouses = [
    "Central",
    "RM Warehouse Tumkur",
    "Central Warehouse - Cold Storage RM",
    "Tumkur Warehouse",
    "Tumkur New Warehouse",
    "HF Factory FG Warehouse",
    "Sproutlife Foods Private Ltd (SNOWMAN)",
    "YB FG Warehouse"
]

# Filter only allowed warehouses
df = df[df["Location"].isin(allowed_warehouses)]

# ─────────────────────────────────────────────
# SIDEBAR FILTER
# ─────────────────────────────────────────────
st.sidebar.title("Sproutlife ERP")
st.sidebar.markdown("**Module:** RM Inventory")
st.sidebar.markdown("---")

selected_wh = st.sidebar.multiselect(
    "Select Warehouse",
    allowed_warehouses,
    default=allowed_warehouses
)

filtered_df = df[df["Location"].isin(selected_wh)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📦 Raw Material Inventory Overview</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI SECTION (CALCULATED ONLY FROM SELECTED WAREHOUSES)
# ─────────────────────────────────────────────
qty_column = df.columns[-1]  # assumes last column is stock

total_qty = filtered_df[qty_column].sum()
total_records = len(filtered_df)
zero_stock = len(filtered_df[filtered_df[qty_column] == 0])

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.metric("Total Stock", f"{total_qty:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.metric("Total SKUs", total_records)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.metric("Out of Stock Items", zero_stock)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>📋 Inventory Records</div>", unsafe_allow_html=True)
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
