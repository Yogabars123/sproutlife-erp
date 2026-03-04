import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="FG Inventory", layout="wide", page_icon="📦")

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
    /* Highlight active page */
    section[data-testid="stSidebar"] .stButton:nth-child(3) > button {
        background: #e0eaff;
        color: #1A56DB;
        font-weight: 700;
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
    st.page_link("Home.py",         label="🏠  Home / Overview")
    st.page_link("pages/GRN.py",    label="📥  GRN")
    st.page_link("pages/FG_Inventory.py", label="📦  FG Inventory")
    st.page_link("pages/RM_Inventory.py", label="🗄️  RM Inventory")
    st.page_link("pages/Consumption.py",  label="🏭  Consumption")
    st.page_link("pages/Forecast.py",     label="📊  Forecast")

    st.markdown("<hr style='margin:10px 0; border-color:#e2e8f0'>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">© 2025 Sproutlife Foods</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 0.8rem !important; padding-bottom: 1rem !important; }
h1, h2, h3 { margin-bottom: 0.3rem !important; }
hr { margin-top: 0.6rem !important; margin-bottom: 0.6rem !important; }

.kpi-card {
    border-radius: 14px;
    padding: 16px 18px;
    color: white;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
.kpi-title { font-size: 13px; font-weight: 600; opacity: 0.9; }
.kpi-value { font-size: 26px; font-weight: 800; margin-top: 4px; }
.kpi-sub   { font-size: 12px; opacity: 0.75; margin-top: 3px; }

.section-title {
    font-size: 13px; font-weight: 600; color: #6b7280;
    letter-spacing: 0.5px; margin: 0.5rem 0 0.4rem 0;
}
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_fg():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")

    df = pd.read_excel(file_path, sheet_name="FG-Inventory")
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()

    for col in ["Inventory Date", "Expiry Date", "MFG Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["Qty Available", "Qty Inward", "Qty (Issue / Hold)",
                "Value (Inc Tax)", "Value (Ex Tax)", "Current Aging (Days)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df_raw = load_fg()

# ─────────────────────────────────────────────
# SHELF LIFE
# ─────────────────────────────────────────────
today = pd.Timestamp(datetime.today().date())

if "Expiry Date" in df_raw.columns and "MFG Date" in df_raw.columns:
    remaining_days = (df_raw["Expiry Date"] - today).dt.days
    total_days     = (df_raw["Expiry Date"] - df_raw["MFG Date"]).dt.days
    df_raw["Remaining Shelf Life (%)"] = ((remaining_days / total_days) * 100).round(1).clip(0, 100)
    df_raw["_remaining_days"]          = remaining_days.fillna(0).astype(int)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📦 FG Inventory")
st.caption("Finished goods stock overview")
st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Search & Filter</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns([3, 2, 2])

with f1:
    search = st.text_input("Search (Item / SKU / Batch)", label_visibility="collapsed",
                           placeholder="Type to search...")

with f2:
    warehouse_options = ["All Warehouses"] + sorted(df_raw["Warehouse"].dropna().unique().tolist())
    selected_warehouse = st.selectbox("Warehouse", warehouse_options)

with f3:
    shelf_filter = st.selectbox("Shelf Life", ["All", "Expiring in 30 days", "Expired"])

df = df_raw.copy()

if search:
    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
    df = df[mask]

if selected_warehouse != "All Warehouses":
    df = df[df["Warehouse"] == selected_warehouse]

if "_remaining_days" in df.columns:
    if shelf_filter == "Expiring in 30 days":
        df = df[(df["_remaining_days"] >= 0) & (df["_remaining_days"] <= 30)]
    elif shelf_filter == "Expired":
        df = df[df["_remaining_days"] < 0]

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

total_qty     = df["Qty Available"].sum()
expiring_soon = (df["_remaining_days"] <= 30).sum() if "_remaining_days" in df.columns else 0
expired_count = (df["_remaining_days"] < 0).sum()  if "_remaining_days" in df.columns else 0

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="kpi-card" style="background:linear-gradient(135deg,#1A56DB,#2563EB);">
        <div class="kpi-title">Available Quantity</div>
        <div class="kpi-value">{total_qty:,.0f}</div>
        <div class="kpi-sub">{len(df):,} filtered records</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card" style="background:linear-gradient(135deg,#F59E0B,#FBBF24);">
        <div class="kpi-title">Expiring in 30 Days</div>
        <div class="kpi-value">{expiring_soon:,}</div>
        <div class="kpi-sub">Requires attention</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card" style="background:linear-gradient(135deg,#DC2626,#EF4444);">
        <div class="kpi-title">Expired Batches</div>
        <div class="kpi-value">{expired_count:,}</div>
        <div class="kpi-sub">Past expiry date</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">FG Records</div>', unsafe_allow_html=True)

if df.empty:
    st.warning("No records match your filters.")
else:
    st.dataframe(df, use_container_width=True, height=500, hide_index=True)
