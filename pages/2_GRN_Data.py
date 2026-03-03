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

df = load_data()

# Convert numeric columns
numeric_cols = ["QuantityOrdered", "QuantityReceived", "QuantityRejected"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ─────────────────────────────────────────────
# FILTER SECTION
# ─────────────────────────────────────────────
st.markdown("### SEARCH & FILTER")

col1, col2, col3, col4 = st.columns([3,2,2,2])

with col1:
    search_text = st.text_input("Search (GRN / Item Code / Item Name / PO No)")

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
# APPLY NORMAL FILTERS (FOR TABLE)
# ─────────────────────────────────────────────
filtered_df = df.copy()

# Search filter
if search_text:
    search_text = search_text.lower()
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row:
                search_text in str(row["GRN No"]).lower()
                or search_text in str(row["Item Code"]).lower()
                or search_text in str(row["Item Name"]).lower()
                or search_text in str(row["PO No"]).lower(),
            axis=1
        )
    ]

if po_number != "All POs":
    filtered_df = filtered_df[filtered_df["PO No"].astype(str) == po_number]

if vendor != "All Vendors":
    filtered_df = filtered_df[filtered_df["Vendor Name"].astype(str) == vendor]

if warehouse != "All Warehouses":
    filtered_df = filtered_df[filtered_df["Warehouse"].astype(str) == warehouse]

# ─────────────────────────────────────────────
# KPI LOGIC (SPECIAL CONDITION)
# Only:
#   - Warehouse = Central
#   - PO No not blank and not "-"
# ─────────────────────────────────────────────
kpi_df = df.copy()

kpi_df = kpi_df[
    (kpi_df["Warehouse"] == "Central") &
    (kpi_df["PO No"].notna()) &
    (kpi_df["PO No"].astype(str).str.strip() != "") &
    (kpi_df["PO No"].astype(str).str.strip() != "-")
]

total_ordered = kpi_df["QuantityOrdered"].sum()
total_received = kpi_df["QuantityReceived"].sum()
total_rejected = kpi_df["QuantityRejected"].sum()
pending_qty = total_ordered - total_received

# ─────────────────────────────────────────────
# KPI DISPLAY
# ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

c1.metric("Central PO Ordered", f"{total_ordered:,.0f}")
c2.metric("Central PO Received", f"{total_received:,.0f}")
c3.metric("Central Pending", f"{pending_qty:,.0f}")
c4.metric("Central Rejected", f"{total_rejected:,.0f}")

st.markdown("---")
st.markdown("### GRN Records")

st.dataframe(filtered_df, use_container_width=True, hide_index=True)
