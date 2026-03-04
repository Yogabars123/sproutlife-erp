python
import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="RM Inventory | ERP",
    layout="wide",
    page_icon="📦"
)

# ---------------- SIMPLE CSS ----------------
st.markdown("""
<style>

.block-container{
padding-top:0rem;
padding-bottom:0.5rem;
}

header{visibility:hidden;}
footer{visibility:hidden;}

.section-title{
font-size:18px;
font-weight:600;
margin-top:6px;
margin-bottom:8px;
}

.kpi-box{
background:linear-gradient(135deg,#1A56DB,#2563EB);
padding:16px;
border-radius:12px;
color:white;
margin-top:8px;
margin-bottom:12px;
}

.kpi-title{
font-size:13px;
}

.kpi-value{
font-size:22px;
font-weight:700;
margin-top:4px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_excel(
        "Sproutlife Inventory.xlsx",
        sheet_name="RM-Inventory"
    )
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ---------------- COLUMN NAMES ----------------
WAREHOUSE_COL = "Warehouse"
STOCK_COL = "Qty Available"
ITEM_COL = "Item code"

if WAREHOUSE_COL not in df.columns:
    st.error("Column 'Warehouse' not found")
    st.stop()

if STOCK_COL not in df.columns:
    st.error("Column 'Qty Available' not found")
    st.stop()

# ---------------- WAREHOUSES ----------------
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

# ---------------- HEADER ----------------
st.markdown('<div class="section-title">📦 Raw Material Inventory</div>', unsafe_allow_html=True)

# ---------------- FILTERS ----------------
col1,col2 = st.columns(2)

with col1:
    search_text = st.text_input("🔎 Item Code")

with col2:
    selected_wh = st.selectbox(
        "🏢 Warehouse",
        ["All Warehouses"] + main_warehouses
    )

# ---------------- FILTER LOGIC ----------------
filtered_df = df[df[WAREHOUSE_COL].isin(main_warehouses)].copy()

if selected_wh != "All Warehouses":
    filtered_df = filtered_df[filtered_df[WAREHOUSE_COL] == selected_wh]

if search_text and ITEM_COL in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df[ITEM_COL].astype(str).str.contains(search_text, case=False, na=False)
    ]

# ---------------- SORT ----------------
filtered_df = filtered_df.sort_values(STOCK_COL, ascending=False)

# ---------------- KPI ----------------
total_stock = filtered_df[STOCK_COL].sum()

st.markdown(f"""
<div class="kpi-box">
<div class="kpi-title">Total Stock</div>
<div class="kpi-value">{total_stock:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# ---------------- TABLE ----------------
st.markdown('<div class="section-title">📋 Records</div>', unsafe_allow_html=True)

st.dataframe(
filtered_df,
use_container_width=True,
hide_index=True,
height=500
)

