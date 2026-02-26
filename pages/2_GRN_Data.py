import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="GRN Data", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("📥 GRN Data")

@st.cache_data
def load_grn():
    file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="GRN-Data")
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if any(x in col.lower() for x in ["quantity", "qty", "value", "rate", "percentage"]):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df = load_grn()

# Auto-detect quantity columns
def find_col(df, keywords):
    for col in df.columns:
        col_lower = col.lower().replace(" ", "").replace("(", "").replace(")", "")
        if all(k.lower().replace(" ", "") in col_lower for k in keywords):
            return col
    return None

col_ordered  = find_col(df, ["quantity", "ordered"])
col_received = find_col(df, ["quantity", "received"])
col_rejected = find_col(df, ["quantity", "rejected"])
col_grn_no   = find_col(df, ["grn", "no"])

# Filters
f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

with f1:
    search = st.text_input("Search GRN")

with f2:
    po_col = find_col(df, ["po", "no"]) or find_col(df, ["po", "number"])
    if po_col and po_col in df.columns:
        po_options = ["All POs"] + sorted(df[po_col].dropna().astype(str).unique().tolist())
        selected_po = st.selectbox("PO Number", po_options)
    else:
        selected_po = "All POs"

with f3:
    vendor_col = find_col(df, ["vendor", "name"])
    if vendor_col and vendor_col in df.columns:
        vendor_options = ["All Vendors"] + sorted(df[vendor_col].dropna().astype(str).unique().tolist())
        selected_vendor = st.selectbox("Vendor", vendor_options)
    else:
        selected_vendor = "All Vendors"

with f4:
    if "Warehouse" in df.columns:
        wh_options = ["All Warehouses"] + sorted(df["Warehouse"].dropna().astype(str).unique().tolist())
        selected_wh = st.selectbox("Warehouse", wh_options)
    else:
        selected_wh = "All Warehouses"

# Apply filters
if search:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]
if selected_po != "All POs" and po_col and po_col in df.columns:
    df = df[df[po_col].astype(str) == selected_po]
if selected_vendor != "All Vendors" and vendor_col and vendor_col in df.columns:
    df = df[df[vendor_col].astype(str) == selected_vendor]
if selected_wh != "All Warehouses" and "Warehouse" in df.columns:
    df = df[df["Warehouse"].astype(str) == selected_wh]

# KPI Cards
total_ordered  = df[col_ordered].sum()  if col_ordered  and col_ordered  in df.columns else 0
total_received = df[col_received].sum() if col_received and col_received in df.columns else 0
total_rejected = df[col_rejected].sum() if col_rejected and col_rejected in df.columns else 0
total_pending  = max(total_ordered - total_received, 0)
total_grns     = df[col_grn_no].nunique() if col_grn_no and col_grn_no in df.columns else len(df)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Qty Ordered</div>
        <div class="value">{total_ordered:,.0f}</div>
        <div class="sub">{total_grns:,} GRNs</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #1a5c38 0%, #27855a 100%);">
        <div class="label">Total Qty Received</div>
        <div class="value">{total_received:,.0f}</div>
        <div class="sub">Against ordered qty</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b5a1a 0%, #b88a30 100%);">
        <div class="label">Pending Qty</div>
        <div class="value">{total_pending:,.0f}</div>
        <div class="sub">Yet to be received</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #7b2d2d 0%, #b94040 100%);">
        <div class="label">Total Qty Rejected</div>
        <div class="value">{total_rejected:,.0f}</div>
        <div class="sub">Rejection across GRNs</div>
    </div>""", unsafe_allow_html=True)

st.divider()
st.dataframe(df, use_container_width=True)
