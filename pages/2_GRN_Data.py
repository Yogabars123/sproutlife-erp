import streamlit as st
import pandas as pd

st.set_page_config(page_title="GRN Data", layout="wide", page_icon="📥")

# ─────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #F8FAFC !important; }

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1280px !important; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid #E2E8F0;">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.3rem;">
        <span style="font-size:1.8rem;">📥</span>
        <h1 style="margin:0;font-size:1.75rem;font-weight:700;">GRN Data</h1>
    </div>
    <p style="margin:0;font-size:0.875rem;color:#94A3B8;padding-left:2.6rem;">
        Goods Receipt Note tracking & analysis
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Sproutlife Inventory.xlsx", sheet_name="GRN-Data")
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# Ensure numeric columns
for col in ["Qty Ordered", "Qty Received", "Qty Rejected"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ─────────────────────────────────────────────────────────────
# FILTER SECTION
# ─────────────────────────────────────────────────────────────
st.markdown("##### SEARCH & FILTER")

col1, col2, col3, col4 = st.columns([3,2,2,2])

with col1:
    search_grn = st.text_input("Search GRN")

with col2:
    po_options = ["All POs"] + sorted(df["PO Number"].dropna().astype(str).unique().tolist())
    po_number = st.selectbox("PO Number", po_options)

with col3:
    vendor_options = ["All Vendors"] + sorted(df["Vendor"].dropna().astype(str).unique().tolist())
    vendor = st.selectbox("Vendor", vendor_options)

with col4:
    warehouse_options = ["All Warehouses"] + sorted(df["Warehouse"].dropna().astype(str).unique().tolist())
    warehouse = st.selectbox("Warehouse", warehouse_options)

# ─────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────
filtered_df = df.copy()

if search_grn and "GRN Number" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["GRN Number"].astype(str)
        .str.contains(search_grn, case=False, na=False)
    ]

if po_number != "All POs":
    filtered_df = filtered_df[filtered_df["PO Number"].astype(str) == po_number]

if vendor != "All Vendors":
    filtered_df = filtered_df[filtered_df["Vendor"].astype(str) == vendor]

if warehouse != "All Warehouses":
    filtered_df = filtered_df[filtered_df["Warehouse"].astype(str) == warehouse]

# ─────────────────────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────────────────────
total_ordered = filtered_df["Qty Ordered"].sum()
total_received = filtered_df["Qty Received"].sum()
total_rejected = filtered_df["Qty Rejected"].sum()
pending_qty = total_ordered - total_received

# ─────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

def card(title, value, subtitle, color):
    return f"""
    <div style="background:{color};
                border-radius:14px;padding:1.4rem 1.6rem;color:white;
                box-shadow:0 6px 20px {color}40;">
        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;">
            {title}
        </div>
        <div style="font-size:1.8rem;font-weight:800;margin-top:5px;">
            {value:,.0f}
        </div>
        <div style="font-size:0.8rem;opacity:0.8;">
            {subtitle}
        </div>
    </div>
    """

with c1:
    st.markdown(card("Total QTY Ordered", total_ordered, "Across GRNs", "#1A56DB"), unsafe_allow_html=True)
with c2:
    st.markdown(card("Total QTY Received", total_received, "Against ordered qty", "#16A34A"), unsafe_allow_html=True)
with c3:
    st.markdown(card("Pending QTY", pending_qty, "Yet to be received", "#B45309"), unsafe_allow_html=True)
with c4:
    st.markdown(card("Total QTY Rejected", total_rejected, "Rejection across GRNs", "#DC2626"), unsafe_allow_html=True)

st.markdown("---")
st.markdown("##### GRN Records")

# ─────────────────────────────────────────────────────────────
# SHOW TABLE
# ─────────────────────────────────────────────────────────────
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
