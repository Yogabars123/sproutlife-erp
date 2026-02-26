import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

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
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 0 8px 0;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_grn():
    file_path = os.path.join(os.path.dirname(__file__), "..", "Sproutlife Inventory.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), "Sproutlife Inventory.xlsx")
    df = pd.read_excel(file_path, sheet_name="GRN-Data")

    # Normalize column names: strip spaces
    df.columns = df.columns.str.strip()
    df["Warehouse"] = df["Warehouse"].astype(str).str.strip()
    df["PO No"] = df["PO No"].astype(str).str.strip()

    for col in df.columns:
        if any(x in col.lower() for x in ["date"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in df.columns:
        if any(x in col.lower() for x in ["quantity", "qty", "value", "rate", "percentage", "rejection"]):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df_raw = load_grn()

# ---------------------------------------------------
# AUTO-DETECT COLUMN NAMES
# ---------------------------------------------------
def find_col(df, keywords):
    """Find column name by matching keywords (case-insensitive)"""
    for col in df.columns:
        col_lower = col.lower().replace(" ", "").replace("(", "").replace(")", "")
        if all(k.lower().replace(" ", "") in col_lower for k in keywords):
            return col
    return None

col_ordered   = find_col(df_raw, ["quantity", "ordered"]) or find_col(df_raw, ["qty", "ordered"])
col_received  = find_col(df_raw, ["quantity", "received"]) or find_col(df_raw, ["qty", "received"])
col_rejected  = find_col(df_raw, ["quantity", "rejected"]) or find_col(df_raw, ["qty", "rejected"])
col_rejection_pct = find_col(df_raw, ["percentage", "rejection"]) or find_col(df_raw, ["rejection", "%"])
col_grn_no    = find_col(df_raw, ["grn", "no"])
col_grn_month = find_col(df_raw, ["grn", "month"])
col_vendor    = find_col(df_raw, ["vendor", "name"])
col_po        = find_col(df_raw, ["po", "no"]) or find_col(df_raw, ["po", "number"]) or "PO No"
col_value_with_tax = find_col(df_raw, ["value", "received", "tax"]) or find_col(df_raw, ["values", "received", "with"])

# ---------------------------------------------------
# FILTER: Central WH + Has PO Number
# ---------------------------------------------------
if col_po in df_raw.columns:
    df_raw[col_po] = df_raw[col_po].astype(str).str.strip()
    df_raw = df_raw[
        df_raw[col_po].notna() &
        (df_raw[col_po] != "") &
        (~df_raw[col_po].str.upper().isin(["NAN", "NONE", "NAT", "NA", ""]))
    ]

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("📋 GRN Data")
st.caption("Central Warehouse — Purchase Order wise GRN tracking")

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# No filters - show all Central WH data with PO numbers
selected_po = "All POs"
df = df_raw.copy()

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
st.divider()

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

# ---------------------------------------------------
# PO SUMMARY (when a specific PO is selected)
# ---------------------------------------------------
if selected_po != "All POs":
    st.divider()
    st.markdown(f'<div class="section-title">📦 PO Summary — {selected_po}</div>', unsafe_allow_html=True)

    po_df = df[df[col_po] == selected_po] if col_po in df.columns else df
    po_ordered  = po_df[col_ordered].sum()  if col_ordered  else 0
    po_received = po_df[col_received].sum() if col_received else 0
    po_pending  = max(po_ordered - po_received, 0)
    po_rejected = po_df[col_rejected].sum() if col_rejected else 0
    po_value    = po_df[col_value_with_tax].sum() if col_value_with_tax and col_value_with_tax in po_df.columns else 0
    fulfillment_pct = (po_received / po_ordered * 100) if po_ordered > 0 else 0

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.metric("Ordered Qty", f"{po_ordered:,.0f}")
    with p2:
        st.metric("Received Qty", f"{po_received:,.0f}")
    with p3:
        st.metric("Pending Qty", f"{po_pending:,.0f}")
    with p4:
        st.metric("Rejected Qty", f"{po_rejected:,.0f}")
    with p5:
        st.metric("Fulfilment", f"{fulfillment_pct:.1f}%")

    st.progress(min(fulfillment_pct / 100, 1.0), text=f"PO Fulfilment: {fulfillment_pct:.1f}%")

# ---------------------------------------------------
# RESULTS COUNT + DOWNLOAD
# ---------------------------------------------------
st.divider()
r1, r2 = st.columns([6, 2])
with r1:
    st.markdown(f'<div class="section-title">📋 Showing {len(df):,} records</div>', unsafe_allow_html=True)
with r2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="GRN Data")
    st.download_button(
        label="⬇️ Download as Excel",
        data=buffer.getvalue(),
        file_name="GRN_Data_Filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ---------------------------------------------------
# DISPLAY TABLE
# ---------------------------------------------------
if df.empty:
    st.warning("No records match your current filters.")
else:
    st.dataframe(
        df,
        use_container_width=True,
        height=500,
        hide_index=True,
    )
