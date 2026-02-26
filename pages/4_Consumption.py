import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Consumption", layout="wide")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .metric-card .label {
        font-size: 13px;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .metric-card .sub {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 4px;
    }
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Consumption")

@st.cache_data
def load_consumption():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="Consumption")
    df.columns = df.columns.str.strip()
    for col in ["Batch Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["Batch Qty", "Damage/Wastage", "Total Produced Qty", "Consumed (As per BOM)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df = load_consumption()

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------
f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

with f1:
    search = st.text_input("Search (Product / Material / Batch)")

with f2:
    if "Warehouse" in df.columns:
        wh_options = ["All Warehouses"] + sorted(df["Warehouse"].dropna().astype(str).unique().tolist())
        selected_wh = st.selectbox("Warehouse", wh_options)
    else:
        selected_wh = "All Warehouses"

with f3:
    if "Category Name" in df.columns:
        cat_options = ["All Categories"] + sorted(df["Category Name"].dropna().astype(str).unique().tolist())
        selected_cat = st.selectbox("Category", cat_options)
    else:
        selected_cat = "All Categories"

with f4:
    if "Batch Date" in df.columns:
        months = ["All Months"] + sorted(
            df["Batch Date"].dropna().dt.strftime("%b-%Y").unique().tolist()
        )
        selected_month = st.selectbox("Month", months)
    else:
        selected_month = "All Months"

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

if selected_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == selected_wh]

if selected_cat != "All Categories" and "Category Name" in df.columns:
    df = df[df["Category Name"].astype(str) == selected_cat]

if selected_month != "All Months" and "Batch Date" in df.columns:
    df = df[df["Batch Date"].dt.strftime("%b-%Y") == selected_month]

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
st.divider()

total_consumed   = df["Consumed (As per BOM)"].sum() if "Consumed (As per BOM)" in df.columns else 0
total_produced   = df["Total Produced Qty"].sum() if "Total Produced Qty" in df.columns else 0
total_batch_qty  = df["Batch Qty"].sum() if "Batch Qty" in df.columns else 0
total_wastage    = df["Damage/Wastage"].sum() if "Damage/Wastage" in df.columns else 0
unique_products  = df["Product Name"].nunique() if "Product Name" in df.columns else 0
unique_materials = df["Material Name"].nunique() if "Material Name" in df.columns else 0

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Consumption</div>
        <div class="value">{total_consumed:,.0f}</div>
        <div class="sub">{unique_materials:,} unique materials</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #1a5c38 0%, #27855a 100%);">
        <div class="label">Total Produced Qty</div>
        <div class="value">{total_produced:,.0f}</div>
        <div class="sub">{unique_products:,} unique products</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4a2070 0%, #6d35a0 100%);">
        <div class="label">Total Batch Qty</div>
        <div class="value">{total_batch_qty:,.0f}</div>
        <div class="sub">Across all batches</div>
    </div>""", unsafe_allow_html=True)

st.divider()
st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
st.dataframe(df, use_container_width=True, hide_index=True)
