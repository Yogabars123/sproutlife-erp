import streamlit as st
import pandas as pd

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

# ── 2. GLOBAL STYLES ─────────────────────────────────────────────────────────
from style import apply_global_styles, stat_card, page_header, section_label
apply_global_styles()

# ── 3. PAGE HEADER ───────────────────────────────────────────────────────────
page_header("📥", "GRN Data", "Goods Receipt Note tracking & analysis")

# ── 4. FILTERS ───────────────────────────────────────────────────────────────
section_label("Search & Filter")

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    search_grn = st.text_input("", placeholder="🔍  Search GRN…", label_visibility="collapsed")
with col2:
    po_number = st.selectbox("PO Number", ["All POs"], label_visibility="visible")
with col3:
    vendor = st.selectbox("Vendor", ["All Vendors"], label_visibility="visible")
with col4:
    warehouse = st.selectbox("Warehouse", ["All Warehouses"], label_visibility="visible")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── 5. KPI STAT CARDS ────────────────────────────────────────────────────────
# Replace values with your actual computed totals
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(stat_card("Total QTY Ordered", "304,726,587", "12,918 GRNs", "#1A56DB", "📋"), unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Total QTY Received", "135,393,246", "Against ordered qty", "#16A34A", "✅"), unsafe_allow_html=True)
with c3:
    st.markdown(stat_card("Pending QTY", "169,333,341", "Yet to be received", "#B45309", "⏳"), unsafe_allow_html=True)
with c4:
    st.markdown(stat_card("Total QTY Rejected", "31,429", "Rejection across GRNs", "#DC2626", "❌"), unsafe_allow_html=True)

st.markdown("---")

# ── 6. DATA TABLE ─────────────────────────────────────────────────────────────
section_label("GRN Records")

# ---- REPLACE THIS BLOCK with your actual data loading logic ----
# Example:
# df = load_grn_data()
# filtered = apply_filters(df, search_grn, po_number, vendor, warehouse)
# st.dataframe(filtered, use_container_width=True, hide_index=True)

st.info("Connect your GRN data source here — the styling will apply automatically.", icon="ℹ️")
