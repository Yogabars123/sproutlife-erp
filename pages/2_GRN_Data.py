import streamlit as st
import pandas as pd

st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Sproutlife Inventory.xlsx", sheet_name="GRN-Data")
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Excel Load Error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# CLEAN NUMERIC COLUMNS
# ─────────────────────────────────────────────
numeric_cols = [
    "QuantityOrdered",
    "QuantityReceived",
    "QuantityRejected"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ─────────────────────────────────────────────
# FILTER SECTION
# ─────────────────────────────────────────────
st.markdown("### SEARCH & FILTER")

col1, col2, col3, col4 = st.columns([3,2,2,2])

with col1:
    search_grn = st.text_input("Search GRN")

with col2:
    po_options = ["All POs"] + sorted(df["PO No"].dropna().astype(str).unique().tolist())
    po_number = st.selectbox("PO No", po_options)

with col3:
    vendor_options = ["All Vendors"] + sorted(df["Vendor Name"].dropna().astype(str).unique().tolist())
    vendor = st.selectbox("Vendor", vendor_options)

with col4:
    warehouse_options = ["All Warehouses"] + sorted(df["Warehouse"].dropna().astype(str).unique().tolist())
    warehouse = st.selectbox("Warehouse", warehouse_options)

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
filtered_df = df.copy()

if search_grn:
    filtered_df = filtered_df[
        filtered_df["GRN No"].astype(str)
        .str.contains(search_grn, case=False, na=False)
    ]

if po_number != "All POs":
    filtered_df = filtered_df[filtered_df["PO No"].astype(str) == po_number]

if vendor != "All Vendors":
    filtered_df = filtered_df[filtered_df["Vendor Name"].astype(str) == vendor]

if warehouse != "All Warehouses":
    filtered_df = filtered_df[filtered_df["Warehouse"].astype(str) == warehouse]

# ─────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────
total_ordered = filtered_df["QuantityOrdered"].sum()
total_received = filtered_df["QuantityReceived"].sum()
total_rejected = filtered_df["QuantityRejected"].sum()
pending_qty = total_ordered - total_received

# ─────────────────────────────────────────────
# KPI DISPLAY
# ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Ordered", f"{total_ordered:,.0f}")
c2.metric("Total Received", f"{total_received:,.0f}")
c3.metric("Pending Qty", f"{pending_qty:,.0f}")
c4.metric("Total Rejected", f"{total_rejected:,.0f}")

st.markdown("---")
st.markdown("### GRN Records")

# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
