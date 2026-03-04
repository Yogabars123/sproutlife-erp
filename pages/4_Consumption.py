import streamlit as st
import pandas as pd
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Consumption", layout="wide", page_icon="🏭")

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1A56DB, #2563EB);
        border-radius: 14px;
        padding: 18px 16px 14px 16px;
        margin-bottom: 8px;
        text-align: center;
    ">
        <div style="font-size: 28px; margin-bottom: 4px;">🌱</div>
        <div style="color: white; font-size: 16px; font-weight: 800; letter-spacing: 0.3px;">Sproutlife</div>
        <div style="color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 2px;">Inventory Management</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
        min-width: 220px !important;
        max-width: 220px !important;
    }
    .nav-label {
        font-size: 10px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        padding: 10px 4px 4px 4px;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        background: transparent;
        border: none;
        border-radius: 10px;
        padding: 9px 12px;
        font-size: 13.5px;
        font-weight: 500;
        color: #374151;
        cursor: pointer;
        transition: all 0.15s ease;
        margin-bottom: 2px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #e0eaff;
        color: #1A56DB;
    }
    .sidebar-footer {
        font-size: 11px;
        color: #94a3b8;
        text-align: center;
        padding-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Main Menu</div>', unsafe_allow_html=True)
    st.page_link("Home.py",                       label="🏠  Home / Overview")
    st.page_link("pages/GRN.py",                  label="📥  GRN")
    st.page_link("pages/FG_Inventory.py",         label="📦  FG Inventory")
    st.page_link("pages/RM_Inventory.py",         label="🗄️  RM Inventory")
    st.page_link("pages/Consumption.py",          label="🏭  Consumption")
    st.page_link("pages/Forecast.py",             label="📊  Forecast")

    st.markdown("<hr style='margin:10px 0; border-color:#e2e8f0'>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">© 2025 Sproutlife Foods</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 0.8rem !important; padding-bottom: 1rem !important; }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 10px;
    }
    .metric-card .label {
        font-size: 13px; opacity: 0.8;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
    }
    .metric-card .value { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }
    .metric-card .sub   { font-size: 12px; opacity: 0.65; margin-top: 4px; }
    .section-title {
        font-size: 14px; font-weight: 600; color: #666;
        text-transform: uppercase; letter-spacing: 1px; margin: 18px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 🏭 Consumption")
st.caption("Material consumption and batch production overview")
st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Search & Filter</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

with f1:
    search = st.text_input("Search", label_visibility="collapsed",
                           placeholder="Search product / material / batch...")

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
        months = ["All Months"] + sorted(df["Batch Date"].dropna().dt.strftime("%b-%Y").unique().tolist())
        selected_month = st.selectbox("Month", months)
    else:
        selected_month = "All Months"

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

if selected_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == selected_wh]

if selected_cat != "All Categories" and "Category Name" in df.columns:
    df = df[df["Category Name"].astype(str) == selected_cat]

if selected_month != "All Months" and "Batch Date" in df.columns:
    df = df[df["Batch Date"].dt.strftime("%b-%Y") == selected_month]

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
total_consumed   = df["Consumed (As per BOM)"].sum() if "Consumed (As per BOM)" in df.columns else 0
total_produced   = df["Total Produced Qty"].sum()    if "Total Produced Qty" in df.columns else 0
total_batch_qty  = df["Batch Qty"].sum()             if "Batch Qty" in df.columns else 0
total_wastage    = df["Damage/Wastage"].sum()        if "Damage/Wastage" in df.columns else 0
unique_products  = df["Product Name"].nunique()      if "Product Name" in df.columns else 0
unique_materials = df["Material Name"].nunique()     if "Material Name" in df.columns else 0

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

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
st.dataframe(df, use_container_width=True, hide_index=True)
