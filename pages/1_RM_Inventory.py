import streamlit as st
import pandas as pd
import os
import io

# ── 1. PAGE CONFIG (must be first) ──────────────────────────────────────────
st.set_page_config(page_title="RM Inventory", layout="wide", page_icon="📦")

# ── 2. APPLY GLOBAL STYLES ───────────────────────────────────────────────────
from style import apply_global_styles, stat_card, page_header, section_label
apply_global_styles()

# ── 3. MOBILE TOGGLE ─────────────────────────────────────────────────────────
mobile_mode = st.toggle("📱 Mobile View", value=False)

# ── 4. PAGE HEADER ───────────────────────────────────────────────────────────
page_header("📦", "RM Inventory", "Live raw material stock")

# ── 5. REFRESH BUTTON ────────────────────────────────────────────────────────
if st.button("🔄  Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── 6. FILTERS ───────────────────────────────────────────────────────────────
section_label("Search & Filter")

col_search, col_wh, col_status = st.columns([3, 2, 2])
with col_search:
    search = st.text_input("", placeholder="🔍  Search item name, SKU or batch…", label_visibility="collapsed")
with col_wh:
    warehouse = st.selectbox("Warehouse", ["All Warehouses"], label_visibility="visible")
with col_status:
    stock_status = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"], label_visibility="visible")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── 7. KPI CARDS ─────────────────────────────────────────────────────────────
# Replace the values below with your actual computed totals
total_qty    = "16,300,788"
total_records = "2,414 records"

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(stat_card("Total QTY Available", total_qty, total_records, "#1A56DB", "📦"), unsafe_allow_html=True)
with kpi2:
    st.markdown(stat_card("Items In Stock", "1,892", "78.3% of catalogue", "#16A34A", "✅"), unsafe_allow_html=True)
with kpi3:
    st.markdown(stat_card("Low / Out of Stock", "522", "Need attention", "#DC2626", "⚠️"), unsafe_allow_html=True)

st.markdown("---")

# ── 8. DATA TABLE ─────────────────────────────────────────────────────────────
section_label("Inventory Records")

# ---- REPLACE THIS BLOCK with your actual data loading logic ----
# Example placeholder:
# df = load_your_data()
# filtered_df = df[df['item_name'].str.contains(search, case=False, na=False)]
# st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.info("Connect your data source here — the styling will apply automatically to the dataframe.", icon="ℹ️")
